pragma solidity ^0.4.13;

import 'ROOT/libraries/Typed.sol';
import 'ROOT/reporting/IReputationToken.sol';
import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/reporting/IMarket.sol';


contract IBranch is Typed {
    function initialize(IBranch _parentBranch, bytes32 _parentPayoutDistributionHash) external returns (bool);
    function fork() public returns (bool);
    function getParentBranch() public constant returns (IBranch);
    function getOrCreateChildBranch(bytes32 _parentPayoutDistributionHash) public returns (IBranch);
    function getChildBranch(bytes32 _parentPayoutDistributionHash) public constant returns (IBranch);
    function getReputationToken() public constant returns (IReputationToken);
    function getForkingMarket() public constant returns (IMarket);
    function getForkEndTime() public constant returns (uint256);
    function getParentPayoutDistributionHash() public constant returns (bytes32);
    function getReportingPeriodDurationInSeconds() public constant returns (uint256);
    function getReportingWindowByTimestamp(uint256 _timestamp) public returns (IReportingWindow);
    function getReportingWindowByMarketEndTime(uint256 _endTime, bool _hasAutomatedReporter) public returns (IReportingWindow);
    function getNextReportingWindow() public returns (IReportingWindow);
    function getReportingWindowForForkEndTime() public constant returns (IReportingWindow);
    function isParentOf(IBranch _shadyChild) constant returns (bool);
    function isContainerForReportingWindow(Typed _shadyTarget) public constant returns (bool);
    function isContainerForRegistrationToken(Typed _shadyTarget) public constant returns (bool);
    function isContainerForMarket(Typed _shadyTarget) public constant returns (bool);
    function isContainerForReportingToken(Typed _shadyTarget) public constant returns (bool);
    function isContainerForShareToken(Typed _shadyTarget) public constant returns (bool);
}
