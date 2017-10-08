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

    // CONSIDER: figure out approprate values for these
    uint256 private constant DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT = 11 * 10**20;
    uint256 private constant LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**21;
    uint256 private constant ALL_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**22;

    // NOTE: We need to maintain this cost to roughly match the gas cost of reporting. This was last updated 10/02/2017
    uint256 private constant GAS_TO_REPORT = 600000;
    uint256 private constant DEFAULT_REPORTING_GAS_PRICE = 5;
    uint256 private constant DEFAULT_REPORTS_PER_MARKET = 10;

    function designatedReportingDurationSeconds() internal constant returns (uint256) { return DESIGNATED_REPORTING_DURATION_SECONDS; }
    function designatedReportingDisputeDurationSeconds() internal constant returns (uint256) { return DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS; }
    function reportingDurationSeconds() internal constant returns (uint256) { return REPORTING_DURATION_SECONDS; }
    function reportingDisputeDurationSeconds() internal constant returns (uint256) { return REPORTING_DISPUTE_DURATION_SECONDS; }
    function claimProceedsWaitTime() internal constant returns (uint256) { return CLAIM_PROCEEDS_WAIT_TIME; }
    function getRegistrationTokenBondAmount() internal constant returns (uint256) { return REGISTRATION_TOKEN_BOND_AMOUNT; }
    function designatedReporterDisputeBondAmount() internal constant returns (uint256) { return DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT; }
    function limitedReportersDisputeBondAmount() internal constant returns (uint256) { return LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT; }
    function allReportersDisputeBondAmount() internal constant returns (uint256) { return ALL_REPORTERS_DISPUTE_BOND_AMOUNT; }
    function gasToReport() internal constant returns (uint256) { return GAS_TO_REPORT; }
    function defaultReportingGasPrice() internal constant returns (uint256) { return DEFAULT_REPORTING_GAS_PRICE; }
    function defaultReportsPerMarket() internal constant returns (uint256) { return DEFAULT_REPORTS_PER_MARKET; }
    function defaultValidityBond() internal constant returns (uint256) { return DEFAULT_VALIDITY_BOND; }
    function defaultDesignatedReportStake() internal constant returns (uint256) { return DEFAULT_DESIGNATED_REPORT_STAKE; }
}
