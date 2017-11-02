pragma solidity 0.4.17;


import 'IController.sol';
import 'libraries/collections/Map.sol';


contract MockMapFactory {
    Map private createMapValue;
    address private createOwnerValue;

    function setMap(Map _map) public {
        createMapValue = _map;
    }

    function getMap() public returns(Map) {
        return createMapValue;
    }

    function getCreateOwner() public returns(address) {
        return createOwnerValue;
    }

    function createMap(IController _controller, address _owner) public returns (Map) {
        createOwnerValue = _owner;
        return createMapValue;
    }
}
