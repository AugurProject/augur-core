pragma solidity 0.4.24;

import 'libraries/CloneFactory.sol';
import 'IController.sol';
import 'libraries/collections/Map.sol';


contract MapFactory is CloneFactory {
    function createMap(IController _controller, address _owner) public returns (Map) {
        Map _map = Map(createClone(_controller.lookup("Map")));
        IControlled(_map).setController(_controller);
        _map.initialize(_owner);
        return _map;
    }
}
