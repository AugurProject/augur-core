pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/IterableMapUint256.sol';
import "ROOT/libraries/Delegator.sol";


contract IterableMapUint256Factory {
    function createIterableMapUint256(Controller _controller, address _owner) returns (IterableMapUint256) {
        Delegator _delegator = new Delegator(_controller, "IterableMapUint256");
        IterableMapUint256 _iterableMapUint256 = IterableMapUint256(_delegator);
        _iterableMapUint256.initialize(_owner);
        return (_iterableMapUint256);
    }
}
