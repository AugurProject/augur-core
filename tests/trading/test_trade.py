#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longTo32Bytes, longToHexString, bytesToHexString, fix, captureFilteredLogs, stringToBytes, EtherDelta
from constants import ASK, BID, YES, NO
from pytest import raises, fixture
from pprint import pprint

def test_minimum_gas_failure(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    tradeGroupID = "42"

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(4), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '6000'))

    # We need to provide a minimum gas amount or we'll get back a failure
    minGas = 500000
    fillOrderID = trade.publicSell(market.address, YES, fix(5), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('5', '4000'), startgas=minGas-1)

    # We get back a sentinal byte value since not enough gas was provided
    assert fillOrderID == longTo32Bytes(1)

    # If we provide enough gas we get a legitimate value
    fillOrderID = trade.publicSell(market.address, YES, fix(5), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('5', '4000'))

    assert fillOrderID != longTo32Bytes(1)

def test_one_bid_on_books_buy_full_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '6000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, fix(2), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('2', '4000'))

    assert len(logs) == 5
    log1 = logs[4]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('2', '6000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('2', '4000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert fillOrderID == longTo32Bytes(1)


def test_one_bid_on_books_buy_partial_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '6000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, fix(1), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('1', '4000'))

    assert len(logs) == 5
    log1 = logs[4]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('1', '6000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('1', '4000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID) == fix(1)
    assert orders.getPrice(orderID) == 6000
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(orderID) == fix('1', '6000')
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert fillOrderID == longTo32Bytes(1)


def test_one_bid_on_books_buy_excess_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(4), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '6000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, fix(5), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('5', '4000'))

    assert len(logs) == 6
    log1 = logs[4]
    log2 = logs[5]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('4', '6000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('4', '4000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert log2["_event_type"] == "OrderCreated"
    assert log2['creator'] == bytesToHexString(tester.a2)
    assert log2["orderId"] == fillOrderID
    assert log2["shareToken"] == market.getShareToken(YES)
    assert log2["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

    assert orders.getAmount(fillOrderID) == fix(1)
    assert orders.getPrice(fillOrderID) == 6000
    assert orders.getOrderCreator(fillOrderID) == bytesToHexString(tester.a2)
    assert orders.getOrderMoneyEscrowed(fillOrderID) == fix('1', '4000')
    assert orders.getOrderSharesEscrowed(fillOrderID) == 0
    assert orders.getBetterOrderId(fillOrderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(fillOrderID) == longTo32Bytes(0)

def test_two_bids_on_books_buy_both(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, fix(4), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '6000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('1', '6000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, fix(5), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('5', '4000'))

    assert len(logs) == 10
    log1 = logs[4]
    log2 = logs[9]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('4', '6000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('4', '4000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert log2["_event_type"] == "OrderFilled"
    assert log2["filler"] == bytesToHexString(tester.a2)
    assert log2["numCreatorShares"] == 0
    assert log2["numCreatorTokens"] == fix('1', '6000')
    assert log2["numFillerShares"] == 0
    assert log2["numFillerTokens"] == fix('1', '4000')
    assert log2["marketCreatorFees"] == 0
    assert log2["reporterFees"] == 0
    assert log2["shareToken"] == market.getShareToken(YES)
    assert log2["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID1) == 0
    assert orders.getPrice(orderID1) == 0
    assert orders.getOrderCreator(orderID1) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID1) == 0
    assert orders.getOrderSharesEscrowed(orderID1) == 0
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID1) == longTo32Bytes(0)

    assert orders.getAmount(orderID2) == 0
    assert orders.getPrice(orderID2) == 0
    assert orders.getOrderCreator(orderID2) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID2) == 0
    assert orders.getOrderSharesEscrowed(orderID2) == 0
    assert orders.getBetterOrderId(orderID2) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID2) == longTo32Bytes(0)

    assert fillOrderID == longTo32Bytes(1)

def test_two_bids_on_books_buy_full_and_partial(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '6000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, fix(7), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '6000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('15', '4000'))

    assert len(logs) == 10
    log1 = logs[4]
    log2 = logs[9]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('12', '6000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('12', '4000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert log2["_event_type"] == "OrderFilled"
    assert log2["filler"] == bytesToHexString(tester.a2)
    assert log2["numCreatorShares"] == 0
    assert log2["numCreatorTokens"] == fix('3', '6000')
    assert log2["numFillerShares"] == 0
    assert log2["numFillerTokens"] == fix('3', '4000')
    assert log2["marketCreatorFees"] == 0
    assert log2["reporterFees"] == 0
    assert log2["shareToken"] == market.getShareToken(YES)
    assert log2["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID1) == 0
    assert orders.getPrice(orderID1) == 0
    assert orders.getOrderCreator(orderID1) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID1) == 0
    assert orders.getOrderSharesEscrowed(orderID1) == 0
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID1) == longTo32Bytes(0)

    assert orders.getAmount(orderID2) == fix(4)
    assert orders.getPrice(orderID2) == 6000
    assert orders.getOrderCreator(orderID2) == bytesToHexString(tester.a3)
    assert orders.getOrderMoneyEscrowed(orderID2) == fix('4', '6000')
    assert orders.getOrderSharesEscrowed(orderID2) == 0
    assert orders.getBetterOrderId(orderID2) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID2) == longTo32Bytes(0)

    assert fillOrderID == longTo32Bytes(1)

def test_two_bids_on_books_buy_one_full_then_create(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '6000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, fix(7), 5000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '5000'))

    # fill/create
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicSell(market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('15', '4000'))

    assert len(logs) == 6
    log1 = logs[4]
    log2 = logs[5]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('12', '6000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('12', '4000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert log2["_event_type"] == "OrderCreated"
    assert log2['creator'] == bytesToHexString(tester.a2)
    assert log2["orderId"] == fillOrderID
    assert log2["shareToken"] == market.getShareToken(YES)
    assert log2["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID1) == 0
    assert orders.getPrice(orderID1) == 0
    assert orders.getOrderCreator(orderID1) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID1) == 0
    assert orders.getOrderSharesEscrowed(orderID1) == 0
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID1) == longTo32Bytes(0)

    assert orders.getAmount(orderID2) == fix(7)
    assert orders.getPrice(orderID2) == 5000
    assert orders.getOrderCreator(orderID2) == bytesToHexString(tester.a3)
    assert orders.getOrderMoneyEscrowed(orderID2) == fix('7', '5000')
    assert orders.getOrderSharesEscrowed(orderID2) == 0
    assert orders.getBetterOrderId(orderID2) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID2) == longTo32Bytes(0)

    assert orders.getAmount(fillOrderID) == fix(3)
    assert orders.getPrice(fillOrderID) == 6000
    assert orders.getOrderCreator(fillOrderID) == bytesToHexString(tester.a2)
    assert orders.getOrderMoneyEscrowed(fillOrderID) == fix('3', '4000')
    assert orders.getOrderSharesEscrowed(fillOrderID) == 0
    assert orders.getBetterOrderId(fillOrderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(fillOrderID) == longTo32Bytes(0)

def test_one_ask_on_books_buy_full_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix(12), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('12', '6000'))

    assert len(logs) == 5
    log1 = logs[4]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('12', '4000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('12', '6000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert fillOrderID == longTo32Bytes(1)

def test_one_ask_on_books_buy_partial_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix(7), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('7', '6000'))

    assert len(logs) == 5
    log1 = logs[4]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('7', '4000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('7', '6000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID) == fix(5)
    assert orders.getPrice(orderID) == 6000
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(orderID) == fix('5', '4000')
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

    assert fillOrderID == longTo32Bytes(1)

def test_one_ask_on_books_buy_excess_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('15', '6000'))

    assert len(logs) == 6
    log1 = logs[4]
    log2 = logs[5]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('12', '4000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('12', '6000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert log2["_event_type"] == "OrderCreated"
    assert log2['creator'] == bytesToHexString(tester.a2)
    assert log2["orderId"] == fillOrderID
    assert log2["shareToken"] == market.getShareToken(YES)
    assert log2["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

    assert orders.getAmount(fillOrderID) == fix(3)
    assert orders.getPrice(fillOrderID) == 6000
    assert orders.getOrderCreator(fillOrderID) == bytesToHexString(tester.a2)
    assert orders.getOrderMoneyEscrowed(fillOrderID) == fix('3', '6000')
    assert orders.getOrderSharesEscrowed(fillOrderID) == 0
    assert orders.getBetterOrderId(fillOrderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(fillOrderID) == longTo32Bytes(0)

def test_two_asks_on_books_buy_both(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, fix(3), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('3', '4000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('15', '6000'))

    assert len(logs) == 10
    log1 = logs[4]
    log2 = logs[9]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('12', '4000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('12', '6000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert log2["_event_type"] == "OrderFilled"
    assert log2["filler"] == bytesToHexString(tester.a2)
    assert log2["numCreatorShares"] == 0
    assert log2["numCreatorTokens"] == fix('3', '4000')
    assert log2["numFillerShares"] == 0
    assert log2["numFillerTokens"] == fix('3', '6000')
    assert log2["marketCreatorFees"] == 0
    assert log2["reporterFees"] == 0
    assert log2["shareToken"] == market.getShareToken(YES)
    assert log2["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID1) == 0
    assert orders.getPrice(orderID1) == 0
    assert orders.getOrderCreator(orderID1) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID1) == 0
    assert orders.getOrderSharesEscrowed(orderID1) == 0
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID1) == longTo32Bytes(0)

    assert orders.getAmount(orderID2) == 0
    assert orders.getPrice(orderID2) == 0
    assert orders.getOrderCreator(orderID2) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID2) == 0
    assert orders.getOrderSharesEscrowed(orderID2) == 0
    assert orders.getBetterOrderId(orderID2) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID2) == longTo32Bytes(0)
    assert fillOrderID == longTo32Bytes(1)

def test_two_asks_on_books_buy_full_and_partial(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, fix(7), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '4000'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('15', '6000'))

    assert len(logs) == 10
    log1 = logs[4]
    log2 = logs[9]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('12', '4000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('12', '6000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert log2["_event_type"] == "OrderFilled"
    assert log2["filler"] == bytesToHexString(tester.a2)
    assert log2["numCreatorShares"] == 0
    assert log2["numCreatorTokens"] == fix('3', '4000')
    assert log2["numFillerShares"] == 0
    assert log2["numFillerTokens"] == fix('3', '6000')
    assert log2["marketCreatorFees"] == 0
    assert log2["reporterFees"] == 0
    assert log2["shareToken"] == market.getShareToken(YES)
    assert log2["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID1) == 0
    assert orders.getPrice(orderID1) == 0
    assert orders.getOrderCreator(orderID1) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID1) == 0
    assert orders.getOrderSharesEscrowed(orderID1) == 0
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID1) == longTo32Bytes(0)

    assert orders.getAmount(orderID2) == fix(4)
    assert orders.getPrice(orderID2) == 6000
    assert orders.getOrderCreator(orderID2) == bytesToHexString(tester.a3)
    assert orders.getOrderMoneyEscrowed(orderID2) == fix('4', '4000')
    assert orders.getOrderSharesEscrowed(orderID2) == 0
    assert orders.getBetterOrderId(orderID2) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID2) == longTo32Bytes(0)

    assert fillOrderID == longTo32Bytes(1)

def test_two_asks_on_books_buy_one_full_then_create(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, fix(7), 7000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '4000'))

    # fill/create
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, sender = tester.k2, value=fix('15', '6000'))

    assert len(logs) == 6
    log1 = logs[4]
    log2 = logs[5]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('12', '4000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('12', '6000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("42")

    assert log2["_event_type"] == "OrderCreated"
    assert log2['creator'] == bytesToHexString(tester.a2)
    assert log2["orderId"] == fillOrderID
    assert log2["shareToken"] == market.getShareToken(YES)
    assert log2["tradeGroupId"] == stringToBytes("42")

    assert orders.getAmount(orderID1) == 0
    assert orders.getPrice(orderID1) == 0
    assert orders.getOrderCreator(orderID1) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID1) == 0
    assert orders.getOrderSharesEscrowed(orderID1) == 0
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID1) == longTo32Bytes(0)

    assert orders.getAmount(orderID2) == fix(7)
    assert orders.getPrice(orderID2) == 7000
    assert orders.getOrderCreator(orderID2) == bytesToHexString(tester.a3)
    assert orders.getOrderMoneyEscrowed(orderID2) == fix('7', '3000')
    assert orders.getOrderSharesEscrowed(orderID2) == 0
    assert orders.getBetterOrderId(orderID2) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID2) == longTo32Bytes(0)

    assert orders.getAmount(fillOrderID) == fix(3)
    assert orders.getPrice(fillOrderID) == 6000
    assert orders.getOrderCreator(fillOrderID) == bytesToHexString(tester.a2)
    assert orders.getOrderMoneyEscrowed(fillOrderID) == fix('3', '6000')
    assert orders.getOrderSharesEscrowed(fillOrderID) == 0
    assert orders.getBetterOrderId(fillOrderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(fillOrderID) == longTo32Bytes(0)

def test_take_best_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    orders = contractsFixture.contracts['Orders']
    initialTester1ETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialTester2ETH = contractsFixture.chain.head_state.get_balance(tester.a2)

    # create order with cash
    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1, value=fix('1', '4000'))
    assert orderID

    # fill order with cash using on-chain matcher
    assert trade.publicTakeBestOrder(BID, market.address, YES, fix(1), 6000, "43", sender=tester.k2, value=fix('1', '6000')) == 0

    assert len(logs) == 6
    log1 = logs[5]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix('1', '4000')
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('1', '6000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("43")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

def test_take_best_order_multiple_orders(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    orders = contractsFixture.contracts['Orders']
    initialTester1ETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialTester2ETH = contractsFixture.chain.head_state.get_balance(tester.a2)

    # create orders with cash
    logs = []
    orderIDs = []
    numOrders = 5
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    for i in range(numOrders):
        orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000 + i, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1, value=fix('1', 4000 - i))
        assert orderID
        orderIDs.append(orderID)

    # fill orders with cash using on-chain matcher
    price = 6000 + numOrders
    assert trade.publicTakeBestOrder(BID, market.address, YES, fix(numOrders), price, "43", sender=tester.k2, value=fix(numOrders, price), startgas=long(6.7 * 10**7)) == 0

    assert len(logs) == numOrders + numOrders * 5

    for i in range(numOrders):
        orderID = orderIDs[i]
        assert orders.getAmount(orderID) == 0
        assert orders.getPrice(orderID) == 0
        assert orders.getOrderCreator(orderID) == longToHexString(0)
        assert orders.getOrderMoneyEscrowed(orderID) == 0
        assert orders.getOrderSharesEscrowed(orderID) == 0
        assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
        assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

        log1 = logs[numOrders + 5 * (i + 1) - 1]
        assert log1["_event_type"] == "OrderFilled"
        assert log1["filler"] == bytesToHexString(tester.a2)
        assert log1["numCreatorShares"] == 0
        assert log1["numCreatorTokens"] == fix('1', 4000 - i)
        assert log1["numFillerShares"] == 0
        assert log1["numFillerTokens"] == fix('1', 6000 + i)
        assert log1["marketCreatorFees"] == 0
        assert log1["reporterFees"] == 0
        assert log1["shareToken"] == market.getShareToken(YES)
        assert log1["tradeGroupId"] == stringToBytes("43")

def test_take_best_order_with_shares_escrowed_buy_with_cash(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    orders = contractsFixture.contracts['Orders']
    completeSets = contractsFixture.contracts['CompleteSets']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))

    # buy complete sets
    assert completeSets.publicBuyCompleteSets(market.address, fix(1), sender=tester.k1, value=fix('1', '10000'))
    assert yesShareToken.balanceOf(tester.a1) == fix(1)

    # create order with shares
    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    assert orderID

    # fill order with cash using on-chain matcher
    assert trade.publicTakeBestOrder(BID, market.address, YES, fix(1), 6000, "43", sender=tester.k2, value=fix('1', '6000')) == 0

    assert len(logs) == 4
    log1 = logs[3]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == fix(1)
    assert log1["numCreatorTokens"] == 0
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix('1', '6000')
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("43")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

def test_take_best_order_with_shares_escrowed_buy_with_shares_categorical(contractsFixture, cash, categoricalMarket, universe):
    market = categoricalMarket
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    orders = contractsFixture.contracts['Orders']
    completeSets = contractsFixture.contracts['CompleteSets']
    firstShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(0))
    secondShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(1))
    thirdShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(2))


    # buy complete sets for both users
    numTicks = market.getNumTicks()
    assert completeSets.publicBuyCompleteSets(market.address, fix(1), sender=tester.k1, value=fix('1', numTicks))
    assert completeSets.publicBuyCompleteSets(market.address, fix(1), sender=tester.k2, value=fix('1', numTicks))
    assert firstShareToken.balanceOf(tester.a1) == firstShareToken.balanceOf(tester.a2) == fix(1)
    assert secondShareToken.balanceOf(tester.a1) == secondShareToken.balanceOf(tester.a2) == fix(1)
    assert thirdShareToken.balanceOf(tester.a1) == thirdShareToken.balanceOf(tester.a2) == fix(1)

    # create order with shares
    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    assert orderID

    # fill order with shares using on-chain matcher
    totalProceeds = fix(1, numTicks)
    totalProceeds -= fix(1, numTicks) / market.getMarketCreatorSettlementFeeDivisor()
    totalProceeds -= fix(1, numTicks) / universe.getOrCacheReportingFeeDivisor()
    expectedTester1Payout = totalProceeds * 6000 / numTicks
    expectedTester2Payout = totalProceeds * (numTicks - 6000) / numTicks
    with EtherDelta(expectedTester1Payout, tester.a1, contractsFixture.chain, "Tester 1 ETH delta wrong"):
        with EtherDelta(expectedTester2Payout, tester.a2, contractsFixture.chain, "Tester 2 ETH delta wrong"):
            assert trade.publicTakeBestOrder(BID, market.address, 0, fix(1), 6000, "43", sender=tester.k2) == 0

    assert firstShareToken.balanceOf(tester.a1) == 0
    assert secondShareToken.balanceOf(tester.a1) == fix(1)
    assert thirdShareToken.balanceOf(tester.a1) == fix(1)

    assert firstShareToken.balanceOf(tester.a2) == fix(1)
    assert secondShareToken.balanceOf(tester.a2) == 0
    assert thirdShareToken.balanceOf(tester.a2) == 0

    assert len(logs) == 10
    log1 = logs[9]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == fix(1)
    assert log1["numCreatorTokens"] == 0
    assert log1["numFillerShares"] == fix(1)
    assert log1["numFillerTokens"] == 0
    assert log1["marketCreatorFees"] == fix(1, numTicks) / market.getMarketCreatorSettlementFeeDivisor()
    assert log1["reporterFees"] == fix(1, numTicks) / universe.getOrCacheReportingFeeDivisor()
    assert log1["shareToken"] == market.getShareToken(0)
    assert log1["tradeGroupId"] == stringToBytes("43")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)