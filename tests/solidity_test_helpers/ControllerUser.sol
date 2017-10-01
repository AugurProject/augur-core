pragma solidity ^0.4.13;

import 'ROOT/IControlled.sol';
import 'ROOT/reporting/IUniverse.sol';


contract ControllerUser is IControlled {
    address public suicideFundsDestination;
    address public updatedController;
    address public universe;

    function setController(IController _controller) public returns(bool) {
        updatedController = _controller;
        return true;
    }

    function suicideFunds(address _destination, IUniverse _universe) public returns (bool) {
        suicideFundsDestination = _destination;
        universe = _universe;
        return true;
    }
}
