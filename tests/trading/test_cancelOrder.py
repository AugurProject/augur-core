#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, mark
from utils import longTo32Bytes, longToHexString, fix, AssertLog, bytesToHexString
from constants import BID, ASK, YES, NO

tester.STARTGAS = long(6.7 * 10**6)

@mark.parametrize('escapeHatch', [
    True,
    False
])
def test_cancelBid(escapeHatch, contractsFixture, cash, market, universe):
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

    if (escapeHatch):
        controller = contractsFixture.contracts['Controller']
        controller.emergencyStop()

    orderCanceledLog = {
        'orderId': orderID,
        'shareToken': yesShareToken.address,
        'sender': bytesToHexString(tester.a1),
        'orderType': orderType,
        'sharesRefund': 0,
        'tokenRefund': fix('1', '6000'),
    }
    with AssertLog(contractsFixture, 'OrderCanceled', orderCanceledLog):
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

@mark.parametrize('escapeHatch', [
    True,
    False
])
def test_cancelAsk(escapeHatch, contractsFixture, cash, market):
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

    if (escapeHatch):
        controller = contractsFixture.contracts['Controller']
        controller.emergencyStop()

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

@mark.parametrize('escapeHatch', [
    True,
    False
])
def test_cancelWithSharesInEscrow(escapeHatch, contractsFixture, cash, market, universe):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    totalProceeds = fix('12', market.getNumTicks())
    marketCreatorFee = totalProceeds / market.getMarketCreatorSettlementFeeDivisor()
    reporterFee = totalProceeds / universe.getOrCacheReportingFeeDivisor()
    completeSetFees = marketCreatorFee + reporterFee

    # buy complete sets
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k1, value=fix('12', market.getNumTicks()))
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == fix(12)

    creatorInitialETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    creatorInitialShares = yesShareToken.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()

    # create BID order for YES with NO shares escrowed
    assert noShareToken.approve(createOrder.address, fix(12), sender = tester.k1)
    orderID = createOrder.publicCreateOrder(BID, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == 0

    if (escapeHatch):
        controller = contractsFixture.contracts['Controller']
        controller.emergencyStop()

    # now cancel the order
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

@mark.parametrize('escapeHatch', [
    True,
    False
])
def test_cancelWithSharesInEscrowAsk(escapeHatch, contractsFixture, cash, market, universe):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    cancelOrder = contractsFixture.contracts['CancelOrder']
    orders = contractsFixture.contracts['Orders']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    totalProceeds = fix('12', market.getNumTicks())
    marketCreatorFee = totalProceeds / market.getMarketCreatorSettlementFeeDivisor()
    reporterFee = totalProceeds / universe.getOrCacheReportingFeeDivisor()
    completeSetFees = marketCreatorFee + reporterFee

    # buy complete sets
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k1, value=fix('12', market.getNumTicks()))
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == fix(12)

    creatorInitialETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    creatorInitialShares = yesShareToken.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    marketInitialYesShares = yesShareToken.totalSupply()
    marketInitialNoShares = noShareToken.totalSupply()

    # create ASK order for YES with YES shares escrowed
    assert noShareToken.approve(createOrder.address, fix(12), sender = tester.k1)
    orderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == fix(12)

    if (escapeHatch):
        controller = contractsFixture.contracts['Controller']
        controller.emergencyStop()

    # now cancel the order
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
