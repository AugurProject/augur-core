pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Market {
    function stub() {}
}


// FIXME: remove once this can be imported as a solidty contract
contract ReportingToken {
    function initialize(Market _market, int256[] _payoutNumerators);
}


contract ReportingTokenFactory {
    function createReportingToken(Controller _controller, Market _market, int256[] _payoutNumerators) returns (ReportingToken) {
        Delegator _delegator = new Delegator(_controller, "reportingToken");
        ReportingToken _reportingToken = ReportingToken(_delegator);
        _reportingToken.initialize(_market, _payoutNumerators);
        return _reportingToken;
    }
}