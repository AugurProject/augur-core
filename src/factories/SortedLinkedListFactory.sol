pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract SortedLinkedList {
    function initialize(address comparor);
}


contract SortedLinkedListFactory {

    function createSortedLinkedList(address controller, address comparor) returns (SortedLinkedList) {
        Delegator del = new Delegator(controller, "sortedLinkedList");
        SortedLinkedList sortedLinkedList = SortedLinkedList(del);
        sortedLinkedList.initialize(comparor);
        return sortedLinkedList;
    }
}