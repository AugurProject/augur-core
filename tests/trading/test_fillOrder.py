#!/usr/bin/env python

from ethereum.tools import tester
from utils import fix, bytesToHexString, captureFilteredLogs, longTo32Bytes, longToHexString
from constants import BID, ASK, YES, NO


def test_publicFillOrder_bid(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    tradeGroupID = 42
    logs = []

    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    creatorCost = fix('2', '0.6')
    fillerCost = fix('2', '0.4')

    # create order
    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, universe, logs)
    fillOrderID = fillOrder.publicFillOrder(orderID, 2, tradeGroupID, sender = tester.k2, value=fillerCost)

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "BuyCompleteSets"
    assert logs[0]["sender"] == fillOrder.address
    assert logs[0]["amount"] == 2
    assert logs[0]["numOutcomes"] == 2
    assert logs[0]["market"] == market.address

    assert logs[1]["_event_type"] == "OrderFilled"
    assert logs[1]["creator"] == bytesToHexString(tester.a1)
    assert logs[1]["filler"] == bytesToHexString(tester.a2)
    assert logs[1]["numCreatorShares"] == 0
    assert logs[1]["numCreatorTokens"] == creatorCost
    assert logs[1]["numFillerShares"] == 0
    assert logs[1]["numFillerTokens"] == fillerCost
    assert logs[1]["price"] == fix('0.6')
    assert logs[1]["settlementFees"] == 0
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH - fillerCost
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == 0

def test_publicFillOrder_ask(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    tradeGroupID = 42
    logs = []

    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    creatorCost = fix('2', '0.4')
    fillerCost = fix('2', '0.6')

    # create order
    orderID = createOrder.publicCreateOrder(ASK, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, universe, logs)
    fillOrderID = fillOrder.publicFillOrder(orderID, 2, tradeGroupID, sender = tester.k2, value=fillerCost)

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "BuyCompleteSets"
    assert logs[0]["sender"] == fillOrder.address
    assert logs[0]["amount"] == 2
    assert logs[0]["numOutcomes"] == 2
    assert logs[0]["market"] == market.address

    assert logs[1]["_event_type"] == "OrderFilled"
    assert logs[1]["creator"] == bytesToHexString(tester.a1)
    assert logs[1]["filler"] == bytesToHexString(tester.a2)
    assert logs[1]["numCreatorShares"] == 0
    assert logs[1]["numCreatorTokens"] == creatorCost
    assert logs[1]["numFillerShares"] == 0
    assert logs[1]["numFillerTokens"] == fillerCost
    assert logs[1]["price"] == fix('0.6')
    assert logs[1]["settlementFees"] == 0
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH - fillerCost
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == 0

def test_publicFillOrder_bid_scalar(contractsFixture, cash, scalarMarket, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    # We're testing the scalar market because it has a different numTicks than 10**18 as the other do. In particular it's numTicks is 40*18**18
    market = scalarMarket
    tradeGroupID = 42
    logs = []

    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    creatorCost = fix('2', '0.6')
    fillerCost = fix('2', '39.4')

    # create order
    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, universe, logs)
    fillOrderID = fillOrder.publicFillOrder(orderID, 2, tradeGroupID, sender = tester.k2, value=fillerCost)

    assert len(logs) == 2

    assert logs[0]["_event_type"] == "BuyCompleteSets"
    assert logs[0]["sender"] == fillOrder.address
    assert logs[0]["amount"] == 2
    assert logs[0]["numOutcomes"] == 2
    assert logs[0]["market"] == market.address

    assert logs[1]["_event_type"] == "OrderFilled"
    assert logs[1]["creator"] == bytesToHexString(tester.a1)
    assert logs[1]["filler"] == bytesToHexString(tester.a2)
    assert logs[1]["numCreatorShares"] == 0
    assert logs[1]["numCreatorTokens"] == creatorCost
    assert logs[1]["numFillerShares"] == 0
    assert logs[1]["numFillerTokens"] == fillerCost
    assert logs[1]["price"] == fix('0.6')
    assert logs[1]["settlementFees"] == 0
    assert logs[1]["shareToken"] == market.getShareToken(YES)
    assert logs[1]["tradeGroupId"] == 42

    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH - fillerCost
    assert ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]
    assert fillOrderID == 0
