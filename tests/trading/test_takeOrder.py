#!/usr/bin/env python

from ethereum.tools import tester
from utils import fix, longToHexString, bytesToHexString, captureFilteredLogs

BID = 1
ASK = 2

NO = 0
YES = 1

BUY = 1
SELL = 2

def test_publicTakeOrder_bid(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    ordersFetcher = contractsFixture.contracts['ordersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = takeOrder.publicTakeOrder(orderID, BID, market.address, YES, fix('1.2'), tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": int(fix('1.2')),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": market.address,
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "type": BID,
            "orderID": longToHexString(orderID),
            "price": int(fix('0.6')),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": int(fix('1.2', '0.6')),
            "takerShares": 0,
            "takerTokens": int(fix('1.2', '0.4')),
            "tradeGroupID": 42,
        },
    ]
    assert ordersFetcher.getOrder(orderID, BID, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert fillOrderID == 0

def test_publicTakeOrder_ask(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    ordersFetcher = contractsFixture.contracts['ordersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = takeOrder.publicTakeOrder(orderID, ASK, market.address, YES, fix('1.2'), tradeGroupID, sender = tester.k2)

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
            "market": market.address
        },
        {
            "_event_type": "TakeOrder",
            "market": market.address,
            "outcome": YES,
            "type": ASK,
            "orderID": longToHexString(orderID),
            "price": fix('0.6'),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix('1.2', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('1.2', '0.6'),
            "tradeGroupID": tradeGroupID
        },
    ]
    assert ordersFetcher.getOrder(orderID, BID, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert fillOrderID == 0
