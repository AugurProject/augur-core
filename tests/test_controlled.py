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

def test_suicide(controlled, token, chain):
    token.faucet(7, sender=tester.k0)
    token.transfer(controlled.address, 7, sender=tester.k0)
    assert token.balanceOf(tester.a0) == 0
    assert token.balanceOf(controlled.address) == 7
    controlled.deposit(value=11, sender=tester.k0)
    assert chain.head_state.get_balance(controlled.address) == 11
    startBalance = chain.head_state.get_balance(tester.a0)

    with raises(TransactionFailed):
        controlled.suicideFunds(tester.a1, [], sender=tester.k1)
    with raises(TransactionFailed):
        controlled.suicideFunds(tester.a1, [tester.a1], sender=tester.k0)
    assert controlled.suicideFunds(tester.a0, [token.address], sender=tester.k0)

    assert chain.head_state.get_balance(controlled.address) == 0
    assert chain.head_state.get_balance(tester.a0) == startBalance + 11
    assert token.balanceOf(controlled.address) == 0
    assert token.balanceOf(tester.a0) == 7

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
