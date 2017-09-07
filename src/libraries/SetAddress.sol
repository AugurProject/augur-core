pragma solidity ^0.4.13;

import "ROOT/libraries/DelegationTarget.sol";
import "ROOT/libraries/Initializable.sol";


contract SetAddress is DelegationTarget, Initializable {

    mapping(address => bool) private collection;
    uint256 private count;
    address private owner;
    bool private initialized;

    function initialize(address _owner) public onlyOwner returns (bool) {
        require(!initialized);
        initialized = true;
        owner = _owner;
        return true;
    }

    function addSetItem(address _item) public onlyOwner returns (bool) {
        require(!contains(_item));
        collection[_item] = true;
        count += 1;
        return true;
    }

    function remove(address _item) public onlyOwner returns (bool) {
        require(contains(_item));
        delete collection[_item];
        count -= 1;
        return true;
    }

    function contains(address _item) public constant returns (bool) {
        return collection[_item];
    }

    function getCount() public constant returns (uint256) {
        return count;
    }
}


  