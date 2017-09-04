pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/IController.sol';


// FIXME: remove once this can be imported as a solidty contract
contract SortedLinkedList {
    function initialize(address _comparor);
}


contract SortedLinkedListFactory {
    function createSortedLinkedList(IController _controller, address _comparor) returns (SortedLinkedList) {
        Delegator _delegator = new Delegator(_controller, "sortedLinkedList");
        SortedLinkedList _sortedLinkedList = SortedLinkedList(_delegator);
        _sortedLinkedList.initialize(_comparor);
        return _sortedLinkedList;
    }
}
