pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/IterableMapUint256.sol';
import "ROOT/libraries/Delegator.sol";


contract SetAddressFactory {
    function createSetAddress(Controller _controller, address _owner) returns (SetAddress) {
        Delegator _delegator = new Delegator(_controller, "SetAddress");
        SetAddress _setAddress = SetAddress(_delegator);
        _setAddress.initialize(_owner);
        return _setAddress;
    }
} 