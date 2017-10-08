pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

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
