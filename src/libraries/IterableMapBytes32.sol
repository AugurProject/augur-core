pragma solidity ^0.4.13;

import "ROOT/libraries/DelegationTarget.sol";
import "ROOT/libraries/Initializable.sol";


contract IterableMapBytes32 is DelegationTarget, Initializable {
    struct Item {
        bool hasItem;
        bytes32 value;
        uint256 offset;
    }

    address private owner;
    bytes32[] private itemsArray;
    mapping(bytes32 => Item) private itemsMap;

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function initialize(address _owner) external beforeInitialized returns (bool) {
        endInitialization();
        owner = _owner;
        return true;
    }

    function add(bytes32 _key, bytes32 _value) public onlyOwner returns (bool) {
        require(!contains(_key));
        itemsArray.push(_key);
        itemsMap[_key].hasItem = true;
        itemsMap[_key].value = _value;
        itemsMap[_key].offset = itemsArray.length - 1;
        return (true);
    }

    function update(bytes32 _key, bytes32 _value) public onlyOwner returns (bool) {
        require(contains(_key));
        itemsMap[_key].value = _value;
        return (true);
    }

    function addOrUpdate(bytes32 _key, bytes32 _value) public onlyOwner returns (bool) {
        if (!contains(_key)) {
            add(_key, _value);
        } else {
            update(_key, _value);
        }

        return (true);
    }

    function remove(bytes32 _key) public onlyOwner returns (bool) {
        require(contains(_key));
        uint256 _keyRemovedOffset = itemsMap[_key].offset;
        delete itemsArray[_keyRemovedOffset];
        delete itemsMap[_key].hasItem;
        delete itemsMap[_key].value;
        delete itemsMap[_key].offset;

        if (itemsArray.length > 1 && _keyRemovedOffset != (itemsArray.length - 1)) { /* move tail item in collection to the newly opened slot from the key we just removed if not last or only item being removed */
            bytes32 _tailItemKey = getByOffset(itemsArray.length - 1);
            delete itemsArray[itemsArray.length - 1];
            itemsArray[_keyRemovedOffset] = _tailItemKey;
            itemsMap[_tailItemKey].offset = itemsArray.length - 2;
        }

        itemsArray.length -= 1;
        return (true);
    }

    function getByKeyOrZero(bytes32 _key) public constant returns (bytes32) {
        return itemsMap[_key].value;
    }

    function getByKey(bytes32 _key) public constant returns (bytes32) {
        require(itemsMap[_key].hasItem);
        return (itemsMap[_key].value);
    }

    function getByOffset(uint256 _offset) public constant returns (bytes32) {
        require(0 <= _offset && _offset < itemsArray.length);
        return itemsArray[_offset];
    }

    function contains(bytes32 _key) public constant returns (bool) {
        return itemsMap[_key].hasItem;
    }

    function count() public constant returns (uint256) {
        return itemsArray.length;
    }
}
