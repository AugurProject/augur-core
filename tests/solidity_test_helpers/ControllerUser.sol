pragma solidity ^0.4.20;

import 'IControlled.sol';
import 'IController.sol';
import 'libraries/token/ERC20Basic.sol';


contract ControllerUser is IControlled {
    address public updatedController;
    address public suicideFundsDestination;
    ERC20Basic[] public suicideFundsTokens;

    function getController() public view returns (IController) {
        return IController(0);
    }

    function setController(IController _controller) public returns(bool) {
        updatedController = _controller;
        return true;
    }

    function suicideFunds(address _destination, ERC20Basic[] _tokens) public returns (bool) {
        suicideFundsDestination = _destination;
        for (uint256 i; i < _tokens.length; ++i) {
            suicideFundsTokens.push(_tokens[i]);
        }
        return true;
    }
}
