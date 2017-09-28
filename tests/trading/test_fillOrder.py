#!/usr/bin/env python

from ethereum.tools import tester
from utils import fix, bytesToHexString, captureFilteredLogs, longTo32Bytes, longToHexString
from constants import BID, ASK, YES, NO


def test_publicFillOrder_bid(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42
    logs = []

    initialMakerETH = contractsFixture.utils.getETHBalance(tester.a1)
    initialFillerETH = contractsFixture.utils.getETHBalance(tester.a2)
    creatorCost = fix('2', '0.6')
    fillerCost = fix('2', '0.4')

    # create order
    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = fillOrder.publicFillOrder(orderID, 2, tradeGroupID, sender = tester.k2, value=fillerCost)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 2,
            "numOutcomes": 2,
            "market": market.address,
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID,
            "price": int(fix('0.6')),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0,
            "creatorTokens": int(creatorCost),
            "fillerShares": 0,
            "fillerTokens": int(fillerCost),
            "tradeGroupId": 42,
        },
    ]

    assert contractsFixture.utils.getETHBalance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.utils.getETHBalance(tester.a2) == initialFillerETH - fillerCost
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == 0

def test_publicFillOrder_ask(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    market = contractsFixture.binaryMarket
    tradeGroupID = 42
    logs = []

    initialMakerETH = contractsFixture.utils.getETHBalance(tester.a1)
    initialFillerETH = contractsFixture.utils.getETHBalance(tester.a2)
    creatorCost = fix('2', '0.4')
    fillerCost = fix('2', '0.6')

    # create order
    orderID = createOrder.publicCreateOrder(ASK, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = fillOrder.publicFillOrder(orderID, 2, tradeGroupID, sender = tester.k2, value=fillerCost)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 2,
            "numOutcomes": 2,
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
            "creatorShares": 0,
            "creatorTokens": creatorCost,
            "fillerShares": 0,
            "fillerTokens": fillerCost,
            "tradeGroupId": tradeGroupID
        },
    ]

    assert contractsFixture.utils.getETHBalance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.utils.getETHBalance(tester.a2) == initialFillerETH - fillerCost
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == 0

def test_publicFillOrder_bid_scalar(contractsFixture):
    cash = contractsFixture.cash
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    # We're testing the scalar market because it has a different numTicks than 10**18 as the other do. In particular it's numTicks is 40*18**18
    market = contractsFixture.scalarMarket
    tradeGroupID = 42
    logs = []

    initialMakerETH = contractsFixture.utils.getETHBalance(tester.a1)
    initialFillerETH = contractsFixture.utils.getETHBalance(tester.a2)
    creatorCost = fix('2', '0.6')
    fillerCost = fix('2', '39.4')

    # create order
    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    fillOrderID = fillOrder.publicFillOrder(orderID, 2, tradeGroupID, sender = tester.k2, value=fillerCost)

    # assert
    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": fillOrder.address,
            "amount": 2,
            "numOutcomes": 2,
            "market": market.address,
        },
        {
            "_event_type": "FillOrder",
            "market": market.address,
            "outcome": YES,
            "orderType": BID,
            "orderId": orderID,
            "price": int(fix('0.6')),
            "creator": bytesToHexString(tester.a1),
            "filler": bytesToHexString(tester.a2),
            "creatorShares": 0,
            "creatorTokens": int(creatorCost),
            "fillerShares": 0,
            "fillerTokens": int(fillerCost),
            "tradeGroupId": 42,
        },
    ]

    assert contractsFixture.utils.getETHBalance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.utils.getETHBalance(tester.a2) == initialFillerETH - fillerCost
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == 0
