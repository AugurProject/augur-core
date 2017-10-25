#!/usr/bin/env python

from ethereum.tools import tester
from utils import longTo32Bytes, longToHexString, bytesToHexString, fix, captureFilteredLogs
from constants import BID, ASK, YES, NO
from pprint import pprint


def test_one_bid_on_books_buy_full_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    tradeGroupID = 42L
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, 2, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('2', '0.4'))

    assert len(logs) == 1

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('2', '0.6')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('2', '0.4')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID) == [0L, 0L, longToHexString(0), 0L, 0L, longTo32Bytes(0), longTo32Bytes(0), 0L]
    assert fillOrderID == longTo32Bytes(1)


def test_one_bid_on_books_buy_partial_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    tradeGroupID = 42L
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, 1, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('1', '0.4'))

    assert len(logs) == 1

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('1', '0.6')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('1', '0.4')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID) == [1, fix('0.6'), bytesToHexString(tester.a1), fix('1', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0L]
    assert fillOrderID == longTo32Bytes(1)


def test_one_bid_on_books_buy_excess_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    tradeGroupID = 42L
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(BID, 4, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, 5, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('5', '0.4'))

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('4', '0.6')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('4', '0.4')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert logs[1]["_event_type"] == "OrderCreated"
    assert logs[1]["amount"] == 1
    assert logs[1]["numSharesEscrowed"] == 0
    assert logs[1]["numTokensEscrowed"] == fix('1', '0.4')
    assert logs[1]["orderId"] == fillOrderID
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [1, fix('0.6'), bytesToHexString(tester.a2), fix('1', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]

def test_two_bids_on_books_buy_both(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, 4, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '0.6'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, 1, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('1', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, 5, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('5', '0.4'))

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('4', '0.6')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('4', '0.4')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert logs[1]["_event_type"] == "OrderFilled"
    assert logs[1]["filler"] == bytesToHexString(tester.a2)
    assert logs[1]["numCreatorShares"] == 0
    assert logs[1]["numCreatorTokens"] == fix('1', '0.6')
    assert logs[1]["numFillerShares"] == 0
    assert logs[1]["numFillerTokens"] == fix('1', '0.4')
    assert logs[1]["settlementFees"] == 0
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_bids_on_books_buy_full_and_partial(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.6'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, 7, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.4'))

    assert len(logs) == 2
    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('12', '0.6')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('12', '0.4')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert logs[1]["_event_type"] == "OrderFilled"
    assert logs[1]["filler"] == bytesToHexString(tester.a2)
    assert logs[1]["numCreatorShares"] == 0
    assert logs[1]["numCreatorTokens"] == fix('3', '0.6')
    assert logs[1]["numFillerShares"] == 0
    assert logs[1]["numFillerTokens"] == fix('3', '0.4')
    assert logs[1]["settlementFees"] == 0
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [4, fix('0.6'), bytesToHexString(tester.a3), fix('4', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_bids_on_books_buy_one_full_then_create(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.6'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, 7, fix('0.5'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '0.6'))

    # fill/create
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.4'))

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('12', '0.6')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('12', '0.4')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert logs[1]["_event_type"] == "OrderCreated"
    assert logs[1]["amount"] == 3
    assert logs[1]["numSharesEscrowed"] == 0
    assert logs[1]["numTokensEscrowed"] == fix('3', '0.4')
    assert logs[1]["orderId"] == fillOrderID
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [7, fix('0.5'), bytesToHexString(tester.a3), fix('7', '0.5'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [3, fix('0.6'), bytesToHexString(tester.a2), fix('3', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]

def test_one_ask_on_books_buy_full_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, 12, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('12', '0.6'))

    assert len(logs) == 1

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('12', '0.4')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('12', '0.6')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_one_ask_on_books_buy_partial_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, 7, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('7', '0.6'))

    assert len(logs) == 1

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('7', '0.4')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('7', '0.6')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID) == [5, fix('0.6'), bytesToHexString(tester.a1), fix('5', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_one_ask_on_books_buy_excess_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.6'))

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('12', '0.4')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('12', '0.6')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert logs[1]["_event_type"] == "OrderCreated"
    assert logs[1]["amount"] == 3
    assert logs[1]["numSharesEscrowed"] == 0
    assert logs[1]["numTokensEscrowed"] == fix('3', '0.6')
    assert logs[1]["orderId"] == fillOrderID
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [3, fix('0.6'), bytesToHexString(tester.a2), fix('3', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]

def test_two_asks_on_books_buy_both(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, 3, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('3', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.6'))

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('12', '0.4')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('12', '0.6')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert logs[1]["_event_type"] == "OrderFilled"
    assert logs[1]["filler"] == bytesToHexString(tester.a2)
    assert logs[1]["numCreatorShares"] == 0
    assert logs[1]["numCreatorTokens"] == fix('3', '0.4')
    assert logs[1]["numFillerShares"] == 0
    assert logs[1]["numFillerTokens"] == fix('3', '0.6')
    assert logs[1]["settlementFees"] == 0
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_asks_on_books_buy_full_and_partial(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, 7, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.6'))

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('12', '0.4')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('12', '0.6')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert logs[1]["_event_type"] == "OrderFilled"
    assert logs[1]["filler"] == bytesToHexString(tester.a2)
    assert logs[1]["numCreatorShares"] == 0
    assert logs[1]["numCreatorTokens"] == fix('3', '0.4')
    assert logs[1]["numFillerShares"] == 0
    assert logs[1]["numFillerTokens"] == fix('3', '0.6')
    assert logs[1]["settlementFees"] == 0
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [4, fix('0.6'), bytesToHexString(tester.a3), fix('4', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_asks_on_books_buy_one_full_then_create(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, 7, fix('0.7'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '0.4'))

    # fill/create
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.6'))

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "OrderFilled"
    assert logs[0]["filler"] == bytesToHexString(tester.a2)
    assert logs[0]["numCreatorShares"] == 0
    assert logs[0]["numCreatorTokens"] == fix('12', '0.4')
    assert logs[0]["numFillerShares"] == 0
    assert logs[0]["numFillerTokens"] == fix('12', '0.6')
    assert logs[0]["settlementFees"] == 0
    assert logs[0]["shareToken"] == market.getShareToken(YES)
    assert logs[0]["tradeGroupId"] == 42

    assert logs[1]["_event_type"] == "OrderCreated"
    assert logs[1]["amount"] == 3
    assert logs[1]["numSharesEscrowed"] == 0
    assert logs[1]["numTokensEscrowed"] == fix('3', '0.6')
    assert logs[1]["orderId"] == fillOrderID
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [7, fix('0.7'), bytesToHexString(tester.a3), fix('7', '0.3'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [3, fix('0.6'), bytesToHexString(tester.a2), fix('3', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
