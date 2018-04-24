#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises
from utils import longTo32Bytes, longToHexString

KEY1 = "1"
KEY2 = "2"
KEY3 = "3"
KEY4 = "4"

NULL_VALUE = longTo32Bytes(0)

VALUE1 = longTo32Bytes(1)
VALUE2 = longTo32Bytes(2)
VALUE3 = longTo32Bytes(3)
VALUE4 = longTo32Bytes(4)

NULL_ADDRESS = longToHexString(0)
ADDRESS = longToHexString(1)

def test_map(testerContractsFixture):
    mapTester = testerContractsFixture.contracts['MapHelper']

    # Initially the map has no data
    assert mapTester.getCount() == 0
    assert mapTester.getValueOrZero(KEY1) == NULL_VALUE
    assert not mapTester.contains(KEY1)
    with raises(TransactionFailed):
        mapTester.get(KEY1)

    # Add a value
    assert mapTester.add(KEY1, VALUE1)

    assert not mapTester.add(KEY1, VALUE1)

    # Confirm the value is present
    assert mapTester.getCount() == 1
    assert mapTester.getValueOrZero(KEY1) == VALUE1
    assert mapTester.contains(KEY1)
    assert mapTester.get(KEY1) == VALUE1

    # Remove the value
    assert mapTester.remove(KEY1)

    assert not mapTester.remove(KEY1)

    # Confirm the value is gone
    assert mapTester.getCount() == 0
    assert mapTester.getValueOrZero(KEY1) == NULL_VALUE
    assert not mapTester.contains(KEY1)
    with raises(TransactionFailed):
        mapTester.get(KEY1)

    # Add several values
    assert mapTester.add(KEY1, VALUE1)
    assert mapTester.add(KEY2, VALUE2)
    assert mapTester.add(KEY3, VALUE3)
    assert mapTester.add(KEY4, VALUE4)

    # Confirm the values are present
    assert mapTester.getCount() == 4
    assert mapTester.getValueOrZero(KEY1) == VALUE1
    assert mapTester.contains(KEY1)
    assert mapTester.get(KEY1) == VALUE1
    assert mapTester.getValueOrZero(KEY2) == VALUE2
    assert mapTester.contains(KEY2)
    assert mapTester.get(KEY2) == VALUE2
    assert mapTester.getValueOrZero(KEY3) == VALUE3
    assert mapTester.contains(KEY3)
    assert mapTester.get(KEY3) == VALUE3
    assert mapTester.getValueOrZero(KEY4) == VALUE4
    assert mapTester.contains(KEY4)
    assert mapTester.get(KEY4) == VALUE4

    # Remove one of the keys
    assert mapTester.remove(KEY3)

    # Confirm it is gone
    assert mapTester.getCount() == 3
    assert mapTester.getValueOrZero(KEY3) == NULL_VALUE
    assert not mapTester.contains(KEY3)
    with raises(TransactionFailed):
        mapTester.get(KEY3)

    # Confirm one of the other is still present
    assert mapTester.getValueOrZero(KEY2) == VALUE2
    assert mapTester.contains(KEY2)
    assert mapTester.get(KEY2) == VALUE2

def test_address_casting(testerContractsFixture):
    mapTester = testerContractsFixture.contracts['MapHelper']

    # With nothing available we'll get a null address from the address casting getters
    assert mapTester.getAsAddressOrZero(KEY1) == NULL_ADDRESS
    with raises(TransactionFailed):
        mapTester.getAsAddress(KEY1)

    # Add a value as an address
    assert mapTester.addAsAddress(KEY1, ADDRESS)

    # Now we can retrieve it as an address
    assert mapTester.getAsAddressOrZero(KEY1) == ADDRESS
    assert mapTester.getAsAddress(KEY1) == ADDRESS



@fixture(scope='session')
def testerSnapshot(sessionFixture):
    mapTester = sessionFixture.upload('solidity_test_helpers/MapHelper.sol')
    mapTester.init(sessionFixture.contracts["Controller"].address)
    return sessionFixture.createSnapshot()

@fixture
def testerContractsFixture(sessionFixture, testerSnapshot):
    sessionFixture.resetToSnapshot(testerSnapshot)
    return sessionFixture
