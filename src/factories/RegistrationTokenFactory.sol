pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/ReportingWindow.sol';
import 'ROOT/reporting/RegistrationToken.sol';
import 'ROOT/Controller.sol';


contract RegistrationTokenFactory {
    function createRegistrationToken(Controller _controller, ReportingWindow _reportingWindow) returns (RegistrationToken) {
        Delegator _delegator = new Delegator(_controller, "RegistrationToken");
        RegistrationToken _registrationToken = RegistrationToken(_delegator);
        _registrationToken.initialize(_reportingWindow);
        return _registrationToken;
    }
}