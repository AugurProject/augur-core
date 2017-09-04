pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/IController.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Map {
    function initialize (address _owner);
}


contract MapFactory {
    function createMap(IController _controller, address _owner) returns (Map) {
        Delegator _delegator = new Delegator(_controller, "map");
        Map _map = Map(_delegator);
        _map.initialize(_owner);
        return _map;
    }
}
