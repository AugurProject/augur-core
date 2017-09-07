pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/IterableMapUint256.sol';
import "ROOT/libraries/Delegator.sol";

contract StackUint256Factory {
    function createStackUint256(Controller _controller, address _owner) returns (StackUint256) {
        Delegator _delegator = new Delegator(_controller, "StackUint256");
        StackUint256 _stackUint256 = StackUint256(_delegator);
        _stackUint256.initialize(_owner);
        return (_stackUint256);
    }
}