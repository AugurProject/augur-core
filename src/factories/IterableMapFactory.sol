pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract IterableMap {
    function initialize(address _owner);
}


contract IterableMapFactory {
    function createIterableMap(Controller _controller, address _owner) returns (IterableMap) {
        Delegator _delegator = new Delegator(_controller, "iterableMap");
        IterableMap _iterableMap = IterableMap(_delegator);
        _iterableMap.initialize(_owner);
        return _iterableMap;
    }
}