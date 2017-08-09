pragma solidity ^0.4.13;

import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/ReportingToken.sol';


contract IReportingWindow is Typed {
    function initialize(Branch, uint256) public returns (bool);
    function noteReport(IMarket, address, int256) public returns (bool);
    function getStartTime() constant returns (uint256);
    function getEndTime() constant returns (uint256);
    function isDoneReporting(address) constant returns (bool);
    function isContainerForRegistrationToken(Typed) constant returns (bool);
    function isContainerForMarket(Typed) constant returns (bool);
    function getBranch() constant returns (Branch);
    function createNewMarket(uint256 _endTime, int256 _numOutcomes, int256 _payoutDenominator, int256 _feePerEthInWei, address _denominationToken, address _sender, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, int256 _topic) public payable returns (IMarket);
}


contract IRegistrationToken is Typed, VariableSupplyToken {
    function register() public returns (bool);
    function redeem() public returns (bool);
    function getReportingWindow() constant returns (IReportingWindow);
}


contract IMarket is Typed {
    function getBranch() constant returns (Branch);
    function getReputationToken() constant returns (ReputationToken);
    function getReportingWindow() constant returns (IReportingWindow);
    function getRegistrationToken() constant returns (IRegistrationToken);
    function getNumberOfOutcomes() constant returns (uint8);
    function getAutomatedReporterDisputeBondToken() constant returns (IDisputeBondToken);
    function getLimitedReportersDisputeBondToken() constant returns (IDisputeBondToken);
    function getAllReportersDisputeBondToken() constant returns (IDisputeBondToken);
    function isContainerForReportingToken(Typed) constant returns (bool);
    function isContainerForDisputeBondToken(Typed) constant returns (bool);
    function isContainerForShareToken(Typed) constant returns (bool);
    function isFinalized() constant returns (bool);
    function canBeReportedOn() constant returns (bool);
    function getFinalWinningReportingToken() constant returns (ReportingToken);
    function getFinalPayoutDistributionHash() constant returns (int256);
    function derivePayoutDistributionHash(int256[]) constant returns (int256);
    function updateTentativeWinningPayoutDistributionHash(int256) public returns (bool);
}


contract IShareToken is Typed {
    function initialize(IMarket _market, uint8 _outcome) public returns (bool);
    function getMarket() constant returns (IMarket);
}


contract IDisputeBondToken is Typed {
    function getDisputedPayoutDistributionHash() constant returns (int256);
    function getBondRemainingToBePaidOut() constant returns (uint256);
    function getMarket() constant returns (IMarket);
}


contract ITopics {
    function initialize() public returns (bool);
    function updatePopularity(bytes32 topic, uint256 amount) public returns (bool);
    function getPopularity(bytes32 topic) constant returns (uint256);
    function getTopicByOffset(uint256 offset) constant returns (bytes32);
    function getPopularityByOffset(uint256 offset) constant returns (uint256);
    function count() constant returns (uint256);
}
