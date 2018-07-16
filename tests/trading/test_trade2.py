#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longTo32Bytes, longToHexString, bytesToHexString, fix, AssertLog, stringToBytes, EtherDelta, PrintGasUsed
from constants import ASK, BID, YES, NO
from pytest import raises, fixture, mark
from pprint import pprint

def test_proof_of_bug_Orders_lines_258_280_case_1(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrderOld']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    nullAddress = longTo32Bytes(0)

    # Orphaned order due to early exit logic from bad data caused by Orders worst order setting bug
    assert orders.getBestOrderId(BID, market.address, 1) == nullAddress
    orderID1 = createOrder.publicCreateOrder(BID, fix(1), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3000'))
    orderID2 = createOrder.publicCreateOrder(BID, fix(2), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '3000'))
    orderID3 = createOrder.publicCreateOrder(BID, fix(3), 2999, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('3', '2999'))
    assert orders.getWorseOrderId(orderID1) == orderID3
    assert orders.getWorseOrderId(orderID3) == longTo32Bytes(0) # order 2 orphaned

def test_proof_of_bug_Orders_line_258_case_2(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrderOld']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    nullAddress = longTo32Bytes(0)

    assert orders.getBestOrderId(BID, market.address, 1) == nullAddress
    orderID1 = createOrder.publicCreateOrder(BID, fix(1), 3001, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3001'))
    orderID2 = createOrder.publicCreateOrder(BID, fix(1), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3000'))
    orderID3 = createOrder.publicCreateOrder(BID, fix(2), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '3000'))
    orderID4 = createOrder.publicCreateOrder(BID, fix(3), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('3', '3000'))
    orderID5 = createOrder.publicCreateOrder(BID, fix(1), 2999, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '2999'))
    orderID6 = createOrder.publicCreateOrder(BID, fix(4), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '3000'))
    assert orders.getWorseOrderId(orderID1) == orderID2
    assert orders.getWorseOrderId(orderID2) == orderID6
    assert orders.getWorseOrderId(orderID4) == orderID3
    assert orders.getWorseOrderId(orderID3) == orderID5
    assert orders.getWorseOrderId(orderID6) == orderID4
    assert orders.getBetterOrderId(orderID2) == orderID1
    assert orders.getBetterOrderId(orderID3) == orderID4
    assert orders.getBetterOrderId(orderID4) == orderID6
    assert orders.getBetterOrderId(orderID5) == orderID3
    assert orders.getBetterOrderId(orderID6) == orderID2

def test_proof_of_bug_OrdersFetcher_line_55(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrderOld']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    nullAddress = longTo32Bytes(0)

    # create orders
    assert orders.getBestOrderId(BID, market.address, 1) == nullAddress
    orderID1 = createOrder.publicCreateOrder(BID, fix(1), 3001, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3001'))
    orderID2 = createOrder.publicCreateOrder(BID, fix(1), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3000'))
    orderID3 = createOrder.publicCreateOrder(BID, fix(2), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '3000'))
    orderID4 = createOrder.publicCreateOrder(BID, fix(3), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('3', '3000'))
    assert orders.getWorseOrderId(orderID1) == orderID2
    assert orders.getWorseOrderId(orderID2) == orderID4
    assert orders.getWorseOrderId(orderID4) == orderID3
    assert orders.getWorseOrderId(orderID3) == longTo32Bytes(0)
    assert orders.getBetterOrderId(orderID2) == orderID1
    assert orders.getBetterOrderId(orderID3) == orderID4
    assert orders.getBetterOrderId(orderID4) == orderID2 # 3 is orphaned
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)

def test_assert_on_dupe_price_for_single_order_orderbook(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    nullAddress = longTo32Bytes(0)

    # create orders
    assert orders.getBestOrderId(BID, market.address, 1) == nullAddress
    orderID1 = createOrder.publicCreateOrder(BID, fix(1), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3000'))
    assert orders.getBestOrderId(BID, market.address, 1) == orderID1
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(BID, fix(2), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '3000'))

def test_fix_of_bug_Orders_line_258_case_2(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    nullAddress = longTo32Bytes(0)

    assert orders.getBestOrderId(BID, market.address, 1) == nullAddress
    orderID1 = createOrder.publicCreateOrder(BID, fix(1), 3001, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3001'))
    orderID2 = createOrder.publicCreateOrder(BID, fix(1), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3000'))
    orderID3 = createOrder.publicCreateOrder(BID, fix(2), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '3000'))
    orderID4 = createOrder.publicCreateOrder(BID, fix(3), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('3', '3000'))
    orderID5 = createOrder.publicCreateOrder(BID, fix(1), 2999, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '2999'))
    orderID6 = createOrder.publicCreateOrder(BID, fix(4), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '3000'))
    assert orders.getWorseOrderId(orderID1) == orderID2
    assert orders.getWorseOrderId(orderID2) == orderID3
    assert orders.getWorseOrderId(orderID3) == orderID4
    assert orders.getWorseOrderId(orderID4) == orderID6
    assert orders.getWorseOrderId(orderID6) == orderID5
    assert orders.getWorseOrderId(orderID5) == longTo32Bytes(0)
    assert orders.getBetterOrderId(orderID2) == orderID1
    assert orders.getBetterOrderId(orderID3) == orderID2
    assert orders.getBetterOrderId(orderID4) == orderID3
    assert orders.getBetterOrderId(orderID5) == orderID6
    assert orders.getBetterOrderId(orderID6) == orderID4
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)

def test_fix_of_bug_OrdersFetcher_line_55(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    nullAddress = longTo32Bytes(0)

    # create orders
    assert orders.getBestOrderId(BID, market.address, 1) == nullAddress
    orderID1 = createOrder.publicCreateOrder(BID, fix(1), 3001, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3001'))
    orderID2 = createOrder.publicCreateOrder(BID, fix(1), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('1', '3000'))
    orderID3 = createOrder.publicCreateOrder(BID, fix(2), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '3000'))
    orderID4 = createOrder.publicCreateOrder(BID, fix(3), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('3', '3000'))
    assert orders.getWorseOrderId(orderID1) == orderID2
    assert orders.getWorseOrderId(orderID2) == orderID3
    assert orders.getWorseOrderId(orderID3) == orderID4
    assert orders.getWorseOrderId(orderID4) == longTo32Bytes(0)
    assert orders.getBetterOrderId(orderID2) == orderID1
    assert orders.getBetterOrderId(orderID3) == orderID2
    assert orders.getBetterOrderId(orderID4) == orderID3
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)
