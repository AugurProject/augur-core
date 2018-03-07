pragma solidity ^0.4.20;

import 'libraries/collections/Map.sol';
import 'factories/MapFactory.sol';
import 'IController.sol';


contract MapHelper {
    Map private map;

    function init(IController _controller) public returns (bool) {
        map = MapFactory(_controller.lookup("MapFactory")).createMap(_controller, this);
    }

    function add(bytes32 _key, bytes32 _value) public returns (bool) {
        return map.add(_key, _value);
    }

    function remove(bytes32 _key) public returns (bool) {
        return map.remove(_key);
    }

    function getValueOrZero(bytes32 _key) public view returns (bytes32) {
        return map.getValueOrZero(_key);
    }

    function get(bytes32 _key) public view returns (bytes32) {
        return map.get(_key);
    }

    function contains(bytes32 _key) public view returns (bool) {
        return map.contains(_key);
    }

    function getCount() public view returns (uint256) {
        return map.getCount();
    }

    // Address casting

    function addAsAddress(bytes32 _key, address _value) public returns (bool) {
        return map.add(_key, _value);
    }

    function getAsAddressOrZero(bytes32 _key) public view returns (address) {
        return map.getAsAddressOrZero(_key);
    }

    function getAsAddress(bytes32 _key) public view returns (address) {
        return map.getAsAddress(_key);
    }
}
