#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

def test_DecreaseTradingFee(contracts):
    t = contracts._ContractLoader__tester
    def test_publicDecreaseTradingFee():
        contracts._ContractLoader__state.mine(1)
        eventID = utils.createBinaryEvent(contracts)
        marketID = utils.createMarket(contracts, eventID)
        assert(contracts.cash.approve(contracts.decreaseTradingFee.address, utils.fix(10), sender=t.k1) == 1), "Approve decreaseTradingFee contract to spend cash from account 1"
        fxpInitialTradingFee = contracts.markets.getTradingFee(marketID)
        assert(fxpInitialTradingFee == utils.fix("0.020000000000000001")), "Initial trading fee should be 20000000000000001"
        fxpNewTradingFee = utils.fix("0.02")
        result = contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, fxpNewTradingFee, sender=t.k1)
        assert(contracts.markets.getTradingFee(marketID) == fxpNewTradingFee), "Updated trading fee should be equal to fxpNewTradingFee"
    def test_exceptions():
        contracts._ContractLoader__state.mine(1)
        eventID = utils.createBinaryEvent(contracts)
        marketID = utils.createMarket(contracts, eventID)
        assert(contracts.cash.approve(contracts.decreaseTradingFee.address, utils.fix(10), sender=t.k1) == 1), "Approve decreaseTradingFee contract to spend cash from account 1"
        assert(contracts.cash.approve(contracts.decreaseTradingFee.address, utils.fix(10), sender=t.k2) == 1), "Approve decreaseTradingFee contract to spend cash from account 2"
        fxpInitialTradingFee = contracts.markets.getTradingFee(marketID)
        assert(fxpInitialTradingFee == utils.fix("0.020000000000000001")), "Initial trading fee should be 20000000000000001"
        fxpNewTradingFee = utils.fix("0.02")

        # Permissions exceptions
        contracts._ContractLoader__state.mine(1)
        try:
            raise Exception(contracts.decreaseTradingFee.decreaseTradingFee(t.a1, marketID, fxpNewTradingFee, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "decreaseTradingFee should fail if called from a non-whitelisted account (account 1)"

        # decreaseTradingFee exceptions
        contracts._ContractLoader__state.mine(1)
        try:
            raise Exception(contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, fxpNewTradingFee, sender=t.k2))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicDecreaseTradingFee should fail if sender is not the market creator"
        try:
            raise Exception(contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, contracts.branches.getMinTradingFee(1010101) - 1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicDecreaseTradingFee should fail if new trading fee is below the minimum fee for the branch"
        try:
            raise Exception(contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, utils.fix("0.020000000000000002"), sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicDecreaseTradingFee should fail if new trading fee is higher than the old trading fee"
        contracts._ContractLoader__state.mine(1)
        result = contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, fxpNewTradingFee, sender=t.k1)
        assert(contracts.markets.getTradingFee(marketID) == fxpNewTradingFee), "Updated trading fee should be equal to fxpNewTradingFee"
    test_publicDecreaseTradingFee()
    test_exceptions()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_DecreaseTradingFee(contracts)
