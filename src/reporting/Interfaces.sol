pragma solidity ^0.4.13;

import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/ReportingToken.sol';
import 'ROOT/reporting/ReportingWindow.sol';
import 'ROOT/reporting/DisputeBondToken.sol';
import 'ROOT/reporting/RegistrationToken.sol';


contract IMarket is Typed {
    function initialize(ReportingWindow, uint256, uint256, uint256, int256, address, address, int256, int256, address, int256) payable public returns (bool);
    function getBranch() constant returns (Branch);
    function getReputationToken() constant returns (ReputationToken);
    function getReportingWindow() constant returns (ReportingWindow);
    function getRegistrationToken() constant returns (RegistrationToken);
    function getNumberOfOutcomes() constant returns (uint8);
    function getAutomatedReporterDisputeBondToken() constant returns (DisputeBondToken);
    function getLimitedReportersDisputeBondToken() constant returns (DisputeBondToken);
    function getAllReportersDisputeBondToken() constant returns (DisputeBondToken);
    function isContainerForReportingToken(Typed) constant returns (bool);
    function isContainerForDisputeBondToken(Typed) constant returns (bool);
    function isContainerForShareToken(Typed) constant returns (bool);
    function isFinalized() constant returns (bool);
    function canBeReportedOn() constant returns (bool);
    function getFinalWinningReportingToken() constant returns (ReportingToken);
    function getFinalPayoutDistributionHash() constant returns (bytes32);
    function derivePayoutDistributionHash(uint256[]) constant returns (bytes32);
    function updateTentativeWinningPayoutDistributionHash(bytes32) public returns (bool);
    function isInAllReportingPhase() constant public returns (bool);
    function isInLimitedReportingPhase() constant public returns (bool);
    function isDoneWithAllReporters() constant public returns (bool);
    function isDoneWithLimitedReporters() constant public returns (bool);
    function getReportingTokenOrZeroByPayoutDistributionHash(bytes32) constant public returns (ReportingToken);
    function getFinalizationTime() constant public returns (uint256);
    function getDenominationToken() constant public returns (ERC20);
    function getPayoutDenominator() constant public returns (uint256);
    function getShareToken(uint8) constant public returns (IShareToken);
    function getCompleteSetCostInAttotokens() constant public returns(uint256);
    function getMarketCreatorSettlementFeeInAttoethPerEth() constant public returns (uint256);
    function getCreator() constant public returns (address);
    function shouldCollectReportingFees() constant public returns (bool);
}


contract IShareToken is ERC20, Typed {
    function initialize(IMarket _market, uint8 _outcome) public returns (bool);
    function getMarket() constant returns (IMarket);
    function destroyShares(address, uint256 balance) public;
}


contract ITopics {
    function initialize() public returns (bool);
    function updatePopularity(bytes32 topic, uint256 amount) public returns (bool);
    function getPopularity(bytes32 topic) constant returns (uint256);
    function getTopicByOffset(uint256 offset) constant returns (bytes32);
    function getPopularityByOffset(uint256 offset) constant returns (uint256);
    function count() constant returns (uint256);
}
