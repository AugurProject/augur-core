pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IRegistrationToken.sol';
import 'IController.sol';


contract RegistrationTokenFactory {
    function createRegistrationToken(IController _controller, IReportingWindow _reportingWindow) returns (IRegistrationToken) {
        Delegator _delegator = new Delegator(_controller, "RegistrationToken");
        IRegistrationToken _registrationToken = IRegistrationToken(_delegator);
        _registrationToken.initialize(_reportingWindow);
        return _registrationToken;
    }
}
