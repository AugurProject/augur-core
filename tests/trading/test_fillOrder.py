#!/usr/bin/env python

from ethereum.tools import tester
from utils import fix, bytesToHexString, AssertLog, longTo32Bytes, longToHexString, stringToBytes
from constants import BID, ASK, YES, NO


def test_publicFillOrder_bid(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    creatorCost = fix('2', '6000')
    fillerCost = fix('2', '4000')

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    orderFilledLog = {
        "filler": bytesToHexString(tester.a2),
        "numCreatorShares": 0,
        "numCreatorTokens": creatorCost,
        "numFillerShares": 0,
        "numFillerTokens": fillerCost,
        "marketCreatorFees": 0,
        "reporterFees": 0,
        "shareToken": market.getShareToken(YES),
        "tradeGroupId": stringToBytes("42"),
        "amountFilled": fix(2),
    }
    with AssertLog(contractsFixture, "OrderFilled", orderFilledLog):
        fillOrderID = fillOrder.publicFillOrder(orderID, fix(2), tradeGroupID, sender = tester.k2, value=fillerCost)
        assert fillOrderID == 0

    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH - creatorCost
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH - fillerCost
    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

def test_publicFillOrder_ask(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    tradeGroupID = "42"

    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    creatorCost = fix('2', '4000')
    fillerCost = fix('2', '6000')

    # create order
    orderID = createOrder.publicCreateOrder(ASK, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    fillOrderID = fillOrder.publicFillOrder(orderID, fix(2), tradeGroupID, sender = tester.k2, value=fillerCost)

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

    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    creatorCost = fix('2', '6000')
    fillerCost = fix('2', '394000')

    # create order
    orderID = createOrder.publicCreateOrder(BID, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    # fill best order
    fillOrderID = fillOrder.publicFillOrder(orderID, fix(2), tradeGroupID, sender = tester.k2, value=fillerCost)

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
    orderID = createOrder.publicCreateOrder(ASK, fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    assert orderID

    # fill order with shares
    assert fillOrder.publicFillOrder(orderID, fix(1), "43", sender=tester.k2) == 0

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
    price = 6000
    orderID = createOrder.publicCreateOrder(ASK, fix(1), price, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    assert orderID

    # fill order with shares
    assert fillOrder.publicFillOrder(orderID, fix(1), "43", sender=tester.k2) == 0

    # The second users corresponding shares were used to fulfil this order
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

def test_fill_buy_order_with_buy_categorical(contractsFixture, cash, categoricalMarket, universe):
    market = categoricalMarket
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    firstShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(0))
    secondShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(1))
    thirdShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(2))

    # create order with cash
    price = 6000
    numTicks = market.getNumTicks()
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

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

def test_malicious_order_creator(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    orders = contractsFixture.contracts['Orders']
    augur = contractsFixture.contracts['Augur']
    completeSets = contractsFixture.contracts['CompleteSets']
    firstShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(0))
    secondShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(1))

    maliciousTrader = contractsFixture.upload('solidity_test_helpers/MaliciousTrader.sol', 'maliciousTrader')
    maliciousTrader.approveAugur(cash.address, augur.address)

    # create order with the malicious contract by escrowing shares
    price = 6000
    numTicks = market.getNumTicks()
    assert completeSets.publicBuyCompleteSets(market.address, fix(1), value=fix('1', numTicks))
    assert firstShareToken.transfer(maliciousTrader.address, fix(1))
    assert secondShareToken.transfer(maliciousTrader.address, fix(1))
    orderID = maliciousTrader.makeOrder(createOrder.address, BID, fix(1), price, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), "42", value=fix(1, price), sender=tester.k1)
    assert orderID

    # Make the fallback function fail
    maliciousTrader.setEvil(True)

    # fill order with cash
    assert fillOrder.publicFillOrder(orderID, fix(1), "43", sender=tester.k2, value=fix(1, numTicks - price)) == 0

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)

    # The malicious contract may have just been a smart contract that has expensive and dumb fallback behavior. We do the right thing and still award them Cash in this case.
    assert cash.balanceOf(maliciousTrader.address) == fix(1, 4000)
