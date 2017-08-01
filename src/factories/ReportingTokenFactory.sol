pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract ReportingToken {
    function initialize(address market, int256[] payoutNumerators);
}


contract ReportingTokenFactory {

    function createReportingToken(address controller, address market, int256[] payoutNumerators) returns (ReportingToken) {
        Delegator del = new Delegator(controller, "reportingToken");
        ReportingToken reportingToken = ReportingToken(del);
        reportingToken.initialize(market, payoutNumerators);
        return reportingToken;
    }
}