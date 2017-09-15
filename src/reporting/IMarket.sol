pragma solidity ^0.4.13;

import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/IOwnable.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/trading/IShareToken.sol';
import 'ROOT/reporting/IBranch.sol';
import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/reporting/IReportingToken.sol';
import 'ROOT/reporting/IDisputeBond.sol';
import 'ROOT/trading/IShareToken.sol';


contract IMarket is Typed, IOwnable {
    enum ReportingState {
        PRE_REPORTING,
        AUTOMATED_REPORTING,
        AUTOMATED_DISPUTE,
        AWAITING_MIGRATION,
        LIMITED_REPORTING,
        LIMITED_DISPUTE,
        ALL_REPORTING,
        ALL_DISPUTE,
        FORKING,
        AWAITING_FINALIZATION,
        FINALIZED
    }

    function initialize(IReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _marketDenominator, uint256 _feePerEthInAttoeth, ICash _cash, address _creator, address _automatedReporterAddress, bytes32 _topic) public payable returns (bool _success);
    function updateTentativeWinningPayoutDistributionHash(bytes32 _payoutDistributionHash) public returns (bool);
    function derivePayoutDistributionHash(uint256[] _payoutNumerators) public constant returns (bytes32);
    function getBranch() public constant returns (IBranch);
    function getReportingWindow() public constant returns (IReportingWindow);
    function getNumberOfOutcomes() public constant returns (uint8);
    function getMinDisplayPrice() public constant returns (uint256);
    function getMaxDisplayPrice() public constant returns (uint256);
    function getCompleteSetCostInAttotokens() public constant returns (uint256);
    function getMarketDenominator() public constant returns (uint256);
    function getTopic() public constant returns (bytes32);
    function getDenominationToken() public constant returns (ICash);
    function getShareToken(uint8 _outcome)  public constant returns (IShareToken);
    function getAutomatedReporterDisputeBondToken() public constant returns (IDisputeBond);
    function getLimitedReportersDisputeBondToken() public constant returns (IDisputeBond);
    function getMarketCreatorSettlementFeeInAttoethPerEth() public constant returns (uint256);
    function getReportingState() public constant returns (ReportingState);
    function getFinalizationTime() public constant returns (uint256);
    function getFinalPayoutDistributionHash() public constant returns (bytes32);
    function getFinalWinningReportingToken() public constant returns (IReportingToken);
    function getReportingTokenOrZeroByPayoutDistributionHash(bytes32 _payoutDistributionHash) public constant returns (IReportingToken);
    function isContainerForReportingToken(Typed _shadyTarget) public constant returns (bool);
    function isContainerForDisputeBondToken(Typed _shadyTarget) public constant returns (bool);
    function isContainerForShareToken(Typed _shadyTarget) public constant returns (bool);
}
