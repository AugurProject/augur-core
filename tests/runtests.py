#!/usr/bin/env python

from __future__ import division
import os
import sys
import trading_tests
import data_api_tests
import helper_tests

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))

from upload_contracts import ContractLoader

contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])

def test_data_api():
    global contracts
    data_api_tests.test_backstops(contracts)
    data_api_tests.test_branches(contracts)
    data_api_tests.test_consensusData(contracts)
    data_api_tests.test_events(contracts)
    data_api_tests.test_expiringEvents(contracts)
    data_api_tests.test_info(contracts)
    data_api_tests.test_markets(contracts)
    data_api_tests.test_mutex(contracts)
    data_api_tests.test_orders(contracts)
    data_api_tests.test_topics(contracts)

def test_trading():
    global contracts
    trading_tests.test_Cash(contracts)
    trading_tests.test_ShareTokens(contracts)
    trading_tests.test_Wallet(contracts)
    trading_tests.test_CreateEvent(contracts)
    trading_tests.test_CreateMarket(contracts)
    trading_tests.test_CompleteSets(contracts)
    trading_tests.test_MakeOrder(contracts)
    trading_tests.test_CancelOrder(contracts)
    trading_tests.test_TakeAskOrder(contracts)
    trading_tests.test_TakeBidOrder(contracts)
    trading_tests.test_TakeOrder(contracts)
    trading_tests.test_DecreaseTradingFee(contracts)
    trading_tests.test_ClaimProceeds(contracts)

def test_helpers():
    helper_tests.test_refund()
    helper_tests.test_float()

if __name__ == "__main__":
    test_data_api()
    test_trading()
    test_helpers()
