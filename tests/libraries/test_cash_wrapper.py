#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises

@fixture(scope='session')
def testerSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    sessionFixture.uploadAndAddToController('solidity_test_helpers/CashWrapperHelper.sol')
    cashWrapperHelper = sessionFixture.contracts['CashWrapperHelper']
    cashWrapperHelper.setController(sessionFixture.controller.address)
    return sessionFixture.chain.snapshot()

@fixture
def testerContractsFixture(sessionFixture, testerSnapshot):
    sessionFixture.chain.revert(testerSnapshot)
    return sessionFixture

def test_modifiers(testerContractsFixture):
    cash = testerContractsFixture.cash
    cashWrapperHelper = testerContractsFixture.contracts['CashWrapperHelper']
    
    originalETHBalance = cashWrapperHelper.getETHBalance(tester.a1)

    # Call a function which converts provided ETH to Cash through modifier use
    cashWrapperHelper.toCashFunction(value=42, sender=tester.k1)
    assert cash.balanceOf(tester.a1) == 42
    assert cashWrapperHelper.getETHBalance(tester.a1) == originalETHBalance - 42

    # Initially we can't call the function which converts existing Cash to ETH since this helper contract isn't whitelisted
    with raises(TransactionFailed):
        cashWrapperHelper.toETHFunction(sender=tester.k1)

    # Whitelist the contract
    testerContractsFixture.controller.addToWhitelist(cashWrapperHelper.address)

    # Now call the function which converts existing Cash balance to ETH and withdraws it
    cashWrapperHelper.toETHFunction(sender=tester.k1)
    assert cash.balanceOf(tester.a1) == 0
    assert cashWrapperHelper.getETHBalance(tester.a1) == originalETHBalance
