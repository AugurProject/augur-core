pragma solidity 0.4.24;

import 'Controlled.sol';
import 'reporting/IAuction.sol';
import 'libraries/Initializable.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IV2ReputationToken.sol';
import 'reporting/IReputationToken.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'reporting/Reporting.sol';
import 'trading/ICash.sol';
import 'reporting/IAuctionToken.sol';
import 'factories/AuctionTokenFactory.sol';


contract Auction is Controlled, Initializable, IAuction {
    using SafeMathUint256 for uint256;

    enum RoundType {
        DORMANT_1,
        DORMANT_2,
        UNRECORDED,
        DORMANT_3,
        DORMANT_4,
        DORMANT_5,
        RECORDED
    }

    IUniverse private universe;
    IV2ReputationToken private reputationToken;
    ICash public cash;
    AuctionTokenFactory public auctionTokenFactory;
    uint256 public manualRepPriceInAttoEth;
    mapping(address => bool) private authorizedPriceFeeders; // The addresses which may alter the manual price feed. They may only enter a new price feed value. They may not add or remove authorized addresses or turn manual mode on or off.

    bool public bootstrapMode; // Indicates the auction is currently bootstrapping by selling off minted REP to get ETH for the ETH auction
    bool public bootstrapped; // Records that a bootstrap initialization occured. We can turn bootstrapping off if this has happened before.
    uint256 public initializationTime; // The time this contract was uploaded and initialized. The auction cadence is relative to this time

    uint256 public feeBalance; // The ETH this contract has received in fees.
    uint256 public currentAuctionIndex; // The current auction index. Indicies starts at 0 relative to epoch where each week has 2
    RoundType public currentRoundType; // The current auction type.
    uint256 public initialAttoRepBalance; // The initial REP balance in attoREP considered for the current auction
    uint256 public initialAttoEthBalance; // The initial ETH balance in attoETH considered for the current auction
    uint256 public initialRepSalePrice; // The initial price of REP in attoETH for the current auction
    uint256 public initialEthSalePrice; // The initial price of ETH in attoREP for the current auction
    uint256 public lastRepPrice; // The last auction's Rep price in attoETH, regardless of wether the result is used in determining reporting fees
    uint256 public repPrice; // The Rep price in attoETH that should be used to determine reporting fees during and immediately after an ignored auction.

    modifier onlyAuthorizedPriceFeeder {
        require(authorizedPriceFeeders[msg.sender]);
        _;
    }

    function initialize(IUniverse _universe) public beforeInitialized returns (bool) {
        endInitialization();
        require(_universe != address(0));
        universe = _universe;
        reputationToken = IV2ReputationToken(universe.getReputationToken());
        cash = ICash(controller.lookup("Cash"));
        auctionTokenFactory = AuctionTokenFactory(controller.lookup("AuctionTokenFactory"));
        initializationTime = controller.getTimestamp();
        authorizedPriceFeeders[controller.owner()] = true;
        manualRepPriceInAttoEth = Reporting.getAuctionInitialRepPrice();
        lastRepPrice = manualRepPriceInAttoEth;
        repPrice = manualRepPriceInAttoEth;
        bootstrapMode = true;
        return true;
    }

    function initializeNewAuction() public returns (bool) {
        uint256 _derivedRepPrice = getDerivedRepPriceInAttoEth();
        if (currentRoundType == RoundType.RECORDED) {
            repPrice = _derivedRepPrice;
        }
        lastRepPrice = _derivedRepPrice;
        currentRoundType = getRoundType();
        uint256 _currentAuctionIndex = getAuctionIndexForCurrentTime();
        require(currentRoundType == RoundType.UNRECORDED || currentRoundType == RoundType.RECORDED);
        require(currentAuctionIndex != _currentAuctionIndex);
        if (bootstrapped) {
            bootstrapMode = false;
        }
        require(!bootstrapMode || currentRoundType == RoundType.UNRECORDED);
        bootstrapped = true;

        // Get any funds from the previously participated in auction that are set to be distributed
        if (repAuctionToken != IAuctionToken(0)) {
            repAuctionToken.retrieveFunds();
        }
        if (ethAuctionToken != IAuctionToken(0)) {
            ethAuctionToken.retrieveFunds();
        }

        uint256 _auctionRepBalanceTarget = reputationToken.totalSupply() / Reporting.getAuctionTargetSupplyDivisor();
        uint256 _repBalance = reputationToken.balanceOf(this);

        if (_repBalance < _auctionRepBalanceTarget) {
            reputationToken.mintForAuction(_auctionRepBalanceTarget.sub(_repBalance));
        }

        initialAttoRepBalance = reputationToken.balanceOf(this);
        initialAttoEthBalance = cash.balanceOf(this);

        currentAuctionIndex = _currentAuctionIndex;

        initialRepSalePrice = lastRepPrice.mul(Reporting.getAuctionInitialPriceMultiplier());
        initialEthSalePrice = Reporting.getAuctionInitialPriceMultiplier().mul(10**36).div(lastRepPrice);

        // Create and fund Tokens
        repAuctionToken = auctionTokenFactory.createAuctionToken(controller, this, reputationToken, currentAuctionIndex);
        if (!bootstrapMode) {
            ethAuctionToken = auctionTokenFactory.createAuctionToken(controller, this, cash, currentAuctionIndex);
        }
        controller.getAugur().recordAuctionTokens(universe);

        reputationToken.transfer(repAuctionToken, initialAttoRepBalance);
        cash.transfer(ethAuctionToken, initialAttoEthBalance);
        return true;
    }

    function initializeNewAuctionIfNeeded() private returns (bool) {
        if (currentAuctionIndex != getAuctionIndexForCurrentTime()) {
            initializeNewAuction();
        }
        return true;
    }

    function tradeRepForEth(uint256 _attoEthAmount) public returns (bool) {
        initializeNewAuctionIfNeeded();
        require(!bootstrapMode);
        uint256 _currentAttoEthBalance = getCurrentAttoEthBalance();
        require(_currentAttoEthBalance > 0);
        require(_attoEthAmount > 0);
        _attoEthAmount = _attoEthAmount.min(_currentAttoEthBalance);
        uint256 _ethPriceInAttoRep = getEthSalePriceInAttoRep();
        uint256 _attoRepCost = _attoEthAmount.mul(_ethPriceInAttoRep) / 10**18;
        reputationToken.trustedAuctionTransfer(msg.sender, this, _attoRepCost);
        ethAuctionToken.mintForPurchaser(msg.sender, _attoRepCost);

        // Burn any REP purchased using fee income
        if (feeBalance > 0) {
            uint256 _feesUsed = feeBalance.min(_attoEthAmount);
            uint256 _burnAmount = _attoRepCost.mul(_feesUsed).div(_attoEthAmount);
            reputationToken.burnForAuction(_burnAmount);
            feeBalance = feeBalance.sub(_feesUsed);
        }

        return true;
    }

    function tradeEthForRep(uint256 _attoRepAmount) public payable returns (bool) {
        initializeNewAuctionIfNeeded();
        uint256 _currentAttoRepBalance = getCurrentAttoRepBalance();
        require(_currentAttoRepBalance > 0);
        require(_attoRepAmount > 0);
        _attoRepAmount = _attoRepAmount.min(_currentAttoRepBalance);
        uint256 _repPriceInAttoEth = getRepSalePriceInAttoEth();
        uint256 _attoEthCost = _attoRepAmount.mul(_repPriceInAttoEth) / 10**18;
        // This will raise an exception if insufficient ETH was sent
        msg.sender.transfer(msg.value.sub(_attoEthCost));
        cash.depositEther.value(_attoEthCost)();
        repAuctionToken.mintForPurchaser(msg.sender, _attoEthCost);
        return true;
    }

    function recordFees(uint256 _feeAmount) public returns (bool) {
        require(msg.sender == controller.lookup("CompleteSets") || msg.sender == controller.lookup("ClaimTradingProceeds"));
        feeBalance = feeBalance.add(_feeAmount);
        return true;
    }

    function getRepSalePriceInAttoEth() public returns (uint256) {
        initializeNewAuctionIfNeeded();
        uint256 _timePassed = controller.getTimestamp().sub(initializationTime).sub(currentAuctionIndex * 1 days);
        uint256 _priceDecrease = initialRepSalePrice.mul(_timePassed) / Reporting.getAuctionDuration();
        return initialRepSalePrice.sub(_priceDecrease);
    }

    function getEthSalePriceInAttoRep() public returns (uint256) {
        initializeNewAuctionIfNeeded();
        require(!bootstrapMode);
        uint256 _timePassed = controller.getTimestamp().sub(initializationTime).sub(currentAuctionIndex * 1 days);
        uint256 _priceDecrease = initialEthSalePrice.mul(_timePassed) / Reporting.getAuctionDuration();
        return initialEthSalePrice.sub(_priceDecrease);
    }

    function getCurrentAttoRepBalance() public returns (uint256) {
        uint256 _repSalePriceInAttoEth = getRepSalePriceInAttoEth();
        uint256 _ethSupply = repAuctionToken.totalSupply();
        uint256 _attoRepSold = _ethSupply.mul(10**18).div(_repSalePriceInAttoEth);
        if (_attoRepSold >= initialAttoRepBalance) {
            return 0;
        }
        return initialAttoRepBalance.sub(_attoRepSold);
    }

    function getCurrentAttoEthBalance() public returns (uint256) {
        uint256 _ethSalePriceInAttoRep = getEthSalePriceInAttoRep();
        uint256 _repSupply = ethAuctionToken.totalSupply();
        uint256 _attoEthSold = _repSupply.mul(10**18).div(_ethSalePriceInAttoRep);
        if (_attoEthSold >= initialAttoEthBalance) {
            return 0;
        }
        return initialAttoEthBalance.sub(_attoEthSold);
    }

    function getDerivedRepPriceInAttoEth() public view returns (uint256) {
        if (repAuctionToken == IAuctionToken(0) || ethAuctionToken == IAuctionToken(0)) {
            return repPrice;
        }
        uint256 _repAuctionTokenMaxSupply = repAuctionToken.maxSupply();
        uint256 _ethAuctionTokenMaxSupply = ethAuctionToken.maxSupply();
        if (_repAuctionTokenMaxSupply == 0 || _ethAuctionTokenMaxSupply == 0) {
            return repPrice;
        }
        uint256 _upperBoundRepPrice = repAuctionToken.maxSupply().mul(10**18).div(initialAttoRepBalance);
        uint256 _lowerBoundRepPrice = initialAttoEthBalance.mul(10**18).div(_ethAuctionTokenMaxSupply);
        return _upperBoundRepPrice.add(_lowerBoundRepPrice) / 2;
    }

    function getRepPriceInAttoEth() public view returns (uint256) {
        // Use the manually provided REP price if the Auction system is not used for setting fees yet
        if (!controller.useAuction()) {
            return manualRepPriceInAttoEth;
        }

        // If this auction is over and it is a recorded auction use the price it found
        if (getAuctionIndexForCurrentTime() != currentAuctionIndex && currentRoundType == RoundType.RECORDED) {
            return getDerivedRepPriceInAttoEth();
        }

        return repPrice;
    }

    function getAuctionIndexForCurrentTime() public view returns (uint256) {
        return controller.getTimestamp().sub(initializationTime) / Reporting.getAuctionDuration();
    }

    function isActive() public view returns (bool) {
        RoundType _roundType = getRoundType();
        return _roundType == RoundType.UNRECORDED || _roundType == RoundType.RECORDED;
    }

    function getRoundType() public view returns (RoundType) {
        uint256 _auctionDay = getAuctionIndexForCurrentTime() % 7;
        return RoundType(_auctionDay);
    }

    function getAuctionStartTime() public view returns (uint256) {
        uint256 _auctionIndex = getAuctionIndexForCurrentTime();
        uint256 _auctionDay = _auctionIndex % 7;
        uint256 _weekStart = initializationTime.add(_auctionIndex).sub(_auctionDay);
        uint256 _addedTime = _auctionDay > uint256(RoundType.UNRECORDED) ? uint256(RoundType.RECORDED) : uint256(RoundType.UNRECORDED);
        return _weekStart.add(_addedTime.mul(Reporting.getAuctionDuration()));
    }

    function getAuctionEndTime() public view returns (uint256) {
        uint256 _auctionIndex = getAuctionIndexForCurrentTime();
        uint256 _auctionDay = _auctionIndex % 7;
        uint256 _weekStart = initializationTime.add(_auctionIndex).sub(_auctionDay);
        uint256 _addedTime = _auctionDay > uint256(RoundType.UNRECORDED) ? uint256(RoundType.RECORDED) : uint256(RoundType.UNRECORDED);
        _addedTime += 1;
        return _weekStart.add(_addedTime.mul(Reporting.getAuctionDuration()));
    }

    function getUniverse() public view afterInitialized returns (IUniverse) {
        return universe;
    }

    function getReputationToken() public view afterInitialized returns (IReputationToken) {
        return IReputationToken(reputationToken);
    }

    function setRepPriceInAttoEth(uint256 _repPriceInAttoEth) external afterInitialized onlyAuthorizedPriceFeeder returns (bool) {
        manualRepPriceInAttoEth = _repPriceInAttoEth;
        return true;
    }

    function addAuthorizedPriceFeeder(address _priceFeeder) public afterInitialized onlyKeyHolder returns (bool) {
        authorizedPriceFeeders[_priceFeeder] = true;
        return true;
    }

    function removeAuthorizedPriceFeeder(address _priceFeeder) public afterInitialized onlyKeyHolder returns (bool) {
        authorizedPriceFeeders[_priceFeeder] = false;
        return true;
    }
}
