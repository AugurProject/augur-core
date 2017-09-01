pragma solidity ^0.4.13;

import "ROOT/libraries/DelegationTarget.sol";
import "ROOT/legacy_reputation/Ownable.sol";
import "ROOT/libraries/ComparorUint256.sol";
import "ROOT/libraries/Delegator.sol";
import "ROOT/Controller.sol";


contract SortedLinkedListUint256 is DelegationTarget, Ownable, ComparorUint256 {

    struct Node {
        bool exists;
        uint256 prev;
        uint256 next;
    }

    mapping (uint256 => Node) private collection;
    uint256 private count;
    uint256 private head;
    uint256 private tail;
    address private owner;
    bool private initialized;

    function initialize(address _owner) public onlyOwner returns (bool) {
        require(!initialized);
        initialized = true;
        owner = _owner;
        return (true);
    }

    function add(uint256 _item, uint256[] _hints) public onlyOwner returns (bool) {
        require(_item != 0);
        if (contains(_item)) {
            remove(_item);
        }

        /* Insert node into an empty list */
        if (count == 0) {
            insertFirstItem(_item);
            return (true);
        }

        /* Use provided hints to get the starting node for traversal */
        uint256 _bestHint = getBestHint(_hints, _item);

        /* If the bestHint == 0 this indicates an item value greater than the head so it is the new head */
        if (_bestHint == 0) {
            insertAtHead(_item);
            return (true);
        }

        /* Try to find the node to insert before given the bestHint node */
        uint256 _itemNext = findNodeToInsertBefore(_item, _bestHint);

        /* This item is less than or equal to the tail so it will be the new tail */
        if (_itemNext == tail) {
            insertAtTail(_item);
            return (true);
        }

        insertInMiddle(_item, _itemNext);
        return (true);

    }

    function insertFirstItem(uint256 _item) private onlyOwner returns (bool) {
        tail = _item;
        head = _item;
        collection[_item].exists = true;
        count += 1;
        return (true);
    }

    function insertAtHead(uint256 _item) private onlyOwner returns (bool) {
        collection[_item].prev = head;
        collection[head].next = _item;
        head = _item;
        collection[_item].exists = true;
        count += 1;
        require(assertInvariants());
        return (true);
    }

    function insertAtTail(uint256 _item) private onlyOwner returns (bool) {
        collection[_item].next = tail;
        collection[tail].prev = _item;
        tail = _item;
        collection[_item].exists = true;
        count += 1;
        require(assertInvariants());
        return (true);
    }

    function insertInMiddle(uint256 _item, uint256 _itemNext) private onlyOwner returns (bool) {
        collection[collection[_itemNext].prev].next = _item;
        collection[_item].prev = collection[_itemNext].prev;
        collection[_itemNext].prev = _item;
        collection[_item].next = _itemNext;
        collection[_item].exists = true;
        count += 1;

        require(assertInvariants());
        return (true);
    }

    function findNodeToInsertBefore(uint256 _item, uint256 _nodeValue) public constant returns (uint256) {
        /* Do traversal to find the insertion point */
        uint256 _newNodeValue = 0;

        while (hasPrev(_nodeValue)) {
            _newNodeValue = getPrev(_nodeValue);
            if (compare(_newNodeValue, _item) == -1) {
                return (_nodeValue);
            }
            _nodeValue = _newNodeValue;
        }

        return (_nodeValue); 
    }

    function getBestHint(uint256[] _hints, uint256 _item) public constant returns (uint256) {
        uint256 _hintIndex = 0;

        /* If the item is greater than the head we can early out */
        if (compare(_item, head) == 1) {
            return (0);
        }

        uint256 _hint;
        while (_hintIndex < _hints.length) {
            _hint = _hints[_hintIndex];
            if (isValidHint(_hint, _item)) {
                return (_hint);
            }
            _hintIndex += 1;
        }

        return (head);
    }

    function remove(uint256 _item) public onlyOwner returns (bool) {
        if (!contains(_item)) {
            return (false);
        }

        bool _hasPrev = hasPrev(_item);
        bool _hasNext = hasNext(_item);

        if (_hasPrev) {
            if (_hasNext) {
                collection[collection[_item].prev].next = getNext(_item);
            } else {
                head = getPrev(_item);
                delete collection[getPrev(_item)].next;
            }
        }

        if (_hasNext) {
            if (_hasPrev) {
                collection[collection[_item].next].prev = getPrev(_item);
            } else {
                tail = getNext(_item);
                delete collection[getNext(_item)].prev;
            }
        }

        delete collection[_item].exists;
        count -= 1;

        if (count == 0) {
            delete head;
            delete tail;
        }
        
        require(assertInvariants());
        return (true);

    } 

    function getHead() public constant returns (uint256) {
        require(count > 0);
        return (head);
    }

    function getTail() public constant returns (uint256) {
        require(count > 0);
        return (tail);
    }

    function getNext(uint256 _item) public constant returns (uint256) {
        require(contains(_item));
        require(hasNext(_item));
        return (collection[_item].next);
    }

    function getPrev(uint256 _item) public constant returns (uint256) {
        require(contains(_item));
        require(hasPrev(_item));
        return (collection[_item].prev);
    }

    function tryGetNext(uint256 _item) public constant returns (uint256) {
        require(contains(_item));
        if (!hasNext(_item)) {
            return (0);
        }
        return (collection[_item].next);
    }

    function tryGetPrev(uint256 _item) public constant returns (uint256) {
        require(contains(_item));
        if (!hasPrev(_item)) {
            return (0);
        }
        return (collection[_item].prev);
    }

    function hasNext(uint256 _item) public constant returns (bool) {
        require(contains(_item));
        return (collection[collection[_item].next].exists);
    }

    function hasPrev(uint256 _item) public constant returns (bool) {
        require(contains(_item));
        return (collection[collection[_item].prev].exists);
    }

    function contains(uint256 _item) public constant returns (bool) {
        return (collection[_item].exists);
    }

    function getCount() public constant returns (uint256) {
        return (count);
    }

    function isEmpty() public constant returns (bool) {
        return (count == 0);
    }

    function isValidHint(uint256 _hint, uint256 _item) public constant returns (bool) {
        if (!contains(_hint)) {
            return (false);
        }
        if (compare(_hint, _item) != 1) {
            return (false);
        }
        return (true);
    }

    function assertInvariants() public constant returns (bool) {
        bool _result = true;
        if (head != 0) {
            _result = _result && (tail != 0);
            _result = _result && (count != 0);
        }

        if (tail != 0) {
            _result = _result && (head != 0);
            _result = _result && (count != 0);
        }

        if (count != 0) {
            _result = _result && (head != 0);
            _result = _result && (tail != 0);
        }

        return (_result);
    }
}


contract SortedLinkedListUint256Factory {
    function createSortedLinkedListUint256(Controller _controller, address _owner) returns (SortedLinkedListUint256) {
        Delegator _delegator = new Delegator(_controller, "SortedLinkedListUint256");
        SortedLinkedListUint256 _sortedLinkedListUint256 = SortedLinkedListUint256(_delegator);
        _sortedLinkedListUint256.initialize(_owner);
        return (_sortedLinkedListUint256);
    }
}
