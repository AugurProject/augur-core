#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture as pytest_fixture
from utils import bytesToHexString

def test_getController(controlled):
    assert controlled.getController() == bytesToHexString(tester.a0)

def test_setController(controlled):
    with raises(TransactionFailed):
        controlled.setController(tester.a1, sender=tester.k1)
    assert controlled.setController(tester.a1, sender=tester.k0)
    assert controlled.getController() == bytesToHexString(tester.a1)
    with raises(TransactionFailed):
        controlled.setController(tester.a2, sender=tester.k0)

@pytest_fixture(scope="session")
def localSnapshot(fixture, baseSnapshot):
    fixture.resetToSnapshot(baseSnapshot)
    fixture.upload('solidity_test_helpers/TestControlled.sol')
    fixture.upload('solidity_test_helpers/StandardTokenHelper.sol')
    return fixture.createSnapshot()

@pytest_fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@pytest_fixture
def controlled(localFixture):
    return localFixture.contracts['TestControlled']

@pytest_fixture
def token(localFixture):
    return localFixture.contracts['StandardTokenHelper']

@pytest_fixture
def chain(localFixture):
    return localFixture.chain
