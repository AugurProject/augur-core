pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Branch {
    function stub() {}
}


// FIXME: remove once this can be imported as a solidty contract
contract ReportingWindow {
    function initialize(Branch _branch, int256 _reportingWindowId);
}


contract ReportingWindowFactory {

    function createReportingWindow(Controller _controller, Branch _branch, int256 _reportingWindowId) returns (ReportingWindow) {
        Delegator _delegator = new Delegator(_controller, "reportingWindow");
        ReportingWindow _reportingWindow = ReportingWindow(_delegator);
        _reportingWindow.initialize(_branch, _reportingWindowId);
        return _reportingWindow;
    }
}