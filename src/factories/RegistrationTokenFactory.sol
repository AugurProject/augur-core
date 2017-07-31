pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';

// FIXME: remove once this can be imported as a solidty contract
contract RegistrationToken {
    function initialize(address reportingWindow);
}

contract RegistrationTokenFactory {

    function createRegistrationToken(address controller, address reportingWindow) returns (RegistrationToken) {
        Delegator del = new Delegator(controller, 'registrationToken');
        RegistrationToken registrationToken = RegistrationToken(del);
        registrationToken.initialize(reportingWindow);
        return registrationToken;
    }
}