pragma solidity 0.4.18;


library Reporting {
    uint256 private constant DESIGNATED_REPORTING_DURATION_SECONDS = 3 days;
    uint256 private constant DISPUTE_ROUND_DURATION_SECONDS = 7 days;
    uint256 private constant CLAIM_PROCEEDS_WAIT_TIME = 3 days;
    uint256 private constant FORK_DURATION_SECONDS = 60 days;

    uint256 private constant INITIAL_REP_SUPPLY = 11 * 10 ** 6 * 10 ** 18; // 11 Million REP
    // CONSIDER: Should this be a constant?
    uint256 private constant DISPUTE_THRESHOLD_FOR_FORK = INITIAL_REP_SUPPLY / 80; // 1.25% of the REP total supply
    uint256 private constant INITIAL_REPORT_MIN_VALUE = DISPUTE_THRESHOLD_FOR_FORK / 2**20; // This value will result in a maximum 20 round dispute sequence
    uint256 private constant DEFAULT_DESIGNATED_REPORT_STAKE = INITIAL_REPORT_MIN_VALUE;
    uint256 private constant DESIGNATED_REPORT_STAKE_FLOOR = INITIAL_REPORT_MIN_VALUE;
    uint256 private constant DEFAULT_DESIGNATED_REPORT_NO_SHOW_BOND = INITIAL_REPORT_MIN_VALUE;
    uint256 private constant DESIGNATED_REPORT_NO_SHOW_BOND_FLOOR = INITIAL_REPORT_MIN_VALUE;
    uint256 private constant DEFAULT_VALIDITY_BOND = 1 ether / 100;
    uint256 private constant VALIDITY_BOND_FLOOR = 1 ether / 100;
    uint256 private constant DEFAULT_REPORTING_FEE_DIVISOR = 100; // 1% fees
    uint256 private constant MAXIMUM_REPORTING_FEE_DIVISOR = 10000; // Minimum .01% fees
    uint256 private constant MINIMUM_REPORTING_FEE_DIVISOR = 3; // Maximum 33.3~% fees. Note than anything less than a value of 2 here will likely result in bugs such as divide by 0 cases.

    // NOTE: We need to maintain this cost to roughly match the gas cost of reporting. This was last updated 10/02/2017
    uint256 private constant GAS_TO_REPORT = 600000;
    uint256 private constant DEFAULT_REPORTING_GAS_PRICE = 5;

    uint256 private constant TARGET_INVALID_MARKETS_DIVISOR = 100; // 1% of markets are expected to be invalid
    uint256 private constant TARGET_INCORRECT_DESIGNATED_REPORT_MARKETS_DIVISOR = 100; // 1% of markets are expected to have an incorrect designate report
    uint256 private constant TARGET_DESIGNATED_REPORT_NO_SHOWS_DIVISOR = 100; // 1% of markets are expected to have an incorrect designate report
    uint256 private constant TARGET_REP_MARKET_CAP_MULTIPLIER = 5;

    uint256 private constant FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR = 20; // 5% bonus to any REP migrated during a fork
    uint256 private constant FORK_REP_MIGRATION_VICTORY_DIVISOR = 2; // 50% of the REP supply in the forking universe has to migrate for a victory

    function getDesignatedReportingDurationSeconds() internal pure returns (uint256) { return DESIGNATED_REPORTING_DURATION_SECONDS; }
    function getDisputeRoundDurationSeconds() internal pure returns (uint256) { return DISPUTE_ROUND_DURATION_SECONDS; }
    function getClaimTradingProceedsWaitTime() internal pure returns (uint256) { return CLAIM_PROCEEDS_WAIT_TIME; }
    function getForkDurationSeconds() internal pure returns (uint256) { return FORK_DURATION_SECONDS; }
    function getGasToReport() internal pure returns (uint256) { return GAS_TO_REPORT; }
    function getDefaultReportingGasPrice() internal pure returns (uint256) { return DEFAULT_REPORTING_GAS_PRICE; }
    function getDefaultValidityBond() internal pure returns (uint256) { return DEFAULT_VALIDITY_BOND; }
    function getDefaultDesignatedReportStake() internal pure returns (uint256) { return DEFAULT_DESIGNATED_REPORT_STAKE; }
    function getDefaultDesignatedReportNoShowBond() internal pure returns (uint256) { return DEFAULT_DESIGNATED_REPORT_NO_SHOW_BOND; }
    function getValidityBondFloor() internal pure returns (uint256) { return VALIDITY_BOND_FLOOR; }
    function getDesignatedReportStakeFloor() internal pure returns (uint256) { return DESIGNATED_REPORT_STAKE_FLOOR; }
    function getDesignatedReportNoShowBondFloor() internal pure returns (uint256) { return DESIGNATED_REPORT_NO_SHOW_BOND_FLOOR; }
    function getTargetInvalidMarketsDivisor() internal pure returns (uint256) { return TARGET_INVALID_MARKETS_DIVISOR; }
    function getTargetIncorrectDesignatedReportMarketsDivisor() internal pure returns (uint256) { return TARGET_INCORRECT_DESIGNATED_REPORT_MARKETS_DIVISOR; }
    function getTargetDesignatedReportNoShowsDivisor() internal pure returns (uint256) { return TARGET_DESIGNATED_REPORT_NO_SHOWS_DIVISOR; }
    function getTargetRepMarketCapMultiplier() internal pure returns (uint256) { return TARGET_REP_MARKET_CAP_MULTIPLIER; }
    function getForkMigrationPercentageBonusDivisor() internal pure returns (uint256) { return FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR; }
    function getForkRepMigrationVictoryDivisor() internal pure returns (uint256) { return FORK_REP_MIGRATION_VICTORY_DIVISOR; }
    function getMaximumReportingFeeDivisor() internal pure returns (uint256) { return MAXIMUM_REPORTING_FEE_DIVISOR; }
    function getMinimumReportingFeeDivisor() internal pure returns (uint256) { return MINIMUM_REPORTING_FEE_DIVISOR; }
    function getDefaultReportingFeeDivisor() internal pure returns (uint256) { return DEFAULT_REPORTING_FEE_DIVISOR; }
    function getInitialREPSupply() internal pure returns (uint256) { return INITIAL_REP_SUPPLY; }
    function getDisputeThresholdForFork() internal pure returns (uint256) { return DISPUTE_THRESHOLD_FOR_FORK; }

    function getCategoricalMarketNumTicks(uint8 _numOutcomes) internal pure returns (uint256) {
        require(_numOutcomes >= 2 && _numOutcomes <= 8);

        if (_numOutcomes == 2) {return 10000;}
        if (_numOutcomes == 3) {return 10002;}
        if (_numOutcomes == 4) {return 10000;}
        if (_numOutcomes == 5) {return 10000;}
        if (_numOutcomes == 6) {return 10002;}
        if (_numOutcomes == 7) {return 10003;}
        if (_numOutcomes == 8) {return 10000;}
    }
}
