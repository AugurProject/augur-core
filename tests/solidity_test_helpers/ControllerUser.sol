pragma solidity ^0.4.13;

import 'ROOT/IControlled.sol';


contract ControllerUser is IControlled {
    address public suicideFundsDestination;
    address public updatedController;

    function setController(IController _controller) public returns(bool) {
        updatedController = _controller;
        return true;
    }

    function suicideFunds(address _destination) public returns (bool) {
        suicideFundsDestination = _destination;
        return true;
    }
}
