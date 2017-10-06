pragma solidity ^0.4.13;

import 'IController.sol';
import 'libraries/token/ERC20Basic.sol';


contract IControlled {
    function setController(IController _controller) public returns(bool);
    function suicideFunds(address _target, ERC20Basic[] _tokens) public returns(bool);
}