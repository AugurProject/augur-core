pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract OrderedSet {
    function initialize(address owner);
}


contract OrderedSetFactory {

    function createOrderedSet(address controller, address owner) returns (OrderedSet) {
        Delegator del = new Delegator(controller, "orderedSet");
        OrderedSet orderedSet = OrderedSet(del);
        orderedSet.initialize(owner);
        return orderedSet;
    }
}