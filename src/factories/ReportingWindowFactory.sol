pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract ReportingWindow {
    function initialize(address branch, int256 reportingWindowId);
}


contract ReportingWindowFactory {

    function createReportingWindow(address controller, address branch, int256 reportingWindowId) returns (ReportingWindow) {
        Delegator del = new Delegator(controller, "reportingWindow");
        ReportingWindow reportingWindow = ReportingWindow(del);
        reportingWindow.initialize(branch, reportingWindowId);
        return reportingWindow;
    }
}