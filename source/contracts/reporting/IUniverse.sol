pragma solidity 0.4.17;


import 'libraries/ITyped.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'reporting/IStakeToken.sol';


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
    function getReportingFeeInAttoethPerEth() public returns (uint256);
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
    function isContainerForReportingWindow(ITyped _shadyTarget) public view returns (bool);
    function isContainerForDisputeBondToken(ITyped _shadyTarget) public view returns (bool);
    function isContainerForMarket(ITyped _shadyTarget) public view returns (bool);
    function isContainerForStakeToken(ITyped _shadyTarget) public view returns (bool);
    function isContainerForShareToken(ITyped _shadyTarget) public view returns (bool);
    function decrementOpenInterest(uint256 _amount) public returns (bool);
    function incrementOpenInterest(uint256 _amount) public returns (bool);
}
