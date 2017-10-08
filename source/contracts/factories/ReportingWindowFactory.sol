pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingWindow.sol';


contract ReportingWindowFactory {
    function createReportingWindow(IController _controller, IUniverse _universe, uint256 _reportingWindowId) returns (IReportingWindow) {
        Delegator _delegator = new Delegator(_controller, "ReportingWindow");
        IReportingWindow _reportingWindow = IReportingWindow(_delegator);
        _reportingWindow.initialize(_universe, _reportingWindowId);
        return _reportingWindow;
    }
}
