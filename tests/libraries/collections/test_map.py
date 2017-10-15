#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises
from utils import longTo32Bytes, longToHexString

KEY1 = "1"
KEY2 = "2"
KEY3 = "3"
KEY4 = "4"

NULL_ADDRESS = longToHexString(0)

ADDRESS1 = longToHexString(1)
ADDRESS2 = longToHexString(2)
ADDRESS3 = longToHexString(3)
ADDRESS4 = longToHexString(4)

def test_map(testerContractsFixture):
    mapTester = testerContractsFixture.contracts['MapHelper']
    
    # Initially the map has no data
    assert mapTester.getCount() == 0
    assert mapTester.getValueOrZero(KEY1) == NULL_ADDRESS
    assert not mapTester.contains(KEY1)
    with raises(TransactionFailed):
        mapTester.get(KEY1)

    # Add a value
    assert mapTester.add(KEY1, ADDRESS1)

    # Confirm the value is present
    assert mapTester.getCount() == 1
    assert mapTester.getValueOrZero(KEY1) == ADDRESS1
    assert mapTester.contains(KEY1)
    assert mapTester.get(KEY1) == ADDRESS1

    # Remove the value
    assert mapTester.remove(KEY1)

    # Confirm the value is gone
    assert mapTester.getCount() == 0
    assert mapTester.getValueOrZero(KEY1) == NULL_ADDRESS
    assert not mapTester.contains(KEY1)
    with raises(TransactionFailed):
        mapTester.get(KEY1)

    # Add several values
    assert mapTester.add(KEY1, ADDRESS1)
    assert mapTester.add(KEY2, ADDRESS2)
    assert mapTester.add(KEY3, ADDRESS3)
    assert mapTester.add(KEY4, ADDRESS4)

    # Confirm the values are present
    assert mapTester.getCount() == 4
    assert mapTester.getValueOrZero(KEY1) == ADDRESS1
    assert mapTester.contains(KEY1)
    assert mapTester.get(KEY1) == ADDRESS1
    assert mapTester.getValueOrZero(KEY2) == ADDRESS2
    assert mapTester.contains(KEY2)
    assert mapTester.get(KEY2) == ADDRESS2
    assert mapTester.getValueOrZero(KEY3) == ADDRESS3
    assert mapTester.contains(KEY3)
    assert mapTester.get(KEY3) == ADDRESS3
    assert mapTester.getValueOrZero(KEY4) == ADDRESS4
    assert mapTester.contains(KEY4)
    assert mapTester.get(KEY4) == ADDRESS4

    # Remove one of the keys
    assert mapTester.remove(KEY3)

    # Confirm it is gone
    assert mapTester.getCount() == 3
    assert mapTester.getValueOrZero(KEY3) == NULL_ADDRESS
    assert not mapTester.contains(KEY3)
    with raises(TransactionFailed):
        mapTester.get(KEY3)

    # Confirm one of the other is still present
    assert mapTester.getValueOrZero(KEY2) == ADDRESS2
    assert mapTester.contains(KEY2)
    assert mapTester.get(KEY2) == ADDRESS2


@fixture(scope='session')
def testerSnapshot(sessionFixture):
    mapTester = sessionFixture.upload('solidity_test_helpers/MapHelper.sol')
    mapTester.init(sessionFixture.contracts["Controller"].address)
    return sessionFixture.createSnapshot()

@fixture
def testerContractsFixture(sessionFixture, testerSnapshot):
    sessionFixture.resetToSnapshot(testerSnapshot)
    return sessionFixture
