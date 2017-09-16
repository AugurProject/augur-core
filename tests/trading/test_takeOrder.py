#!/usr/bin/env python

from ethereum.tools import tester
from utils import fix, bytesToHexString, captureFilteredLogs, longTo32Bytes, longToHexString
from constants import BID, ASK, YES, NO


def test_publicTakeOrder_bid(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42
    logs = []

    # create order
    assert cash.depositEther(value=fix('2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('2', '0.6'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('2', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('2', '0.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = takeOrder.publicTakeOrder(orderID, 2, tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "amount": 2,
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
            "makerTokens": int(fix('2', '0.6')),
            "takerShares": 0,
            "takerTokens": int(fix('2', '0.4')),
            "tradeGroupId": 42,
        },
    ]
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == 0

def test_publicTakeOrder_ask(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42
    logs = []

    # create order
    assert cash.depositEther(value=fix('2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('2', '0.4'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(ASK, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('2', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('2', '0.6'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = takeOrder.publicTakeOrder(orderID, 2, tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "amount": 2,
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
            "makerTokens": fix('2', '0.4'),
            "takerShares": 0,
            "takerTokens": fix('2', '0.6'),
            "tradeGroupId": tradeGroupID
        },
    ]
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == 0

def test_publicTakeOrder_bid_scalar(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['MakeOrder']
    takeOrder = contractsFixture.contracts['TakeOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.scalarMarket
    tradeGroupID = 42
    logs = []

    # create order
    assert cash.depositEther(value=fix('2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('2', '0.6'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1)

    # take best order
    assert cash.depositEther(value=fix('2', '39.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('2', '39.4'), sender = tester.k2)
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = takeOrder.publicTakeOrder(orderID, 2, tradeGroupID, sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": takeOrder.address,
            "amount": 2,
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
            "makerTokens": int(fix('2', '0.6')),
            "takerShares": 0,
            "takerTokens": int(fix('2', '39.4')),
            "tradeGroupId": 42,
        },
    ]
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == 0
