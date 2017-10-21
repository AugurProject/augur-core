pragma solidity 0.4.17;

import 'libraries/Delegator.sol';
import 'reporting/IReportingAttendanceToken.sol';
import 'reporting/IReportingWindow.sol';
import 'IController.sol';


contract MockReportingAttendanceTokenFactory {

    IReportingAttendanceToken private attendanceTokenValue;
    IController private createReportingAttendanceTokenControllerValue;
    IReportingWindow private createReportingAttendanceTokenReportingWindow;

    function setAttendanceTokenValue(IReportingAttendanceToken _attendanceTokenValue) public {
        attendanceTokenValue = _attendanceTokenValue;
    }

    function getCreateReportingAttendanceTokenControllerValue() public returns(IController) {
        return createReportingAttendanceTokenControllerValue;
    }

    function getCreateReportingAttendanceTokenReportingWindow() public returns(IReportingWindow) {
        return createReportingAttendanceTokenReportingWindow;
    }

    function createReportingAttendanceToken(IController _controller, IReportingWindow _reportingWindow) public returns (IReportingAttendanceToken) {
        createReportingAttendanceTokenControllerValue = _controller;
        createReportingAttendanceTokenReportingWindow = _reportingWindow;
        return attendanceTokenValue;
    }
}
