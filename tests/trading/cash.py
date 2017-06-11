#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

def test_Cash(contracts):
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    initialEtherBalance2 = contracts._ContractLoader__state.block.get_balance(t.a2)
    def test_init():
        assert(utils.hex2str(contracts.cash.getName()) == "4361736800000000000000000000000000000000000000000000000000000000"), "currency name"
        assert(contracts.cash.getDecimals() == 18), "number of decimals"
        assert(utils.hex2str(contracts.cash.getSymbol()) == "4341534800000000000000000000000000000000000000000000000000000000"), "currency symbol"
    def test_publicDepositEther():
        contracts._ContractLoader__state.mine(1)
        initialEtherBalance = contracts._ContractLoader__state.block.get_balance(t.a1)
        initialCashSupply = contracts.cash.totalSupply()
        initialCashBalance = contracts.cash.balanceOf(t.a1)
        depositEtherAmount = 100
        assert(contracts.cash.publicDepositEther(value=depositEtherAmount, sender=t.k1) == 1), "deposit ether"
        assert(contracts.cash.balanceOf(t.a1) == initialCashBalance + depositEtherAmount), "account 1 cash balance should be equal to initial cash balance plus amount of ether deposited"
        assert(contracts.cash.totalSupply() == initialCashSupply + depositEtherAmount), "total cash supply should be equal to initial cash supply plus amount of ether deposited"
        assert(contracts._ContractLoader__state.block.get_balance(t.a1) <= initialEtherBalance - depositEtherAmount), "account 1 ether balance should be at most the initial ether balance minus the amount of ether deposited"
    def test_publicWithdrawEther():
        contracts._ContractLoader__state.mine(1)
        initialCashBalance = contracts.cash.balanceOf(t.a1)
        initialTotalSupply = contracts.cash.totalSupply()
        assert(contracts.cash.getInitiated(sender=t.k1) == 0), "withdraw not initiated"
        try:
            raise Exception(contracts.cash.publicWithdrawEther(t.a1, initialCashBalance + 1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdraw should throw due to insufficient funds"
        assert(contracts.cash.publicWithdrawEther(t.a2, 30, sender=t.k1)), "initiate withdrawal"
        assert(contracts.cash.getInitiated(sender=t.k1) == contracts._ContractLoader__state.block.timestamp), "withdraw initiated"
        try:
            raise Exception(contracts.cash.publicWithdrawEther(t.a2, 30, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdraw should throw (3 days haven't passed)"
        contracts._ContractLoader__state.block.timestamp += 259199
        try:
            raise Exception(contracts.cash.publicWithdrawEther(t.a2, 30, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdraw should throw (3 days still haven't passed)"
        contracts._ContractLoader__state.block.timestamp += 1
        assert(contracts.cash.publicWithdrawEther(t.a2, 30, sender=t.k1)), "withdraw should succeed"
        assert(contracts.cash.balanceOf(t.a1) == initialCashBalance - 30), "decrease sender's balance by 30"
        assert(contracts.cash.balanceOf(t.a2) == 0), "receiver's cash balance still equals 0"
        assert(contracts._ContractLoader__state.block.get_balance(t.a2) - initialEtherBalance2 == 30), "receiver's ether balance increased by 30"
        assert(contracts.cash.totalSupply() == initialTotalSupply - 30), "total supply decreased by 30"
        try:
            raise Exception(contracts.cash.publicWithdrawEther(t.a2, -10, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative withdraw should throw"
        assert(contracts.cash.getInitiated(sender=t.k1) == 0), "withdraw no longer initiated"
    def test_transfer():
        contracts._ContractLoader__state.mine(1)
        initialCashBalance1 = contracts.cash.balanceOf(t.a1)
        initialCashBalance2 = contracts.cash.balanceOf(t.a2)
        initialTotalSupply = contracts.cash.totalSupply()
        with iocapture.capture() as captured:
            retval = contracts.cash.transfer(t.a2, 5, sender=t.k1)
            logged = utils.parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transfer 5 cash to a2"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == 5)
        assert(contracts.cash.balanceOf(t.a1) == initialCashBalance1 - 5), "balance of a1 decreased by 5"
        assert(contracts.cash.balanceOf(t.a2) == initialCashBalance2 + 5), "balance of a2 increased by 5"
        assert(contracts.cash.totalSupply() == initialTotalSupply), "totalSupply unchanged"
        try:
            raise Exception(contracts.cash.transfer(t.a2, contracts.cash.balanceOf(t.a1) + 1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should throw if insufficient funds"
        try:
            raise Exception(contracts.cash.transfer(t.a2, -5, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative transfer should throw"
        with iocapture.capture() as captured:
            retval = contracts.cash.transfer(t.a2, 0, sender=t.k1)
            logged = utils.parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transfer should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == 0)
        assert(contracts.cash.balanceOf(t.a1) == initialCashBalance1 - 5), "balance of a1 unchanged"
        assert(contracts.cash.balanceOf(t.a2) == initialCashBalance2 + 5), "balance of a2 unchanged"
        assert(contracts.cash.totalSupply() == initialTotalSupply), "totalSupply unchanged"
    def test_transferFrom():
        try:
            raise Exception(contracts.cash.transferFrom(t.a1, t.a2, 7, sender=t.k2))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transferFrom should throw, msg.sender is not approved"
    def test_approve():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.allowance(t.a1, t.a2) == 0), "initial allowance is 0"
        with iocapture.capture() as captured:
            retval = contracts.cash.approve(t.a2, 10, sender=t.k1)
            logged = utils.parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "approve a2 to spend 10 cash from a1"
        assert(logged["_event_type"] == "Approval")
        assert(long(logged["owner"], 16) == address1)
        assert(long(logged["spender"], 16) == address2)
        assert(logged["value"] == 10)
        assert(contracts.cash.allowance(t.a1, t.a2) == 10), "allowance is 10 after approval"
        with iocapture.capture() as captured:
            retval = contracts.cash.transferFrom(t.a1, t.a2, 7, sender=t.k2)
            logged = utils.parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transferFrom should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == 7)
    def test_setController():
        try:
            raise Exception(contracts.wallet.setController(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "setController should fail when attempted by non-controller address"
    def test_suicideFunds():
        try:
            raise Exception(contracts.cash.suicideFunds(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "suicideFunds should fail when attempted by non-controller address"
    def test_exceptions():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = utils.fix(10)
        fxpWithdrawAmount = utils.fix(2)
        try:
            raise Exception(contracts.cash.depositEther(t.a1, value=fxpAmount, sender=t.k1), "deposit ether")
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "depositEther should fail if called from a non-whitelisted account (account 1)"
        assert(contracts.cash.publicDepositEther(value=fxpAmount, sender=t.k1) == 1), "publicDepositEther should succeed"
        try:
            raise Exception(contracts.cash.withdrawEther(t.a1, t.a1, fxpWithdrawAmount, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdrawEther should fail if called from a non-whitelisted account (account 1)"
    test_publicDepositEther()
    test_publicWithdrawEther()
    test_transfer()
    test_transferFrom()
    test_approve()
    test_setController()
    test_suicideFunds()
    test_exceptions()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_Cash(contracts)
