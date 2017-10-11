pragma solidity ^0.4.17;

import 'reporting/IMarket.sol';
import 'reporting/Reporting.sol';
import 'trading/Order.sol';


contract Constants {
    IMarket.ReportingState public constant PRE_REPORTING = IMarket.ReportingState.PRE_REPORTING;
    IMarket.ReportingState public constant DESIGNATED_REPORTING = IMarket.ReportingState.DESIGNATED_REPORTING;
    IMarket.ReportingState public constant DESIGNATED_DISPUTE = IMarket.ReportingState.DESIGNATED_DISPUTE;
    IMarket.ReportingState public constant AWAITING_FORK_MIGRATION = IMarket.ReportingState.AWAITING_FORK_MIGRATION;
    IMarket.ReportingState public constant ROUND1_REPORTING = IMarket.ReportingState.ROUND1_REPORTING;
    IMarket.ReportingState public constant FIRST_DISPUTE = IMarket.ReportingState.FIRST_DISPUTE;
    IMarket.ReportingState public constant AWAITING_NO_REPORT_MIGRATION = IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION;
    IMarket.ReportingState public constant ROUND2_REPORTING = IMarket.ReportingState.ROUND2_REPORTING;
    IMarket.ReportingState public constant LAST_DISPUTE = IMarket.ReportingState.LAST_DISPUTE;
    IMarket.ReportingState public constant FORKING = IMarket.ReportingState.FORKING;
    IMarket.ReportingState public constant AWAITING_FINALIZATION = IMarket.ReportingState.AWAITING_FINALIZATION;
    IMarket.ReportingState public constant FINALIZED = IMarket.ReportingState.FINALIZED;

    uint256 public constant DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT = Reporting.designatedReporterDisputeBondAmount();
    uint256 public constant ROUND1_REPORTERS_DISPUTE_BOND_AMOUNT = Reporting.round1ReportersDisputeBondAmount();
    uint256 public constant ROUND2_REPORTERS_DISPUTE_BOND_AMOUNT = Reporting.round2ReportersDisputeBondAmount();

    uint256 public constant DESIGNATED_REPORTING_DURATION_SECONDS = Reporting.designatedReportingDurationSeconds();
    uint256 public constant DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS = Reporting.designatedReportingDisputeDurationSeconds();

    uint256 public constant REPORTING_DURATION_SECONDS = Reporting.reportingDurationSeconds();
    uint256 public constant REPORTING_DISPUTE_DURATION_SECONDS = Reporting.reportingDisputeDurationSeconds();

    uint256 public constant GAS_TO_REPORT = Reporting.gasToReport();
    uint256 public constant DEFAULT_REPORTING_GAS_PRICE = Reporting.defaultReportingGasPrice();

    uint256 public constant DEFAULT_VALIDITY_BOND = Reporting.defaultValidityBond();
    uint256 public constant DEFAULT_DESIGNATED_REPORT_STAKE = Reporting.defaultDesignatedReportStake();
    uint256 public constant DEFAULT_DESIGNATED_REPORT_NO_SHOW_BOND = Reporting.defaultDesignatedReportNoShowBond();

    uint8 public constant BID = uint8(Order.TradeTypes.Bid);
    uint8 public constant ASK = uint8(Order.TradeTypes.Ask);
    uint8 public constant LONG = uint8(Order.TradeDirections.Long);
    uint8 public constant SHORT = uint8(Order.TradeDirections.Short);
}
