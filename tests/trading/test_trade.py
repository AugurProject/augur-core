#!/usr/bin/env python

from ethereum.tools import tester
from utils import longTo32Bytes, longToHexString, bytesToHexString, fix, captureFilteredLogs
from constants import BID, ASK, YES, NO


def test_one_bid_on_books_buy_full_order(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42L
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, 2, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('2', '0.4'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            u"sender": fillOrder.address,
            u"amount": 2,
            u"numOutcomes": 2L,
            u"market": market.address
        },
        {
            "_event_type": "FillOrder",
            u"market": market.address,
            u"outcome": YES,
            u"orderType": BID,
            u"orderId": orderID,
            u"price": fix('0.6'),
            u"creator": bytesToHexString(tester.a1),
            u"filler": bytesToHexString(tester.a2),
            u"creatorShares": 0L,
            u"creatorTokens": fix('2', '0.6'),
            u"fillerShares": 0L,
            u"fillerTokens": fix('2', '0.4'),
            u"tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID) == [0L, 0L, longToHexString(0), 0L, 0L, longTo32Bytes(0), longTo32Bytes(0), 0L]
    assert fillOrderID == longTo32Bytes(1)


def test_one_bid_on_books_buy_partial_order(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42L
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('2', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, 1, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('1', '0.4'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 1,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('1', '0.6'),
            "fillerShares": 0L,
            "fillerTokens": fix('1', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID) == [1, fix('0.6'), bytesToHexString(tester.a1), fix('1', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0L]
    assert fillOrderID == longTo32Bytes(1)


def test_one_bid_on_books_buy_excess_order(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42L
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(BID, 4, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, 5, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('5', '0.4'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 4,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('4', '0.6'),
            "fillerShares": 0L,
            "fillerTokens": fix('4', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "CreateOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": fillOrderID,
            "price": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "amount": 1,
            "moneyEscrowed": fix('1', '0.4'),
            "sharesEscrowed": 0L,
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [1, fix('0.6'), bytesToHexString(tester.a2), fix('1', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]

def test_two_bids_on_books_buy_both(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, 4, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('4', '0.6'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, 1, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('1', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, 5, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('5', '0.4'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 4,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID1,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('4', '0.6'),
            "fillerShares": 0L,
            "fillerTokens": fix('4', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 1,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID2,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a3),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('1', '0.6'),
            "fillerShares": 0L,
            "fillerTokens": fix('1', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_bids_on_books_buy_full_and_partial(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.6'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, 7, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '0.6'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.4'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 12,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID1,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('12', '0.6'),
            "fillerShares": 0L,
            "fillerTokens": fix('12', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 3,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID2,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a3),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('3', '0.6'),
            "fillerShares": 0L,
            "fillerTokens": fix('3', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [4, fix('0.6'), bytesToHexString(tester.a3), fix('4', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_bids_on_books_buy_one_full_then_create(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(BID, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.6'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(BID, 7, fix('0.5'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '0.6'))

    # fill/create
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.4'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 12,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID1,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('12', '0.6'),
            "fillerShares": 0L,
            "fillerTokens": fix('12', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "CreateOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": fillOrderID,
            "price": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "amount": 3,
            "moneyEscrowed": fix('3', '0.4'),
            "sharesEscrowed": 0L,
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [7, fix('0.5'), bytesToHexString(tester.a3), fix('7', '0.5'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [3, fix('0.6'), bytesToHexString(tester.a2), fix('3', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]

def test_one_ask_on_books_buy_full_order(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, 12, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('12', '0.6'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 12,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('12', '0.4'),
            "fillerShares": 0L,
            "fillerTokens": fix('12', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_one_ask_on_books_buy_partial_order(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, 7, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('7', '0.6'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 7,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('7', '0.4'),
            "fillerShares": 0L,
            "fillerTokens": fix('7', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
    ]


    assert ordersFetcher.getOrder(orderID) == [5, fix('0.6'), bytesToHexString(tester.a1), fix('5', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_one_ask_on_books_buy_excess_order(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    orderID = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.6'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 12,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('12', '0.4'),
            "fillerShares": 0L,
            "fillerTokens": fix('12', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "CreateOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": fillOrderID,
            "price": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "amount": 3,
            "moneyEscrowed": fix('3', '0.6'),
            "sharesEscrowed": 0L,
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [3, fix('0.6'), bytesToHexString(tester.a2), fix('3', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]

def test_two_asks_on_books_buy_both(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, 3, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('3', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.6'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 12,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID1,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('12', '0.4'),
            "fillerShares": 0L,
            "fillerTokens": fix('12', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 3,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID2,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a3),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('3', '0.4'),
            "fillerShares": 0L,
            "fillerTokens": fix('3', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_asks_on_books_buy_full_and_partial(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, 7, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '0.4'))

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.6'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 12,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID1,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('12', '0.4'),
            "fillerShares": 0L,
            "fillerTokens": fix('12', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 3,
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID2,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a3),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('3', '0.4'),
            "fillerShares": 0L,
            "fillerTokens": fix('3', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [4, fix('0.6'), bytesToHexString(tester.a3), fix('4', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_asks_on_books_buy_one_full_then_create(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    trade = contractsFixture.contracts['Trade']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    orderID1 = createOrder.publicCreateOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=fix('12', '0.4'))
    # create order 2
    orderID2 = createOrder.publicCreateOrder(ASK, 7, fix('0.7'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3, value=fix('7', '0.4'))

    # fill/create
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, 15, fix('0.6'), tradeGroupID, sender = tester.k2, value=fix('15', '0.6'))

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "market": market.address,
            "amount": 12,
            "numOutcomes": 2L,
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID1,
            "price": fix('0.6'),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0L,
            "creatorTokens": fix('12', '0.4'),
            "fillerShares": 0L,
            "fillerTokens": fix('12', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "CreateOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": fillOrderID,
            "price": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "amount": 3,
            "moneyEscrowed": fix('3', '0.6'),
            "sharesEscrowed": 0L,
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [7, fix('0.7'), bytesToHexString(tester.a3), fix('7', '0.3'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [3, fix('0.6'), bytesToHexString(tester.a2), fix('3', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
