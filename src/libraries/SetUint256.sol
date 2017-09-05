pragma solidity ^0.4.13;

import "ROOT/libraries/DelegationTarget.sol";
import "ROOT/legacy_reputation/Ownable.sol";
import "ROOT/libraries/Delegator.sol";
import "ROOT/Controller.sol";


contract SetUint256 is DelegationTarget, Ownable {

    mapping(uint256 => bool) private collection;
    uint private count;
    address private owner;
    bool private initialized;

    function initialize(address _owner) public onlyOwner returns (bool) {
        require(!initialized);
        initialized = true;
        owner = _owner;
        return (true);
    }

    function addSetItem(uint256 _item) public onlyOwner returns (bool) {
        require(!contains(_item));
        collection[_item] = true;
        count += 1;
        return (true);
    }

    function remove(uint256 _item) public onlyOwner returns (bool) {
        require(contains(_item));
        delete collection[_item];
        count -= 1;
        return (true);
    }

    function contains(uint256 _item) public constant returns (bool) {
        return (collection[_item]);
    }

    function getCount() public constant returns (uint256) {
        return (count);
    }
}


contract SetUint256Factory {
    function createSetUint256(Controller _controller, address _owner) returns (SetUint256) {
        Delegator _delegator = new Delegator(_controller, "SetUint256");
        SetUint256 _setUint256 = SetUint256(_delegator);
        _setUint256.initialize(_owner);
        return (_setUint256);
    }
}   