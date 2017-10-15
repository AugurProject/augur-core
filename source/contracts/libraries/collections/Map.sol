pragma solidity 0.4.17;

import 'libraries/DelegationTarget.sol';
import 'libraries/Ownable.sol';
import 'libraries/Initializable.sol';


contract Map is DelegationTarget ,Ownable, Initializable {
    mapping(bytes32 => address) private items;
    uint256 private count;

    function initialize(address _owner) public beforeInitialized returns (bool) {
        endInitialization();
        owner = _owner;
        return true;
    }

    function add(bytes32 _key, address _value) public onlyOwner returns (bool) {
        if (contains(_key)) {
            return false;
        }
        items[_key] = _value;
        count += 1;
        return true;
    }

    function remove(bytes32 _key) public onlyOwner returns (bool) {
        if (!contains(_key)) {
            return false;
        }
        delete items[_key];
        count -= 1;
        return true;
    }

    function getValueOrZero(bytes32 _key) public view returns (address) {
        return items[_key];
    }

    function get(bytes32 _key) public view returns (address) {
        address _value = items[_key];
        require(_value != address(0));
        return _value;
    }

    function contains(bytes32 _key) public view returns (bool) {
        return items[_key] != address(0);
    }

    function getCount() public view returns (uint256) {
        return count;
    }
}
