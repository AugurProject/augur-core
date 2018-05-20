pragma solidity 0.4.20;


import 'Controlled.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/IFeeWindow.sol';
import 'reporting/IReputationToken.sol';
import 'trading/IShareToken.sol';
import 'trading/Order.sol';


// AUDIT/CONSIDER: Is it better that this contract provide generic functions that are limited to whitelisted callers or for it to have many specific functions which have more limited and specific validation?
contract MockAugur is Controlled {

    function reset() public {
        logMarketCreatedCalledValue = false;
        logReportsDisputedCalledValue = false;
        logUniverseForkedCalledValue = false;
        logReputationTokensTransferredCalledValue = false;
        logMarketFinalizedCalledValue = false;
    }

    function trustedTransfer(ERC20 _token, address _from, address _to, uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        return true;
    }

    //
    // Logging
    //
    bool private logMarketCreatedCalledValue;

    function logMarketCreatedCalled() public returns(bool) {return logMarketCreatedCalledValue;}

    function logMarketCreated(bytes32 _topic, string _description, string _extraInfo, IUniverse _universe, address _market, address _marketCreator, bytes32[] _outcomes, int256 _minPrice, int256 _maxPrice, IMarket.MarketType _marketType) public returns (bool) {
        logMarketCreatedCalledValue = true;
        return true;
    }

    function logMarketCreated(bytes32 _topic, string _description, string _extraInfo, IUniverse _universe, address _market, address _marketCreator, int256 _minPrice, int256 _maxPrice, IMarket.MarketType _marketType) public returns (bool) {
        logMarketCreatedCalledValue = true;
        return true;
    }

    function logDesignatedReportSubmitted(IUniverse _universe, address _reporter, address _market, uint256 _amountStaked, uint256[] _payoutNumerators) public returns (bool) {
        return true;
    }

    function logReportSubmitted(IUniverse _universe, address _reporter, address _market, address _reportingParticipant, uint256 _amountStaked, uint256[] _payoutNumerators) public returns (bool) {
        return true;
    }

    function logReportingParticipantDisavowed(IUniverse _universe, IMarket _market) public returns (bool) {
        return true;
    }

    function logMarketParticipantsDisavowed(IUniverse _universe) public returns (bool) {
        return true;
    }

    function logInitialReporterRedeemed(IUniverse _universe, address _reporter, address _market, uint256 _amountRedeemed, uint256 _repReceived, uint256 _reportingFeesReceived, uint256[] _payoutNumerators) public returns (bool) {
        return true;
    }

    function logDisputeCrowdsourcerRedeemed(IUniverse _universe, address _reporter, address _market, uint256 _amountRedeemed, uint256 _repReceived, uint256 _reportingFeesReceived, uint256[] _payoutNumerators) public returns (bool) {
        return true;
    }

    function logFeeWindowRedeemed(IUniverse _universe, address _reporter, uint256 _amountRedeemed, uint256 _reportingFeesReceived) public returns (bool) {
        return true;
    }

    function logInitialReporterTransferred(IUniverse _universe, IMarket _market, address _from, address _to) public returns (bool) {
        return true;
    }

    bool private logReportsDisputedCalledValue;

    function logReportsDisputedCalled() public returns(bool) { return logReportsDisputedCalledValue; }

    function logReportsDisputed(IUniverse _universe, address _disputer, address _market, uint256 _disputeBondAmount) public returns (bool) {
        logReportsDisputedCalledValue = true;
        return true;
    }

    function logMarketFinalizedCalled() public returns (bool) { return logMarketFinalizedCalledValue; }

    bool private logMarketFinalizedCalledValue;

    function logMarketFinalized(IUniverse _universe) public returns (bool) {
        logMarketFinalizedCalledValue = true;
        return true;
    }

    function logMarketMigrated(IMarket _market, IUniverse _originalUniverse) public returns (bool) {
        return true;
    }

    function logOrderCanceled(IUniverse _universe, address _shareToken, address _sender, bytes32 _orderId, Order.Types _orderType, uint256 _tokenRefund, uint256 _sharesRefund) public onlyWhitelistedCallers returns (bool) {
        return true;
    }

    function disputeCrowdsourcerCreated(IUniverse _universe, IMarket _market, IDisputeCrowdsourcer _crowdsourcer, uint256[] _payoutNumerators, uint256 _size, bool _invalid) public returns (bool) {
        return true;
    }

    function logOrderCreated(Order.Types _orderType, uint256 _amount, uint256 _price, address _creator, uint256 _moneyEscrowed, uint256 _sharesEscrowed, bytes32 _tradeGroupId, bytes32 _orderId, IUniverse _universe, address _shareToken) public onlyWhitelistedCallers returns (bool) {
        return true;
    }

    function logOrderFilled(IUniverse _universe, address _shareToken, address _filler, bytes32 _orderId, uint256 _numCreatorShares, uint256 _numCreatorTokens, uint256 _numFillerShares, uint256 _numFillerTokens, uint256 _marketCreatorFees, uint256 _reporterFees, uint256 _amountFilled, bytes32 _tradeGroupId) public onlyWhitelistedCallers returns (bool) {
        return true;
    }

    function logCompleteSetsPurchased(IUniverse _universe, IMarket _market, address _account, uint256 _numCompleteSets) public onlyWhitelistedCallers returns (bool) {
        return true;
    }

    function logCompleteSetsSold(IUniverse _universe, IMarket _market, address _account, uint256 _numCompleteSets) public onlyWhitelistedCallers returns (bool) {
        return true;
    }

    function logProceedsClaimed(IUniverse _universe, address _shareToken, address _sender, address _market, uint256 _numShares, uint256 _numPayoutTokens, uint256 _finalTokenBalance) public onlyWhitelistedCallers returns (bool) {
        return true;
    }

    function logReputationTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        return true;
    }

    function logReputationTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        return true;
    }

    function logShareTokenBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        return true;
    }

    function logShareTokenMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        return true;
    }

    function logFeeWindowBurned(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        return true;
    }

    function logFeeWindowMinted(IUniverse _universe, address _target, uint256 _amount) public returns (bool) {
        return true;
    }

    bool private logUniverseForkedCalledValue;

    function logUniverseForkedCalled() public returns (bool) { return logUniverseForkedCalledValue; }

    function logUniverseForked() public returns (bool) {
        logUniverseForkedCalledValue = true;
        return true;
    }

    bool private logUniverseCreatedCalledValue;

    function logUniverseCreatedCalled() public returns(bool) { return logUniverseCreatedCalledValue;}

    function logUniverseCreated(IUniverse _childUniverse, uint256[] _payoutNumerators, bool _invalid) public returns (bool) {
        logUniverseCreatedCalledValue = true;
        return true;
    }

    function logFeeWindowsTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        return true;
    }

    bool private logReputationTokensTransferredCalledValue;

    function logReputationTokensTransferredCalled() public returns(bool) { return logReputationTokensTransferredCalledValue;}

    function logReputationTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        logReputationTokensTransferredCalledValue = true;
        return true;
    }

    function logShareTokensTransferred(IUniverse _universe, address _from, address _to, uint256 _value) public returns (bool) {
        return true;
    }

    function logFeeWindowCreated(IFeeWindow _feeWindow, uint256 _id) public returns (bool) {
        return true;
    }

    function logInitialReportSubmitted(IUniverse _universe, address _reporter, address _market, uint256 _amountStaked, bool _isDesignatedReporter, uint256[] _payoutNumerators, bool _invalid) public returns (bool) {
        return true;
    }

    function logDisputeCrowdsourcerCreated(IUniverse _universe, address _market, address _disputeCrowdsourcer, uint256[] _payoutNumerators, uint256 _size, bool _invalid) public returns (bool) {
        return true;
    }

    function logDisputeCrowdsourcerContribution(IUniverse _universe, address _reporter, address _market, address _disputeCrowdsourcer, uint256 _amountStaked) public returns (bool) {
        return true;
    }

    function logDisputeCrowdsourcerCompleted(IUniverse _universe, address _market, address _disputeCrowdsourcer) public returns (bool) {
        return true;
    }

    function logTimestampSet(uint256 _newTimestamp) public returns (bool) {
        return true;
    }

    function logMarketTransferred(IUniverse _universe, address _from, address _to) public returns (bool) {
        return true;
    }

    function logMarketMailboxTransferred(IUniverse _universe, IMarket _market, address _from, address _to) public returns (bool) {
        return true;
    }
}
