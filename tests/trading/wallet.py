#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

shareTokenContractTranslator = ethereum.abi.ContractTranslator('[{"constant": false, "type": "function", "name": "allowance(address,address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "address", "name": "spender"}]}, {"constant": false, "type": "function", "name": "approve(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "balanceOf(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "address"}]}, {"constant": false, "type": "function", "name": "changeTokens(int256,int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "trader"}, {"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "createShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "destroyShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "getDecimals()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getName()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getSymbol()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "modifySupply(int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "setController(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "newController"}]}, {"constant": false, "type": "function", "name": "suicideFunds(address)", "outputs": [], "inputs": [{"type": "address", "name": "to"}]}, {"constant": false, "type": "function", "name": "totalSupply()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "transfer(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "transferFrom(address,address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "from"}, {"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval(address,address,uint256)"}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer(address,address,uint256)"}, {"inputs": [{"indexed": false, "type": "int256", "name": "from"}, {"indexed": false, "type": "int256", "name": "to"}, {"indexed": false, "type": "int256", "name": "value"}, {"indexed": false, "type": "int256", "name": "senderBalance"}, {"indexed": false, "type": "int256", "name": "sender"}, {"indexed": false, "type": "int256", "name": "spenderMaxValue"}], "type": "event", "name": "echo(int256,int256,int256,int256,int256,int256)"}]')

def test_Wallet(contracts):
    t = contracts._ContractLoader__tester
    def test_initialize():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.wallet.initialize(contracts.cash.address, sender=t.k1) == 1), "Should initialize wallet with cash currency"
    def test_transfer():
        contracts._ContractLoader__state.mine(1)
        fxpValue = utils.fix(100)
        assert(contracts.wallet.initialize(contracts.cash.address, sender=t.k1) == 1), "Should initialize wallet with cash currency"
        contracts._ContractLoader__state.mine(1)
        initialBalanceWallet = contracts.cash.balanceOf(contracts.wallet.address)
        initialBalance2 = contracts.cash.balanceOf(t.a2)
        assert(contracts.cash.publicDepositEther(value=fxpValue, sender=t.k2) == 1), "Should deposit ether to account 2"
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.balanceOf(contracts.wallet.address) == initialBalanceWallet), "Wallet balance unchanged"
        assert(contracts.cash.balanceOf(t.a2) - initialBalance2 == fxpValue), "Account 2 balance increase equal to deposit"
        assert(contracts.cash.transfer(contracts.wallet.address, fxpValue, sender=t.k2) == 1), "Should transfer ether to wallet address"
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.balanceOf(contracts.wallet.address) - initialBalanceWallet == fxpValue), "Wallet balance increase equal to deposit"
        assert(contracts.cash.balanceOf(t.a2) == initialBalance2), "Account 2 balance unchanged"
        fxpTransferValue = contracts.cash.balanceOf(contracts.wallet.address)
        try:
            raise Exception(contracts.wallet.transfer(t.a2, fxpTransferValue, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should fail when attempted by non-whitelisted address"
        try:
            raise Exception(contracts.wallet.transfer(t.a2, 0, sender=t.k0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should fail if value is zero"
        try:
            raise Exception(contracts.wallet.transfer(t.a2, -1, sender=t.k0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "transfer should fail if value is negative"
        try:
            raise Exception(contracts.wallet.transfer(0, fxpTransferValue, sender=t.k0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should fail if receiver address is zero"
        assert(contracts.wallet.transfer(t.a1, fxpTransferValue, sender=t.k0) == 1), "transfer should succeed"
        contracts._ContractLoader__state.mine(1)
        try:
            raise Exception(contracts.wallet.transfer(t.a2, fxpTransferValue, sender=t.k0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should fail if insufficient balance"
    def test_setController():
        try:
            raise Exception(contracts.wallet.setController(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "setController should fail when attempted by non-controller address"
    def test_suicideFunds():
        try:
            raise Exception(contracts.wallet.suicideFunds(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "suicideFunds should fail when attempted by non-controller address"
    test_initialize()
    test_transfer()
    test_setController()
    test_suicideFunds()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_Wallet(contracts)
