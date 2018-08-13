#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longTo32Bytes, longToHexString, bytesToHexString, fix, AssertLog, stringToBytes, EtherDelta, PrintGasUsed
from constants import ASK, BID, YES, NO
from pytest import raises, fixture, mark
from pprint import pprint

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
