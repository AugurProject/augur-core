pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/reporting/Interfaces.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Set is Typed {
    function initialize(address owner);
    function addSetItem(address) public returns (bool);
    function remove(address) public returns (bool);
    function contains(address) public constant returns (bool);
    function count() public constant returns (uint256);
}


contract SetFactory {
    function createSet(Controller _controller, address owner) returns (Set) {
        Delegator _delegator = new Delegator(_controller, "set");
        Set _set = Set(_delegator);
        _set.initialize(owner);
        return _set;
    }
}