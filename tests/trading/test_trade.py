#!/usr/bin/env python

from ethereum.tools import tester
from utils import longTo32Bytes, longToHexString, bytesToHexString, fix, captureFilteredLogs
from constants import BID, ASK, YES, NO


def test_one_bid_on_books_buy_full_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42L
    logs = []

    # create order
    assert cash.depositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('1.2', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, fix('1.2'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            u"sender": takeOrder.address,
            u"fxpAmount": fix('1.2'),
            u"numOutcomes": 2L,
            u"market": market.address
        },
        {
            "_event_type": "TakeOrder",
            u"market": market.address,
            u"outcome": YES,
            u"orderType": BID,
            u"orderId": orderID,
            u"price": fix('0.6'),
            u"maker": bytesToHexString(tester.a1),
            u"taker": bytesToHexString(tester.a2),
            u"makerShares": 0L,
            u"makerTokens": fix('1.2', '0.6'),
            u"takerShares": 0L,
            u"takerTokens": fix('1.2', '0.4'),
            u"tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID) == [0L, 0L, longToHexString(0), 0L, 0L, longTo32Bytes(0), longTo32Bytes(0), 0L]
    assert fillOrderID == longTo32Bytes(1)


def test_one_bid_on_books_buy_partial_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42L
    logs = []

    # create order
    assert cash.depositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('0.7', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('0.7', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, fix('0.7'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('0.7'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('0.7', '0.6'),
            "takerShares": 0L,
            "takerTokens": fix('0.7', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID) == [fix('0.5'), fix('0.6'), bytesToHexString(tester.a1), fix('0.5', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0L]
    assert fillOrderID == longTo32Bytes(1)


def test_one_bid_on_books_buy_excess_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42L
    logs = []

    # create order
    assert cash.depositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('1.5', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    assert cash.approve(makeOrder.address, fix('0.3', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, fix('1.5'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('1.2'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('1.2', '0.6'),
            "takerShares": 0L,
            "takerTokens": fix('1.2', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "MakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": fillOrderID,
            "price": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "fxpAmount": fix('0.3'),
            "fxpMoneyEscrowed": fix('0.3', '0.4'),
            "fxpSharesEscrowed": 0L,
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [fix('0.3'), fix('0.6'), bytesToHexString(tester.a2), fix('0.3', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]

def test_two_bids_on_books_buy_both(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.depositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderID1 = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)
    # create order 2
    assert cash.depositEther(value=fix('0.3', '0.6'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.3', '0.6'), sender = tester.k3)
    orderID2 = makeOrder.publicMakeOrder(BID, fix('0.3'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3)

    # take best order
    assert cash.depositEther(value=fix('1.5', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.5', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, fix('1.5'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('1.2'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID1,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('1.2', '0.6'),
            "takerShares": 0L,
            "takerTokens": fix('1.2', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('0.3'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID2,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a3),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('0.3', '0.6'),
            "takerShares": 0L,
            "takerTokens": fix('0.3', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_bids_on_books_buy_full_and_partial(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.depositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderID1 = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)
    # create order 2
    assert cash.depositEther(value=fix('0.7', '0.6'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.7', '0.6'), sender = tester.k3)
    orderID2 = makeOrder.publicMakeOrder(BID, fix('0.7'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3)

    # take best order
    assert cash.depositEther(value=fix('1.5', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.5', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, fix('1.5'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('1.2'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID1,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('1.2', '0.6'),
            "takerShares": 0L,
            "takerTokens": fix('1.2', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('0.3'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID2,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a3),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('0.3', '0.6'),
            "takerShares": 0L,
            "takerTokens": fix('0.3', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [fix('0.4'), fix('0.6'), bytesToHexString(tester.a3), fix('0.4', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_bids_on_books_buy_one_full_then_make(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.depositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderID1 = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)
    # create order 2
    assert cash.depositEther(value=fix('0.7', '0.6'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.7', '0.6'), sender = tester.k3)
    orderID2 = makeOrder.publicMakeOrder(BID, fix('0.7'), fix('0.5'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3)

    # take/make
    assert cash.depositEther(value=fix('1.5', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    assert cash.approve(makeOrder.address, fix('0.3', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicSell(market.address, YES, fix('1.5'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('1.2'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID1,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('1.2', '0.6'),
            "takerShares": 0L,
            "takerTokens": fix('1.2', '0.4'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "MakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": fillOrderID,
            "price": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "fxpAmount": fix('0.3'),
            "fxpMoneyEscrowed": fix('0.3', '0.4'),
            "fxpSharesEscrowed": 0L,
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [fix('0.7'), fix('0.5'), bytesToHexString(tester.a3), fix('0.7', '0.5'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [fix('0.3'), fix('0.6'), bytesToHexString(tester.a2), fix('0.3', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]

def test_one_ask_on_books_buy_full_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.depositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix('1.2'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('1.2'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0L,
            "takerTokens": fix('1.2', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_one_ask_on_books_buy_partial_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.depositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('0.7', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('0.7', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix('0.7'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('0.7'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('0.7', '0.4'),
            "takerShares": 0L,
            "takerTokens": fix('0.7', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
    ]


    assert ordersFetcher.getOrder(orderID) == [fix('0.5'), fix('0.6'), bytesToHexString(tester.a1), fix('0.5', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_one_ask_on_books_buy_excess_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.depositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('1.5', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(makeOrder.address, fix('0.3', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix('1.5'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('1.2'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0L,
            "takerTokens": fix('1.2', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "MakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": fillOrderID,
            "price": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "fxpAmount": fix('0.3'),
            "fxpMoneyEscrowed": fix('0.3', '0.6'),
            "fxpSharesEscrowed": 0L,
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [fix('0.3'), fix('0.6'), bytesToHexString(tester.a2), fix('0.3', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]

def test_two_asks_on_books_buy_both(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.depositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderID1 = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)
    # create order 2
    assert cash.depositEther(value=fix('0.3', '0.4'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.3', '0.4'), sender = tester.k3)
    orderID2 = makeOrder.publicMakeOrder(ASK, fix('0.3'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3)

    # take best order
    assert cash.depositEther(value=fix('1.5', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.5', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix('1.5'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('1.2'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID1,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0L,
            "takerTokens": fix('1.2', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('0.3'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID2,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a3),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('0.3', '0.4'),
            "takerShares": 0L,
            "takerTokens": fix('0.3', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_asks_on_books_buy_full_and_partial(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.depositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderID1 = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)
    # create order 2
    assert cash.depositEther(value=fix('0.7', '0.4'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.7', '0.4'), sender = tester.k3)
    orderID2 = makeOrder.publicMakeOrder(ASK, fix('0.7'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3)

    # take best order
    assert cash.depositEther(value=fix('1.5', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.5', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix('1.5'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('1.2'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID1,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0L,
            "takerTokens": fix('1.2', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "fxpAmount": fix('0.3'),
            "numOutcomes": 2L,
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID2,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a3),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('0.3', '0.4'),
            "takerShares": 0L,
            "takerTokens": fix('0.3', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
    ]

    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [fix('0.4'), fix('0.6'), bytesToHexString(tester.a3), fix('0.4', '0.4'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == longTo32Bytes(1)

def test_two_asks_on_books_buy_one_full_then_make(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    trade = contractsFixture.contracts['Trade']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = 42L
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.depositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderID1 = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)
    # create order 2
    assert cash.depositEther(value=fix('0.7', '0.4'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.7', '0.4'), sender = tester.k3)
    orderID2 = makeOrder.publicMakeOrder(ASK, fix('0.7'), fix('0.7'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k3)

    # take/make
    assert cash.depositEther(value=fix('1.5', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(makeOrder.address, fix('0.3', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = trade.publicBuy(market.address, YES, fix('1.5'), fix('0.6'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "market": market.address,
            "fxpAmount": fix('1.2'),
            "numOutcomes": 2L,
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": ASK,
            "orderId": orderID1,
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0L,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0L,
            "takerTokens": fix('1.2', '0.6'),
            "tradeGroupId": tradeGroupID,
        },
        {
            "_event_type": "MakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": fillOrderID,
            "price": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "fxpAmount": fix('0.3'),
            "fxpMoneyEscrowed": fix('0.3', '0.6'),
            "fxpSharesEscrowed": 0L,
            "tradeGroupId": tradeGroupID,
        },
    ]
    assert ordersFetcher.getOrder(orderID1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(orderID2) == [fix('0.7'), fix('0.7'), bytesToHexString(tester.a3), fix('0.7', '0.3'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert ordersFetcher.getOrder(fillOrderID) == [fix('0.3'), fix('0.6'), bytesToHexString(tester.a2), fix('0.3', '0.6'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]
