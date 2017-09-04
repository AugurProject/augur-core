pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/reporting/IRegistrationToken.sol';
import 'ROOT/IController.sol';


contract RegistrationTokenFactory {
    function createRegistrationToken(IController _controller, IReportingWindow _reportingWindow) returns (IRegistrationToken) {
        Delegator _delegator = new Delegator(_controller, "RegistrationToken");
        IRegistrationToken _registrationToken = IRegistrationToken(_delegator);
        _registrationToken.initialize(_reportingWindow);
        return _registrationToken;
    }
}
