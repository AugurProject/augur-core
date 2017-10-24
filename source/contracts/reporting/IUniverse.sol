pragma solidity 0.4.17;


import 'libraries/ITyped.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'reporting/IStakeToken.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IParticipationToken.sol';
import 'trading/IShareToken.sol';


contract IUniverse is ITyped {
    function initialize(IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) external returns (bool);
    function fork() public returns (bool);
    function getParentUniverse() public view returns (IUniverse);
    function getOrCreateChildUniverse(bytes32 _parentPayoutDistributionHash) public returns (IUniverse);
    function getChildUniverse(bytes32 _parentPayoutDistributionHash) public view returns (IUniverse);
    function getReputationToken() public view returns (IReputationToken);
    function getForkingMarket() public view returns (IMarket);
    function getForkEndTime() public view returns (uint256);
    function getParentPayoutDistributionHash() public view returns (bytes32);
    function getReportingPeriodDurationInSeconds() public view returns (uint256);
    function getReportingWindowByTimestamp(uint256 _timestamp) public returns (IReportingWindow);
    function getReportingWindowByMarketEndTime(uint256 _endTime) public returns (IReportingWindow);
    function getCurrentReportingWindow() public returns (IReportingWindow);
    function getNextReportingWindow() public returns (IReportingWindow);
    function getReportingWindowForForkEndTime() public returns (IReportingWindow);
    function getOpenInterestInAttoEth() public view returns (uint256);
    function getRepMarketCapInAttoeth() public view returns (uint256);
    function getTargetRepMarketCapInAttoeth() public view returns (uint256);
    function getValidityBond() public returns (uint256);
    function getDesignatedReportStake() public returns (uint256);
    function getDesignatedReportNoShowBond() public returns (uint256);
    function getReportingFeeDivisor() public returns (uint256);
    function getRepAvailableForExtraBondPayouts() public view returns (uint256);
    function increaseRepAvailableForExtraBondPayouts(uint256 _amount) public returns (bool);
    function decreaseRepAvailableForExtraBondPayouts(uint256 _amount) public returns (bool);
    function getExtraDisputeBondRemainingToBePaidOut() public view returns (uint256);
    function increaseExtraDisputeBondRemainingToBePaidOut(uint256 _amount) public returns (bool);
    function decreaseExtraDisputeBondRemainingToBePaidOut(uint256 _amount) public returns (bool);
    function calculateFloatingValue(uint256 _badMarkets, uint256 _totalMarkets, uint256 _targetDivisor, uint256 _previousValue, uint256 _defaultValue, uint256 _floor) public pure returns (uint256 _newValue);
    function getTargetReporterGasCosts() public returns (uint256);
    function getMarketCreationCost() public returns (uint256);
    function isParentOf(IUniverse _shadyChild) public view returns (bool);
    function isContainerForReportingWindow(IReportingWindow _shadyTarget) public view returns (bool);
    function isContainerForDisputeBondToken(IDisputeBond _shadyTarget) public view returns (bool);
    function isContainerForMarket(IMarket _shadyTarget) public view returns (bool);
    function isContainerForStakeToken(IStakeToken _shadyTarget) public view returns (bool);
    function isContainerForShareToken(IShareToken _shadyTarget) public view returns (bool);
    function isContainerForParticipationToken(IParticipationToken _shadyTarget) public view returns (bool);
    function decrementOpenInterest(uint256 _amount) public returns (bool);
    function incrementOpenInterest(uint256 _amount) public returns (bool);
    // Logging
    function logMarketCreated(address _market, address _marketCreator, uint256 _marketCreationFee, string _extraInfo) public returns (bool);
    function logDesignatedReportSubmitted(address _reporter, address _market, address _reportingToken, uint256 _amountStaked, uint256[] _payoutNumerators) public returns (bool);
    function logReportSubmitted(address _reporter, address _market, address _reportingToken, uint256 _amountStaked, uint256[] _payoutNumerators) public returns (bool);    
    function logWinningTokensRedeemed(address _reporter, address _market, address _reportingToken, uint256 _amountRedeemed, uint256 _reportingFeesReceived, uint256[] _payoutNumerators) public returns (bool);    
    function logReportsDisputed(address _disputer, address _market, uint8 _reportingPhase, uint256 _disputeBondAmount) public returns (bool);
    function logMarketFinalized(address _market) public returns (bool);
    function logOrderCanceled(address _shareToken, address _sender, bytes32 _orderId, uint8 _orderType, uint256 _tokenRefund, uint256 _sharesRefund) public returns (bool);
    function logOrderCreated(address _shareToken, address _creator, bytes32 _orderId, uint256 _price, uint256 _amount, uint256 _numTokensEscrowed, uint256 _numSharesEscrowed, uint256 _tradeGroupId) public returns (bool);
    function logOrderFilled(address _shareToken, address _creator, address _filler, uint256 _price, uint256 _numCreatorShares, uint256 _numCreatorTokens, uint256 _numFillerShares, uint256 _numFillerTokens, uint256 _settlementFees, uint256 _tradeGroupId) public returns (bool);    
    function logProceedsClaimed(address _sender, address _market, uint256 _numShares, uint256 _numPayoutTokens) public returns (bool);
    /* TODO: Do we need this?
    function logTokensTransferred(address _token, address _from, address _to, uint256 _value) public returns (bool);
    */
}
