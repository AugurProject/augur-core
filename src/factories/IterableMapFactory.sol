pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/IController.sol';
import 'ROOT/reporting/Interfaces.sol';


contract IterableMapFactory {
    function createIterableMap(IController _controller, address _owner) returns (IIterableMap) {
        Delegator _delegator = new Delegator(_controller, "iterableMap");
        IIterableMap _iterableMap = IIterableMap(_delegator);
        _iterableMap.initialize(_owner);
        return _iterableMap;
    }
}
