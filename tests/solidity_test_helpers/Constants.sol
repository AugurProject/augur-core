pragma solidity ^0.4.17;

import 'reporting/IMarket.sol';
import 'reporting/Reporting.sol';
import 'trading/Order.sol';


contract Constants {
    IMarket.ReportingState public constant PRE_REPORTING = IMarket.ReportingState.PRE_REPORTING;
    IMarket.ReportingState public constant DESIGNATED_REPORTING = IMarket.ReportingState.DESIGNATED_REPORTING;
    IMarket.ReportingState public constant DESIGNATED_DISPUTE = IMarket.ReportingState.DESIGNATED_DISPUTE;
    IMarket.ReportingState public constant AWAITING_FORK_MIGRATION = IMarket.ReportingState.AWAITING_FORK_MIGRATION;
    IMarket.ReportingState public constant FIRST_REPORTING = IMarket.ReportingState.FIRST_REPORTING;
    IMarket.ReportingState public constant FIRST_DISPUTE = IMarket.ReportingState.FIRST_DISPUTE;
    IMarket.ReportingState public constant AWAITING_NO_REPORT_MIGRATION = IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION;
    IMarket.ReportingState public constant LAST_REPORTING = IMarket.ReportingState.LAST_REPORTING;
    IMarket.ReportingState public constant LAST_DISPUTE = IMarket.ReportingState.LAST_DISPUTE;
    IMarket.ReportingState public constant FORKING = IMarket.ReportingState.FORKING;
    IMarket.ReportingState public constant AWAITING_FINALIZATION = IMarket.ReportingState.AWAITING_FINALIZATION;
    IMarket.ReportingState public constant FINALIZED = IMarket.ReportingState.FINALIZED;

    uint256 public constant DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT = Reporting.getDesignatedReporterDisputeBondAmount();
    uint256 public constant FIRST_REPORTERS_DISPUTE_BOND_AMOUNT = Reporting.getFirstReportersDisputeBondAmount();
    uint256 public constant LAST_REPORTERS_DISPUTE_BOND_AMOUNT = Reporting.getLastReportersDisputeBondAmount();

    uint256 public constant DESIGNATED_REPORTING_DURATION_SECONDS = Reporting.getDesignatedReportingDurationSeconds();
    uint256 public constant DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS = Reporting.getDesignatedReportingDisputeDurationSeconds();

    uint256 public constant REPORTING_DURATION_SECONDS = Reporting.getReportingDurationSeconds();
    uint256 public constant REPORTING_DISPUTE_DURATION_SECONDS = Reporting.getReportingDisputeDurationSeconds();
    uint256 public constant FORK_DURATION_SECONDS = Reporting.getForkDurationSeconds();

    uint256 public constant GAS_TO_REPORT = Reporting.getGasToReport();
    uint256 public constant DEFAULT_REPORTING_GAS_PRICE = Reporting.getDefaultReportingGasPrice();

    uint256 public constant DEFAULT_VALIDITY_BOND = Reporting.getDefaultValidityBond();
    uint256 public constant DEFAULT_DESIGNATED_REPORT_STAKE = Reporting.getDefaultDesignatedReportStake();
    uint256 public constant DEFAULT_DESIGNATED_REPORT_NO_SHOW_BOND = Reporting.getDefaultDesignatedReportNoShowBond();

    uint256 public constant FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR = Reporting.getForkMigrationPercentageBonusDivisor();
    uint256 public constant TARGET_REP_MARKET_CAP_MULTIPLIER = Reporting.getTargetRepMarketCapMultiplier();
    uint256 public constant TARGET_INVALID_MARKETS_DIVISOR = Reporting.getTargetInvalidMarketsDivisor();
    uint256 public constant DEFAULT_VALIDITY_BOND_FLOOR = Reporting.getDefaultValidityBondFloor();
    uint256 public constant TARGET_INCORRECT_DESIGNATED_REPORT_MARKETS_DIVISOR = Reporting.getTargetIncorrectDesignatedReportMarketsDivisor();
    uint256 public constant DESIGNATED_REPORT_STAKE_FLOOR = Reporting.getDesignatedReportStakeFloor();
    uint256 public constant TARGET_DESIGNATED_REPORT_NO_SHOWS_DIVISOR = Reporting.getTargetDesignatedReportNoShowsDivisor();
    uint256 public constant DESIGNATED_REPORT_NO_SHOW_BOND_FLOOR = Reporting.getDesignatedReportNoShowBondFloor();

    uint8 public constant BID = uint8(Order.Types.Bid);
    uint8 public constant ASK = uint8(Order.Types.Ask);
    uint8 public constant LONG = uint8(Order.TradeDirections.Long);
    uint8 public constant SHORT = uint8(Order.TradeDirections.Short);
}
