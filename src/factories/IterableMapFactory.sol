pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract IterableMap {
    function initialize(address owner);
}


contract IterableMapFactory {

    function createIterableMap(address controller, address owner) returns (IterableMap) {
        Delegator del = new Delegator(controller, "iterableMap");
        IterableMap iterableMap = IterableMap(del);
        iterableMap.initialize(owner);
        return iterableMap;
    }
}