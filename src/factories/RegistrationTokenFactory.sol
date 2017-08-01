pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract ReportingWindow {
    function stub() {}
}


// FIXME: remove once this can be imported as a solidty contract
contract RegistrationToken {
    function initialize(ReportingWindow _reportingWindow);
}


contract RegistrationTokenFactory {
    function createRegistrationToken(Controller _controller, ReportingWindow _reportingWindow) returns (RegistrationToken) {
        Delegator _delegator = new Delegator(_controller, "registrationToken");
        RegistrationToken _registrationToken = RegistrationToken(_delegator);
        _registrationToken.initialize(_reportingWindow);
        return _registrationToken;
    }
}