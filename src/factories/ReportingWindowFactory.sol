pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';
import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/ReportingWindow.sol';
import 'ROOT/reporting/Interfaces.sol';


contract ReportingWindowFactory {
    function createReportingWindow(Controller _controller, Branch _branch, uint256 _reportingWindowId) returns (ReportingWindow) {
        Delegator _delegator = new Delegator(_controller, "ReportingWindow");
        ReportingWindow _reportingWindow = ReportingWindow(_delegator);
        _reportingWindow.initialize(_branch, _reportingWindowId);
        return _reportingWindow;
    }
}
