pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/IReportingToken.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/IController.sol';


contract ReportingTokenFactory {
    function createReportingToken(IController _controller, IMarket _market, uint256[] _payoutNumerators) public returns (IReportingToken) {
        Delegator _delegator = new Delegator(_controller, "ReportingToken");
        IReportingToken _reportingToken = IReportingToken(_delegator);
        _reportingToken.initialize(_market, _payoutNumerators);
        return _reportingToken;
    }
}
