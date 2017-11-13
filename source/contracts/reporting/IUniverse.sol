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
    function getForkReputationGoal() public view returns (uint256);
    function getParentPayoutDistributionHash() public view returns (bytes32);
    function getReportingPeriodDurationInSeconds() public view returns (uint256);
    function getOrCreateReportingWindowByTimestamp(uint256 _timestamp) public returns (IReportingWindow);
    function getOrCreateReportingWindowByMarketEndTime(uint256 _endTime) public returns (IReportingWindow);
    function getOrCreateCurrentReportingWindow() public returns (IReportingWindow);
    function getOrCreateNextReportingWindow() public returns (IReportingWindow);
    function getOrCreateReportingWindowForForkEndTime() public returns (IReportingWindow);
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
    function calculateFloatingValue(uint256 _badMarkets, uint256 _totalMarkets, uint256 _targetDivisor, uint256 _previousValue, uint256 _defaultValue, uint256 _floor) public pure returns (uint256 _newValue);
    function getTargetReporterGasCosts() public returns (uint256);
    function getMarketCreationCost() public returns (uint256);
    function isParentOf(IUniverse _shadyChild) public view returns (bool);
    function isContainerForReportingWindow(IReportingWindow _shadyTarget) public view returns (bool);
    function isContainerForDisputeBond(IDisputeBond _shadyTarget) public view returns (bool);
    function isContainerForMarket(IMarket _shadyTarget) public view returns (bool);
    function isContainerForStakeToken(IStakeToken _shadyTarget) public view returns (bool);
    function isContainerForShareToken(IShareToken _shadyTarget) public view returns (bool);
    function isContainerForParticipationToken(IParticipationToken _shadyTarget) public view returns (bool);
    function decrementOpenInterest(uint256 _amount) public returns (bool);
    function incrementOpenInterest(uint256 _amount) public returns (bool);
}
