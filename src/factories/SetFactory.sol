pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Set {
    function initialize(address owner);
}


contract SetFactory {

    function createSet(address controller, address owner) returns (Set) {
        Delegator del = new Delegator(controller, "set");
        Set set = Set(del);
        set.initialize(owner);
        return set;
    }
}