pragma solidity 0.4.20;

import 'libraries/DelegationTarget.sol';
import 'libraries/Ownable.sol';
import 'libraries/Initializable.sol';


// Provides a mapping that has a count and more control over the behavior of Key errors. Additionally allows for a clean way to clear an existing map by simply creating a new one on owning contracts.
contract Map is DelegationTarget, Ownable, Initializable {
    mapping(bytes32 => bytes32) private items;
    uint256 private count;

    function initialize(address _owner) public beforeInitialized returns (bool) {
        endInitialization();
        owner = _owner;
        return true;
    }

    function add(bytes32 _key, bytes32 _value) public onlyOwner returns (bool) {
        if (contains(_key)) {
            return false;
        }
        items[_key] = _value;
        count += 1;
        return true;
    }

    function add(bytes32 _key, address _value) public onlyOwner returns (bool) {
        return add(_key, bytes32(_value));
    }

    function remove(bytes32 _key) public onlyOwner returns (bool) {
        if (!contains(_key)) {
            return false;
        }
        delete items[_key];
        count -= 1;
        return true;
    }

    function getValueOrZero(bytes32 _key) public view returns (bytes32) {
        return items[_key];
    }

    function get(bytes32 _key) public view returns (bytes32) {
        bytes32 _value = items[_key];
        require(_value != bytes32(0));
        return _value;
    }

    function getAsAddressOrZero(bytes32 _key) public view returns (address) {
        return address(getValueOrZero(_key));
    }

    function getAsAddress(bytes32 _key) public view returns (address) {
        return address(get(_key));
    }

    function contains(bytes32 _key) public view returns (bool) {
        return items[_key] != bytes32(0);
    }

    function getCount() public view returns (uint256) {
        return count;
    }

    function onTransferOwnership(address, address) internal returns (bool) {
        return true;
    }
}
