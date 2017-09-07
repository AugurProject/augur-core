pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/IterableMapUint256.sol';
import 'ROOT/libraries/Delegator.sol';

contract SortedLinkedListUint256Factory {
    function createSortedLinkedListUint256(Controller _controller, address _owner) returns (SortedLinkedListUint256) {
        Delegator _delegator = new Delegator(_controller, "SortedLinkedListUint256");
        SortedLinkedListUint256 _sortedLinkedListUint256 = SortedLinkedListUint256(_delegator);
        _sortedLinkedListUint256.initialize(_owner);
        return (_sortedLinkedListUint256);
    }
}