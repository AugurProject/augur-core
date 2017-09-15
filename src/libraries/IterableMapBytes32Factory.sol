pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/IterableMapBytes32.sol';
import "ROOT/libraries/Delegator.sol";


contract IterableMapBytes32Factory {
    function createIterableMapBytes32(Controller _controller, address _owner) returns (IterableMapBytes32) {
        Delegator _delegator = new Delegator(_controller, "IterableMapBytes32");
        IterableMapBytes32 _iterableMapBytes32 = IterableMapBytes32(_delegator);
        _iterableMapBytes32.initialize(_owner);
        return (_iterableMapBytes32);
    }
}
