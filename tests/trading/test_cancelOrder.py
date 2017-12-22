#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import longTo32Bytes, longToHexString, fix, captureFilteredLogs, bytesToHexString
from constants import BID, ASK, YES, NO

tester.STARTGAS = long(6.7 * 10**6)

def test_cancelBid(contractsFixture, cash, market, universe):
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']

    orderType = BID
    fxpAmount = fix(1)
    fxpPrice = 6000
    outcomeID = YES
    tradeGroupID = "42"
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    creatorInitialETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    creatorInitialShares = yesShareToken.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()
    orderID = createOrder.publicCreateOrder(orderType, fxpAmount, fxpPrice, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender=tester.k1, value = fix('10000'))

    assert orderID, "Order ID should be non-zero"
    assert orders.getOrderCreator(orderID), "Order should have an owner"

    assert contractsFixture.chain.head_state.get_balance(tester.a1) == creatorInitialETH - fix('1', '6000'), "ETH should be deducted from the creator balance"

    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)

    assert(cancelOrder.cancelOrder(orderID, sender=tester.k1) == 1), "cancelOrder should succeed"

    # Confirm cancel order logging works correctly
    assert len(logs) == 1
    assert logs[0]['_event_type'] == 'OrderCanceled'
    assert logs[0]['orderId'] == orderID
    assert logs[0]['shareToken'] == yesShareToken.address
    assert logs[0]['sender'] == bytesToHexString(tester.a1)
    assert logs[0]['orderType'] == orderType
    assert logs[0]['sharesRefund'] == 0
    assert logs[0]['tokenRefund'] == fix('1', '6000')

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert(creatorInitialETH == contractsFixture.chain.head_state.get_balance(tester.a1)), "Maker's ETH should be the same as before the order was placed"
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(creatorInitialShares == yesShareToken.balanceOf(tester.a1)), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_cancelAsk(contractsFixture, cash, market):
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']

    orderType = ASK
    fxpAmount = fix(1)
    fxpPrice = 6000
    outcomeID = 1
    tradeGroupID = "42"
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    creatorInitialETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    creatorInitialShares = yesShareToken.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()
    orderID = createOrder.publicCreateOrder(orderType, fxpAmount, fxpPrice, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender=tester.k1, value = fix('10000'))
    assert(orderID != bytearray(32)), "Order ID should be non-zero"
    assert orders.getOrderCreator(orderID), "Order should have an owner"

    assert contractsFixture.chain.head_state.get_balance(tester.a1) == creatorInitialETH - fix('1', '4000'), "ETH should be deducted from the creator balance"

    assert(cancelOrder.cancelOrder(orderID, sender=tester.k1) == 1), "cancelOrder should succeed"

    assert orders.getAmount(orderID) == 0
    assert orders.getPrice(orderID) == 0
    assert orders.getOrderCreator(orderID) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderID) == longTo32Bytes(0)
    assert(creatorInitialETH == contractsFixture.chain.head_state.get_balance(tester.a1)), "Maker's ETH should be the same as before the order was placed"
    assert(marketInitialCash == cash.balanceOf(market.address)), "Market's cash balance should be the same as before the order was placed"
    assert(creatorInitialShares == yesShareToken.balanceOf(tester.a1)), "Maker's shares should be unchanged"
    assert(marketInitialYesShares == yesShareToken.totalSupply()), "Market's yes shares should be unchanged"
    assert marketInitialNoShares == noShareToken.totalSupply(), "Market's no shares should be unchanged"

def test_exceptions(contractsFixture, cash, market):
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']

    orderType = BID
    fxpAmount = fix(1)
    fxpPrice = 6000
    outcomeID = YES
    tradeGroupID = "42"
    marketInitialCash = cash.balanceOf(market.address)
    orderID = createOrder.publicCreateOrder(orderType, fxpAmount, fxpPrice, market.address, outcomeID, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender=tester.k1, value = fix('10000'))
    assert(orderID != bytearray(32)), "Order ID should be non-zero"

    # cancelOrder exceptions
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(longTo32Bytes(0), sender=tester.k1)
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(longTo32Bytes(1), sender=tester.k1)
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(orderID, sender=tester.k2)
    assert(cancelOrder.cancelOrder(orderID, sender=tester.k1) == 1), "cancelOrder should succeed"
    with raises(TransactionFailed):
        cancelOrder.cancelOrder(orderID, sender=tester.k1)
