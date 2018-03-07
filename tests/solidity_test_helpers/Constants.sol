pragma solidity ^0.4.20;

import 'reporting/IMarket.sol';
import 'reporting/Reporting.sol';
import 'trading/Order.sol';


contract Constants {
    uint256 public constant DESIGNATED_REPORTING_DURATION_SECONDS = Reporting.getDesignatedReportingDurationSeconds();
    uint256 public constant DISPUTE_ROUND_DURATION_SECONDS = Reporting.getDisputeRoundDurationSeconds();
    uint256 public constant CLAIM_PROCEEDS_WAIT_TIME = Reporting.getClaimTradingProceedsWaitTime();
    uint256 public constant FORK_DURATION_SECONDS = Reporting.getForkDurationSeconds();

    uint256 public constant DEFAULT_VALIDITY_BOND = Reporting.getDefaultValidityBond();
    uint256 public constant VALIDITY_BOND_FLOOR = Reporting.getValidityBondFloor();
    uint256 public constant DEFAULT_REPORTING_FEE_DIVISOR = Reporting.getDefaultReportingFeeDivisor();
    uint256 public constant MAXIMUM_REPORTING_FEE_DIVISOR = Reporting.getMaximumReportingFeeDivisor();
    uint256 public constant MINIMUM_REPORTING_FEE_DIVISOR = Reporting.getMinimumReportingFeeDivisor();

    // NOTE: We need to maintain this cost to roughly match the gas cost of reporting. This was last updated 10/02/2017
    uint256 public constant GAS_TO_REPORT = Reporting.getGasToReport();
    uint256 public constant DEFAULT_REPORTING_GAS_PRICE = Reporting.getDefaultReportingGasPrice();

    uint256 public constant TARGET_INVALID_MARKETS_DIVISOR = Reporting.getTargetInvalidMarketsDivisor();
    uint256 public constant TARGET_INCORRECT_DESIGNATED_REPORT_MARKETS_DIVISOR = Reporting.getTargetIncorrectDesignatedReportMarketsDivisor();
    uint256 public constant TARGET_DESIGNATED_REPORT_NO_SHOWS_DIVISOR = Reporting.getTargetDesignatedReportNoShowsDivisor();
    uint256 public constant TARGET_REP_MARKET_CAP_MULTIPLIER = Reporting.getTargetRepMarketCapMultiplier();
    uint256 public constant TARGET_REP_MARKET_CAP_DIVISOR = Reporting.getTargetRepMarketCapDivisor();

    uint256 public constant INITIAL_REP_SUPPLY = Reporting.getInitialREPSupply();
    uint256 public constant FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR = Reporting.getForkMigrationPercentageBonusDivisor();

    uint256 public constant BID = uint256(Order.Types.Bid);
    uint256 public constant ASK = uint256(Order.Types.Ask);
    uint256 public constant LONG = uint256(Order.TradeDirections.Long);
    uint256 public constant SHORT = uint256(Order.TradeDirections.Short);
}
