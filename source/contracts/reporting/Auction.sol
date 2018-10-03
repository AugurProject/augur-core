pragma solidity 0.4.24;

import 'libraries/DelegationTarget.sol';
import 'reporting/IAuction.sol';
import 'libraries/Initializable.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'reporting/Reporting.sol';


contract Auction is DelegationTarget, Initializable, IAuction {
    using SafeMathUint256 for uint256;

    enum AuctionType {
        DORMANT_1,
        DORMANT_2,
        UNRECORDED,
        DORMANT_3,
        DORMANT_4,
        DORMANT_5,
        RECORDED
    }

    IUniverse private universe;
    IReputationToken private reputationToken;
    uint256 public manualRepPriceInAttoEth;
    mapping(address => bool) private authorizedPriceFeeders; // The addresses which may alter the manual price feed. They may only enter a new price feed value. They may not add or remove authorized addresses or turn manual mode on or off.

    bool public bootstrapMode; // Indicates the auction is currently bootstrapping by selling off minted REP to get ETH for the ETH auction
    bool public bootstrapped; // Records that a bootstrap initialization occured. We can turn bootstrapping off if this has happened before.
    uint256 public initializationTime; // The time this contract was uploaded and initialized. The auction cadence is relative to this time

    uint256 public currentAuctionIndex; // The current auction index. Inicies starts at 0 relative to epoch where each week has 2
    AuctionType public currentAuctionType; // The current auction type.
    uint256 public initialAttoRepBalance; // The initial REP balance in attoREP considered for the current auction
    uint256 public initialAttoEthBalance; // The initial ETH balance in attoETH considered for the current auction
    uint256 public currentAttoRepBalance; // The REP balance in attoREP considered for the current auction
    uint256 public currentAttoEthBalance; // The ETH balance in attoETH considered for the current auction
    uint256 public currentUpperBoundRepPriceInAttoEth; // The upper bound for the price of REP in attoEth
    uint256 public currentLowerBoundRepPriceInAttoEth; // The lower bound for the price of REP in attoEth
    uint256 public initialRepSalePrice; // The initial price of REP in attoETH for the current auction
    uint256 public initialEthSalePrice; // The initial price of ETH in attoREP for the current auction
    uint256 public lastRepPrice; // The last auction's Rep price in attoETH, regardless of wether the result is used in determining reporting fees
    uint256 public repPrice; // The Rep price in attoETH that should be used to determine reporting fees during and immediately after an ignored auction.
    uint256 public currentRepPrice; // The Rep price in attoETH currently being derived via an active auction. Once the auction ends this will be used until it can be officially recorded as the repPrice at the beginning of an ignored auction

    modifier onlyAuthorizedPriceFeeder {
        require(authorizedPriceFeeders[msg.sender]);
        _;
    }

    modifier initializeNewAuctionIfNeeded {
        if (currentAuctionIndex != getAuctionIndexForCurrentTime()) {
            initializeNewAuction();
        }
        _;
    }

    function initialize(IUniverse _universe) public beforeInitialized returns (bool) {
        endInitialization();
        require(_universe != address(0));
        universe = _universe;
        reputationToken = universe.getReputationToken();
        initializationTime = controller.getTimestamp();
        authorizedPriceFeeders[controller.owner()] = true;
        manualRepPriceInAttoEth = Reporting.getAuctionInitialRepprice();
        lastRepPrice = manualRepPriceInAttoEth;
        repPrice = manualRepPriceInAttoEth;
        currentRepPrice = manualRepPriceInAttoEth;
        bootstrapMode = true;
        return true;
    }

    function initializeNewAuction() public returns (bool) {
        if (currentAuctionType == AuctionType.RECORDED) {
            repPrice = currentRepPrice;
        }
        lastRepPrice = currentRepPrice;
        currentAuctionType = getAuctionType();
        uint256 _currentAuctionIndex = getAuctionIndexForCurrentTime();
        require(currentAuctionType == AuctionType.UNRECORDED || currentAuctionType == AuctionType.RECORDED);
        require(currentAuctionIndex != _currentAuctionIndex);
        if (bootstrapped) {
            bootstrapMode = false;
        }
        require(!bootstrapMode || currentAuctionType == AuctionType.UNRECORDED);
        bootstrapped = true;

        uint256 _auctionRepBalanceTarget = reputationToken.totalSupply() / Reporting.getAuctionTargetSupplyDivisor();
        uint256 _repBalance = reputationToken.balanceOf(this);

        if (_repBalance < _auctionRepBalanceTarget) {
            reputationToken.mintForAuction(_auctionRepBalanceTarget.sub(_repBalance));
        } else {
            reputationToken.burnForAuction(_repBalance.sub(_auctionRepBalanceTarget));
        }

        initialAttoRepBalance = _auctionRepBalanceTarget;
        initialAttoEthBalance = address(this).balance;

        currentAttoRepBalance = initialAttoRepBalance;
        currentAttoEthBalance = initialAttoEthBalance;

        currentUpperBoundRepPriceInAttoEth = 0;
        currentLowerBoundRepPriceInAttoEth = 0;

        currentAuctionIndex = _currentAuctionIndex;

        initialRepSalePrice = lastRepPrice.mul(Reporting.getAuctionInitialPriceMultiplier());
        initialEthSalePrice = Reporting.getAuctionInitialPriceMultiplier().mul(10**36).div(lastRepPrice);
        return true;
    }

    function tradeRepForEth(uint256 _attoEthAmount) public initializeNewAuctionIfNeeded returns (bool) {
        require(!bootstrapMode);
        require(currentAttoEthBalance > 0);
        require(_attoEthAmount > 0);
        _attoEthAmount = _attoEthAmount.min(currentAttoEthBalance);
        uint256 _ethPriceInAttoRep = getEthSalePriceInAttoRep();
        uint256 _attoRepCost = _attoEthAmount.mul(_ethPriceInAttoRep) / 10**18;
        reputationToken.trustedAuctionTransfer(msg.sender, this, _attoRepCost);
        msg.sender.transfer(_attoEthAmount);
        uint256 _attoEthSold = initialAttoEthBalance.sub(currentAttoEthBalance);
        uint256 _newTotalAttoEthSold = _attoEthSold.add(_attoEthAmount);
        uint256 _repPriceInAttoEth = (10**36) / _ethPriceInAttoRep;
        currentLowerBoundRepPriceInAttoEth = currentLowerBoundRepPriceInAttoEth
            .mul(_attoEthSold)
            .add(_attoEthAmount.mul(_repPriceInAttoEth))
            .div(_newTotalAttoEthSold);
        currentAttoEthBalance = currentAttoEthBalance.sub(_attoEthAmount);
        currentRepPrice = currentLowerBoundRepPriceInAttoEth.add(currentUpperBoundRepPriceInAttoEth) / 2;
        return true;
    }

    function tradeEthForRep(uint256 _attoRepAmount) public initializeNewAuctionIfNeeded payable returns (bool) {
        require(currentAttoRepBalance > 0);
        require(_attoRepAmount > 0);
        _attoRepAmount = _attoRepAmount.min(currentAttoRepBalance);
        uint256 _repPriceInAttoEth = getRepSalePriceInAttoEth();
        uint256 _attoEthCost = _attoRepAmount.mul(_repPriceInAttoEth) / 10**18;
        // This will raise an exception if insufficient ETH was sent
        msg.sender.transfer(msg.value.sub(_attoEthCost));
        reputationToken.transfer(msg.sender, _attoRepAmount);
        uint256 _attoRepSold = initialAttoRepBalance.sub(currentAttoRepBalance);
        uint256 _newTotalAttoRepSold = _attoRepSold.add(_attoRepAmount);
        currentUpperBoundRepPriceInAttoEth = currentUpperBoundRepPriceInAttoEth
            .mul(_attoRepSold)
            .add(_attoRepAmount.mul(_repPriceInAttoEth))
            .div(_newTotalAttoRepSold);
        currentAttoRepBalance = currentAttoRepBalance.sub(_attoRepAmount);
        // We don't update the price while in bootstrap mode since its a one sided auction
        if (!bootstrapMode) {
            currentRepPrice = currentUpperBoundRepPriceInAttoEth.add(currentUpperBoundRepPriceInAttoEth) / 2;
        }
        return true;
    }

    function getRepSalePriceInAttoEth() public initializeNewAuctionIfNeeded returns (uint256) {
        uint256 _timePassed = controller.getTimestamp().sub(initializationTime).sub(currentAuctionIndex * 1 days);
        uint256 _priceDecrease = initialRepSalePrice.mul(_timePassed) / Reporting.getAuctionDuration();
        return initialRepSalePrice.sub(_priceDecrease);
    }

    function getEthSalePriceInAttoRep() public initializeNewAuctionIfNeeded returns (uint256) {
        require(!bootstrapMode);
        uint256 _timePassed = controller.getTimestamp().sub(initializationTime).sub(currentAuctionIndex * 1 days);
        uint256 _priceDecrease = initialEthSalePrice.mul(_timePassed) / Reporting.getAuctionDuration();
        return initialEthSalePrice.sub(_priceDecrease);
    }

    function getRepPriceInAttoEth() public view returns (uint256) {
        // Use the manually provided REP price if the Auction system is not used for setting fees yet
        if (!controller.useAuction()) {
            return manualRepPriceInAttoEth;
        }

        // If this auction is over and it is a recorded auction use the price it found
        if (getAuctionIndexForCurrentTime() != currentAuctionIndex && currentAuctionType == AuctionType.RECORDED) {
            return currentRepPrice;
        }

        return repPrice;
    }

    function getAuctionIndexForCurrentTime() public view returns (uint256) {
        return controller.getTimestamp().sub(initializationTime) / Reporting.getAuctionDuration();
    }

    function isActive() public view returns (bool) {
        AuctionType _auctionType = getAuctionType();
        return _auctionType == AuctionType.UNRECORDED || _auctionType == AuctionType.RECORDED;
    }

    function getAuctionType() public view returns (AuctionType) {
        uint256 _auctionDay = getAuctionIndexForCurrentTime() % 7;
        return AuctionType(_auctionDay);
    }

    function getAuctionStartTime() public view returns (uint256) {
        uint256 _auctionIndex = getAuctionIndexForCurrentTime();
        uint256 _auctionDay = _auctionIndex % 7;
        uint256 _weekStart = initializationTime.add(_auctionIndex).sub(_auctionDay);
        uint256 _addedTime = _auctionDay > uint256(AuctionType.UNRECORDED) ? uint256(AuctionType.RECORDED) : uint256(AuctionType.UNRECORDED);
        return _weekStart.add(_addedTime.mul(Reporting.getAuctionDuration()));
    }

    function getAuctionEndTime() public view returns (uint256) {
        uint256 _auctionIndex = getAuctionIndexForCurrentTime();
        uint256 _auctionDay = _auctionIndex % 7;
        uint256 _weekStart = initializationTime.add(_auctionIndex).sub(_auctionDay);
        uint256 _addedTime = _auctionDay > uint256(AuctionType.UNRECORDED) ? uint256(AuctionType.RECORDED) : uint256(AuctionType.UNRECORDED);
        _addedTime += 1;
        return _weekStart.add(_addedTime.mul(Reporting.getAuctionDuration()));
    }

    function getUniverse() public view afterInitialized returns (IUniverse) {
        return universe;
    }

    function getReputationToken() public view afterInitialized returns (IReputationToken) {
        return reputationToken;
    }

    function setRepPriceInAttoEth(uint256 _repPriceInAttoEth) external afterInitialized onlyAuthorizedPriceFeeder returns (bool) {
        manualRepPriceInAttoEth = _repPriceInAttoEth;
        return true;
    }

    function addToAuthorizedPriceFeeders(address _priceFeeder) public afterInitialized onlyKeyHolder returns (bool) {
        authorizedPriceFeeders[_priceFeeder] = true;
        return true;
    }

    function removeFromAuthorizedPriceFeeders(address _priceFeeder) public afterInitialized onlyKeyHolder returns (bool) {
        authorizedPriceFeeders[_priceFeeder] = false;
        return true;
    }
}
