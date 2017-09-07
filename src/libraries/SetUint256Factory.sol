pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/IterableMapUint256.sol';
import "ROOT/libraries/Delegator.sol";


contract SetUint256Factory {
    function createSetUint256(Controller _controller, address _owner) returns (SetUint256) {
        Delegator _delegator = new Delegator(_controller, "SetUint256");
        SetUint256 _setUint256 = SetUint256(_delegator);
        _setUint256.initialize(_owner);
        return (_setUint256);
    }
} 