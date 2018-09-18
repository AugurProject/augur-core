#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longTo32Bytes, longToHexString, bytesToHexString, fix, AssertLog, stringToBytes, EtherDelta, PrintGasUsed
from constants import ASK, BID, YES, NO, LONG, SHORT
from pytest import raises, fixture, mark
from pprint import pprint

@mark.parametrize('withSelf', [
    True,
    False
])
def test_one_bid_on_books_buy_full_order(withSelf, contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create order
    sender = tester.k2 if withSelf else tester.k1
    orderID = createOrder.publicCreateOrder(BID, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = sender, value=fix('2', '6000'))

    # fill best order
    orderFilledLog = {
        "filler": bytesToHexString(tester.a2),
        "numCreatorShares": 0,
        "numCreatorTokens": fix('2', '6000'),
        "numFillerShares": 0,
        "numFillerTokens": fix('2', '4000'),
        "marketCreatorFees": 0,
        "reporterFees": 0,
        "shareToken": market.getShareToken(YES),
        "tradeGroupId": stringToBytes("42"),
    }
    with AssertLog(contractsFixture, "OrderFilled", orderFilledLog):
        assert trade.publicTrade(SHORT,market.address, YES, fix(2), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('2', '4000'))

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

def test_one_bid_on_books_buy_partial_order(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '6000'))

    # fill best order
    fillOrderID = None
    orderFilledLog = {
        "amountFilled": fix(1),
    }
    with AssertLog(contractsFixture, "OrderFilled", orderFilledLog):
        with PrintGasUsed(contractsFixture, "publicTrade", 0):
            fillOrderID = trade.publicTrade(1, market.address, YES, fix(1), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('1', '4000'))

    assert orders.getAmount(orderID) == fix(1)
    assert orders.getPrice(orderID) == 6000
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(orderID) == fix('1', '6000')
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert fillOrderID == longTo32Bytes(1)

def test_one_bid_on_books_buy_partial_order_fill_loop_limit(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '6000'))

    # fill best order
    fillOrderID = None
    orderFilledLog = {
        "amountFilled": fix(1),
    }
    with AssertLog(contractsFixture, "OrderFilled", orderFilledLog):
        with PrintGasUsed(contractsFixture, "publicTrade", 0):
            fillOrderID = trade.publicTrade(1, market.address, YES, fix(1), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('1', '4000'))

    assert orders.getAmount(orderID) == fix(1)
    assert orders.getPrice(orderID) == 6000
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(orderID) == fix('1', '6000')
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert fillOrderID == longTo32Bytes(1)

@mark.parametrize('withTotalCost', [
    True,
    False
])
def test_one_bid_on_books_buy_excess_order(withTotalCost, contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(4), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '6000'))

    fillOrderID = None

    # fill best order
    orderFilledLog = {
        "filler": bytesToHexString(tester.a2),
        "numCreatorShares": 0,
        "numCreatorTokens": fix('4', '6000'),
        "numFillerShares": 0,
        "numFillerTokens": fix('4', '4000'),
        "marketCreatorFees": 0,
        "reporterFees": 0,
        "shareToken": market.getShareToken(YES),
        "tradeGroupId": stringToBytes("42"),
    }
    orderCreatedLog = {
        "creator": bytesToHexString(tester.a2),
        "shareToken": market.getShareToken(YES),
        "tradeGroupId": stringToBytes("42"),
    }
    with AssertLog(contractsFixture, "OrderFilled", orderFilledLog):
        with AssertLog(contractsFixture, "OrderCreated", orderCreatedLog):
            if withTotalCost:
                fillOrderID = trade.publicTradeWithTotalCost(SHORT,market.address, YES, fix(5, 6000), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('5', '4000'))
            else:
                fillOrderID = trade.publicTrade(SHORT,market.address, YES, fix(5), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('5', '4000'))

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

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, fix(4), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '6000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('1', '6000'))

    # fill best order
    with PrintGasUsed(contractsFixture, "Fill two", 0):
        fillOrderID = trade.publicTrade(SHORT,market.address, YES, fix(5), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('5', '4000'))

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

def test_two_bids_on_books_buy_one_with_limit(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, fix(4), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '6000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('1', '6000'))

    # fill best order
    with PrintGasUsed(contractsFixture, "Fill two", 0):
        fillOrderID = trade.publicTrade(SHORT,market.address, YES, fix(5), 6000, "0", "0", tradeGroupID, 1, sender = tester.k2, value=fix('5', '4000'))

    assert orders.getAmount(orderID1) == 0
    assert orders.getPrice(orderID1) == 0
    assert orders.getOrderCreator(orderID1) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID1) == 0
    assert orders.getOrderSharesEscrowed(orderID1) == 0
    assert orders.getBetterOrderId(orderID1) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID1) == longTo32Bytes(0)

    assert orders.getAmount(orderID2) == fix(1)

    # We dont create an order since an existing match is on the books
    assert fillOrderID == longTo32Bytes(1)

def test_two_bids_on_books_buy_full_and_partial(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '6000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, fix(7), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '6000'))

    # fill best order
    fillOrderID = trade.publicTrade(SHORT,market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('15', '4000'))

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

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '6000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, fix(7), 5000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '5000'))

    # fill/create
    with PrintGasUsed(contractsFixture, "buy one and create", 0):
        fillOrderID = trade.publicTrade(SHORT,market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('15', '4000'))

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

@mark.parametrize('withTotalCost', [
    True,
    False
])
def test_one_ask_on_books_buy_full_order(withTotalCost, contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create order
    orderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))

    # fill best order
    if withTotalCost:
        fillOrderID = trade.publicTradeWithTotalCost(LONG, market.address, YES, fix(12, 6000), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('12', '6000'))
    else:
        fillOrderID = trade.publicTrade(LONG, market.address, YES, fix(12), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('12', '6000'))

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

    # create order
    orderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))

    # fill best order
    fillOrderID = trade.publicTrade(LONG, market.address, YES, fix(7), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('7', '6000'))

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

    # create order
    orderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))

    # fill best order
    fillOrderID = trade.publicTrade(LONG,market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('15', '6000'))

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

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, fix(3), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('3', '4000'))

    # fill best order
    fillOrderID = trade.publicTrade(LONG,market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('15', '6000'))

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

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, fix(7), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '4000'))

    # fill best order
    fillOrderID = trade.publicTrade(LONG,market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('15', '6000'))

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

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '4000'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, fix(7), 7000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '4000'))

    # fill/create
    fillOrderID = trade.publicTrade(LONG,market.address, YES, fix(15), 6000, "0", "0", tradeGroupID, 6, sender = tester.k2, value=fix('15', '6000'))

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

@mark.parametrize('withTotalCost', [
    True,
    False
])
def test_take_best_order(withTotalCost, contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    orders = contractsFixture.contracts['Orders']
    initialTester1ETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialTester2ETH = contractsFixture.chain.head_state.get_balance(tester.a2)

    # create order with cash
    orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1, value=fix('1', '4000'))
    assert orderID

    # fill order with cash using on-chain matcher
    if withTotalCost:
        assert trade.publicFillBestOrderWithTotalCost(BID, market.address, YES, fix(1, 6000), 6000, "43", 6, sender=tester.k2, value=fix('1', '6000')) == 0
    else:
        assert trade.publicFillBestOrder(BID, market.address, YES, fix(1), 6000, "43", 6, sender=tester.k2, value=fix('1', '6000')) == 0

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
    orderIDs = []
    numOrders = 5
    for i in range(numOrders):
        orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000 + i, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1, value=fix('1', 4000 - i))
        assert orderID
        orderIDs.append(orderID)

    # fill orders with cash using on-chain matcher
    price = 6000 + numOrders
    with PrintGasUsed(contractsFixture, "fill multiple asks", 0):
        assert trade.publicFillBestOrder(BID, market.address, YES, fix(numOrders), price, "43", 6, sender=tester.k2, value=fix(numOrders, price)) == 0

    for i in range(numOrders):
        orderID = orderIDs[i]
        assert orders.getAmount(orderID) == 0
        assert orders.getPrice(orderID) == 0
        assert orders.getOrderCreator(orderID) == longToHexString(0)
        assert orders.getOrderMoneyEscrowed(orderID) == 0
        assert orders.getOrderSharesEscrowed(orderID) == 0
        assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
        assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

@mark.parametrize('withSelf', [
    True,
    False
])
def test_take_best_order_with_shares_escrowed_buy_with_cash(withSelf, contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    orders = contractsFixture.contracts['Orders']
    completeSets = contractsFixture.contracts['CompleteSets']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))

    # buy complete sets
    sender = tester.k2 if withSelf else tester.k1
    account = tester.a2 if withSelf else tester.a1
    assert completeSets.publicBuyCompleteSets(market.address, fix(1), sender=sender, value=fix('1', '10000'))
    assert yesShareToken.balanceOf(account) == fix(1)

    # create order with shares
    orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=sender)
    assert orderID

    # fill order with cash using on-chain matcher
    with PrintGasUsed(contractsFixture, "buy shares escrowed order", 0):
        assert trade.publicFillBestOrder(BID, market.address, YES, fix(1), 6000, "43", 6, sender=tester.k2, value=fix('1', '6000')) == 0

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
            with PrintGasUsed(contractsFixture, "categoricalFill", 0):
                assert trade.publicFillBestOrder(BID, market.address, 0, fix(1), 6000, "43", 6, sender=tester.k2) == 0

    assert firstShareToken.balanceOf(tester.a1) == 0
    assert secondShareToken.balanceOf(tester.a1) == fix(1)
    assert thirdShareToken.balanceOf(tester.a1) == fix(1)

    assert firstShareToken.balanceOf(tester.a2) == fix(1)
    assert secondShareToken.balanceOf(tester.a2) == 0
    assert thirdShareToken.balanceOf(tester.a2) == 0

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

def test_trade_with_self(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(4), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '6000'))

    fillOrderID = None

    # fill best order
    orderFilledLog = {
        "filler": bytesToHexString(tester.a1),
        "numCreatorShares": 0,
        "numCreatorTokens": fix('4', '6000'),
        "numFillerShares": 0,
        "numFillerTokens": fix('4', '4000'),
        "marketCreatorFees": 0,
        "reporterFees": 0,
        "shareToken": market.getShareToken(YES),
        "tradeGroupId": stringToBytes("42"),
    }
    orderCreatedLog = {
        "creator": bytesToHexString(tester.a1),
        "shareToken": market.getShareToken(YES),
        "tradeGroupId": stringToBytes("42"),
    }
    with AssertLog(contractsFixture, "OrderFilled", orderFilledLog):
        with AssertLog(contractsFixture, "OrderCreated", orderCreatedLog):
            fillOrderID = trade.publicTrade(SHORT,market.address, YES, fix(5), 6000, "0", "0", tradeGroupID, 6, sender = tester.k1, value=fix('5', '4000'))

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

    assert orders.getAmount(fillOrderID) == fix(1)
    assert orders.getPrice(fillOrderID) == 6000
    assert orders.getOrderCreator(fillOrderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(fillOrderID) == fix(1, 4000)
    assert orders.getOrderSharesEscrowed(fillOrderID) == 0
    assert orders.getBetterOrderId(fillOrderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(fillOrderID) == longTo32Bytes(0)

@mark.parametrize('withTotalCost', [
    True,
    False
])
def test_trade_with_self_take_order_make_order(withTotalCost, contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create order
    createCost = fix('0.003', '6000')
    orderID = createOrder.publicCreateOrder(ASK, fix('0.003'), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=createCost)

    fillOrderID = None

    # fill best order
    takeCost = fix('1', '5000')
    if withTotalCost:
        fillOrderID = trade.publicTradeWithTotalCost(BID, market.address, YES, takeCost, 5000, "0", "0", tradeGroupID, 6, sender = tester.k1, value=takeCost)
    else:
        fillOrderID = trade.publicTrade(BID, market.address, YES, fix(1), 5000, "0", "0", tradeGroupID, 6, sender = tester.k1, value=takeCost)

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

    orderAmount = fix(1) - fix('0.003')
    assert orders.getAmount(fillOrderID) == orderAmount
    assert orders.getPrice(fillOrderID) == 5000
    assert orders.getOrderCreator(fillOrderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(fillOrderID) == fix('0.997', 5000)
    # Note that we never ended up with the original orders shares. The ETH escrowed for those was simply returned to us for this case.
    assert orders.getOrderSharesEscrowed(fillOrderID) == 0
    assert orders.getBetterOrderId(fillOrderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(fillOrderID) == longTo32Bytes(0)

@mark.parametrize('isMatch', [
    True,
    False
])
def test_create_order_after_exhausting_book(isMatch, contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    # create orders
    createCost = fix('1', '6000')
    orderID = createOrder.publicCreateOrder(ASK, fix('1'), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=createCost)
    if isMatch:
        createCost = fix('1', '5000')
        orderID2 = createOrder.publicCreateOrder(ASK, fix('1'), 5000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=createCost)
    else:
        createCost = fix('1', '3000')
        orderID2 = createOrder.publicCreateOrder(ASK, fix('1'), 7000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=createCost)

    fillOrderID = None

    # fill best order
    takeCost = fix('2', '6000')
    fillOrderID = trade.publicTrade(BID, market.address, YES, fix(2), 6000, "0", "0", tradeGroupID, 6, value=takeCost)

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

    if isMatch:
        assert orders.getAmount(orderID2) == 0
        assert orders.getPrice(orderID2) == 0
        assert orders.getOrderCreator(orderID2) == longToHexString(0)
        assert orders.getOrderMoneyEscrowed(orderID2) == 0
        assert orders.getOrderSharesEscrowed(orderID2) == 0
        assert orders.getBetterOrderId(orderID2) == longTo32Bytes(0)
        assert orders.getWorseOrderId(orderID2) == longTo32Bytes(0)
        assert fillOrderID == longTo32Bytes(1)
    else:
        orderAmount = fix(1)
        assert orders.getAmount(orderID2) == fix(1)
        assert orders.getAmount(fillOrderID) == orderAmount
        assert orders.getPrice(fillOrderID) == 6000
        assert orders.getOrderCreator(fillOrderID) == bytesToHexString(tester.a0)
        assert orders.getOrderMoneyEscrowed(fillOrderID) == fix(6000)
        assert orders.getOrderSharesEscrowed(fillOrderID) == 0
        assert orders.getBetterOrderId(fillOrderID) == longTo32Bytes(0)
        assert orders.getWorseOrderId(fillOrderID) == longTo32Bytes(0)

@mark.parametrize('useFill', [
    True,
    False
])
def test_take_best_order_with_shares_escrowed_buy_with_cash_by_ignoring_shares(useFill, contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    orders = contractsFixture.contracts['Orders']
    completeSets = contractsFixture.contracts['CompleteSets']
    firstShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(0))
    secondShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(1))

    # buy complete sets for both users
    numTicks = market.getNumTicks()
    assert completeSets.publicBuyCompleteSets(market.address, fix(1), sender=tester.k1, value=fix('1', numTicks))
    assert completeSets.publicBuyCompleteSets(market.address, fix(1), sender=tester.k2, value=fix('1', numTicks))
    assert firstShareToken.balanceOf(tester.a1) == firstShareToken.balanceOf(tester.a2) == fix(1)
    assert secondShareToken.balanceOf(tester.a1) == secondShareToken.balanceOf(tester.a2) == fix(1)

    # create order with shares
    orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    assert orderID

    # Since we're ignoring owned shares we need to put up the required cost of the fill
    with raises(TransactionFailed):
        if useFill:
            trade.publicFillBestOrder(BID, market.address, 0, fix(1), 6000, "43", 6, True, sender=tester.k2) == 0
        else:
            trade.publicTrade(BID, market.address, 0, fix(1), 6000, longTo32Bytes(0), longTo32Bytes(0), "43", 6, True, sender=tester.k2)

    # fill order with cash using on-chain matcher and ignoring owned shares
    if useFill:
        assert trade.publicFillBestOrder(BID, market.address, 0, fix(1), 6000, "43", 6, True, sender=tester.k2, value=fix(6000)) == 0
    else:
        assert trade.publicTrade(BID, market.address, 0, fix(1), 6000, longTo32Bytes(0), longTo32Bytes(0), "43", 6, True, sender=tester.k2, value=fix(6000))

    assert firstShareToken.balanceOf(tester.a1) == 0
    assert secondShareToken.balanceOf(tester.a1) == fix(1)

    assert firstShareToken.balanceOf(tester.a2) == fix(2)
    assert secondShareToken.balanceOf(tester.a2) == fix(1)

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
