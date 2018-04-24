#!/usr/bin/env python

from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import stringToBytes

tester.GASPRICE = 0

def test_init(cash):
    assert cash.name() == 'Cash'
    assert cash.decimals() == 18
    assert cash.symbol() == 'CASH'

    assert cash.getTypeName() == stringToBytes('Cash')

def test_depositEther(contractsFixture, cash):
    startingUserEthBalance = contractsFixture.chain.head_state.get_balance(tester.a0)
    startingUserCashBalance = cash.balanceOf(tester.a0)
    startingCashEthBalance = contractsFixture.chain.head_state.get_balance(cash.address)
    startingCashSupply = cash.totalSupply()

    assert cash.depositEther(value = 7, sender = tester.k0)

    assert startingUserEthBalance - 7 == contractsFixture.chain.head_state.get_balance(tester.a0)
    assert startingUserCashBalance + 7 == cash.balanceOf(tester.a0)
    assert startingCashEthBalance + 7 == contractsFixture.chain.head_state.get_balance(cash.address)
    assert startingCashSupply + 7 == cash.totalSupply()

def test_withdrawEther(contractsFixture, cash):
    cash.depositEther(value = 7)
    startingUserEthBalance = contractsFixture.chain.head_state.get_balance(tester.a0)
    startingUserCashBalance = cash.balanceOf(tester.a0)
    startingCashEthBalance = contractsFixture.chain.head_state.get_balance(cash.address)
    startingCashSupply = cash.totalSupply()

    assert cash.withdrawEther(5)

    assert startingUserEthBalance + 5 == contractsFixture.chain.head_state.get_balance(tester.a0)
    assert startingUserCashBalance - 5 == cash.balanceOf(tester.a0)
    assert startingCashEthBalance - 5 == contractsFixture.chain.head_state.get_balance(cash.address)
    assert startingCashSupply - 5 == cash.totalSupply()

def test_withdrawEther_failures(contractsFixture, cash):
    cash.depositEther(value = 7)

    with raises(TransactionFailed):
        cash.withdrawEther(0)
    with raises(TransactionFailed):
        cash.withdrawEther(8)
    with raises(TransactionFailed):
        cash.withdrawEther(5, sender = tester.k1)
    # NOTE: this one must be last because it mutates chain
    cash.withdrawEther(5)
    with raises(TransactionFailed):
        cash.withdrawEther(5)

def test_transfer(contractsFixture, cash):
    cash.depositEther(value = 7, sender = tester.k0)
    startingBalance0 = cash.balanceOf(tester.a0)
    startingBalance1 = cash.balanceOf(tester.a1)
    startingSupply = cash.totalSupply()

    assert cash.transfer(tester.a0, 5, sender = tester.k0)
    assert cash.transfer(tester.a1, 5, sender = tester.k0)
    assert cash.transfer(tester.a1, 2, sender = tester.k0)
    assert cash.transfer(tester.a1, 0, sender = tester.k0)

    assert startingBalance0 - 7 == cash.balanceOf(tester.a0)
    assert startingBalance1 + 7 == cash.balanceOf(tester.a1)
    assert startingSupply == cash.totalSupply()

def test_transfer_failures(contractsFixture, cash):
    cash.depositEther(value = 7, sender = tester.k0)

    with raises(TransactionFailed):
        cash.transfer(tester.a1, 8, sender = tester.k0)
    with raises(TransactionFailed):
        cash.transfer(tester.a1, 5, sender = tester.k2)

def test_approve(contractsFixture, cash):
    cash.depositEther(value = 7, sender = tester.k0)

    assert cash.approve(tester.a1, 10, sender = tester.k0)
    assert 10 == cash.allowance(tester.a0, tester.a1)
    assert cash.approve(tester.a1, 2**256 - 1, sender = tester.k0)
    assert 2**256 - 1 == cash.allowance(tester.a0, tester.a1)

def test_transferFrom(contractsFixture, cash):
    cash.depositEther(value = 7, sender = tester.k0)
    cash.approve(tester.a1, 10, sender = tester.k0)
    startingBalance0 = cash.balanceOf(tester.a0)
    startingBalance1 = cash.balanceOf(tester.a1)
    startingSupply = cash.totalSupply()

    assert cash.transferFrom(tester.a0, tester.a2, 5, sender = tester.k1)

    assert startingBalance0 - 5 == cash.balanceOf(tester.a0)
    assert startingBalance1 + 5 == cash.balanceOf(tester.a2)
    assert startingSupply == cash.totalSupply()

def test_transferFrom_failures(contractsFixture, cash):
    cash.depositEther(value = 7, sender = tester.k0)
    cash.approve(tester.a1, 10, sender = tester.k0)

    with raises(TransactionFailed):
        cash.transferFrom(tester.a0, tester.a1, 8, sender = tester.k1)
    with raises(TransactionFailed):
        cash.transferFrom(tester.a0, tester.a1, 5, sender = tester.k2)

def test_setController_failure(contractsFixture, cash):
    with raises(TransactionFailed):
        cash.setController(tester.a1, sender = tester.k1)

def test_suicideFunds_failure(contractsFixture, cash):
    with raises(TransactionFailed):
        cash.suicideFunds(tester.a1, [], sender = tester.k1)
