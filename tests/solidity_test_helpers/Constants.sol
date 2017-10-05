pragma solidity ^0.4.17;

import 'reporting/IMarket.sol';
import 'reporting/Reporting.sol';
import 'trading/Order.sol';


contract Constants {
    IMarket.ReportingState public constant PRE_REPORTING = IMarket.ReportingState.PRE_REPORTING;
    IMarket.ReportingState public constant DESIGNATED_REPORTING = IMarket.ReportingState.DESIGNATED_REPORTING;
    IMarket.ReportingState public constant DESIGNATED_DISPUTE = IMarket.ReportingState.DESIGNATED_DISPUTE;
    IMarket.ReportingState public constant AWAITING_FORK_MIGRATION = IMarket.ReportingState.AWAITING_FORK_MIGRATION;
    IMarket.ReportingState public constant LIMITED_REPORTING = IMarket.ReportingState.LIMITED_REPORTING;
    IMarket.ReportingState public constant LIMITED_DISPUTE = IMarket.ReportingState.LIMITED_DISPUTE;
    IMarket.ReportingState public constant AWAITING_NO_REPORT_MIGRATION = IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION;
    IMarket.ReportingState public constant ALL_REPORTING = IMarket.ReportingState.ALL_REPORTING;
    IMarket.ReportingState public constant ALL_DISPUTE = IMarket.ReportingState.ALL_DISPUTE;
    IMarket.ReportingState public constant FORKING = IMarket.ReportingState.FORKING;
    IMarket.ReportingState public constant AWAITING_FINALIZATION = IMarket.ReportingState.AWAITING_FINALIZATION;
    IMarket.ReportingState public constant FINALIZED = IMarket.ReportingState.FINALIZED;

    uint256 public constant DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT = Reporting.designatedReporterDisputeBondAmount();
    uint256 public constant LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT = Reporting.limitedReportersDisputeBondAmount();
    uint256 public constant ALL_REPORTERS_DISPUTE_BOND_AMOUNT = Reporting.allReportersDisputeBondAmount();

    uint256 public constant DESIGNATED_REPORTING_DURATION_SECONDS = Reporting.designatedReportingDurationSeconds();
    uint256 public constant DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS = Reporting.designatedReportingDisputeDurationSeconds();

    uint256 public constant REGISTRATION_TOKEN_BOND_AMOUNT = Reporting.getRegistrationTokenBondAmount();

    uint256 public constant GAS_TO_REPORT = Reporting.gasToReport();
    uint256 public constant DEFAULT_REPORTING_GAS_PRICE = Reporting.defaultReportingGasPrice();
    uint256 public constant DEFAULT_REPORTS_PER_MARKET = Reporting.defaultReportsPerMarket();

    uint256 public constant DEFAULT_VALIDITY_BOND = Reporting.defaultValidityBond();
    uint256 public constant DEFAULT_DESIGNATED_REPORT_STAKE = Reporting.defaultDesignatedReportStake();

    uint8 public constant BID = uint8(Order.TradeTypes.Bid);
    uint8 public constant ASK = uint8(Order.TradeTypes.Ask);
    uint8 public constant LONG = uint8(Order.TradeDirections.Long);
    uint8 public constant SHORT = uint8(Order.TradeDirections.Short);
}
