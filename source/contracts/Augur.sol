pragma solidity 0.4.18;

import 'Controlled.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/IParticipationToken.sol';
import 'reporting/IStakeToken.sol';
import 'reporting/IReputationToken.sol';
import 'trading/IShareToken.sol';
import 'trading/Order.sol';
import 'libraries/Extractable.sol';


// Centralized approval authority and event emissions
contract Augur is Controlled, Extractable {
    event MarketCreated(address indexed universe, bytes32 indexed topic, address indexed marketCreator, address market, uint256 marketCreationFee, string extraInfo);
    event DesignatedReportSubmitted(address indexed universe, address indexed reporter, address indexed market, address stakeToken, uint256 amountStaked, uint256[] payoutNumerators);
    event ReportSubmitted(address indexed universe, address indexed reporter, address indexed market, address stakeToken, uint256 amountStaked, uint256[] payoutNumerators);
    event WinningTokensRedeemed(address indexed universe, address indexed reporter, address indexed market, address stakeToken, uint256 amountRedeemed, uint256 reportingFeesReceived, uint256[] payoutNumerators);
    event ReportsDisputed(address indexed universe, address indexed disputer, address indexed market, IMarket.ReportingState reportingPhase, uint256 disputeBondAmount);
    event MarketFinalized(address indexed universe, address indexed market);
    event UniverseForked(address indexed universe);
    event OrderCanceled(address indexed universe, address indexed shareToken, address indexed sender, bytes32 orderId, Order.Types orderType, uint256 tokenRefund, uint256 sharesRefund);
    event OrderCreated(address indexed universe, address indexed shareToken, address indexed creator, bytes32 orderId, uint256 tradeGroupId);
    event OrderFilled(address indexed universe, address indexed shareToken, address filler, bytes32 orderId, uint256 numCreatorShares, uint256 numCreatorTokens, uint256 numFillerShares, uint256 numFillerTokens, uint256 marketCreatorFees, uint256 reporterFees, uint256 tradeGroupId);
    event TradingProceedsClaimed(address indexed universe, address indexed shareToken, address indexed sender, address market, uint256 numShares, uint256 numPayoutTokens, uint256 finalTokenBalance);
    event UniverseCreated(address indexed parentUniverse, address indexed childUniverse);
    event TokensTransferred(address indexed universe, address indexed token, address indexed from, address to, uint256 value);
    event TokensMinted(address indexed universe, address indexed token, address indexed target, uint256 amount);
    event TokensBurned(address indexed universe, address indexed token, address indexed target, uint256 amount);

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

    function logMarketCreated(IUniverse _universe, address _market, address _marketCreator, uint256 _marketCreationFee, bytes32 _topic, string _extraInfo) public returns (bool) {
        require(_universe == IUniverse(msg.sender));
        MarketCreated(_universe, _topic, _marketCreator, _market, _marketCreationFee, _extraInfo);
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

    function logReportsDisputed(IUniverse _universe, address _disputer, address _market, IMarket.ReportingState _reportingPhase, uint256 _disputeBondAmount) public returns (bool) {
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        ReportsDisputed(_universe, _disputer, _market, _reportingPhase, _disputeBondAmount);
        return true;
    }

    function logMarketFinalized(IUniverse _universe, address _market) public returns (bool) {
        require(_universe.isContainerForMarket(IMarket(msg.sender)));
        MarketFinalized(_universe, _market);
        return true;
    }

    function logOrderCanceled(IUniverse _universe, address _shareToken, address _sender, bytes32 _orderId, Order.Types _orderType, uint256 _tokenRefund, uint256 _sharesRefund) public onlyWhitelistedCallers returns (bool) {
        OrderCanceled(_universe, _shareToken, _sender, _orderId, _orderType, _tokenRefund, _sharesRefund);
        return true;
    }

    function logOrderCreated(IUniverse _universe, address _shareToken, address _creator, bytes32 _orderId, uint256 _tradeGroupId) public onlyWhitelistedCallers returns (bool) {
        OrderCreated(_universe, _shareToken, _creator, _orderId, _tradeGroupId);
        return true;
    }

    function logOrderFilled(IUniverse _universe, address _shareToken, address _filler, bytes32 _orderId, uint256 _numCreatorShares, uint256 _numCreatorTokens, uint256 _numFillerShares, uint256 _numFillerTokens, uint256 _marketCreatorFees, uint256 _reporterFees, uint256 _tradeGroupId) public onlyWhitelistedCallers returns (bool) {
        OrderFilled(_universe, _shareToken, _filler, _orderId, _numCreatorShares, _numCreatorTokens, _numFillerShares, _numFillerTokens, _marketCreatorFees, _reporterFees, _tradeGroupId);
        return true;
    }

    function logTradingProceedsClaimed(IUniverse _universe, address _shareToken, address _sender, address _market, uint256 _numShares, uint256 _numPayoutTokens, uint256 _finalTokenBalance) public onlyWhitelistedCallers returns (bool) {
        TradingProceedsClaimed(_universe, _shareToken, _sender, _market, _numShares, _numPayoutTokens, _finalTokenBalance);
        return true;
    }

    function logUniverseForked() public returns (bool) {
        UniverseForked(msg.sender);
        return true;
    }

    function logUniverseCreated(IUniverse _childUniverse) public returns (bool) {
        IUniverse _parentUniverse = IUniverse(msg.sender);
        require(_parentUniverse.isParentOf(_childUniverse));
        UniverseCreated(_parentUniverse, _childUniverse);
        return true;
    }

    function logParticipationTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(_universe.isContainerForParticipationToken(IParticipationToken(msg.sender)));
        TokensTransferred(_universe, msg.sender, _from, _to, _value);
        return true;
    }

    function logReputationTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(_universe.getReputationToken() == IReputationToken(msg.sender));
        TokensTransferred(_universe, msg.sender, _from, _to, _value);
        return true;
    }

    function logStakeTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(_universe.isContainerForStakeToken(IStakeToken(msg.sender)));
        TokensTransferred(_universe, msg.sender, _from, _to, _value);
        return true;
    }

    function logShareTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        require(_universe.isContainerForShareToken(IShareToken(msg.sender)));
        TokensTransferred(_universe, msg.sender, _from, _to, _value);
        return true;
    }

    function logReputationTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(_universe.getReputationToken() == IReputationToken(msg.sender));
        TokensBurned(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logReputationTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(_universe.getReputationToken() == IReputationToken(msg.sender));
        TokensMinted(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logShareTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(_universe.isContainerForShareToken(IShareToken(msg.sender)));
        TokensBurned(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logShareTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(_universe.isContainerForShareToken(IShareToken(msg.sender)));
        TokensMinted(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logParticipationTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(_universe.isContainerForParticipationToken(IParticipationToken(msg.sender)));
        TokensBurned(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logParticipationTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(_universe.isContainerForParticipationToken(IParticipationToken(msg.sender)));
        TokensMinted(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logStakeTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(_universe.isContainerForStakeToken(IStakeToken(msg.sender)));
        TokensBurned(_universe, msg.sender, _target, _amount);
        return true;
    }

    function logStakeTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        require(_universe.isContainerForStakeToken(IStakeToken(msg.sender)));
        TokensMinted(_universe, msg.sender, _target, _amount);
        return true;
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
