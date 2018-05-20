pragma solidity 0.4.20;

import 'reporting/IInitialReporter.sol';
import 'reporting/IMarket.sol';


contract MockInitialReporter is IInitialReporter {
    address private market;
    address private designatedReporter;
    bytes32 private payoutDistributionHash;
    uint256 private reportTimestamp;
    bool private reportWasCalledValue;

    function setReportTimestamp(uint256 _reportTimestamp) public returns (bool) {
        reportTimestamp = _reportTimestamp;
        return true;
    }

    function setPayoutDistributionHash(bytes32 _payoutDistributionHash) public returns (bool) {
        payoutDistributionHash = _payoutDistributionHash;
        return true;
    }

    function initialize(IMarket _market, address _designatedReporter) public returns (bool) {
        market = _market;
        designatedReporter = _designatedReporter;
        return true;
    }

    function callMintFeeTokens(IFeeWindow _feeWindow, uint256 _amount) public returns (bool) {
        return _feeWindow.mintFeeTokens(_amount);
    }

    function reportWasCalled() public returns(bool) { return reportWasCalledValue; }

    function report(address _reporter, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public returns (bool) {
        reportWasCalledValue = true;
        return true;
    }

    function resetReportTimestamp() public returns (bool) {
        return true;
    }

    function designatedReporterShowed() public view returns (bool) {
        return true;
    }

    function designatedReporterWasCorrect() public view returns (bool) {
        return true;
    }

    function getDesignatedReporter() public view returns (address) {
        return designatedReporter;
    }

    function getReportTimestamp() public view returns (uint256) {
        return reportTimestamp;
    }

    function getStake() public view returns (uint256) {
        return 0;
    }

    function getPayoutDistributionHash() public view returns (bytes32) {
        return payoutDistributionHash;
    }

    function liquidateLosing() public returns (bool) {
        return true;
    }

    function fork() internal returns (bool) {
        return true;
    }

    function redeem(address _redeemer) public returns (bool) {
        return true;
    }

    function isInvalid() public view returns (bool) {
        return true;
    }

    function isDisavowed() public view returns (bool) {
        return true;
    }

    function migrate() public returns (bool) {
        return true;
    }

    function getPayoutNumerator(uint256 _outcome) public view returns (uint256) {
        return 0;
    }

    function getMarket() public view returns (IMarket) {
        return IMarket(0);
    }

    function getSize() public view returns (uint256) {
        return 0;
    }

    function migrateREP() public returns (bool) {
        return true;
    }
}
