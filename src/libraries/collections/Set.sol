pragma solidity ^0.4.13;


library Set {
    struct Item {
        bytes32 value;
        bool exists;
    }

    struct Data {
        mapping(bytes32 => Item) items;
        uint256 count;
    }

    function add(Data storage _this, bytes32 _value) internal returns (bool) {
        Item storage _item = _this.items[_value];
        if (_item.exists) {
            return false;
        }
        _item.value = _value;
        _item.exists = true;
        _this.count += 1;
        return true;
    }

    function add(Data storage _this, address _value) internal returns (bool) {
        return add(_this, bytes32(_value));
    }

    function remove(Data storage _this, bytes32 _value) internal returns (bool) {
        Item storage _item = _this.items[_value];
        if (!_item.exists) {
            return false;
        }
        delete _this.items[_value];
        _this.count -= 1;
        return true;
    }

    function remove(Data storage _this, address _value) internal returns (bool) {
        return remove(_this, bytes32(_value));
    }

    function contains(Data storage _this, bytes32 _value) internal returns (bool) {
        return _this.items[_value].exists;
    }

    function contains(Data storage _this, address _value) internal returns (bool) {
        return contains(_this, bytes32(_value));
    }
}
