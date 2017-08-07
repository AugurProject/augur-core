#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises
from ethereum.config import config_metropolis

#config_metropolis['BLOCK_GAS_LIMIT'] = 2**128
 
@fixture(scope="session")
def arraySnapshot(sessionFixture):
    arrayHelper = sessionFixture.upload('solidity_test_helpers/ArrayHelper.sol')
    return sessionFixture.chain.snapshot()

@fixture
def arrayContractsFixture(sessionFixture, arraySnapshot):
    sessionFixture.chain.revert(arraySnapshot)
    return sessionFixture

def test_arraySlicingOnEmpty(arrayContractsFixture):

    arrayHelper = arrayContractsFixture.contracts['ArrayHelper']

    assert arrayHelper.getSlice(0, 1) == []
    assert arrayHelper.getSlice(0, 0) == []
    assert arrayHelper.getSlice(1, 1) == []
    assert arrayHelper.getSlice(1, 0) == []

def test_arraySlicing(arrayContractsFixture):

    arrayHelper = arrayContractsFixture.contracts['ArrayHelper']

    # Set some initial data
    arrayHelper.setData([1,2,3,4,5])

    # Confirm the data we set is stored correctly
    assert arrayHelper.getSize() == 5
    assert arrayHelper.getItem(0) == 1
    assert arrayHelper.getItem(4) == 5

    # Get empty arrays by request
    assert arrayHelper.getSlice(0, 0) == []
    assert arrayHelper.getSlice(1, 0) == []

    # Get single item arrays
    assert arrayHelper.getSlice(0, 1) == [1]
    assert arrayHelper.getSlice(1, 1) == [2]
    assert arrayHelper.getSlice(4, 1) == [5]

    # Get truncated results from requesting more items than actually exist
    assert arrayHelper.getSlice(5, 1) == []
    assert arrayHelper.getSlice(4, 2) == [5]

    # Get slices with multiple items
    assert arrayHelper.getSlice(0, 5) == [1,2,3,4,5]
    assert arrayHelper.getSlice(0, 3) == [1,2,3]
    assert arrayHelper.getSlice(2, 2) == [3,4]
    assert arrayHelper.getSlice(3, 2) == [4,5]