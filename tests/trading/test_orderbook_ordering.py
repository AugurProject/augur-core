#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longTo32Bytes, longToHexString, bytesToHexString, fix, AssertLog, stringToBytes, EtherDelta, PrintGasUsed
from constants import ASK, BID, YES, NO
from pytest import raises, fixture, mark
from pprint import pprint

def test_correct_order_for_same_price(contractsFixture, cash, market, universe):
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

def test_no_orphans_when_same_price(contractsFixture, cash, market, universe):
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
