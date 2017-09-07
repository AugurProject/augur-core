pragma solidity ^0.4.13;


library Reporting {
    uint256 private constant AUTOMATED_REPORTING_DURATION_SECONDS = 3 days;
    uint256 private constant AUTOMATED_REPORTING_DISPUTE_DURATION_SECONDS = 3 days;
    uint256 private constant REPORTING_DURATION_SECONDS = 27 * 1 days;
    uint256 private constant REPORTING_DISPUTE_DURATION_SECONDS = 3 days;
    uint256 private constant CLAIM_PROCEEDS_WAIT_TIME = 3 days;
    uint256 private constant REGISTRATION_TOKEN_BOND_AMOUNT = 1 ether;

    function automatedReportingDurationSeconds() internal constant returns (uint256) { return AUTOMATED_REPORTING_DURATION_SECONDS; }
    function automatedReportingDisputeDurationSeconds() internal constant returns (uint256) { return AUTOMATED_REPORTING_DISPUTE_DURATION_SECONDS; }
    function reportingDurationSeconds() internal constant returns (uint256) { return REPORTING_DURATION_SECONDS; }
    function reportingDisputeDurationSeconds() internal constant returns (uint256) { return REPORTING_DISPUTE_DURATION_SECONDS; }
    function claimProceedsWaitTime() internal constant returns (uint256) { return CLAIM_PROCEEDS_WAIT_TIME; }
    function getRegistrationTokenBondAmount() internal constant returns (uint256) { return REGISTRATION_TOKEN_BOND_AMOUNT; }
}
