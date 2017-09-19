#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture
from utils import bytesToLong, longTo32Bytes, longToHexString, fix, unfix
from constants import BID, ASK, YES, NO

tester.STARTGAS = long(6.7 * 10**6)

def test_cancelBid(contractsFixture):
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    makeOrder = contractsFixture.contracts['MakeOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']

    orderType = BID
    fxpAmount = 1
    fxpPrice = fix('0.6')
    outcomeID = YES
    tradeGroupID = 42
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    assert cash.depositEther(value = fix('10000'), sender = tester.k1) == 1, "Deposit cash"
    assert(cash.approve(makeOrder.address, fix('10000'), sender = tester.k1) == 1), "Approve makeOrder contract to spend cash"
    makerInitialCash = cash.balanceOf(tester.a1)
    makerInitialShares = yesShareToken.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()
    orderID = makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender=tester.k1)
    assert orderID, "Order ID should be non-zero"
    _,_,owner,_,_,_,_,_ = ordersFetcher.getOrder(orderID)
    assert owner, "Order should have an owner"

    assert(cancelOrder.cancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k1) == 1), "cancelOrder should succeed"

    assert(ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "Canceled order elements should all be zero"
    assert(makerInitialCash == cash.balanceOf(tester.a1)), "Maker's cash should be the same as before the order was placed"
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(makerInitialShares == yesShareToken.balanceOf(tester.a1)), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_cancelAsk(contractsFixture):
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    makeOrder = contractsFixture.contracts['MakeOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']

    orderType = ASK
    fxpAmount = 1
    fxpPrice = fix('0.6')
    outcomeID = 1
    tradeGroupID = 42
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    assert cash.depositEther(value = fix('10000'), sender = tester.k1) == 1, "Deposit cash"
    assert(cash.approve(makeOrder.address, fix('10000'), sender = tester.k1) == 1), "Approve makeOrder contract to spend cash"
    makerInitialCash = cash.balanceOf(tester.a1)
    makerInitialShares = yesShareToken.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()
    orderID = makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender=tester.k1)
    assert(orderID != bytearray(32)), "Order ID should be non-zero"
    _,_,owner,_,_,_,_,_ = ordersFetcher.getOrder(orderID)
    assert owner, "Order should have an owner"

    assert(cancelOrder.cancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k1) == 1), "cancelOrder should succeed"

    assert(ordersFetcher.getOrder(orderID) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "Canceled order elements should all be zero"
    assert(makerInitialCash == cash.balanceOf(tester.a1)), "Maker's cash should be the same as before the order was placed"
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(makerInitialShares == yesShareToken.balanceOf(tester.a1)), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_exceptions(contractsFixture):
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    makeOrder = contractsFixture.contracts['MakeOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']

    orderType = BID
    fxpAmount = 1
    fxpPrice = fix('0.6')
    outcomeID = YES
    tradeGroupID = 42
    assert cash.depositEther(value = fix('10000'), sender = tester.k1) == 1, "Deposit cash"
    assert(cash.approve(makeOrder.address, fix('10000'), sender = tester.k1) == 1), "Approve makeOrder contract to spend cash"
    makerInitialCash = cash.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    orderID = makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender=tester.k1)
    assert(orderID != bytearray(32)), "Order ID should be non-zero"

    # cancelOrder exceptions
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(longTo32Bytes(0), orderType, market.address, outcomeID, sender=tester.k1)
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(longTo32Bytes(1), orderType, market.address, outcomeID, sender=tester.k1)
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k2)
    assert(cancelOrder.cancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k1) == 1), "cancelOrder should succeed"
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(orderID, orderType, market.address, outcomeID, sender=tester.k1)
