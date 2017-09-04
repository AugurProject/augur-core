pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/IController.sol';


// FIXME: remove once this can be imported as a solidty contract
contract OrderedSet {
    function initialize(address _owner);
}


contract OrderedSetFactory {
    function createOrderedSet(IController _controller, address _owner) returns (OrderedSet) {
        Delegator _delegator = new Delegator(_controller, "orderedSet");
        OrderedSet _orderedSet = OrderedSet(_delegator);
        _orderedSet.initialize(_owner);
        return _orderedSet;
    }
}
