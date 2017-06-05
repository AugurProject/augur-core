#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

shareTokenContractTranslator = ethereum.abi.ContractTranslator('[{"constant": false, "type": "function", "name": "allowance(address,address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "address", "name": "spender"}]}, {"constant": false, "type": "function", "name": "approve(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "balanceOf(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "address"}]}, {"constant": false, "type": "function", "name": "changeTokens(int256,int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "trader"}, {"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "createShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "destroyShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "getDecimals()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getName()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getSymbol()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "modifySupply(int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "setController(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "newController"}]}, {"constant": false, "type": "function", "name": "suicideFunds(address)", "outputs": [], "inputs": [{"type": "address", "name": "to"}]}, {"constant": false, "type": "function", "name": "totalSupply()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "transfer(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "transferFrom(address,address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "from"}, {"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval(address,address,uint256)"}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer(address,address,uint256)"}, {"inputs": [{"indexed": false, "type": "int256", "name": "from"}, {"indexed": false, "type": "int256", "name": "to"}, {"indexed": false, "type": "int256", "name": "value"}, {"indexed": false, "type": "int256", "name": "senderBalance"}, {"indexed": false, "type": "int256", "name": "sender"}, {"indexed": false, "type": "int256", "name": "spenderMaxValue"}], "type": "event", "name": "echo(int256,int256,int256,int256,int256,int256)"}]')

def test_ShareTokens(contracts):
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    def test_init():
        assert(utils.hex2str(contracts.shareTokens.getName()) == '5368617265730000000000000000000000000000000000000000000000000000'), "currency name"
        assert(contracts.shareTokens.getDecimals() == 18), "number of decimals"
        assert(utils.hex2str(contracts.shareTokens.getSymbol()) == '5348415245000000000000000000000000000000000000000000000000000000'), "currency symbol"
    def test_createShares():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = utils.fix(10)
        initialTotalSupply = contracts.shareTokens.totalSupply()
        initialBalance = contracts.shareTokens.balanceOf(t.a1)
        assert(contracts.shareTokens.createShares(t.a1, fxpAmount, sender=t.k0) == 1), "Create share tokens for address 1"
        assert(contracts.shareTokens.totalSupply() - initialTotalSupply == fxpAmount), "Total supply increase should equal the number of tokens created"
        assert(contracts.shareTokens.balanceOf(t.a1) - initialBalance == fxpAmount), "Address 1 token balance increase should equal the number of tokens created"
    def test_destroyShares():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = utils.fix(10)
        initialTotalSupply = contracts.shareTokens.totalSupply()
        initialBalance = contracts.shareTokens.balanceOf(t.a1)
        assert(contracts.shareTokens.destroyShares(t.a1, fxpAmount, sender=t.k0) == 1), "Destroy share tokens owned by address 1"
        assert(initialTotalSupply - contracts.shareTokens.totalSupply() == fxpAmount), "Total supply decrease should equal the number of tokens destroyed"
        assert(initialBalance - contracts.shareTokens.balanceOf(t.a1) == fxpAmount), "Address 1 token balance decrease should equal the number of tokens destroyed"
    def test_transfer():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = utils.fix(10)
        fxpTransferAmount = utils.fix(2)
        assert(contracts.shareTokens.createShares(t.a1, fxpAmount, sender=t.k0) == 1), "Create share tokens for address 1"
        initialTotalSupply = contracts.shareTokens.totalSupply()
        initialBalance1 = contracts.shareTokens.balanceOf(t.a1)
        initialBalance2 = contracts.shareTokens.balanceOf(t.a2)
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.transfer(t.a2, fxpTransferAmount, sender=t.k1)
            logged = captured.stdout
        logged = utils.parseCapturedLogs(logged)[-1]
        assert(retval == 1), "transfer should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == fxpTransferAmount)
        afterTransferBalance1 = contracts.shareTokens.balanceOf(t.a1)
        afterTransferBalance2 = contracts.shareTokens.balanceOf(t.a2)
        assert(initialBalance1 - afterTransferBalance1 == fxpTransferAmount), "Decrease in address 1's balance should equal amount transferred"
        assert(afterTransferBalance2 - initialBalance2 == fxpTransferAmount), "Increase in address 2's balance should equal amount transferred"
        assert(contracts.shareTokens.totalSupply() == initialTotalSupply), "Total supply should be unchanged"
        try:
            raise Exception(contracts.shareTokens.transfer(t.a2, utils.fix(70), sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should throw if insufficient funds"
        try:
            raise Exception(contracts.shareTokens.transfer(t.a2, -5, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative transfer should throw"
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.transfer(t.a2, 0, sender=t.k1)
            logged = captured.stdout
        logged = utils.parseCapturedLogs(logged)[-1]
        assert(retval == 1), "transfer with 0 value should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == 0)
        assert(contracts.shareTokens.balanceOf(t.a1) == afterTransferBalance1), "Balance of a1 should be unchanged"
        assert(contracts.shareTokens.balanceOf(t.a2) == afterTransferBalance2), "Balance of a2 should be unchanged"
        assert(contracts.shareTokens.totalSupply() == initialTotalSupply), "Total supply should be unchanged"
    def test_transferFrom():
        try:
            raise Exception(contracts.shareTokens.transferFrom(t.a1, t.a2, 7, sender=t.k2))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transferFrom should throw, msg.sender is not approved"
    def test_approve():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.shareTokens.allowance(t.a1, t.a2) == 0), "initial allowance is 0"
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.approve(t.a2, 10, sender=t.k1)
            logged = utils.parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "approve a2 to spend 10 cash from a1"
        assert(logged["_event_type"] == "Approval")
        assert(long(logged["owner"], 16) == address1)
        assert(long(logged["spender"], 16) == address2)
        assert(logged["value"] == 10)
        assert(contracts.shareTokens.allowance(t.a1, t.a2) == 10), "allowance is 10 after approval"
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.transferFrom(t.a1, t.a2, 7, sender=t.k2)
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
            raise Exception(contracts.shareTokens.suicideFunds(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "suicideFunds should fail when attempted by non-controller address"
    def test_exceptions():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = utils.fix(10)
        fxpTransferAmount = utils.fix(2)
        assert(contracts.shareTokens.createShares(t.a1, fxpAmount, sender=t.k0) == 1), "Create share tokens for address 1"
        try:
            raise Exception(contracts.shareTokens.createShares(t.a1, fxpTransferAmount, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "createShares should fail if called from a non-whitelisted account (account 1)"
        try:
            raise Exception(contracts.shareTokens.destroyShares(t.a1, fxpTransferAmount, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "destroyShares should fail if called from a non-whitelisted account (account 1)"
    test_init()
    test_createShares()
    test_destroyShares()
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
    test_ShareTokens(contracts)
