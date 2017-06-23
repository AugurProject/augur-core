#!/usr/bin/env python

from __future__ import division
import os
import sys
from data_api import backstops, branches, consensusData, events, expiringEvents, info, markets, mutex, orders, topics
from trading import cash, shareTokens, wallet, createEvent, createMarket, completeSets, makeOrder, cancelOrder, takeAskOrder, takeBidOrder, takeOrder, decreaseTradingFee, claimProceeds, trade, tradingEscapeHatch
import helper_tests
import wcl_tests

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))

from upload_contracts import ContractLoader

contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])

def test_data_api():
    global contracts
    backstops.test_backstops(contracts)
    branches.test_branches(contracts)
    consensusData.test_consensusData(contracts)
    events.test_events(contracts)
    expiringEvents.test_expiringEvents(contracts)
    info.test_info(contracts)
    markets.test_markets(contracts)
    mutex.test_mutex(contracts)
    orders.test_orders(contracts)
    topics.test_topics(contracts)

def test_trading():
    global contracts
    cash.test_Cash(contracts)
    shareTokens.test_ShareTokens(contracts)
    wallet.test_Wallet(contracts)
    createEvent.test_CreateEvent(contracts)
    createMarket.test_CreateMarket(contracts)
    completeSets.test_CompleteSets(contracts)
    makeOrder.test_MakeOrder(contracts)
    cancelOrder.test_CancelOrder(contracts)
    takeAskOrder.test_TakeAskOrder(contracts)
    takeBidOrder.test_TakeBidOrder(contracts)
    takeOrder.test_TakeOrder(contracts)
    decreaseTradingFee.test_DecreaseTradingFee(contracts)
    claimProceeds.test_ClaimProceeds(contracts)
    trade.test_Trade(contracts)
    tradingEscapeHatch.test_EscapeHatch(contracts)

def test_helpers():
    helper_tests.test_assertZeroValue()
    helper_tests.test_float()

def test_wcl():
    global contracts
    # contracts, amount of tests through fuzzer
    wcl_tests.test_wcl(contracts, 5)

if __name__ == "__main__":
    test_data_api()
    test_trading()
    test_helpers()
    test_wcl()
