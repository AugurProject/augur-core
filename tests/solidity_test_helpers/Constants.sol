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

    uint256 public constant DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT = Reporting.designatedReporterDisputeBondAmount();
    uint256 public constant FIRST_REPORTERS_DISPUTE_BOND_AMOUNT = Reporting.firstReportersDisputeBondAmount();
    uint256 public constant LAST_REPORTERS_DISPUTE_BOND_AMOUNT = Reporting.lastReportersDisputeBondAmount();

    uint256 public constant DESIGNATED_REPORTING_DURATION_SECONDS = Reporting.designatedReportingDurationSeconds();
    uint256 public constant DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS = Reporting.designatedReportingDisputeDurationSeconds();

    uint256 public constant REPORTING_DURATION_SECONDS = Reporting.reportingDurationSeconds();
    uint256 public constant REPORTING_DISPUTE_DURATION_SECONDS = Reporting.reportingDisputeDurationSeconds();
    uint256 public constant FORK_DURATION_SECONDS = Reporting.forkDurationSeconds();

    uint256 public constant GAS_TO_REPORT = Reporting.gasToReport();
    uint256 public constant DEFAULT_REPORTING_GAS_PRICE = Reporting.defaultReportingGasPrice();

    uint256 public constant DEFAULT_VALIDITY_BOND = Reporting.defaultValidityBond();
    uint256 public constant DEFAULT_DESIGNATED_REPORT_STAKE = Reporting.defaultDesignatedReportStake();
    uint256 public constant DEFAULT_DESIGNATED_REPORT_NO_SHOW_BOND = Reporting.defaultDesignatedReportNoShowBond();

    uint256 public constant FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR = Reporting.forkMigrationPercentageBonusDivisor();
    uint256 public constant TARGET_REP_MARKET_CAP_MULTIPLIER = Reporting.targetRepMarketCapMultiplier();
    uint256 public constant TARGET_INVALID_MARKETS_DIVISOR = Reporting.targetInvalidMarketsDivisor();
    uint256 public constant DEFAULT_VALIDITY_BOND_FLOOR = Reporting.defaultValidityBondFloor();
    uint256 public constant TARGET_INCORRECT_DESIGNATED_REPORT_MARKETS_DIVISOR = Reporting.targetIncorrectDesignatedReportMarketsDivisor();
    uint256 public constant DESIGNATED_REPORT_STAKE_FLOOR = Reporting.designatedReportStakeFloor();
    uint256 public constant TARGET_DESIGNATED_REPORT_NO_SHOWS_DIVISOR = Reporting.targetDesignatedReportNoShowsDivisor();
    uint256 public constant DESIGNATED_REPORT_NO_SHOW_BOND_FLOOR = Reporting.designatedReportNoShowBondFloor();

    uint8 public constant BID = uint8(Order.Types.Bid);
    uint8 public constant ASK = uint8(Order.Types.Ask);
    uint8 public constant LONG = uint8(Order.TradeDirections.Long);
    uint8 public constant SHORT = uint8(Order.TradeDirections.Short);
}
