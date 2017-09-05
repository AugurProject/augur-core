pragma solidity ^0.4.13;

import "ROOT/libraries/DelegationTarget.sol";
import "ROOT/legacy_reputation/Ownable.sol";
import "ROOT/libraries/Delegator.sol";
import "ROOT/Controller.sol";


contract OrderedSetUint256 is DelegationTarget, Ownable {

    struct OrderedSetItem {
        uint256 prev;
        uint256 next;
        uint256 value;
    }

    mapping (uint256 => OrderedSetItem) private collection;
    mapping (uint256 => uint256) private values;
    uint256 private count;
    uint256 private head;
    uint256 private tail;
    uint256 private nextId;
    address private owner;
    bool private initialized;

    function initialize(address _owner) public onlyOwner returns (bool) {
        require(!initialized);
        initialized = true;
        owner = _owner;
        return (true);
    }

    function push(uint256 _value) public onlyOwner returns (bool) {
        uint256 _itemId = nextId;
        nextId += 1;
        values[_value] = _itemId;
        collection[_itemId].value = _value;
        collection[_itemId].value = head;
        head = _itemId;
        if (tail == 0) {
            tail = _itemId;
        }
        count += 1;
        require(invariants());
        return (true);
    }

    function pop() public onlyOwner returns (uint256) {
        require(isNotEmpty());
        uint256 _index = head;
        uint256 _value = collection[_index].value;
        uint256 _prev = collection[_index].prev;
        delete values[_index];
        delete collection[_index].prev;
        delete collection[_index].value;
        head = _prev;
        if (tail == _index) {
            delete tail;
        }
        count -= 1;
        require(invariants());
        return (_value);
    }

    function insertAfter(uint256 _prevItem, uint256 _newItem) public onlyOwner returns (bool) {
        require(contains(_prevItem));
        uint256 _itemId = nextId;
        nextId += 1;
        uint256 _prevId = values[_prevItem];
        uint256 _nextId = collection[_prevItem].next;
        values[_newItem] = _itemId;
        collection[_itemId].value = _newItem;
        collection[_itemId].prev = _prevId;
        collection[_prevId].next = _itemId;
        if (_nextId != 0) {
            collection[_itemId].next = _nextId;
            collection[_nextId].prev = _itemId;
        } else {
            head = _itemId;
        }
        count += 1;
        require(invariants());
        return (true);
    }

    function insertBefore(uint256 _nextItem, uint256 _newItem) public onlyOwner returns (bool) {
        require(contains(_nextItem));
        uint256 _itemId = nextId;
        nextId += 1;
        uint256 _nextId = values[_nextItem];
        uint256 _prevId = collection[_nextId].prev;
        values[_newItem] = _itemId;
        collection[_itemId].value = _newItem;
        collection[_itemId].next = _nextId;
        collection[_nextId].prev = _itemId;
        if (_prevId != 0) {
            collection[_itemId].prev = _prevId;
            collection[_prevId].next = _itemId;
        } else {
            tail = _itemId;
        }
        count += 1;
        require(invariants());
        return (true);
    }

    function getHead() public constant returns (uint256) {
        return (collection[head].value);
    }

    function getNext(uint256 _item) public constant returns (uint256) {
        require(contains(_item));
        uint256 _itemId = values[_item];
        uint256 _nextId = collection[_itemId].next;
        return (collection[_nextId].value);
    }

    function getPrev(uint256 _item) public constant returns (uint256) {
        uint256 _itemId = values[_item];
        uint256 _prevId = collection[_itemId].prev;
        return (collection[_prevId].value);
    }

    function contains(uint256 _item) public constant returns (bool) {
        return (values[_item] != 0);
    }

    function isEmpty() public constant returns (bool) {
        return (count == 0);
    }

    function isNotEmpty() public constant returns (bool) {
        return (count != 0);
    }

    function invariants() public constant returns (bool) {
        bool _result = true;
        if (head == 0) {
            if (tail != 0 || count != 0) {
                _result = false;
                return (_result);
            }
        }
        if (tail == 0) {
            if (head != 0 || count != 0) {
                _result = false;
                return (_result);
            }
        }
        if (count == 0) {
            if (head != 0 || tail != 0) {
                _result = false;
                return (_result);
            }
        }
        return (_result);
    } 
}


contract OrderedSetUint256Factory {
    function createOrderedSetUint256(Controller _controller, address _owner) returns (OrderedSetUint256) {
        Delegator _delegator = new Delegator(_controller, "OrderedSetUint256");
        OrderedSetUint256 _orderedSetUint256 = OrderedSetUint256(_delegator);
        _orderedSetUint256.initialize(_owner);
        return (_orderedSetUint256);
    }
}