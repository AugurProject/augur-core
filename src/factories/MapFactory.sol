pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Map {
    function initialize (address owner);
}


contract MapFactory {

    function createMap(address controller, address owner) returns (Map) {
        Delegator del = new Delegator(controller, "map");
        Map map = Map(del);
        map.initialize(owner);
        return map;
    }
}