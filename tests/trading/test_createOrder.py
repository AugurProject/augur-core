#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture
from utils import bytesToLong, longTo32Bytes, longToHexString, bytesToHexString, fix, unfix, AssertLog, EtherDelta, stringToBytes
from uuid import uuid4
from constants import BID, ASK, YES, NO

tester.STARTGAS = long(6.7 * 10**6)

ATTOSHARES = 0
DISPLAY_PRICE = 1
OWNER = 2
TOKENS_ESCROWED = 3
SHARES_ESCROWED = 4
BETTER_ORDER_ID = 5
WORSE_ORDER_ID = 6
GAS_PRICE = 7

def test_publicCreateOrder_bid(contractsFixture, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    orderID = createOrder.publicCreateOrder(BID, fix(1), 4000, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 4000))
    assert orderID

    assert orders.getAmount(orderID) == fix(1)
    assert orders.getPrice(orderID) == 4000
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a0)
    assert orders.getOrderMoneyEscrowed(orderID) == fix(1, 4000)
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == bytearray(32)
    assert orders.getWorseOrderId(orderID) == bytearray(32)

def test_publicCreateOrder_ask(contractsFixture, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    orderID = createOrder.publicCreateOrder(ASK, fix(1), 4000, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 6000))

    assert orders.getAmount(orderID) == fix(1)
    assert orders.getPrice(orderID) == 4000
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a0)
    assert orders.getOrderMoneyEscrowed(orderID) == fix(1, 6000)
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == bytearray(32)
    assert orders.getWorseOrderId(orderID) == bytearray(32)
    assert cash.balanceOf(market.address) == fix(1, 6000)

def test_publicCreateOrder_List_Logic(contractsFixture, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    orderID_10 = createOrder.publicCreateOrder(BID, fix(1), 4010, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "1", value = fix(1, 4010))
    orderID_8 = createOrder.publicCreateOrder(BID, fix(1), 4008, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "2", value = fix(1, 4008))
    orderID_6 = createOrder.publicCreateOrder(BID, fix(1), 4006, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "3", value = fix(1, 4006))
    orderID_2 = createOrder.publicCreateOrder(BID, fix(1), 4002, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "4", value = fix(1, 4002))
    orderID_1 = createOrder.publicCreateOrder(BID, fix(1), 4001, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "5", value = fix(1, 4001))

    orderID_7 = createOrder.publicCreateOrder(BID, fix(1), 4007, market.address, 1, orderID_10, orderID_1, "6", value = fix(1, 4007))
    assert orderID_7
    assert orders.getBetterOrderId(orderID_7) == orderID_8
    assert orders.getWorseOrderId(orderID_7) == orderID_6

    orderID_5 = createOrder.publicCreateOrder(BID, fix(1), 4005, market.address, 1, orderID_6, orderID_1, "7", value = fix(1, 4005))
    assert orderID_5
    assert orders.getBetterOrderId(orderID_5) == orderID_6
    assert orders.getWorseOrderId(orderID_5) == orderID_2

    orderID_3 = createOrder.publicCreateOrder(BID, fix(1), 4003, market.address, 1, orderID_5, orderID_2, "8", value = fix(1, 4003))
    assert orderID_3
    assert orders.getBetterOrderId(orderID_3) == orderID_5
    assert orders.getWorseOrderId(orderID_3) == orderID_2

def test_publicCreateOrder_bid2(contractsFixture, cash, market, universe):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    orderType = BID
    amount = fix(1)
    fxpPrice = 4000
    outcome = 0
    tradeGroupID = "42"

    marketInitialCash = cash.balanceOf(market.address)
    creatorInitialETH = contractsFixture.chain.head_state.get_balance(tester.a1)

    orderID = None
    shareToken = contractsFixture.getShareToken(market, 0)

    orderCreatedLog = {
        'creator': bytesToHexString(tester.a1),
        'shareToken': shareToken.address,
        'tradeGroupId': stringToBytes("42"),
    }

    with AssertLog(contractsFixture, "OrderCreated", orderCreatedLog):
        orderID = createOrder.publicCreateOrder(orderType, amount, fxpPrice, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender=tester.k1, value = fix('1', '4000'))
    assert orderID != bytearray(32), "Order ID should be non-zero"

    assert orders.getAmount(orderID) == amount
    assert orders.getPrice(orderID) == fxpPrice
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(orderID) == fix(1, 4000)
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert cash.balanceOf(tester.a1) == 0
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == creatorInitialETH - long(4000 * 10**18)
    assert cash.balanceOf(market.address) - marketInitialCash == 4000 * 10**18

def test_createOrder_failure(contractsFixture, universe, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    completeSets = contractsFixture.contracts['CompleteSets']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    with raises(TransactionFailed):
        createOrder.createOrder(tester.a1, ASK, fix(1), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    # createOrder exceptions (pre-escrowFunds)
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(3, fix(1), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    # escrowFundsForBid exceptions
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(BID, fix(1), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(BID, fix(1), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    # escrowFundsForAsk exceptions
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, 1, 1, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, fix(1), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender=tester.k1, value=fix('12', market.getNumTicks()))
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, fix(1), 12000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    assert yesShareToken.approve(createOrder.address, fix(12), sender=tester.k1) == 1, "Approve createOrder contract to spend shares from the user's account (account 1)"
    assert yesShareToken.allowance(tester.a1, createOrder.address) == fix(12), "CreateOrder contract's allowance should be equal to the amount approved"

    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, fix(1), 4000, tester.a1, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    assert createOrder.publicCreateOrder(ASK, fix(1), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1) != 0, "Order ID should be non-zero"

    # createOrder exceptions (post-escrowFunds)
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, fix(1), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

def test_ask_withPartialShares(contractsFixture, universe, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    completeSets = contractsFixture.contracts['CompleteSets']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # buy fix(2) complete sets
    assert completeSets.publicBuyCompleteSets(market.address, fix(2), sender = tester.k1, value= fix(2, market.getNumTicks()))
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix(2)
    assert noShareToken.balanceOf(tester.a1) == fix(2)

    orderID = None

    orderCreatedLog = {
        'creator': bytesToHexString(tester.a1),
        'shareToken': yesShareToken.address,
        'tradeGroupId': stringToBytes("42"),
    }
    with AssertLog(contractsFixture, "OrderCreated", orderCreatedLog):
        orderID = createOrder.publicCreateOrder(ASK, fix(3), 4000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1, value=fix('6000'))
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == fix(2)

    # validate the order contains expected results
    assert orderID != bytearray(32), "Order ID should be non-zero"
    assert orders.getAmount(orderID) == fix(3)
    assert orders.getPrice(orderID) == 4000
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(orderID) == fix('6000')
    assert orders.getOrderSharesEscrowed(orderID) == fix(2)

def test_duplicate_creation_transaction(contractsFixture, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    with EtherDelta(-fix(1, 4000), tester.a0, contractsFixture.chain):
        orderID = createOrder.publicCreateOrder(BID, fix(1), 4000, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 4000))

    assert orderID

    with raises(TransactionFailed):
        createOrder.publicCreateOrder(BID, fix(1), 4000, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 4000))
