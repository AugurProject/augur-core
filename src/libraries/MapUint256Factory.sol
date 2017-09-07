pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/IterableMapUint256.sol';
import "ROOT/libraries/Delegator.sol";


contract MapFactoryUint256 {
    function createMapUint256(Controller _controller, address _owner) returns (MapUint256) {
        Delegator _delegator = new Delegator(_controller, "MapUint256");
        MapUint256 _mapUint256 = MapUint256(_delegator);
        _mapUint256.initialize(_owner);
        return (_mapUint256);
    }
}