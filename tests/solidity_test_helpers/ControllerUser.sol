pragma solidity ^0.4.13;

import 'IControlled.sol';
import 'libraries/token/ERC20Basic.sol';


contract ControllerUser is IControlled {
    address public suicideFundsDestination;
    address public updatedController;
    ERC20Basic[] public tokens;

    function setController(IController _controller) public returns(bool) {
        updatedController = _controller;
        return true;
    }

    function suicideFunds(address _destination, ERC20Basic[] _tokens) public returns (bool) {
        suicideFundsDestination = _destination;
        tokens = _tokens;
        return true;
    }
}
