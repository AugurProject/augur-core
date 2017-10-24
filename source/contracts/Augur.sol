pragma solidity 0.4.17;


import 'Controlled.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';


// AUDIT/CONSIDER: Is it better that this contract provide generic functions that are limited to whitelisted callers or for it to have many specific functions which have more limited and specific validation?
contract Augur is Controlled {
    event MarketCreated(address universe, address indexed market, address indexed marketCreator, uint256 marketCreationFee, string extraInfo);
    event DesignatedReportSubmitted(address universe, address indexed reporter, address indexed market, address stakeToken, uint256 amountStaked, uint256[] payoutNumerators);
    event ReportSubmitted(address universe, address indexed reporter, address indexed market, address stakeToken, uint256 amountStaked, uint256[] payoutNumerators);
    event WinningTokensRedeemed(address universe, address indexed reporter, address indexed market, address stakeToken, uint256 amountRedeemed, uint256 reportingFeesReceived, uint256[] payoutNumerators);
    event ReportsDisputed(address universe, address indexed disputer, address indexed market, uint8 reportingPhase, uint256 disputeBondAmount);
    event MarketFinalized(address universe, address indexed market);
    event UniverseForked(address indexed universe);
    event OrderCanceled(address universe, address indexed shareToken, address indexed sender, bytes32 indexed orderId, uint8 orderType, uint256 tokenRefund, uint256 sharesRefund);
    event OrderCreated(address universe, address indexed shareToken, address indexed creator, bytes32 indexed orderId, uint256 price, uint256 amount, uint256 numTokensEscrowed, uint256 numSharesEscrowed, uint256 tradeGroupId);
    event OrderFilled(address universe, address indexed shareToken, address indexed creator, address indexed filler, uint256 price, uint256 numCreatorShares, uint256 numCreatorTokens, uint256 numFillerShares, uint256 numFillerTokens, uint256 settlementFees, uint256 tradeGroupId);
    event ProceedsClaimed(address universe, address indexed sender, address indexed market, uint256 numShares, uint256 numPayoutTokens, uint256 finalTokenBalance);
    event UniverseCreated(address indexed parentUniverse, address indexed childUniverse);

    function trustedTransfer(ERC20 _token, address _from, address _to, uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        require(_amount > 0);
        _token.transferFrom(_from, _to, _amount);
        return true;
    }

    //
    // Logging
    //

    function logMarketCreated(IUniverse _universe, address _market, address _marketCreator, uint256 _marketCreationFee, string _extraInfo) public returns (bool) {
        require(_universe.isContainerForReportingWindow(IReportingWindow(msg.sender)));
        MarketCreated(_universe, _market, _marketCreator, _marketCreationFee, _extraInfo);
        return true;
    }

    function logDesignatedReportSubmitted(IUniverse _universe, address _reporter, address _market, address _stakeToken, uint256 _amountStaked, uint256[] _payoutNumerators) public returns (bool) {
        require(_universe.isContainerForStakeToken(IStakeToken(msg.sender)));
        DesignatedReportSubmitted(_universe, _reporter, _market, _stakeToken, _amountStaked, _payoutNumerators);
        return true;
    }

    function logReportSubmitted(IUniverse _universe, address _reporter, address _market, address _stakeToken, uint256 _amountStaked, uint256[] _payoutNumerators) public returns (bool) {
        require(_universe.isContainerForStakeToken(IStakeToken(msg.sender)));
        ReportSubmitted(_universe, _reporter, _market, _stakeToken, _amountStaked, _payoutNumerators);
        return true;
    }

    function logWinningTokensRedeemed(IUniverse _universe, address _reporter, address _market, address _stakeToken, uint256 _amountRedeemed, uint256 _reportingFeesReceived, uint256[] _payoutNumerators) public returns (bool) {
        require(_universe.isContainerForStakeToken(IStakeToken(msg.sender)));
        WinningTokensRedeemed(_universe, _reporter, _market, _stakeToken, _amountRedeemed, _reportingFeesReceived, _payoutNumerators);
        return true;
    }

    function logReportsDisputed(IUniverse _universe, address _disputer, address _market, uint8 _reportingPhase, uint256 _disputeBondAmount) public returns (bool) {
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        ReportsDisputed(_universe, _disputer, _market, _reportingPhase, _disputeBondAmount);
        return true;
    }

    function logMarketFinalized(IUniverse _universe, address _market) public returns (bool) {
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        MarketFinalized(_universe, _market);
        return true;
    }

    function logOrderCanceled(IUniverse _universe, address _shareToken, address _sender, bytes32 _orderId, uint8 _orderType, uint256 _tokenRefund, uint256 _sharesRefund) public onlyWhitelistedCallers returns (bool) {
        OrderCanceled(_universe, _shareToken, _sender, _orderId, _orderType, _tokenRefund, _sharesRefund);
        return true;
    }

    function logOrderCreated(IUniverse _universe, address _shareToken, address _creator, bytes32 _orderId, uint256 _price, uint256 _amount, uint256 _numTokensEscrowed, uint256 _numSharesEscrowed, uint256 _tradeGroupId) public onlyWhitelistedCallers returns (bool) {
        OrderCreated(_universe, _shareToken, _creator, _orderId, _price, _amount, _numTokensEscrowed, _numSharesEscrowed, _tradeGroupId);
        return true;
    }

    function logOrderFilled(IUniverse _universe, address _shareToken, address _creator, address _filler, uint256 _price, uint256 _numCreatorShares, uint256 _numCreatorTokens, uint256 _numFillerShares, uint256 _numFillerTokens, uint256 _settlementFees, uint256 _tradeGroupId) public onlyWhitelistedCallers returns (bool) {
        OrderFilled(_universe, _shareToken, _creator, _filler, _price, _numCreatorShares, _numCreatorTokens, _numFillerShares, _numFillerTokens, _settlementFees, _tradeGroupId);
        return true;
    }

    function logProceedsClaimed(IUniverse _universe, address _sender, address _market, uint256 _numShares, uint256 _numPayoutTokens, uint256 _finalTokenBalance) public onlyWhitelistedCallers returns (bool) {
        ProceedsClaimed(_universe, _sender, _market, _numShares, _numPayoutTokens, _finalTokenBalance);
        return true;
    }

    function logUniverseForked() public returns (bool) {
        UniverseForked(msg.sender);
    }

    function logUniverseCreated(IUniverse _childUniverse) public returns (bool) {
        IUniverse _parentUniverse = IUniverse(msg.sender);
        require(_parentUniverse.isParentOf(_childUniverse));
        UniverseCreated(_parentUniverse, _childUniverse);
        return true;
    }
}
