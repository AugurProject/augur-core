pragma solidity ^0.4.13;

import 'Controlled.sol';
import 'libraries/token/ERC20Basic.sol';


contract ControllerUser is Controlled {
    address public updatedController;

    function setController(IController _controller) public returns(bool) {
        super.setController(_controller);
        updatedController = _controller;
        return true;
    }

    function suicideFunds(address _destination, ERC20Basic[] _tokens) public returns (bool) {
        return super.suicideFunds(_destination, _tokens);
    }
}
