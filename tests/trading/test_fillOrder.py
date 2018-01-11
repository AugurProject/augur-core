#!/usr/bin/env python

from ethereum.tools import tester
from utils import fix, bytesToHexString, captureFilteredLogs, longTo32Bytes, longToHexString, stringToBytes
from constants import BID, ASK, YES, NO


def test_publicFillOrder_bid(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    creatorCost = fix('2', '6000')
    fillerCost = fix('2', '4000')

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = fillOrder.publicFillOrder(orderID, fix(2), tradeGroupID, sender = tester.k2, value=fillerCost)

    assert len(logs) == 5

    assert logs[4]["_event_type"] == "OrderFilled"
    assert logs[4]["filler"] == bytesToHexString(tester.a2)
    assert logs[4]["numCreatorShares"] == 0
    assert logs[4]["numCreatorTokens"] == creatorCost
    assert logs[4]["numFillerShares"] == 0
    assert logs[4]["numFillerTokens"] == fillerCost
    assert logs[4]["marketCreatorFees"] == 0
    assert logs[4]["reporterFees"] == 0
    assert logs[4]["shareToken"] == market.getShareToken(YES)
    assert logs[4]["tradeGroupId"] == stringToBytes("42")

    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH - fillerCost
    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert fillOrderID == 0

def test_publicFillOrder_ask(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"
    logs = []

    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    creatorCost = fix('2', '4000')
    fillerCost = fix('2', '6000')

    # create order
    orderID = createOrder.publicCreateOrder(ASK, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = fillOrder.publicFillOrder(orderID, fix(2), tradeGroupID, sender = tester.k2, value=fillerCost)

    assert len(logs) == 5

    assert logs[4]["_event_type"] == "OrderFilled"
    assert logs[4]["filler"] == bytesToHexString(tester.a2)
    assert logs[4]["numCreatorShares"] == 0
    assert logs[4]["numCreatorTokens"] == creatorCost
    assert logs[4]["numFillerShares"] == 0
    assert logs[4]["numFillerTokens"] == fillerCost
    assert logs[4]["marketCreatorFees"] == 0
    assert logs[4]["reporterFees"] == 0
    assert logs[4]["shareToken"] == market.getShareToken(YES)
    assert logs[4]["tradeGroupId"] == stringToBytes("42")

    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH - fillerCost
    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert fillOrderID == 0

def test_publicFillOrder_bid_scalar(contractsFixture, cash, scalarMarket, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    # We're testing the scalar market because it has a different numTicks than 10**18 as the other do. In particular it's numTicks is 40*18**18
    market = scalarMarket
    tradeGroupID = "42"
    logs = []

    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    creatorCost = fix('2', '6000')
    fillerCost = fix('2', '394000')

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    fillOrderID = fillOrder.publicFillOrder(orderID, fix(2), tradeGroupID, sender = tester.k2, value=fillerCost)

    assert len(logs) == 5

    assert logs[4]["_event_type"] == "OrderFilled"
    assert logs[4]["filler"] == bytesToHexString(tester.a2)
    assert logs[4]["numCreatorShares"] == 0
    assert logs[4]["numCreatorTokens"] == creatorCost
    assert logs[4]["numFillerShares"] == 0
    assert logs[4]["numFillerTokens"] == fillerCost
    assert logs[4]["marketCreatorFees"] == 0
    assert logs[4]["reporterFees"] == 0
    assert logs[4]["shareToken"] == market.getShareToken(YES)
    assert logs[4]["tradeGroupId"] == stringToBytes("42")

    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH - fillerCost
    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert fillOrderID == 0

def test_fill_order_with_shares_escrowed_sell_with_shares(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    completeSets = contractsFixture.contracts['CompleteSets']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # buy complete sets for both users
    assert completeSets.publicBuyCompleteSets(market.address, fix(1), sender=tester.k1, value=fix('1', '10000'))
    assert yesShareToken.balanceOf(tester.a1) == fix(1)
    assert completeSets.publicBuyCompleteSets(market.address, fix(1), sender=tester.k2, value=fix('1', '10000'))
    assert noShareToken.balanceOf(tester.a2) == fix(1)

    # create order with shares
    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    assert orderID

    # fill order with shares
    assert fillOrder.publicFillOrder(orderID, fix(1), "43", sender=tester.k2) == 0

    assert len(logs) == 8
    log1 = logs[7]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == fix(1)
    assert log1["numCreatorTokens"] == 0
    assert log1["numFillerShares"] == fix(1)
    assert log1["numFillerTokens"] == 0
    assert log1["marketCreatorFees"] == fix(1, 10000) / market.getMarketCreatorSettlementFeeDivisor()
    assert log1["reporterFees"] == fix(1, 10000) / universe.getOrCacheReportingFeeDivisor()
    assert log1["shareToken"] == market.getShareToken(YES)
    assert log1["tradeGroupId"] == stringToBytes("43")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

def test_fill_order_with_shares_escrowed_sell_with_shares_categorical(contractsFixture, cash, categoricalMarket, universe):
    market = categoricalMarket
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
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
    logs = []
    price = 6000
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    orderID = createOrder.publicCreateOrder(ASK, fix(1), price, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    assert orderID

    # fill order with shares
    assert fillOrder.publicFillOrder(orderID, fix(1), "43", sender=tester.k2) == 0

    # The second users corresponding shares were used to fulfil this order
    assert firstShareToken.balanceOf(tester.a2) == fix(1)
    assert secondShareToken.balanceOf(tester.a2) == 0
    assert thirdShareToken.balanceOf(tester.a2) == 0

    assert len(logs) == 10
    log1 = logs[9]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == fix(1)
    assert log1["numCreatorTokens"] == 0
    assert log1["numFillerShares"] == fix(1)
    assert log1["numFillerTokens"] == 0
    assert log1["marketCreatorFees"] == fix(1, numTicks) / market.getMarketCreatorSettlementFeeDivisor()
    assert log1["reporterFees"] == fix(1, numTicks) / universe.getOrCacheReportingFeeDivisor()
    assert log1["shareToken"] == market.getShareToken(0)
    assert log1["tradeGroupId"] == stringToBytes("43")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

def test_fill_buy_order_with_buy_categorical(contractsFixture, cash, categoricalMarket, universe):
    market = categoricalMarket
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    firstShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(0))
    secondShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(1))
    thirdShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(2))

    # create order with cash
    logs = []
    price = 6000
    numTicks = market.getNumTicks()
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    orderID = createOrder.publicCreateOrder(BID, fix(1), price, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), "42", value=fix(1, price), sender=tester.k1)
    assert orderID

    # fill order with cash
    assert fillOrder.publicFillOrder(orderID, fix(1), "43", sender=tester.k2, value=fix(1, numTicks - price)) == 0

    # A complete set was purchased with the provided cash and the shares were provided to each user
    assert firstShareToken.balanceOf(tester.a1) == fix(1)
    assert secondShareToken.balanceOf(tester.a1) == 0
    assert thirdShareToken.balanceOf(tester.a1) == 0
    
    assert firstShareToken.balanceOf(tester.a2) == 0
    assert secondShareToken.balanceOf(tester.a2) == fix(1)
    assert thirdShareToken.balanceOf(tester.a2) == fix(1)

    assert len(logs) == 8
    log1 = logs[7]

    assert log1["_event_type"] == "OrderFilled"
    assert log1["filler"] == bytesToHexString(tester.a2)
    assert log1["numCreatorShares"] == 0
    assert log1["numCreatorTokens"] == fix(1, price)
    assert log1["numFillerShares"] == 0
    assert log1["numFillerTokens"] == fix(1, numTicks - price)
    assert log1["marketCreatorFees"] == 0
    assert log1["reporterFees"] == 0
    assert log1["shareToken"] == market.getShareToken(0)
    assert log1["tradeGroupId"] == stringToBytes("43")

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
