pragma solidity ^0.4.13;

import "ROOT/libraries/DelegationTarget.sol";
import "ROOT/libraries/Initializable.sol";


contract MapUint256 is DelegationTarget, Initializable {

    struct MapItem {
        bool hasValue;
        uint256 value;
    }

    mapping(uint256 => MapItem) private collection;
    address private owner;
    bool private initialized;
    uint256 private count;
    

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function initialize(address _owner) external beforeInitialized returns (bool) {
        endInitialization();
        owner = _owner;
        return true;
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
