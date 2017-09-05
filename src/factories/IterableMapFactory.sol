pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/IController.sol';


contract IIterableMap {
    function initialize(address _owner) public returns (bool);
    function add(bytes32, uint256) public returns (bool);
    function update(bytes32, uint256) public returns (bool);
    function addOrUpdate(bytes32, uint256) public returns (bool);
    function remove(bytes32) public returns (bool);
    function getByKeyOrZero(bytes32) public constant returns (uint256);
    function getByKey(bytes32) public constant returns (uint256);
    function getByOffset(uint256) public constant returns (bytes32);
    function contains(bytes32) public constant returns (bool);
    function count() public constant returns (uint256);
}


contract IterableMapFactory {
    function createIterableMap(IController _controller, address _owner) returns (IIterableMap) {
        Delegator _delegator = new Delegator(_controller, "iterableMap");
        IIterableMap _iterableMap = IIterableMap(_delegator);
        _iterableMap.initialize(_owner);
        return _iterableMap;
    }
}
