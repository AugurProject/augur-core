pragma solidity 0.4.24;


import 'libraries/Delegator.sol';
import 'IController.sol';
import 'libraries/collections/Map.sol';


contract MapFactory {
    function createMap(IController _controller, address _owner) public returns (Map) {
        Delegator _delegator = new Delegator(_controller, "Map");
        Map _map = Map(_delegator);
        _map.initialize(_owner);
        return _map;
    }
}
