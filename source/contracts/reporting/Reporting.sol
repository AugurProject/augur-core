pragma solidity 0.4.17;



library Reporting {
    uint256 private constant DESIGNATED_REPORTING_DURATION_SECONDS = 3 days;
    uint256 private constant DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS = 3 days;
    uint256 private constant REPORTING_DURATION_SECONDS = 27 * 1 days;
    uint256 private constant REPORTING_DISPUTE_DURATION_SECONDS = 3 days;
    uint256 private constant CLAIM_PROCEEDS_WAIT_TIME = 3 days;
    uint256 private constant REGISTRATION_TOKEN_BOND_AMOUNT = 1 ether;

    uint256 private constant DEFAULT_VALIDITY_BOND = 1 ether / 100;
    uint256 private constant DEFAULT_DESIGNATED_REPORT_STAKE = 2 ether;
    uint256 private constant DEFAULT_DESIGNATED_REPORT_NO_SHOW_BOND = 10 ether;
    uint256 private constant DESIGNATED_REPORT_NO_SHOW_BOND_FLOOR = 0.1 ether;

    // CONSIDER: figure out approprate values for these
    uint256 private constant DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT = 11 * 10**20;
    uint256 private constant ROUND1_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**21;
    uint256 private constant ROUND2_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**22;

    // NOTE: We need to maintain this cost to roughly match the gas cost of reporting. This was last updated 10/02/2017
    uint256 private constant GAS_TO_REPORT = 600000;
    uint256 private constant DEFAULT_REPORTING_GAS_PRICE = 5;

    function designatedReportingDurationSeconds() internal pure returns (uint256) { return DESIGNATED_REPORTING_DURATION_SECONDS; }
    function designatedReportingDisputeDurationSeconds() internal pure returns (uint256) { return DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS; }
    function reportingDurationSeconds() internal pure returns (uint256) { return REPORTING_DURATION_SECONDS; }
    function reportingDisputeDurationSeconds() internal pure returns (uint256) { return REPORTING_DISPUTE_DURATION_SECONDS; }
    function claimProceedsWaitTime() internal pure returns (uint256) { return CLAIM_PROCEEDS_WAIT_TIME; }
    function designatedReporterDisputeBondAmount() internal pure returns (uint256) { return DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT; }
    function round1ReportersDisputeBondAmount() internal pure returns (uint256) { return ROUND1_REPORTERS_DISPUTE_BOND_AMOUNT; }
    function round2ReportersDisputeBondAmount() internal pure returns (uint256) { return ROUND2_REPORTERS_DISPUTE_BOND_AMOUNT; }
    function gasToReport() internal pure returns (uint256) { return GAS_TO_REPORT; }
    function defaultReportingGasPrice() internal pure returns (uint256) { return DEFAULT_REPORTING_GAS_PRICE; }
    function defaultValidityBond() internal pure returns (uint256) { return DEFAULT_VALIDITY_BOND; }
    function defaultDesignatedReportStake() internal pure returns (uint256) { return DEFAULT_DESIGNATED_REPORT_STAKE; }
    function defaultDesignatedReportNoShowBond() internal pure returns (uint256) { return DEFAULT_DESIGNATED_REPORT_STAKE; }
    function designatedReportNoShowBondFloor() internal pure returns (uint256) { return DESIGNATED_REPORT_NO_SHOW_BOND_FLOOR; }
}
