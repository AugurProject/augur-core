#!/usr/bin/env python

from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises

tester.GASPRICE = 0

def test_init(contractsFixture):
    cash = contractsFixture.cash

    assert cash.getName() == 0x4361736800000000000000000000000000000000000000000000000000000000L, "currency name"
    assert cash.getDecimals() == 18, "number of decimals"
    assert cash.getSymbol() == 0x4341534800000000000000000000000000000000000000000000000000000000L, "currency symbol"

def test_publicDepositEther(contractsFixture):
    cash = contractsFixture.cash
    startingUserEthBalance = contractsFixture.chain.head_state.get_balance(tester.a0)
    startingUserCashBalance = cash.balanceOf(tester.a0)
    startingCashEthBalance = contractsFixture.chain.head_state.get_balance(hex(cash.address)[2:-1])
    startingCashSupply = cash.totalSupply()

    assert cash.publicDepositEther(value = 7, sender = tester.k0)

    assert startingUserEthBalance - 7 == contractsFixture.chain.head_state.get_balance(tester.a0)
    assert startingUserCashBalance + 7 == cash.balanceOf(tester.a0)
    assert startingCashEthBalance + 7 == contractsFixture.chain.head_state.get_balance(hex(cash.address)[2:-1])
    assert startingCashSupply + 7 == cash.totalSupply()

def test_publicDepositEther_failures(contractsFixture):
    cash = contractsFixture.cash

    with raises(TransactionFailed):
        cash.depositEther(tester.a0, value = 7)
    with raises(TransactionFailed):
        cash.publicDepositEther(value = 0)

def test_publicWithdrawEther(contractsFixture):
    cash = contractsFixture.cash
    cash.publicDepositEther(value = 7)
    startingUserEthBalance = contractsFixture.chain.head_state.get_balance(tester.a0)
    startingUserCashBalance = cash.balanceOf(tester.a0)
    startingCashEthBalance = contractsFixture.chain.head_state.get_balance(hex(cash.address)[2:-1])
    startingCashSupply = cash.totalSupply()

    assert cash.publicWithdrawEther(tester.a0, 5)
    contractsFixture.chain.head_state.timestamp += long(timedelta(days=3).total_seconds())
    assert cash.publicWithdrawEther(tester.a0, 5)

    assert startingUserEthBalance + 5 == contractsFixture.chain.head_state.get_balance(tester.a0)
    assert startingUserCashBalance - 5 == cash.balanceOf(tester.a0)
    assert startingCashEthBalance - 5 == contractsFixture.chain.head_state.get_balance(hex(cash.address)[2:-1])
    assert startingCashSupply - 5 == cash.totalSupply()

def test_publicWithdrawEther_failures(contractsFixture):
    cash = contractsFixture.cash
    cash.publicDepositEther(value = 7)

    with raises(TransactionFailed):
        cash.withdrawEther(tester.a0, tester.a0, 5)
    with raises(TransactionFailed):
        cash.publicWithdrawEther(tester.a0, 0)
    with raises(TransactionFailed):
        cash.publicWithdrawEther(tester.a0, 8)
    with raises(TransactionFailed):
        cash.publicWithdrawEther(tester.a0, 5, sender = tester.k1)
    # NOTE: this one must be last because it mutates chain
    cash.publicWithdrawEther(tester.a0, 5)
    with raises(TransactionFailed):
        cash.publicWithdrawEther(tester.a0, 5)

def test_transfer(contractsFixture):
    cash = contractsFixture.cash
    cash.publicDepositEther(value = 7, sender = tester.k0)
    startingBalance0 = cash.balanceOf(tester.a0)
    startingBalance1 = cash.balanceOf(tester.a1)
    startingSupply = cash.totalSupply()
    logs = []
    contractsFixture.chain.head_state.log_listeners.append(lambda x: logs.append(cash.translator.listen(x)))

    assert cash.transfer(tester.a1, 5, sender = tester.k0)
    assert cash.transfer(tester.a1, 2, sender = tester.k0)

    assert startingBalance0 - 7 == cash.balanceOf(tester.a0)
    assert startingBalance1 + 7 == cash.balanceOf(tester.a1)
    assert startingSupply == cash.totalSupply()
    assert logs == [
        { "_event_type": "Transfer", "from": '0x'+tester.a0.encode("hex"), "to": '0x'+tester.a1.encode("hex"), "value": 5L },
        { "_event_type": "Transfer", "from": '0x'+tester.a0.encode("hex"), "to": '0x'+tester.a1.encode("hex"), "value": 2L },
    ]

def test_transfer_failures(contractsFixture):
    cash = contractsFixture.cash
    cash.publicDepositEther(value = 7, sender = tester.k0)

    with raises(TransactionFailed):
        cash.transfer(tester.a1, 0, sender = tester.k0)
    with raises(TransactionFailed):
        cash.transfer(tester.a1, 8, sender = tester.k0)
    with raises(TransactionFailed):
        cash.transfer(tester.a1, 5, sender = tester.k2)
    with raises(TransactionFailed):
        cash.transfer(tester.a0, 5, sender = tester.k0)

def test_approve(contractsFixture):
    cash = contractsFixture.cash
    cash.publicDepositEther(value = 7, sender = tester.k0)
    logs = []
    contractsFixture.chain.head_state.log_listeners.append(lambda x: logs.append(cash.translator.listen(x)))

    assert cash.approve(tester.a1, 10, sender = tester.k0)

    assert 10 == cash.allowance(tester.a0, tester.a1)
    assert logs == [ { "_event_type": "Approval", "owner": '0x'+tester.a0.encode("hex"), "spender": '0x'+tester.a1.encode("hex"), "value": 10 } ]

def test_approve_failures(contractsFixture):
    cash = contractsFixture.cash
    cash.publicDepositEther(value = 7, sender = tester.k0)

    with raises(TransactionFailed):
        cash.approve(tester.a1, -1)
    with raises(TransactionFailed):
        cash.approve(tester.a1, 2**255-1)
    with raises(TransactionFailed):
        cash.approve(tester.a0, 10)

def test_transferFrom(contractsFixture):
    cash = contractsFixture.cash
    cash.publicDepositEther(value = 7, sender = tester.k0)
    cash.approve(tester.a1, 10, sender = tester.k0)
    startingBalance0 = cash.balanceOf(tester.a0)
    startingBalance1 = cash.balanceOf(tester.a1)
    startingSupply = cash.totalSupply()
    logs = []
    contractsFixture.chain.head_state.log_listeners.append(lambda x: logs.append(cash.translator.listen(x)))

    assert cash.transferFrom(tester.a0, tester.a2, 5, sender = tester.k1)

    assert startingBalance0 - 5 == cash.balanceOf(tester.a0)
    assert startingBalance1 + 5 == cash.balanceOf(tester.a2)
    assert startingSupply == cash.totalSupply()
    assert logs == [ { "_event_type": "Transfer", "from": '0x'+tester.a0.encode("hex"), "to": '0x'+tester.a2.encode("hex"), "value": 5 } ]

def test_transferFrom_failures(contractsFixture):
    cash = contractsFixture.cash
    cash.publicDepositEther(value = 7, sender = tester.k0)
    cash.approve(tester.a1, 10, sender = tester.k0)

    with raises(TransactionFailed):
        cash.transferFrom(tester.a0, tester.a1, 0, sender = tester.k1)
    with raises(TransactionFailed):
        cash.transferFrom(tester.a0, tester.a1, 8, sender = tester.k1)
    with raises(TransactionFailed):
        cash.transferFrom(tester.a0, tester.a1, 5, sender = tester.k2)
    with raises(TransactionFailed):
        cash.transferFrom(tester.a0, tester.a0, 5, sender = tester.k1)

def test_setController_failure(contractsFixture):
    cash = contractsFixture.cash

    with raises(TransactionFailed):
        cash.setController(tester.a1, sender = tester.k1)

def test_suicideFunds_failure(contractsFixture):
    cash = contractsFixture.cash

    with raises(TransactionFailed):
        cash.suicideFunds(tester.a1, sender = tester.k1)
