pragma solidity ^0.4.13;

import 'ROOT/reporting/Market.sol';


contract Constants {
    Market.ReportingState public constant PRE_REPORTING = Market.ReportingState.PRE_REPORTING;
    Market.ReportingState public constant AUTOMATED_REPORTING = Market.ReportingState.AUTOMATED_REPORTING;
    Market.ReportingState public constant AUTOMATED_DISPUTE = Market.ReportingState.AUTOMATED_DISPUTE;
    Market.ReportingState public constant AWAITING_MIGRATION = Market.ReportingState.AWAITING_MIGRATION;
    Market.ReportingState public constant LIMITED_REPORTING = Market.ReportingState.LIMITED_REPORTING;
    Market.ReportingState public constant LIMITED_DISPUTE = Market.ReportingState.LIMITED_DISPUTE;
    Market.ReportingState public constant ALL_REPORTING = Market.ReportingState.ALL_REPORTING;
    Market.ReportingState public constant ALL_DISPUTE = Market.ReportingState.ALL_DISPUTE;
    Market.ReportingState public constant FORKING = Market.ReportingState.FORKING;
    Market.ReportingState public constant AWAITING_FINALIZATION = Market.ReportingState.AWAITING_FINALIZATION;
    Market.ReportingState public constant FINALIZED = Market.ReportingState.FINALIZED;

    uint256 public constant AUTOMATED_REPORTING_DURATION_SECONDS = 3 days;
    uint256 public constant AUTOMATED_REPORTING_DISPUTE_DURATION_SECONDS = 3 days;
}