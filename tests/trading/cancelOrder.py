#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

def test_CancelOrder(contracts):
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    def test_publicCancelOrder():
        def test_cancelBid():
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10000), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            assert(contracts.orders.getOrder(orderID, orderType, marketID, outcomeID) != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "Order should have non-zero elements"
            assert(contracts.cancelOrder.publicCancelOrder(orderID, orderType, marketID, outcomeID, sender=t.k1) == 1), "publicCancelOrder should succeed"
            assert(contracts.orders.getOrder(orderID, orderType, marketID, outcomeID) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "Canceled order elements should all be zero"
            assert(makerInitialCash == contracts.cash.balanceOf(t.a1)), "Maker's cash should be the same as before the order was placed"
            assert(marketInitialCash == contracts.cash.balanceOf(contracts.info.getWallet(marketID))), "Market's cash balance should be the same as before the order was placed"
            assert(makerInitialShares == contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)), "Maker's shares should be unchanged"
            assert(marketInitialTotalShares == contracts.markets.getTotalSharesPurchased(marketID)), "Market's total shares should be unchanged"
        def test_cancelAsk():
            contracts._ContractLoader__state.mine(1)
            orderType = 2                   # ask
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10000), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            assert(contracts.orders.getOrder(orderID, orderType, marketID, outcomeID) != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "Order should have non-zero elements"
            assert(contracts.cancelOrder.publicCancelOrder(orderID, orderType, marketID, outcomeID, sender=t.k1) == 1), "publicCancelOrder should succeed"
            assert(contracts.orders.getOrder(orderID, orderType, marketID, outcomeID) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "Canceled order elements should all be zero"
            assert(makerInitialCash == contracts.cash.balanceOf(t.a1)), "Maker's cash should be the same as before the order was placed"
            assert(marketInitialCash == contracts.cash.balanceOf(contracts.info.getWallet(marketID))), "Market's cash balance should be the same as before the order was placed"
            assert(makerInitialShares == contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)), "Maker's shares should be unchanged"
            assert(marketInitialTotalShares == contracts.markets.getTotalSharesPurchased(marketID)), "Market's total shares should be unchanged"
        def test_exceptions():
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10000), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"

            # Permissions exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.cancelOrder.cancelOrder(t.a1, orderID, orderType, marketID, outcomeID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "cancelOrder should fail if called from a non-whitelisted account (account 1)"
            try:
                raise Exception(contracts.cancelOrder.refundOrder(t.a1, orderType, 0, fxpAmount, marketID, outcomeID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "refundOrder should fail if called directly"

            # cancelOrder exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.cancelOrder.publicCancelOrder(0, orderType, marketID, outcomeID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicCancelOrder should fail if order ID is zero"
            try:
                raise Exception(contracts.cancelOrder.publicCancelOrder(orderID + 1, orderType, marketID, outcomeID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicCancelOrder should fail if order does not exist"
            try:
                raise Exception(contracts.cancelOrder.publicCancelOrder(orderID, orderType, marketID, outcomeID, sender=t.k2))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicCancelOrder should fail if sender does not own the order"
            assert(contracts.cancelOrder.publicCancelOrder(orderID, orderType, marketID, outcomeID, sender=t.k1) == 1), "publicCancelOrder should succeed"
            try:
                raise Exception(contracts.cancelOrder.publicCancelOrder(orderID, orderType, marketID, outcomeID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicCancelOrder should fail if the order has already been cancelled"
        test_cancelBid()
        test_cancelAsk()
        test_exceptions()
    test_publicCancelOrder()


if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_CancelOrder(contracts)
