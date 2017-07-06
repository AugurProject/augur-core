#!/usr/bin/env python

from ContractsFixture import ContractsFixture
from ethereum.tester import TransactionFailed
from pytest import raises

def test_sortedLinkedList():
    fixture = ContractsFixture()
    int256Comparor = fixture.upload('serpent_test_helpers/int256Comparor.se')

    assert int256Comparor.compare(1, 1) == 0
    assert int256Comparor.compare(0, 1) == -1
    assert int256Comparor.compare(1, 0) == 1

    sortedLinkedList = fixture.upload('../src/libraries/sortedLinkedList.se')
    sortedLinkedList.initialize(int256Comparor.address)

    # The list is empty initially
    assert sortedLinkedList.isEmpty()
    assert sortedLinkedList.count() == 0

    # The list is empty. Attempts to get items fail
    with raises(TransactionFailed):
        assert sortedLinkedList.getHead()

    # We can add items
    assert sortedLinkedList.add(42)
    assert sortedLinkedList.count() == 1

    # Adding the same item fails
    assert sortedLinkedList.add(42) == 0

    # head and tail are the same node with 1 item
    assert sortedLinkedList.getHead() == 42
    assert sortedLinkedList.getTail() == 42

    # Adding another item
    assert sortedLinkedList.add(43)
    assert sortedLinkedList.count() == 2

    # Head and tail point to two different nodes
    assert sortedLinkedList.getHead() == 43
    assert sortedLinkedList.getTail() == 42

    # We can get the prev node value for an item
    assert sortedLinkedList.getPrev(43) == 42

    # We can get the next node value for an item
    assert sortedLinkedList.getNext(42) == 43

    # We can remove items by value
    assert sortedLinkedList.remove(42)
    assert sortedLinkedList.count() == 1

    # head and tail are the same node again
    assert sortedLinkedList.getHead() == 43
    assert sortedLinkedList.getTail() == 43

    # The item being removed isn't present. We fail on this
    assert sortedLinkedList.remove(42) == 0

    # Let's add many items and confirm the behavior is as expected
    assert sortedLinkedList.add(42)
    assert sortedLinkedList.add(41)

    assert sortedLinkedList.count() == 3

    assert sortedLinkedList.getHead() == 43
    assert sortedLinkedList.getTail() == 41

    assert sortedLinkedList.getNext(42) == 43
    assert sortedLinkedList.getPrev(42) == 41

    assert sortedLinkedList.getNext(41) == 42
    assert sortedLinkedList.getPrev(43) == 42

    assert sortedLinkedList.hasNext(43) == 0
    assert sortedLinkedList.hasPrev(41) == 0

    # Add to the ends and inbetween
    assert sortedLinkedList.add(45)
    assert sortedLinkedList.add(35)
    assert sortedLinkedList.add(40)

    assert sortedLinkedList.getPrev(45) == 43
    assert sortedLinkedList.getNext(35) == 40
    assert sortedLinkedList.getNext(40) == 41
    assert sortedLinkedList.getPrev(41) == 40

    assert sortedLinkedList.getTail() == 35
    assert sortedLinkedList.getHead() == 45

    assert sortedLinkedList.count() == 6

    # We can provide hints to optimize node ordering during insertion
    # note that the optimization itself is not tested here. We're merely
    # doing code coverage
    assert sortedLinkedList.add(36, [40])

    assert sortedLinkedList.count() == 7
    assert sortedLinkedList.getNext(35) == 36

    # nothing bad happens if we provide invalid hints
    assert sortedLinkedList.contains(38) == 0
    assert sortedLinkedList.add(37, [38])

    assert sortedLinkedList.count() == 8
    assert sortedLinkedList.getNext(36) == 37

    # Ordered backward
    val = sortedLinkedList.getHead()
    while (sortedLinkedList.hasPrev(val)):
        newVal = sortedLinkedList.getPrev(val)
        assert newVal < val
        val = newVal

    # Ordered forward
    val = sortedLinkedList.getTail()
    while (sortedLinkedList.hasNext(val)):
        newVal = sortedLinkedList.getNext(val)
        assert newVal > val
        val = newVal

    # Remove an inbetween
    assert sortedLinkedList.remove(42)
    assert sortedLinkedList.getPrev(43) == 41
    assert sortedLinkedList.getNext(41) == 43

    # Remove ends
    assert sortedLinkedList.remove(35)
    assert sortedLinkedList.getTail() == 36
    assert sortedLinkedList.hasPrev(36) == 0

    assert sortedLinkedList.remove(45)
    assert sortedLinkedList.getHead() == 43
    assert sortedLinkedList.hasNext(43) == 0