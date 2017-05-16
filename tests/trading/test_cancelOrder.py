#!/usr/bin/env python

from ContractsFixture import ContractsFixture
from ethereum import tester
from ethereum.tester import TransactionFailed
from iocapture import capture
from pytest import raises, fixture
from utils import parseCapturedLogs, bytesToLong, fix, unfix

tester.gas_limit = long(4.2 * 10**6)

BID = 1
ASK = 2

YES = 1
NO = 0

ATTOSHARES = 0
DISPLAY_PRICE = 1
OWNER = 2
OUTCOME = 3
TOKENS_ESCROWED = 4
SHARES_ESCROWED = 5
BETTER_ORDER_ID = 6
WORSE_ORDER_ID = 7
GAS_PRICE = 8

def test_cancelBid():
    fixture = ContractsFixture()
    (_, cash, market, orders, makeOrder, cancelOrder) = fixture.prepOrders()

    orderType = BID
    fxpAmount = fix(1)
    fxpPrice = fix("0.6")
    outcomeID = YES
    tradeGroupID = 42
    yesShareToken = fixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('shareToken', market.getShareToken(NO))
    assert cash.publicDepositEther(value = fix(10000), sender = tester.k1) == 1, "Deposit cash"
    assert(cash.approve(makeOrder.address, fix(10000), sender = tester.k1) == 1), "Approve makeOrder contract to spend cash"
    makerInitialCash = cash.balanceOf(tester.a1)
    makerInitialShares = yesShareToken.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()
    orderID = makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, market.address, outcomeID, tradeGroupID, sender=tester.k1)
    assert orderID, "Order ID should be non-zero"
    assert orders.getOrder(orderID, orderType, market.address, outcomeID)[OWNER], "Order should have non-zero elements"

    assert(cancelOrder.publicCancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k1) == 1), "publicCancelOrder should succeed"

    assert(orders.getOrder(orderID, orderType, market.address, outcomeID) == [0, 0, 0, 1, 0, 0, 0, 0, 0]), "Canceled order elements should all be zero"
    assert(makerInitialCash == cash.balanceOf(tester.a1)), "Maker's cash should be the same as before the order was placed"
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(makerInitialShares == yesShareToken.balanceOf(tester.a1)), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_cancelAsk():
    fixture = ContractsFixture()
    (_, cash, market, orders, makeOrder, cancelOrder) = fixture.prepOrders()

    orderType = ASK
    fxpAmount = fix(1)
    fxpPrice = fix("0.6")
    outcomeID = 1
    tradeGroupID = 42
    yesShareToken = fixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('shareToken', market.getShareToken(NO))
    assert cash.publicDepositEther(value = fix(10000), sender = tester.k1) == 1, "Deposit cash"
    assert(cash.approve(makeOrder.address, fix(10000), sender = tester.k1) == 1), "Approve makeOrder contract to spend cash"
    makerInitialCash = cash.balanceOf(tester.a1)
    makerInitialShares = yesShareToken.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()
    orderID = makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, market.address, outcomeID, tradeGroupID, sender=tester.k1)
    assert(orderID != 0), "Order ID should be non-zero"
    assert orders.getOrder(orderID, orderType, market.address, outcomeID)[OWNER], "Order should have non-zero elements"

    assert(cancelOrder.publicCancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k1) == 1), "publicCancelOrder should succeed"

    assert(orders.getOrder(orderID, orderType, market.address, outcomeID) == [0, 0, 0, 1, 0, 0, 0, 0, 0]), "Canceled order elements should all be zero"
    assert(makerInitialCash == cash.balanceOf(tester.a1)), "Maker's cash should be the same as before the order was placed"
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(makerInitialShares == yesShareToken.balanceOf(tester.a1)), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_exceptions():
    fixture = ContractsFixture()
    (_, cash, market, orders, makeOrder, cancelOrder) = fixture.prepOrders()

    orderType = BID
    fxpAmount = fix(1)
    fxpPrice = fix("0.6")
    outcomeID = YES
    tradeGroupID = 42
    assert cash.publicDepositEther(value = fix(10000), sender = tester.k1) == 1, "Deposit cash"
    assert(cash.approve(makeOrder.address, fix(10000), sender = tester.k1) == 1), "Approve makeOrder contract to spend cash"
    makerInitialCash = cash.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    orderID = makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, market.address, outcomeID, tradeGroupID, sender=tester.k1)
    assert(orderID != 0), "Order ID should be non-zero"

    # Permissions exceptions
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(tester.a1, orderID, orderType, market.address, outcomeID, sender=tester.k1)
    with raises(TransactionFailed):
        cancelOrder.refundOrder(tester.a1, orderType, 0, fxpAmount, market.address, outcomeID, sender=tester.k1)

    # cancelOrder exceptions
    with raises(TransactionFailed):
        cancelOrder.publicCancelOrder(0, orderType, market.address, outcomeID, sender=tester.k1)
    with raises(TransactionFailed):
        cancelOrder.publicCancelOrder(orderID + 1, orderType, market.address, outcomeID, sender=tester.k1)
    with raises(TransactionFailed):
        cancelOrder.publicCancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k2)
    assert(cancelOrder.publicCancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k1) == 1), "publicCancelOrder should succeed"
    with raises(TransactionFailed):
        cancelOrder.publicCancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k1)
