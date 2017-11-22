pragma solidity 0.4.18;


import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';


contract MockReportingWindowFactory {
    IUniverse private createReportingWindowUniverseValue;
    IReportingWindow private createReportingWindowValue;

    function getCreateReportingWindowUniverseValue() public returns(IUniverse) {
        return createReportingWindowUniverseValue;
    }

    function setCreateReportingWindowValue(IReportingWindow _reportingWindowValue) public {
        createReportingWindowValue = _reportingWindowValue;
    }

    function createReportingWindow(IController _controller, IUniverse _universe, uint256 _reportingWindowId) public returns (IReportingWindow) {
        createReportingWindowUniverseValue = _universe;
        return createReportingWindowValue;
    }
}
