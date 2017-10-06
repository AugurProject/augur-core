pragma solidity ^0.4.17;

import 'libraries/Delegator.sol';
import 'reporting/IReportingToken.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';


contract ReportingTokenFactory {
    function createReportingToken(IController _controller, IMarket _market, uint256[] _payoutNumerators) public returns (IReportingToken) {
        Delegator _delegator = new Delegator(_controller, "ReportingToken");
        IReportingToken _reportingToken = IReportingToken(_delegator);
        _reportingToken.initialize(_market, _payoutNumerators);
        return _reportingToken;
    }
}
