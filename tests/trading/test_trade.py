#!/usr/bin/env python

from ethereum.tools import tester
from utils import longToHexString, bytesToLong, bytesToHexString, fix, captureFilteredLogs

NO = 0
YES = 1

BID = 1
ASK = 2

# complete set log type
BUY = 1
SELL = 2

def test_one_bid_on_books_buy_full_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderId = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicSell(market.address, YES, fix('1.2'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0L,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0L,
            "numOutcomes": 2L,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BID,
            "orderId": longToHexString(orderId),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.6'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.4'),
        },
    ]
    assert orders.getOrder(orderId, BID, market.address, YES) == [0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L]
    assert fillOrderId == 0

def test_one_bid_on_books_buy_partial_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderId = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix('0.7', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('0.7', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicSell(market.address, YES, fix('0.7'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('0.7'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BID,
            "orderId": longToHexString(orderId),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('0.7', '0.6'),
            "takerShares": 0,
            "takerTokens": fix('0.7', '0.4'),
        },
    ]
    assert orders.getOrder(orderId, BID, market.address, YES) == [fix('0.5'), fix('0.6'), bytesToLong(tester.a1), fix('0.5', '0.6'), 0, 0, 0, 0L]
    assert fillOrderId == 0

def test_one_bid_on_books_buy_excess_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderId = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix('1.5', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    assert cash.approve(makeOrder.address, fix('0.3', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicSell(market.address, YES, fix('1.5'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BID,
            "orderId": longToHexString(orderId),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.6'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.4'),
        },
        {
            "_event_type": "MakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderID": longToHexString(fillOrderId),
            "fxpPrice": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "fxpAmount": fix('0.3'),
            "fxpMoneyEscrowed": fix('0.3', '0.4'),
            "fxpSharesEscrowed": 0,
            "tradeGroupID": 42,
        },
    ]
    assert orders.getOrder(orderId, BID, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert orders.getOrder(fillOrderId, ASK, market.address, YES) == [fix('0.3'), fix('0.6'), bytesToLong(tester.a2), fix('0.3', '0.4'), 0, 0, 0, 0]

def test_two_bids_on_books_buy_both(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderId1 = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    # create order 2
    assert cash.publicDepositEther(value=fix('0.3', '0.6'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.3', '0.6'), sender = tester.k3)
    orderId2 = makeOrder.publicMakeOrder(BID, fix('0.3'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k3)

    # take best order
    assert cash.publicDepositEther(value=fix('1.5', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.5', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicSell(market.address, YES, fix('1.5'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BID,
            "orderId": longToHexString(orderId1),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.6'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.4'),
        },
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('0.3'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BID,
            "orderId": longToHexString(orderId2),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a3),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('0.3', '0.6'),
            "takerShares": 0,
            "takerTokens": fix('0.3', '0.4'),
        },
    ]
    assert orders.getOrder(orderId1, BID, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert orders.getOrder(orderId2, BID, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert fillOrderId == 0

def test_two_bids_on_books_buy_full_and_partial(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderId1 = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    # create order 2
    assert cash.publicDepositEther(value=fix('0.7', '0.6'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.7', '0.6'), sender = tester.k3)
    orderId2 = makeOrder.publicMakeOrder(BID, fix('0.7'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k3)

    # take best order
    assert cash.publicDepositEther(value=fix('1.5', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.5', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicSell(market.address, YES, fix('1.5'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BID,
            "orderId": longToHexString(orderId1),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.6'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.4'),
        },
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('0.3'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BID,
            "orderId": longToHexString(orderId2),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a3),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('0.3', '0.6'),
            "takerShares": 0,
            "takerTokens": fix('0.3', '0.4'),
        },
    ]
    assert orders.getOrder(orderId1, BID, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert orders.getOrder(orderId2, BID, market.address, YES) == [fix('0.4'), fix('0.6'), bytesToLong(tester.a3), fix('0.4', '0.6'), 0, 0, 0, 0]
    assert fillOrderId == 0

def test_two_bids_on_books_buy_one_full_then_make(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderId1 = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    # create order 2
    assert cash.publicDepositEther(value=fix('0.7', '0.6'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.7', '0.6'), sender = tester.k3)
    orderId2 = makeOrder.publicMakeOrder(BID, fix('0.7'), fix('0.5'), market.address, YES, 0, 0, 42, sender = tester.k3)

    # take/make
    assert cash.publicDepositEther(value=fix('1.5', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    assert cash.approve(makeOrder.address, fix('0.3', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicSell(market.address, YES, fix('1.5'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BID,
            "orderId": longToHexString(orderId1),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.6'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.4'),
        },
        {
            "_event_type": "MakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderID": longToHexString(fillOrderId),
            "fxpPrice": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "fxpAmount": fix('0.3'),
            "fxpMoneyEscrowed": fix('0.3', '0.4'),
            "fxpSharesEscrowed": 0,
            "tradeGroupID": 42,
        },
    ]
    assert orders.getOrder(orderId1, BID, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert orders.getOrder(orderId2, BID, market.address, YES) == [fix('0.7'), fix('0.5'), bytesToLong(tester.a3), fix('0.7', '0.5'), 0, 0, 0, 0]
    assert orders.getOrder(fillOrderId, ASK, market.address, YES) == [fix('0.3'), fix('0.6'), bytesToLong(tester.a2), fix('0.3', '0.4'), 0, 0, 0, 0]

def test_one_ask_on_books_buy_full_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderId = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicBuy(market.address, YES, fix('1.2'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderId": longToHexString(orderId),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.6'),
        },
    ]
    assert orders.getOrder(orderId, ASK, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert fillOrderId == 0

def test_one_ask_on_books_buy_partial_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderId = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix('0.7', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('0.7', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicBuy(market.address, YES, fix('0.7'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('0.7'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderId": longToHexString(orderId),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('0.7', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('0.7', '0.6'),
        },
    ]
    assert orders.getOrder(orderId, ASK, market.address, YES) == [fix('0.5'), fix('0.6'), bytesToLong(tester.a1), fix('0.5', '0.4'), 0, 0, 0, 0]
    assert fillOrderId == 0

def test_one_ask_on_books_buy_excess_order(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderId = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix('1.5', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(makeOrder.address, fix('0.3', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicBuy(market.address, YES, fix('1.5'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderId": longToHexString(orderId),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.6'),
        },
        {
            "_event_type": "MakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BUY,
            "orderID": longToHexString(fillOrderId),
            "fxpPrice": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "fxpAmount": fix('0.3'),
            "fxpMoneyEscrowed": fix('0.3', '0.6'),
            "fxpSharesEscrowed": 0,
            "tradeGroupID": 42,
        },
    ]
    assert orders.getOrder(orderId, ASK, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert orders.getOrder(fillOrderId, BID, market.address, YES) == [fix('0.3'), fix('0.6'), bytesToLong(tester.a2), fix('0.3', '0.6'), 0, 0, 0, 0]

def test_two_asks_on_books_buy_both(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderId1 = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    # create order 2
    assert cash.publicDepositEther(value=fix('0.3', '0.4'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.3', '0.4'), sender = tester.k3)
    orderId2 = makeOrder.publicMakeOrder(ASK, fix('0.3'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k3)

    # take best order
    assert cash.publicDepositEther(value=fix('1.5', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.5', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicBuy(market.address, YES, fix('1.5'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderId": longToHexString(orderId1),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.6'),
        },
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('0.3'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderId": longToHexString(orderId2),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a3),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('0.3', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('0.3', '0.6'),
        },
    ]
    assert orders.getOrder(orderId1, ASK, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert orders.getOrder(orderId2, ASK, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert fillOrderId == 0

def test_two_asks_on_books_buy_full_and_partial(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderId1 = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    # create order 2
    assert cash.publicDepositEther(value=fix('0.7', '0.4'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.7', '0.4'), sender = tester.k3)
    orderId2 = makeOrder.publicMakeOrder(ASK, fix('0.7'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k3)

    # take best order
    assert cash.publicDepositEther(value=fix('1.5', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.5', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicBuy(market.address, YES, fix('1.5'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderId": longToHexString(orderId1),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.6'),
        },
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('0.3'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderId": longToHexString(orderId2),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a3),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('0.3', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('0.3', '0.6'),
        },
    ]
    assert orders.getOrder(orderId1, ASK, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert orders.getOrder(orderId2, ASK, market.address, YES) == [fix('0.4'), fix('0.6'), bytesToLong(tester.a3), fix('0.4', '0.4'), 0, 0, 0, 0]
    assert fillOrderId == 0

def test_two_asks_on_books_buy_one_full_then_make(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    trade = contractsFixture.contracts['trade']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order 1
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderId1 = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    # create order 2
    assert cash.publicDepositEther(value=fix('0.7', '0.4'), sender = tester.k3)
    assert cash.approve(makeOrder.address, fix('0.7', '0.4'), sender = tester.k3)
    orderId2 = makeOrder.publicMakeOrder(ASK, fix('0.7'), fix('0.7'), market.address, YES, 0, 0, 42, sender = tester.k3)

    # take/make
    assert cash.publicDepositEther(value=fix('1.5', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(makeOrder.address, fix('0.3', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderId = trade.publicBuy(market.address, YES, fix('1.5'), fix('0.6'), 42, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderId": longToHexString(orderId1),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.6'),
        },
        {
            "_event_type": "MakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BUY,
            "orderID": longToHexString(fillOrderId),
            "fxpPrice": fix('0.6'),
            "sender": bytesToHexString(tester.a2),
            "fxpAmount": fix('0.3'),
            "fxpMoneyEscrowed": fix('0.3', '0.6'),
            "fxpSharesEscrowed": 0,
            "tradeGroupID": 42,
        },
    ]
    assert orders.getOrder(orderId1, ASK, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert orders.getOrder(orderId2, ASK, market.address, YES) == [fix('0.7'), fix('0.7'), bytesToLong(tester.a3), fix('0.7', '0.3'), 0, 0, 0, 0]
    assert orders.getOrder(fillOrderId, BID, market.address, YES) == [fix('0.3'), fix('0.6'), bytesToLong(tester.a2), fix('0.3', '0.6'), 0, 0, 0, 0]
