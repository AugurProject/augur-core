#!/usr/bin/env python

from ethereum.tools import tester
from utils import fix, bytesToHexString, captureFilteredLogs

BID = 1
ASK = 2

NO = 0
YES = 1

BUY = 1
SELL = 2

ZEROED_ORDER_ID = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

def test_publicTakeOrder_bid(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42
    logs = []

    # create order
    assert cash.depositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, ZEROED_ORDER_ID, ZEROED_ORDER_ID, tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('1.2', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = takeOrder.publicTakeOrder(orderID, BID, market.address, YES, fix('1.2'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": takeOrder.address,
            "reportingFee": 0,
            "orderType": BUY,
            "fxpAmount": int(fix('1.2')),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": market.address,
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID,
            "price": int(fix('0.6')),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": int(fix('1.2', '0.6')),
            "takerShares": 0,
            "takerTokens": int(fix('1.2', '0.4')),
            "tradeGroupId": 42,
        },
    ]
    assert ordersFetcher.getOrder(orderID, BID, market.address, YES) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]
    assert fillOrderID == 0

def test_publicTakeOrder_ask(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42
    logs = []

    # create order
    assert cash.depositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, ZEROED_ORDER_ID, ZEROED_ORDER_ID, tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = takeOrder.publicTakeOrder(orderID, ASK, market.address, YES, fix('1.2'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": takeOrder.address,
            "reportingFee": 0,
            "orderType": BUY,
            "fxpAmount": fix('1.2'),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
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
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.6'),
            "tradeGroupId": tradeGroupID
        },
    ]
    assert ordersFetcher.getOrder(orderID, BID, market.address, YES) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]
    assert fillOrderID == 0
