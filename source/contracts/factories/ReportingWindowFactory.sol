pragma solidity ^0.4.13;

import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IBranch.sol';
import 'reporting/IReportingWindow.sol';


contract ReportingWindowFactory {
    function createReportingWindow(IController _controller, IBranch _branch, uint256 _reportingWindowId) returns (IReportingWindow) {
        Delegator _delegator = new Delegator(_controller, "ReportingWindow");
        IReportingWindow _reportingWindow = IReportingWindow(_delegator);
        _reportingWindow.initialize(_branch, _reportingWindowId);
        return _reportingWindow;
    }
}
