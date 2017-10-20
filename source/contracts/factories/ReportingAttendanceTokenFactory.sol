pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IReportingAttendanceToken.sol';
import 'reporting/IReportingWindow.sol';
import 'IController.sol';


contract ReportingAttendanceTokenFactory {
    function createReportingAttendanceToken(IController _controller, IReportingWindow _reportingWindow) public returns (IReportingAttendanceToken) {
        Delegator _delegator = new Delegator(_controller, "ReportingAttendanceToken");
        IReportingAttendanceToken _token = IReportingAttendanceToken(_delegator);
        _token.initialize(_reportingWindow);
        return _token;
    }
}
