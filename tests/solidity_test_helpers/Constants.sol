pragma solidity ^0.4.13;

import 'ROOT/reporting/IMarket.sol';
import 'ROOT/reporting/Reporting.sol';
import 'ROOT/trading/Order.sol';


contract Constants {
    IMarket.ReportingState public constant PRE_REPORTING = IMarket.ReportingState.PRE_REPORTING;
    IMarket.ReportingState public constant AUTOMATED_REPORTING = IMarket.ReportingState.AUTOMATED_REPORTING;
    IMarket.ReportingState public constant AUTOMATED_DISPUTE = IMarket.ReportingState.AUTOMATED_DISPUTE;
    IMarket.ReportingState public constant AWAITING_MIGRATION = IMarket.ReportingState.AWAITING_MIGRATION;
    IMarket.ReportingState public constant LIMITED_REPORTING = IMarket.ReportingState.LIMITED_REPORTING;
    IMarket.ReportingState public constant LIMITED_DISPUTE = IMarket.ReportingState.LIMITED_DISPUTE;
    IMarket.ReportingState public constant ALL_REPORTING = IMarket.ReportingState.ALL_REPORTING;
    IMarket.ReportingState public constant ALL_DISPUTE = IMarket.ReportingState.ALL_DISPUTE;
    IMarket.ReportingState public constant FORKING = IMarket.ReportingState.FORKING;
    IMarket.ReportingState public constant AWAITING_FINALIZATION = IMarket.ReportingState.AWAITING_FINALIZATION;
    IMarket.ReportingState public constant AWAITING_FINALIZATION_MIGRATION = IMarket.ReportingState.AWAITING_FINALIZATION_MIGRATION;
    IMarket.ReportingState public constant FINALIZED = IMarket.ReportingState.FINALIZED;

    uint256 public constant AUTOMATED_REPORTING_DURATION_SECONDS = Reporting.automatedReportingDurationSeconds();
    uint256 public constant AUTOMATED_REPORTING_DISPUTE_DURATION_SECONDS = Reporting.automatedReportingDisputeDurationSeconds();

    uint256 public constant REGISTRATION_TOKEN_BOND_AMOUNT = Reporting.getRegistrationTokenBondAmount();

    uint8 public constant BID = uint8(Order.TradeTypes.Bid);
    uint8 public constant ASK = uint8(Order.TradeTypes.Ask);
    uint8 public constant LONG = uint8(Order.TradeDirections.Long);
    uint8 public constant SHORT = uint8(Order.TradeDirections.Short);
}
