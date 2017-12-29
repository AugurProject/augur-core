#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture as pytest_fixture, raises

def test_convertToAndFromCash(cash, cashWrapperHelper, controller, augur, chain):
    originalETHBalance = chain.head_state.get_balance(tester.a1)

    # We'll manually provide the tester with Cash since no normal code path will allow them to keep a non-zero balance
    assert cash.depositEther(sender=tester.k1, value=40)
    assert cash.balanceOf(tester.a1) == 40
    assert cash.approve(augur.address, 2**256-1, sender=tester.k1)

    # Initially we can't call the function since this helper contract isn't whitelisted
    with raises(TransactionFailed):
        cashWrapperHelper.toEthFunction(sender=tester.k1)

    # Whitelist the contract
    controller.addToWhitelist(cashWrapperHelper.address)

    # Now call the function which converts existing Cash balance to ETH and withdraws it at the end of the call
    cashWrapperHelper.toEthFunction(sender=tester.k1)
    assert cash.balanceOf(tester.a1) == 0
    assert chain.head_state.get_balance(tester.a1) == originalETHBalance

@pytest_fixture(scope='session')
def localSnapshot(fixture, controllerSnapshot):
    fixture.resetToSnapshot(controllerSnapshot)
    fixture.uploadAugur()
    fixture.uploadAndAddToController('../source/contracts/trading/Cash.sol')
    fixture.contracts['Cash'].setController(fixture.contracts['Controller'].address)
    fixture.uploadAndAddToController('solidity_test_helpers/CashWrapperHelper.sol')
    fixture.contracts['CashWrapperHelper'].setController(fixture.contracts['Controller'].address)
    return fixture.createSnapshot()

@pytest_fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@pytest_fixture
def cash(localFixture):
    return localFixture.contracts['Cash']

@pytest_fixture
def cashWrapperHelper(localFixture):
    return localFixture.contracts['CashWrapperHelper']

@pytest_fixture
def controller(localFixture):
    return localFixture.contracts['Controller']

@pytest_fixture
def augur(localFixture):
    return localFixture.contracts['Augur']

@pytest_fixture
def chain(localFixture):
    return localFixture.chain
