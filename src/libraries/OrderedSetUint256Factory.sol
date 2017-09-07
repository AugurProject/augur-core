pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/IterableMapUint256.sol';
import "ROOT/libraries/Delegator.sol";


contract OrderedSetUint256Factory {
    function createOrderedSetUint256(Controller _controller, address _owner) returns (OrderedSetUint256) {
        Delegator _delegator = new Delegator(_controller, "OrderedSetUint256");
        OrderedSetUint256 _orderedSetUint256 = OrderedSetUint256(_delegator);
        _orderedSetUint256.initialize(_owner);
        return (_orderedSetUint256);
    }
}