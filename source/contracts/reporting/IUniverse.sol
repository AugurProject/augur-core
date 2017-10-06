pragma solidity ^0.4.17;

import 'libraries/Typed.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReportingToken.sol';


contract IUniverse is Typed {
    function initialize(IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) external returns (bool);
    function fork() public returns (bool);
    function getParentUniverse() public constant returns (IUniverse);
    function getOrCreateChildUniverse(bytes32 _parentPayoutDistributionHash) public returns (IUniverse);
    function getChildUniverse(bytes32 _parentPayoutDistributionHash) public constant returns (IUniverse);
    function getReputationToken() public constant returns (IReputationToken);
    function getForkingMarket() public constant returns (IMarket);
    function getForkEndTime() public constant returns (uint256);
    function getParentPayoutDistributionHash() public constant returns (bytes32);
    function getReportingPeriodDurationInSeconds() public constant returns (uint256);
    function getReportingWindowByTimestamp(uint256 _timestamp) public returns (IReportingWindow);
    function getReportingWindowByMarketEndTime(uint256 _endTime, bool _hasDesignatedReporter) public returns (IReportingWindow);
    function getCurrentReportingWindow() public returns (IReportingWindow);
    function getNextReportingWindow() public returns (IReportingWindow);
    function getReportingWindowForForkEndTime() public returns (IReportingWindow);
    function getOpenInterestInAttoEth() public constant returns (uint256);
    function isParentOf(IUniverse _shadyChild) public constant returns (bool);
    function isContainerForReportingWindow(Typed _shadyTarget) public constant returns (bool);
    function isContainerForRegistrationToken(Typed _shadyTarget) public constant returns (bool);
    function isContainerForMarket(Typed _shadyTarget) public constant returns (bool);
    function isContainerForReportingToken(Typed _shadyTarget) public constant returns (bool);
    function isContainerForShareToken(Typed _shadyTarget) public constant returns (bool);
    function decrementOpenInterest(uint256 _amount) public returns (bool);
    function incrementOpenInterest(uint256 _amount) public returns (bool);
}
