pragma solidity ^0.4.13;

import 'IController.sol';
import 'reporting/IUniverse.sol';


contract IControlled {
    function setController(IController _controller) public returns(bool);
    function suicideFunds(address _target, IUniverse _universe) public returns(bool);
}
