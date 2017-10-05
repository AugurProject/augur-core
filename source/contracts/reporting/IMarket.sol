pragma solidity ^0.4.13;

import 'libraries/Typed.sol';
import 'libraries/IOwnable.sol';
import 'trading/ICash.sol';
import 'trading/IShareToken.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IReportingToken.sol';
import 'reporting/IDisputeBond.sol';
import 'trading/IShareToken.sol';


contract IMarket is Typed, IOwnable {
    enum ReportingState {
        PRE_REPORTING,
        DESIGNATED_REPORTING,
        DESIGNATED_DISPUTE,
        AWAITING_FORK_MIGRATION,
        LIMITED_REPORTING,
        LIMITED_DISPUTE,
        AWAITING_NO_REPORT_MIGRATION,
        ALL_REPORTING,
        ALL_DISPUTE,
        FORKING,
        AWAITING_FINALIZATION,
        FINALIZED
    }

    function initialize(IReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _numTicks, uint256 _feePerEthInAttoeth, ICash _cash, address _creator, address _designatedReporterAddress) public payable returns (bool _success);
    function updateTentativeWinningPayoutDistributionHash(bytes32 _payoutDistributionHash) public returns (bool);
    function derivePayoutDistributionHash(uint256[] _payoutNumerators) public constant returns (bytes32);
    function getUniverse() public constant returns (IUniverse);
    function getReportingWindow() public constant returns (IReportingWindow);
    function getNumberOfOutcomes() public constant returns (uint8);
    function getNumTicks() public constant returns (uint256);
    function getDenominationToken() public constant returns (ICash);
    function getShareToken(uint8 _outcome)  public constant returns (IShareToken);
    function getDesignatedReporterDisputeBondToken() public constant returns (IDisputeBond);
    function getLimitedReportersDisputeBondToken() public constant returns (IDisputeBond);
    function getMarketCreatorSettlementFeeInAttoethPerEth() public constant returns (uint256);
    function getReportingState() public constant returns (ReportingState);
    function getFinalizationTime() public constant returns (uint256);
    function getFinalPayoutDistributionHash() public constant returns (bytes32);
    function getFinalWinningReportingToken() public constant returns (IReportingToken);
    function getReportingTokenOrZeroByPayoutDistributionHash(bytes32 _payoutDistributionHash) public constant returns (IReportingToken);
    function getPayoutDistributionHashStake(bytes32 _payoutDistributionHash) public constant returns (int256);
    function migrateDueToNoReports() public returns (bool);
    function isContainerForReportingToken(Typed _shadyTarget) public constant returns (bool);
    function isContainerForDisputeBondToken(Typed _shadyTarget) public constant returns (bool);
    function isContainerForShareToken(Typed _shadyTarget) public constant returns (bool);
    function isValid() public constant returns (bool);
}
