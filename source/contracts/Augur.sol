pragma solidity 0.4.18;

import 'Controlled.sol';
import 'IAugur.sol';
import 'libraries/token/ERC20.sol';
import 'factories/UniverseFactory.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/IFeeWindow.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingParticipant.sol';
import 'reporting/IDisputeCrowdsourcer.sol';
import 'trading/IShareToken.sol';
import 'trading/Order.sol';
import 'libraries/Extractable.sol';


// Centralized approval authority and event emissions
contract Augur is Controlled, Extractable, IAugur {
    event MarketCreated(bytes32 indexed topic, string description, string extraInfo, address indexed universe, address market, address indexed marketCreator, bytes32[] outcomes, uint256 marketCreationFee, int256 minPrice, int256 maxPrice, IMarket.MarketType marketType);
    event InitialReportSubmitted(address indexed universe, address indexed reporter, address indexed market, uint256 amountStaked, bool isDesignatedReporter, uint256[] payoutNumerators);
    event DisputeCrowdsourcerCreated(address indexed universe, address indexed market, address disputeCrowdsourcer, uint256[] payoutNumerators, uint256 size);
    event DisputeCrowdsourcerContribution(address indexed universe, address indexed reporter, address indexed market, address disputeCrowdsourcer, uint256 amountStaked);
    event DisputeCrowdsourcerCompleted(address indexed universe, address indexed market, address disputeCrowdsourcer);
    event WinningsRedeemed(address indexed universe, address indexed reporter, address indexed market, address reportingParticipant, uint256 amountRedeemed, uint256 reportingFeesReceived, uint256[] payoutNumerators);
    event MarketFinalized(address indexed universe, address indexed market);
    event UniverseForked(address indexed universe);
    event UniverseCreated(address indexed parentUniverse, address indexed childUniverse);
    event OrderCanceled(address indexed universe, address indexed shareToken, address indexed sender, bytes32 orderId, Order.Types orderType, uint256 tokenRefund, uint256 sharesRefund);
    // The ordering here is to match functions higher in the call chain to avoid stack depth issues
    event OrderCreated(Order.Types orderType, uint256 amount, uint256 price, address indexed creator, uint256 moneyEscrowed, uint256 sharesEscrowed, bytes32 tradeGroupId, bytes32 orderId, address indexed universe, address indexed shareToken);
    event OrderFilled(address indexed universe, address indexed shareToken, address filler, bytes32 orderId, uint256 numCreatorShares, uint256 numCreatorTokens, uint256 numFillerShares, uint256 numFillerTokens, uint256 marketCreatorFees, uint256 reporterFees, bytes32 tradeGroupId);
    event TradingProceedsClaimed(address indexed universe, address indexed shareToken, address indexed sender, address market, uint256 numShares, uint256 numPayoutTokens, uint256 finalTokenBalance);
    event TokensTransferred(address indexed universe, address indexed token, address indexed from, address to, uint256 value);
    event TokensMinted(address indexed universe, address indexed token, address indexed target, uint256 amount);
    event TokensBurned(address indexed universe, address indexed token, address indexed target, uint256 amount);
    event FeeWindowCreated(address indexed universe, address feeWindow, uint256 startTime, uint256 endTime, uint256 id);
    event WhitelistAddition(address addition);
    event RegistryAddition(bytes32 key, address addition, bytes20 commitHash, bytes32 bytecodeHash);

    mapping(address => bool) private universes;

    //
    // Universe
    //

    function createGenesisUniverse() public returns (IUniverse) {
        return createUniverse(IUniverse(0), bytes32(0));
    }

    function createChildUniverse(bytes32 _parentPayoutDistributionHash) public returns (IUniverse) {
        IUniverse _parentUniverse = IUniverse(msg.sender);
        require(isKnownUniverse(_parentUniverse));
        return createUniverse(_parentUniverse, _parentPayoutDistributionHash);
    }

    function createUniverse(IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) private returns (IUniverse) {
        UniverseFactory _universeFactory = UniverseFactory(controller.lookup("UniverseFactory"));
        IUniverse _newUniverse = _universeFactory.createUniverse(controller, _parentUniverse, _parentPayoutDistributionHash);
        universes[_newUniverse] = true;
        return _newUniverse;
    }

    function isKnownUniverse(IUniverse _universe) public view returns (bool) {
        return universes[_universe];
    }

    //
    // Transfer
    //

    function trustedTransfer(ERC20 _token, address _from, address _to, uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        require(_amount > 0);
        _token.transferFrom(_from, _to, _amount);
        return true;
    }

    //
    // Logging
    //

    // This signature is intended for the categorical market creation. We use two signatures for the same event because of stack depth issues which can be circumvented by maintaining order of paramaters
    function logMarketCreated(bytes32 _topic, string _description, string _extraInfo, IUniverse _universe, address _market, address _marketCreator, bytes32[] _outcomes, int256 _minPrice, int256 _maxPrice, IMarket.MarketType _marketType) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe == IUniverse(msg.sender));
        MarketCreated(_topic, _description, _extraInfo, _universe, _market, _marketCreator, _outcomes, _universe.getOrCacheMarketCreationCost(), _minPrice, _maxPrice, _marketType);
        return true;
    }

    // This signature is intended for binary and scalar market creation. See function comment above for explanation.
    function logMarketCreated(bytes32 _topic, string _description, string _extraInfo, IUniverse _universe, address _market, address _marketCreator, int256 _minPrice, int256 _maxPrice, IMarket.MarketType _marketType) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe == IUniverse(msg.sender));
        MarketCreated(_topic, _description, _extraInfo, _universe, _market, _marketCreator, new bytes32[](0), _universe.getOrCacheMarketCreationCost(), _minPrice, _maxPrice, _marketType);
        return true;
    }

    function logInitialReportSubmitted(IUniverse _universe, address _reporter, address _market, uint256 _amountStaked, bool _isDesignatedReporter, uint256[] _payoutNumerators) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        InitialReportSubmitted(_universe, _reporter, _market, _amountStaked, _isDesignatedReporter, _payoutNumerators);
        return true;
    }

    function logDisputeCrowdsourcerCreated(IUniverse _universe, address _market, address _disputeCrowdsourcer, uint256[] _payoutNumerators, uint256 _size) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        DisputeCrowdsourcerCreated(_universe, _market, _disputeCrowdsourcer, _payoutNumerators, _size);
        return true;
    }

    function logDisputeCrowdsourcerContribution(IUniverse _universe, address _reporter, address _market, address _disputeCrowdsourcer, uint256 _amountStaked) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        DisputeCrowdsourcerContribution(_universe, _reporter, _market, _disputeCrowdsourcer, _amountStaked);
        return true;
    }

    function logDisputeCrowdsourcerCompleted(IUniverse _universe, address _market, address _disputeCrowdsourcer) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        DisputeCrowdsourcerCompleted(_universe, _market, _disputeCrowdsourcer);
        return true;
    }

    function logWinningStakeRedeemed(IUniverse _universe, address _reporter, address _market, address _reportingParticipant, uint256 _amountRedeemed, uint256 _reportingFeesReceived, uint256[] _payoutNumerators) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        WinningsRedeemed(_universe, _reporter, _market, _reportingParticipant, _amountRedeemed, _reportingFeesReceived, _payoutNumerators);
        return true;
    }

    function logMarketFinalized(IUniverse _universe) public returns (bool) {
        require(isKnownUniverse(_universe));
        IMarket _market = IMarket(msg.sender);
        require(_universe.isContainerForMarket(_market));
        MarketFinalized(_universe, _market);
        return true;
    }

    function logOrderCanceled(IUniverse _universe, address _shareToken, address _sender, bytes32 _orderId, Order.Types _orderType, uint256 _tokenRefund, uint256 _sharesRefund) public onlyWhitelistedCallers returns (bool) {
        OrderCanceled(_universe, _shareToken, _sender, _orderId, _orderType, _tokenRefund, _sharesRefund);
        return true;
    }

    function logOrderCreated(Order.Types _orderType, uint256 _amount, uint256 _price, address _creator, uint256 _moneyEscrowed, uint256 _sharesEscrowed, bytes32 _tradeGroupId, bytes32 _orderId, IUniverse _universe, address _shareToken) public onlyWhitelistedCallers returns (bool) {
        OrderCreated(_orderType, _amount, _price, _creator, _moneyEscrowed, _sharesEscrowed, _tradeGroupId, _orderId, _universe, _shareToken);
        return true;
    }

    function logOrderFilled(IUniverse _universe, address _shareToken, address _filler, bytes32 _orderId, uint256 _numCreatorShares, uint256 _numCreatorTokens, uint256 _numFillerShares, uint256 _numFillerTokens, uint256 _marketCreatorFees, uint256 _reporterFees, bytes32 _tradeGroupId) public onlyWhitelistedCallers returns (bool) {
        OrderFilled(_universe, _shareToken, _filler, _orderId, _numCreatorShares, _numCreatorTokens, _numFillerShares, _numFillerTokens, _marketCreatorFees, _reporterFees, _tradeGroupId);
        return true;
    }

    function logTradingProceedsClaimed(IUniverse _universe, address _shareToken, address _sender, address _market, uint256 _numShares, uint256 _numPayoutTokens, uint256 _finalTokenBalance) public onlyWhitelistedCallers returns (bool) {
        TradingProceedsClaimed(_universe, _shareToken, _sender, _market, _numShares, _numPayoutTokens, _finalTokenBalance);
        return true;
    }

    function logUniverseForked() public returns (bool) {
        require(universes[msg.sender]);
        UniverseForked(msg.sender);
        return true;
    }

    function logUniverseCreated(IUniverse _childUniverse) public returns (bool) {
        require(universes[msg.sender]);
        IUniverse _parentUniverse = IUniverse(msg.sender);
        require(_parentUniverse.isParentOf(_childUniverse));
        UniverseCreated(_parentUniverse, _childUniverse);
        return true;
    }

    function logFeeWindowTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForFeeWindow(IFeeWindow(msg.sender)));
        TokensTransferred(_universe, msg.sender, _from, _to, _value);
        return true;
    }

    function logReputationTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.getReputationToken() == IReputationToken(msg.sender));
        TokensTransferred(_universe, msg.sender, _from, _to, _value);
        return true;
    }

    function logDisputeCrowdsourcerTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        TokensTransferred(_universe, msg.sender, _from, _to, _value);
        return true;
    }

    function logShareTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForShareToken(IShareToken(msg.sender)));
        TokensTransferred(_universe, msg.sender, _from, _to, _value);
        return true;
    }

    function logReputationTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.getReputationToken() == IReputationToken(msg.sender));
        TokensBurned(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logReputationTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.getReputationToken() == IReputationToken(msg.sender));
        TokensMinted(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logShareTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForShareToken(IShareToken(msg.sender)));
        TokensBurned(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logShareTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForShareToken(IShareToken(msg.sender)));
        TokensMinted(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logFeeWindowBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForFeeWindow(IFeeWindow(msg.sender)));
        TokensBurned(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logFeeWindowMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForFeeWindow(IFeeWindow(msg.sender)));
        TokensMinted(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logDisputeCrowdsourcerTokensBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        TokensBurned(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logDisputeCrowdsourcerTokensMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        TokensMinted(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logFeeWindowCreated(IFeeWindow _feeWindow, uint256 _id) public returns (bool) {
        require(universes[msg.sender]);
        FeeWindowCreated(msg.sender, _feeWindow, _feeWindow.getStartTime(), _feeWindow.getEndTime(), _id);
        return true;
    }

    function logFeeTokenTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForFeeToken(IFeeToken(msg.sender)));
        TokensTransferred(_universe, msg.sender, _from, _to, _value);
        return true;
    }

    function logFeeTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForFeeToken(IFeeToken(msg.sender)));
        TokensBurned(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logFeeTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(isKnownUniverse(_universe));
        require(_universe.isContainerForFeeToken(IFeeToken(msg.sender)));
        TokensMinted(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logContractAddedToWhitelist(address _addition) public onlyControllerCaller returns (bool) {
        WhitelistAddition(_addition);
        return true;
    }

    function logContractAddedToRegistry(bytes32 _key, address _address, bytes20 _commitHash, bytes32 _bytecodeHash) public onlyControllerCaller returns (bool) {
        RegistryAddition(_key, _address, _commitHash, _bytecodeHash);
        return true;
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
