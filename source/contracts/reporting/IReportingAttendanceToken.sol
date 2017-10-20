pragma solidity 0.4.17;

import 'libraries/token/ERC20.sol';
import 'reporting/IReportingWindow.sol';


contract IReportingAttendanceToken is ERC20 {
    function initialize(IReportingWindow _reportingWindow) public returns (bool);
    function getReportingWindow() public view returns (IReportingWindow);
}
