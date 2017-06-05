#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

def test_CompleteSets(contracts):
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    def test_publicBuyCompleteSets():
        contracts._ContractLoader__state.mine(1)
        eventID = utils.createBinaryEvent(contracts)
        marketID = utils.createMarket(contracts, eventID)
        fxpAmount = utils.fix(10)
        senderInitialCash = contracts.cash.balanceOf(t.a1)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
        assert(contracts.cash.approve(contracts.completeSets.address, utils.fix(10000), sender=t.k1) == 1), "Approve completeSets contract to spend cash"
        with iocapture.capture() as captured:
            result = contracts.completeSets.publicBuyCompleteSets(marketID, fxpAmount, sender=t.k1)
            logged = captured.stdout
        logCompleteSets = utils.parseCapturedLogs(logged)[-1]
        assert(logCompleteSets["_event_type"] == "CompleteSets"), "Should emit a CompleteSets event"
        assert(logCompleteSets["sender"] == address1), "Logged sender should match input"
        assert(logCompleteSets["type"] == 1), "Logged type should be 1 (buy)"
        assert(logCompleteSets["fxpAmount"] == fxpAmount), "Logged fxpAmount should match input"
        assert(logCompleteSets["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match input"
        assert(logCompleteSets["numOutcomes"] == contracts.events.getNumOutcomes(eventID)), "Logged numOutcomes should match event's number of outcomes"
        assert(logCompleteSets["fxpFee"] == 0), "Logged fee should be 0"
        assert(logCompleteSets["market"] == marketID), "Logged market should match input"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1) == fxpAmount), "Should have 10 shares of outcome 1"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2) == fxpAmount), "Should have 10 shares of outcome 2"
        assert(senderInitialCash - contracts.cash.balanceOf(t.a1) == fxpAmount), "Decrease in sender's cash should equal 10"
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == fxpAmount), "Increase in market's cash should equal 10"
        assert(contracts.markets.getTotalSharesPurchased(marketID) - marketInitialTotalShares == 2*fxpAmount), "Increase in total shares purchased for this market should be 18"
        def test_exceptions():
            contracts._ContractLoader__state.mine(1)
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            fxpAmount = utils.fix(10)
            assert(contracts.cash.approve(contracts.completeSets.address, fxpAmount, sender=t.k1) == 1), "Approve completeSets contract to spend cash"

            # Permissions exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.completeSets.buyCompleteSets(t.a1, marketID, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "buyCompleteSets should fail if called from a non-whitelisted account (account 1)"

            # buyCompleteSets exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.completeSets.publicBuyCompleteSets(marketID + 1, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicBuyCompleteSets should fail if market ID is invalid"
            try:
                raise Exception(contracts.completeSets.publicBuyCompleteSets(marketID, utils.fix(-10), sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "publicBuyCompleteSets should throw ValueOutOfBounds exception if fxpAmount is negative"
            try:
                raise Exception(contracts.completeSets.publicBuyCompleteSets(marketID, 0, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicBuyCompleteSets should fail if fxpAmount is zero"
            assert(contracts.cash.approve(contracts.completeSets.address, fxpAmount - 1, sender=t.k1) == 1), "Approve completeSets contract to spend slightly less cash than needed"
            try:
                raise Exception(contracts.completeSets.publicBuyCompleteSets(marketID, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicBuyCompleteSets should fail if the completeSets contract is not approved for the full amount needed"
        test_exceptions()
    def test_publicSellCompleteSets():
        contracts._ContractLoader__state.mine(1)
        eventID = utils.createBinaryEvent(contracts)
        marketID = utils.createMarket(contracts, eventID)
        utils.buyCompleteSets(contracts, marketID, utils.fix(10))
        fxpAmount = utils.fix(9)
        senderInitialCash = contracts.cash.balanceOf(t.a1)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
        with iocapture.capture() as captured:
            result = contracts.completeSets.publicSellCompleteSets(marketID, fxpAmount, sender=t.k1)
            logged = captured.stdout
        logCompleteSets = utils.parseCapturedLogs(logged)[-1]
        assert(logCompleteSets["_event_type"] == "CompleteSets"), "Should emit a CompleteSets event"
        assert(logCompleteSets["sender"] == address1), "Logged sender should match input"
        assert(logCompleteSets["type"] == 2), "Logged type should be 2 (sell)"
        assert(logCompleteSets["fxpAmount"] == fxpAmount), "Logged fxpAmount should match input"
        assert(logCompleteSets["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match input"
        assert(logCompleteSets["numOutcomes"] == contracts.events.getNumOutcomes(eventID)), "Logged numOutcomes should match event's number of outcomes"
        assert(logCompleteSets["fxpFee"] > 0), "Logged fees should be > 0"
        assert(logCompleteSets["market"] == marketID), "Logged market should match input"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1) == utils.fix(1)), "Should have 1 share of outcome 1"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2) == utils.fix(1)), "Should have 1 share of outcome 2"
        assert(marketInitialTotalShares - contracts.markets.getTotalSharesPurchased(marketID) == 2*fxpAmount), "Decrease in total shares purchased for this market should be 18"
        def test_exceptions():
            contracts._ContractLoader__state.mine(1)
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            fxpAmount = utils.fix(10)
            utils.buyCompleteSets(contracts, marketID, fxpAmount)

            # Permissions exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.completeSets.sellCompleteSets(t.a1, marketID, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "sellCompleteSets should fail if called from a non-whitelisted account (account 1)"

            # sellCompleteSets exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.completeSets.publicSellCompleteSets(marketID + 1, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicSellCompleteSets should fail if market ID is invalid"
            try:
                raise Exception(contracts.completeSets.publicSellCompleteSets(marketID, utils.fix(-10), sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "publicSellCompleteSets should throw ValueOutOfBounds exception if fxpAmount is negative"
            try:
                raise Exception(contracts.completeSets.publicSellCompleteSets(marketID, 0, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicSellCompleteSets should fail if fxpAmount is zero"
            try:
                raise Exception(contracts.completeSets.publicSellCompleteSets(marketID, fxpAmount + 1, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicSellCompleteSets should fail if the sender has insufficient shares in any outcome"
        test_exceptions()
    test_publicBuyCompleteSets()
    test_publicSellCompleteSets()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_CompleteSets(contracts)
