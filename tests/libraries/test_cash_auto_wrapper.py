#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises

def test_convertToAndFromCash(testerContractsFixture):
    cash = testerContractsFixture.cash
    cashWrapperHelper = testerContractsFixture.contracts['CashWrapperHelper']

    originalETHBalance = testerContractsFixture.utils.getETHBalance(tester.a1)

    # We'll manually provide the tester with Cash since no normal code path will allow them to keep a non-zero balance
    assert cash.depositEther(sender=tester.k1, value=40)
    assert cash.balanceOf(tester.a1) == 40

    # Initially we can't call the function since this helper contract isn't whitelisted
    with raises(TransactionFailed):
        cashWrapperHelper.toETHFunction(sender=tester.k1)

    # Whitelist the contract
    testerContractsFixture.controller.addToWhitelist(cashWrapperHelper.address)

    # Now call the function which converts existing Cash balance to ETH and withdraws it at the end of the call
    cashWrapperHelper.toETHFunction(sender=tester.k1)
    assert cash.balanceOf(tester.a1) == 0
    assert testerContractsFixture.utils.getETHBalance(tester.a1) == originalETHBalance

@fixture(scope='session')
def testerSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    sessionFixture.uploadAndAddToController('solidity_test_helpers/CashWrapperHelper.sol')
    cashWrapperHelper = sessionFixture.contracts['CashWrapperHelper']
    cashWrapperHelper.setController(sessionFixture.controller.address)
    return sessionFixture.createSnapshot()

@fixture
def testerContractsFixture(sessionFixture, testerSnapshot):
    sessionFixture.resetToSnapshot(testerSnapshot)
    return sessionFixture
