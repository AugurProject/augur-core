pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/ReportingToken.sol';
import 'ROOT/reporting/Market.sol';


contract ReportingTokenFactory {
    function createReportingToken(Controller _controller, Market _market, uint256[] _payoutNumerators) public returns (ReportingToken) {
        Delegator _delegator = new Delegator(_controller, "ReportingToken");
        ReportingToken _reportingToken = ReportingToken(_delegator);
        _reportingToken.initialize(_market, _payoutNumerators);
        return _reportingToken;
    }
}
