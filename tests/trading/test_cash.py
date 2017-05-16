#!/usr/bin/env python

from ContractsFixture import ContractsFixture
from datetime import timedelta
from ethereum import tester
from ethereum.tester import TransactionFailed
from iocapture import capture
from pytest import raises
from utils import parseCapturedLogs

def test_init():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')

    cash.initialize(fixture.controller.address)

    assert cash.getName() == 0x4361736800000000000000000000000000000000000000000000000000000000L, "currency name"
    assert cash.getDecimals() == 18, "number of decimals"
    assert cash.getSymbol() == 0x4341534800000000000000000000000000000000000000000000000000000000L, "currency symbol"

def test_publicDepositEther():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)
    startingUserEthBalance = fixture.state.block.get_balance(tester.a0)
    startingUserCashBalance = cash.balanceOf(tester.a0)
    startingCashEthBalance = fixture.state.block.get_balance(hex(cash.address)[2:-1])
    startingCashSupply = cash.totalSupply()

    assert cash.publicDepositEther(value = 7, sender = tester.k0)

    assert startingUserEthBalance - 7 == fixture.state.block.get_balance(tester.a0)
    assert startingUserCashBalance + 7 == cash.balanceOf(tester.a0)
    assert startingCashEthBalance + 7 == fixture.state.block.get_balance(hex(cash.address)[2:-1])
    assert startingCashSupply + 7 == cash.totalSupply()

def test_publicDepositEther_failures():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)

    with raises(TransactionFailed):
        cash.depositEther(tester.a0, value = 7)
    with raises(TransactionFailed):
        cash.publicDepositEther(value = 0)

def test_publicWithdrawEther():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)
    cash.publicDepositEther(value = 7)
    startingUserEthBalance = fixture.state.block.get_balance(tester.a0)
    startingUserCashBalance = cash.balanceOf(tester.a0)
    startingCashEthBalance = fixture.state.block.get_balance(hex(cash.address)[2:-1])
    startingCashSupply = cash.totalSupply()

    assert cash.publicWithdrawEther(tester.a0, 5)
    fixture.state.block.timestamp += long(timedelta(days=3).total_seconds())
    assert cash.publicWithdrawEther(tester.a0, 5)

    assert startingUserEthBalance + 5 == fixture.state.block.get_balance(tester.a0)
    assert startingUserCashBalance - 5 == cash.balanceOf(tester.a0)
    assert startingCashEthBalance - 5 == fixture.state.block.get_balance(hex(cash.address)[2:-1])
    assert startingCashSupply - 5 == cash.totalSupply()

def test_publicWithdrawEther_failures():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)
    cash.publicDepositEther(value = 7)

    with raises(TransactionFailed):
        cash.withdrawEther(tester.a0, tester.a0, 5)
    with raises(TransactionFailed):
        cash.publicWithdrawEther(tester.a0, 0)
    with raises(TransactionFailed):
        cash.publicWithdrawEther(tester.a0, 8)
    with raises(TransactionFailed):
        cash.publicWithdrawEther(tester.a0, 5, sender = tester.k1)
    # NOTE: this one must be last because it mutates state
    cash.publicWithdrawEther(tester.a0, 5)
    with raises(TransactionFailed):
        cash.publicWithdrawEther(tester.a0, 5)

def test_transfer():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)
    cash.publicDepositEther(value = 7, sender = tester.k0)
    startingBalance0 = cash.balanceOf(tester.a0)
    startingBalance1 = cash.balanceOf(tester.a1)
    startingSupply = cash.totalSupply()

    assert cash.transfer(tester.a1, 5, sender = tester.k0)
    with capture() as captured:
        assert cash.transfer(tester.a1, 2, sender = tester.k0)
        logs = parseCapturedLogs(captured.stdout)[-1]

    assert startingBalance0 - 7 == cash.balanceOf(tester.a0)
    assert startingBalance1 + 7 == cash.balanceOf(tester.a1)
    assert startingSupply == cash.totalSupply()
    assert logs["_event_type"] == "Transfer"
    assert logs["from"] == tester.a0.encode("hex")
    assert logs["to"] == tester.a1.encode("hex")
    assert logs["value"] == 2

def test_transfer_failures():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)
    cash.publicDepositEther(value = 7, sender = tester.k0)

    with raises(TransactionFailed):
        cash.transfer(tester.a1, 0, sender = tester.k0)
    with raises(TransactionFailed):
        cash.transfer(tester.a1, 8, sender = tester.k0)
    with raises(TransactionFailed):
        cash.transfer(tester.a1, 5, sender = tester.k2)
    with raises(TransactionFailed):
        cash.transfer(tester.a0, 5, sender = tester.k0)

def test_approve():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)
    cash.publicDepositEther(value = 7, sender = tester.k0)

    with capture() as capturedLogs:
        assert cash.approve(tester.a1, 10, sender = tester.k0)
        logs = parseCapturedLogs(capturedLogs.stdout)[-1]

    assert 10 == cash.allowance(tester.a0, tester.a1)
    assert logs["_event_type"] == "Approval"
    assert logs["owner"] == tester.a0.encode("hex")
    assert logs["spender"] == tester.a1.encode("hex")
    assert logs["value"] == 10

def test_approve_failures():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)
    cash.publicDepositEther(value = 7, sender = tester.k0)

    with raises(TransactionFailed):
        cash.approve(tester.a1, -1)
    with raises(TransactionFailed):
        cash.approve(tester.a1, 2**255-1)
    with raises(TransactionFailed):
        cash.approve(tester.a0, 10)

def test_transferFrom():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)
    cash.publicDepositEther(value = 7, sender = tester.k0)
    cash.approve(tester.a1, 10, sender = tester.k0)
    startingBalance0 = cash.balanceOf(tester.a0)
    startingBalance1 = cash.balanceOf(tester.a1)
    startingSupply = cash.totalSupply()

    with capture() as captured:
        assert cash.transferFrom(tester.a0, tester.a2, 5, sender = tester.k1)
        logs = parseCapturedLogs(captured.stdout)[-1]

    assert startingBalance0 - 5 == cash.balanceOf(tester.a0)
    assert startingBalance1 + 5 == cash.balanceOf(tester.a2)
    assert startingSupply == cash.totalSupply()
    assert logs["_event_type"] == "Transfer"
    assert logs["from"] == tester.a0.encode("hex")
    assert logs["to"] == tester.a2.encode("hex")
    assert logs["value"] == 5

def test_transferFrom_failures():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)
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

def test_setController_failure():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)

    with raises(TransactionFailed):
        cash.setController(tester.a1, sender = tester.k1)

def test_suicideFunds_failure():
    fixture = ContractsFixture()
    cash = fixture.uploadAndAddToController('../src/trading/cash.se')
    cash.initialize(fixture.controller.address)

    with raises(TransactionFailed):
        cash.suicideFunds(tester.a1, sender = tester.k1)
