pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Set {
    function initialize(address owner);
}


contract SetFactory {
    function createSet(Controller _controller, address owner) returns (Set) {
        Delegator _delegator = new Delegator(_controller, "set");
        Set _set = Set(_delegator);
        _set.initialize(owner);
        return _set;
    }
}