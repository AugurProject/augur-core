#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longTo32Bytes, longToHexString, bytesToHexString, fix, AssertLog, stringToBytes, EtherDelta, PrintGasUsed
from constants import ASK, BID, YES, NO
from pytest import raises, fixture, mark
from pprint import pprint

def test_case_1(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFinder = contractsFixture.contracts['OrdersFinder']
    tradeGroupID = "42"
    nullAddress = longTo32Bytes(0)

    # Orphaned order due to early exit logic from bad data caused by Orders worst order setting bug
    assert orders.getBestOrderId(BID, market.address, 1) == nullAddress
    orderID1 = createOrder.publicCreateOrder(BID, fix(1), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('1', '3000'))
    orderID2 = createOrder.publicCreateOrder(BID, fix(2), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('2', '3000'))
    orderID3 = createOrder.publicCreateOrder(BID, fix(3), 2999, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('3', '2999'))
    assert orders.getWorseOrderId(orderID1) == orderID3
    assert orders.getWorseOrderId(orderID3) == longTo32Bytes(0) # order 2 orphaned

    orderIds = ordersFinder.getExistingOrders5(BID, market.address, 1)

    assert orderID1 in orderIds
    assert orderID3 in orderIds
    assert orderID2 not in orderIds

def test_case_2(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFinder = contractsFixture.contracts['OrdersFinder']
    tradeGroupID = "42"
    nullAddress = longTo32Bytes(0)

    # create orders
    assert orders.getBestOrderId(BID, market.address, 1) == nullAddress
    orderID1 = createOrder.publicCreateOrder(BID, fix(1), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('1', '3000'))
    orderID2 = createOrder.publicCreateOrder(BID, fix(2), 3000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('2', '3000'))
    assert cancelOrder.cancelOrder(orderID1)
    orderID3 = createOrder.publicCreateOrder(BID, fix(3), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('3', '4000'))
    assert orders.getBestOrderId(BID, market.address, 1) == orderID3
    assert orders.getWorseOrderId(orderID3) == nullAddress # order 2 orphaned

    orderIds = ordersFinder.getExistingOrders5(BID, market.address, 1)

    assert orderID1 not in orderIds
    assert orderID2 not in orderIds
    assert orderID3 in orderIds

def test_overflow(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    ordersFinder = contractsFixture.contracts['OrdersFinder']
    tradeGroupID = "42"
    nullAddress = longTo32Bytes(0)

    # create orders
    orderID1 = createOrder.publicCreateOrder(BID, fix(1), 1, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('1', '1'))
    orderID2 = createOrder.publicCreateOrder(BID, fix(1), 2, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('1', '2'))
    orderID3 = createOrder.publicCreateOrder(BID, fix(1), 3, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('1', '3'))
    orderID4 = createOrder.publicCreateOrder(BID, fix(1), 4, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('1', '4'))
    orderID5 = createOrder.publicCreateOrder(BID, fix(1), 5, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('1', '5'))
    orderID6 = createOrder.publicCreateOrder(BID, fix(1), 6, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, value=fix('1', '6'))

    with raises(TransactionFailed):
        orderIds = ordersFinder.getExistingOrders5(BID, market.address, 1)

    orderIds = ordersFinder.getExistingOrders10(BID, market.address, 1)
