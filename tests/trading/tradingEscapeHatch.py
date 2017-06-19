#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

def test_EscapeHatch(contracts):
    t = contracts._ContractLoader__tester
    def test_escapeHatch():
        fxpEtherDepositValue = utils.fix(100)
        assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
        assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 1 should succeed"
        contracts._ContractLoader__state.mine(1)
        orderType = 2                   # ask
        fxpAmount = utils.fix(1)
        fxpPrice = utils.fix("1.6")
        outcomeID = 2
        tradeGroupID = 42
        eventID = utils.createBinaryEvent(contracts)
        marketID = utils.createMarket(contracts, eventID)
        assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
        assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
        makerInitialCash = contracts.cash.balanceOf(t.a1)
        takerInitialCash = contracts.cash.balanceOf(t.a2)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        with iocapture.capture() as captured:
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            logged = captured.stdout
        assert(orderID != 0), "Order ID should be non-zero"
        contracts._ContractLoader__state.mine(1)
        fxpAmountTakerWants = fxpAmount
        t.gas_price = 5
        try:
            raise Exception(contracts.takeOrder.publicTakeOrder(orderID, orderType, marketID, outcomeID, fxpAmountTakerWants, sender=t.k2))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails, tx.gasprice check in orders isn't working"
        t.gas_price = 1
        with iocapture.capture() as captured:
            fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, orderType, marketID, outcomeID, fxpAmountTakerWants, sender=t.k2)
            logged = captured.stdout
        sharesOwnedByA1 = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
        sharesOwnedByA2 = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
        balanceOfA1 = contracts.cash.balanceOf(t.a1)
        balanceOfA2 = contracts.cash.balanceOf(t.a2)
        balanceOfMarket = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        try:
            raise Exception(contracts.tradingEscapeHatch.claimSharesInUpdate(marketID))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed))
        contracts.controller.emergencyStop()
        assert(contracts.tradingEscapeHatch.claimSharesInUpdate(marketID, sender = t.k1))
        assert(contracts.tradingEscapeHatch.claimSharesInUpdate(marketID, sender = t.k2))
        assert(contracts.cash.balanceOf(t.a2) > balanceOfA2 and contracts.cash.balanceOf(t.a1) > balanceOfA1)
        assert(balanceOfMarket > contracts.cash.balanceOf(contracts.info.getWallet(marketID)))
        contracts.controller.release()

    test_escapeHatch()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_EscapeHatch(contracts)
