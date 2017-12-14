pragma solidity 0.4.18;

import 'reporting/IReportingParticipant.sol';
import 'reporting/IMarket.sol';


contract IInitialReporter is IReportingParticipant {
    function initialize(IMarket _market, address _designatedReporter) public returns (bool);
    function report(address _reporter, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public returns (bool);
    function resetReportTimestamp() public returns (bool);
    function designatedReporterShowed() public view returns (bool);
    function designatedReporterWasCorrect() public view returns (bool);
    function getDesignatedReporter() public view returns (address);
    function getReportTimestamp() public view returns (uint256);
    function depositGasBond() public payable returns (bool);
}
