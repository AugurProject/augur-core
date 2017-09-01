pragma solidity ^0.4.13;

import "ROOT/libraries/DelegationTarget.sol";
import "ROOT/legacy_reputation/Ownable.sol";
import "ROOT/libraries/Delegator.sol";
import "ROOT/Controller.sol";


contract MapUint256 is DelegationTarget, Ownable {

    struct MapItem {
        bool hasValue;
        uint256 value;
    }

    mapping(uint256 => MapItem) private collection;
    address private owner;
    bool private initialized;
    uint256 private count;
    

    function initialize(address _owner) public onlyOwner returns (bool) {
        require(!initialized);
        initialized = true;
        owner = _owner;
        return (true);
    }

    function addMapItem(uint256 _key, uint256 _value) public onlyOwner returns (bool) {
        require(!contains(_key));
        collection[_key].hasValue = true;
        collection[_key].value = _value;
        count += 1;
        return (true);
    }

    function remove(uint256 _key) public onlyOwner returns (bool) {
        require(contains(_key));
        delete collection[_key].hasValue;
        delete collection[_key].value;
        count -= 1;
        return (true);
    }

    function contains(uint256 _key) public constant returns (bool) {
        return (collection[_key].hasValue); 
    } 

    function getValueOrZero(uint256 _key) public constant returns (uint256) {
        return (collection[_key].value);
    }

    function getValue(uint256 _key) public constant returns (uint256) {
        require(contains(_key));
        return (collection[_key].value);
    }

    function getCount() public constant returns (uint256) {
        return (count);
    }
}


contract MapFactoryUint256 {
    function createMapUint256(Controller _controller, address _owner) returns (MapUint256) {
        Delegator _delegator = new Delegator(_controller, "MapUint256");
        MapUint256 _mapUint256 = MapUint256(_delegator);
        _mapUint256.initialize(_owner);
        return (_mapUint256);
    }
}