#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture, mark, lazy_fixture
from utils import bytesToLong, longToHexString, longTo32Bytes, bytesToHexString, fix, unfix
from constants import BID, ASK, YES, NO

tester.STARTGAS = long(6.7 * 10**6)


def test_make_ask_with_shares_take_with_shares(fundedRepFixture):
    completeSets = fundedRepFixture.contracts['CompleteSets']
    makeOrder = fundedRepFixture.contracts['MakeOrder']
    takeOrder = fundedRepFixture.contracts['TakeOrder']
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket

    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))
    completeSetFees = fix('12', '0.01') + fix('12', '0.0001')

    # 1. both accounts buy a complete set
    assert cash.depositEther(value=fix('12'), sender = tester.k1)
    assert cash.depositEther(value=fix('12'), sender = tester.k2)
    assert cash.approve(completeSets.address, fix('12'), sender = tester.k1)
    assert cash.approve(completeSets.address, fix('12'), sender = tester.k2)
    assert completeSets.publicBuyCompleteSets(market.address, 12, sender = tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, 12, sender = tester.k2)
    assert yesShareToken.balanceOf(tester.a1) == 12
    assert yesShareToken.balanceOf(tester.a2) == 12
    assert noShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a2) == 12

    # 2. make ASK order for YES with YES shares for escrow
    assert yesShareToken.approve(makeOrder.address, 12, sender = tester.k1)
    askOrderID = makeOrder.publicMakeOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), 42, sender = tester.k1)
    assert askOrderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 12

    # 3. take ASK order for YES with NO shares
    assert noShareToken.approve(takeOrder.address, 12, sender = tester.k2)
    fxpAmountRemaining = takeOrder.publicTakeOrder(askOrderID, 12, sender = tester.k2)
    makerFee = completeSetFees * 0.6
    takerFee = completeSetFees * 0.4
    assert fxpAmountRemaining == 0
    assert cash.balanceOf(tester.a1) == fix('12', '0.6') - makerFee
    assert cash.balanceOf(tester.a2) == fix('12', '0.4') - takerFee
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 12
    assert noShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a2) == 0

def test_make_ask_with_shares_take_with_cash(fundedRepFixture):
    completeSets = fundedRepFixture.contracts['CompleteSets']
    makeOrder = fundedRepFixture.contracts['MakeOrder']
    takeOrder = fundedRepFixture.contracts['TakeOrder']
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket

    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy a complete set with account 1
    assert cash.depositEther(value=fix('12'), sender = tester.k1)
    assert cash.approve(completeSets.address, fix('12'), sender = tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, 12, sender = tester.k1)
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 12, "Account 1 should have 12 shares of outcome 1"
    assert noShareToken.balanceOf(tester.a1) == 12, "Account 1 should have 12 shares of outcome 2"

    # 2. make ASK order for YES with YES shares for escrow
    assert yesShareToken.approve(makeOrder.address, 12, sender = tester.k1)
    askOrderID = makeOrder.publicMakeOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), 42, sender = tester.k1)
    assert askOrderID, "Order ID should be non-zero"
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 12

    # 3. take ASK order for YES with cash
    assert cash.depositEther(value=fix('12', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('12', '0.6'), sender = tester.k2)
    fxpAmountRemaining = takeOrder.publicTakeOrder(askOrderID, 12, sender = tester.k2)
    assert fxpAmountRemaining == 0
    assert cash.balanceOf(tester.a1) == fix('12', '0.6')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 12
    assert noShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a2) == 0

def test_make_ask_with_cash_take_with_shares(fundedRepFixture):
    completeSets = fundedRepFixture.contracts['CompleteSets']
    makeOrder = fundedRepFixture.contracts['MakeOrder']
    takeOrder = fundedRepFixture.contracts['TakeOrder']
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket

    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 2
    assert cash.depositEther(value=fix('12'), sender = tester.k2)
    assert cash.approve(completeSets.address, fix('12'), sender = tester.k2)
    assert completeSets.publicBuyCompleteSets(market.address, 12, sender = tester.k2)
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == 12
    assert noShareToken.balanceOf(tester.a2) == 12

    # 2. make ASK order for YES with cash escrowed
    assert cash.depositEther(value=fix('12', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('12', '0.4'), sender = tester.k1)
    askOrderID = makeOrder.publicMakeOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), 42, sender = tester.k1)
    assert askOrderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 0

    # 3. take ASK order for YES with shares of NO
    assert noShareToken.approve(takeOrder.address, 12, sender = tester.k2)
    amountRemaining = takeOrder.publicTakeOrder(askOrderID, 12, sender = tester.k2)
    assert amountRemaining == 0, "Amount remaining should be 0"
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('12', '0.4')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 12
    assert noShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a2) == 0

def test_make_ask_with_cash_take_with_cash(fundedRepFixture):
    completeSets = fundedRepFixture.contracts['CompleteSets']
    makeOrder = fundedRepFixture.contracts['MakeOrder']
    takeOrder = fundedRepFixture.contracts['TakeOrder']
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket

    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. make ASK order for YES with cash escrowed
    assert cash.depositEther(value=fix('12', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('12', '0.4'), sender = tester.k1)
    askOrderID = makeOrder.publicMakeOrder(ASK, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), 42, sender = tester.k1)
    assert askOrderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 0

    # 2. take ASK order for YES with cash
    assert cash.depositEther(value=fix('12', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('12', '0.6'), sender = tester.k2)
    fxpAmountRemaining = takeOrder.publicTakeOrder(askOrderID, 12, sender = tester.k2)
    assert fxpAmountRemaining == 0
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 12
    assert noShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a2) == 0

def test_make_bid_with_shares_take_with_shares(fundedRepFixture):
    completeSets = fundedRepFixture.contracts['CompleteSets']
    makeOrder = fundedRepFixture.contracts['MakeOrder']
    takeOrder = fundedRepFixture.contracts['TakeOrder']
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket

    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))
    completeSetFees = fix('12', '0.01') + fix('12', '0.0001')

    # 1. buy complete sets with both accounts
    assert cash.depositEther(value=fix('12'), sender = tester.k1) == 1
    assert cash.depositEther(value=fix('12'), sender = tester.k2) == 1
    assert cash.approve(completeSets.address, fix('12'), sender = tester.k1)
    assert cash.approve(completeSets.address, fix('12'), sender = tester.k2)
    assert completeSets.publicBuyCompleteSets(market.address, 12, sender = tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, 12, sender = tester.k2)
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == 12
    assert yesShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a2) == 12

    # 2. make BID order for YES with NO shares escrowed
    assert noShareToken.approve(makeOrder.address, 12, sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), 42, sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a1) == 0

    # 3. take BID order for YES with shares of YES
    assert yesShareToken.approve(takeOrder.address, 12, sender = tester.k2)
    leftoverInOrder = takeOrder.publicTakeOrder(orderID, 12, sender = tester.k2)
    makerFee = completeSetFees * 0.4
    takerFee = completeSetFees * 0.6
    assert leftoverInOrder == 0
    makerBalance = fix('12', '0.4') - makerFee
    takerBalance = fix('12', '0.6') - takerFee
    assert cash.balanceOf(tester.a1) == makerBalance
    assert cash.balanceOf(tester.a2) == takerBalance
    assert yesShareToken.balanceOf(tester.a1) == 12
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 12

def test_make_bid_with_shares_take_with_cash(fundedRepFixture):
    completeSets = fundedRepFixture.contracts['CompleteSets']
    makeOrder = fundedRepFixture.contracts['MakeOrder']
    takeOrder = fundedRepFixture.contracts['TakeOrder']
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket

    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 1
    assert cash.depositEther(value=fix('12'), sender = tester.k1) == 1
    assert cash.approve(completeSets.address, fix('12'), sender = tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, 12, sender = tester.k1)
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a1) == 12

    # 2. make BID order for YES with NO shares escrowed
    assert noShareToken.approve(makeOrder.address, 12, sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), 42, sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 12
    assert noShareToken.balanceOf(tester.a1) == 0

    # 3. take BID order for YES with cash
    assert cash.depositEther(value=fix('12', '0.4'), sender = tester.k2) == 1
    assert cash.approve(takeOrder.address, fix('12', '0.4'), sender = tester.k2)
    leftoverInOrder = takeOrder.publicTakeOrder(orderID, 12, sender = tester.k2)
    assert leftoverInOrder == 0
    assert cash.balanceOf(tester.a1) == fix('12', '0.4')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 12
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 12

def test_make_bid_with_cash_take_with_shares(fundedRepFixture):
    completeSets = fundedRepFixture.contracts['CompleteSets']
    makeOrder = fundedRepFixture.contracts['MakeOrder']
    takeOrder = fundedRepFixture.contracts['TakeOrder']
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket

    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 2
    assert cash.depositEther(value=fix('12'), sender = tester.k2)
    assert cash.approve(completeSets.address, fix('12'), sender = tester.k2)
    assert completeSets.publicBuyCompleteSets(market.address, 12, sender = tester.k2)
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == 12
    assert noShareToken.balanceOf(tester.a2) == 12

    # 2. make BID order for YES with cash escrowed
    assert cash.depositEther(value=fix('12', '0.6'), sender = tester.k1) == 1
    assert cash.approve(makeOrder.address, fix('12', '0.6'), sender = tester.k1) == 1
    orderID = makeOrder.publicMakeOrder(BID, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), 42, sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 0

    # 3. take BID order for YES with shares of YES
    assert yesShareToken.approve(takeOrder.address, 12, sender = tester.k2)
    leftoverInOrder = takeOrder.publicTakeOrder(orderID, 12, sender = tester.k2)
    assert leftoverInOrder == 0
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('12', '0.6')
    assert yesShareToken.balanceOf(tester.a1) == 12
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 12

def test_make_bid_with_cash_take_with_cash(fundedRepFixture):
    completeSets = fundedRepFixture.contracts['CompleteSets']
    makeOrder = fundedRepFixture.contracts['MakeOrder']
    takeOrder = fundedRepFixture.contracts['TakeOrder']
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket

    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. make BID order for YES with cash escrowed
    assert cash.depositEther(value=fix('12', '0.6'), sender = tester.k1) == 1
    assert cash.approve(makeOrder.address, fix('12', '0.6'), sender = tester.k1) == 1
    orderID = makeOrder.publicMakeOrder(BID, 12, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), 42, sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 0

    # 2. take BID order for YES with cash
    assert cash.depositEther(value=fix('12', '0.4'), sender = tester.k2) == 1
    assert cash.approve(takeOrder.address, fix('12', '0.4'), sender = tester.k2)
    leftoverInOrder = takeOrder.publicTakeOrder(orderID, 12, sender = tester.k2)
    assert leftoverInOrder == 0
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 12
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 12

import contextlib
@contextlib.contextmanager
def placeholder_context():
    yield None

@mark.parametrize('type,outcome,displayPrice,orderSize,makerYesShares,makerNoShares,makerTokens,takeSize,takerYesShares,takerNoShares,takerTokens,expectMakeRaise,expectedMakerYesShares,expectedMakerNoShares,expectedMakerTokens,expectTakeRaise,expectedTakerYesShares,expectedTakerNoShares,expectedTakerTokens,fixture', [
    # | ------ ORDER ------ |   | ------ MAKER START ------ |   | ------ TAKER START ------ |  | ------- MAKER FINISH -------  |    | ------- TAKER FINISH -------  |
    #   type,outcome,  price,   size,    yes,     no,   tkns,   size,    yes,     no,   tkns,  raise,    yes,     no,      tkns,    raise,    yes,     no,      tkns,
    (    BID,    YES,  '0.6',  '12',    '0',    '0', '7.2',  '12',  '12',    '0',    '0',  False,  '12',    '0',       '0',    False,    '0',    '0',    '7.2', lazy_fixture('fundedRepFixture')),
    (    BID,    YES,  '0.6',  '12',    '0',  '12',    '0',  '12',  '12',    '0',    '0',  False,    '0',    '0','4.75152',    False,    '0',    '0','7.12728', lazy_fixture('fundedRepFixture')),
    (    BID,    YES,  '0.6',  '12',    '0',    '0', '7.2',  '12',    '0',    '0', '4.8',  False,  '12',    '0',       '0',    False,    '0',  '12',       '0', lazy_fixture('fundedRepFixture')),
    (    BID,    YES,  '0.6',  '12',    '0',  '12',    '0',  '12',    '0',    '0', '4.8',  False,    '0',    '0',    '4.8',    False,    '0',  '12',       '0', lazy_fixture('fundedRepFixture')),

    (    BID,    YES,  '0.6',  '24',    '0',  '12', '7.2',  '24',  '24',    '0',    '0',  False,  '12',    '0','4.75152',    False,    '0',    '0','14.32728', lazy_fixture('fundedRepFixture')),
    (    BID,    YES,  '0.6',  '24',    '0',  '12', '7.2',  '24',    '0',    '0', '9.6',  False,  '12',    '0',    '4.8',    False,    '0',  '24',       '0', lazy_fixture('fundedRepFixture')),
    (    BID,    YES,  '0.6',  '24',    '0',    '0', '14.4',  '24',  '12',    '0', '4.8',  False,  '24',    '0',       '0',    False,    '0',  '12',    '7.2', lazy_fixture('fundedRepFixture')),
    (    BID,    YES,  '0.6',  '24',    '0',  '24',    '0',  '24',  '12',    '0', '4.8',  False,    '0',    '0','9.55152',    False,    '0',  '12','7.12728', lazy_fixture('fundedRepFixture')),

    (    BID,    YES,  '0.6',  '24',    '0',  '12', '7.2',  '24',  '12',    '0', '4.8',  False,  '12',    '0','4.75152',    False,    '0',  '12','7.12728', lazy_fixture('fundedRepFixture')),

    (    BID,     NO,  '0.6',  '12',    '0',    '0', '7.2',  '12',    '0',  '12',    '0',  False,    '0',  '12',       '0',    False,    '0',    '0',    '7.2', lazy_fixture('fundedRepFixture')),
    (    BID,     NO,  '0.6',  '12',  '12',    '0',    '0',  '12',    '0',  '12',    '0',  False,    '0',    '0','4.75152',    False,    '0',    '0','7.12728', lazy_fixture('fundedRepFixture')),
    (    BID,     NO,  '0.6',  '12',    '0',    '0', '7.2',  '12',    '0',    '0', '4.8',  False,    '0',  '12',       '0',    False,  '12',    '0',       '0', lazy_fixture('fundedRepFixture')),
    (    BID,     NO,  '0.6',  '12',  '12',    '0',    '0',  '12',    '0',    '0', '4.8',  False,    '0',    '0',    '4.8',    False,  '12',    '0',       '0', lazy_fixture('fundedRepFixture')),

    (    BID,     NO,  '0.6',  '24',  '12',    '0', '7.2',  '24',    '0',  '24',    '0',  False,    '0',  '12','4.75152',    False,    '0',    '0','14.32728', lazy_fixture('fundedRepFixture')),
    (    BID,     NO,  '0.6',  '24',  '12',    '0', '7.2',  '24',    '0',    '0', '9.6',  False,    '0',  '12',    '4.8',    False,  '24',    '0',       '0', lazy_fixture('fundedRepFixture')),
    (    BID,     NO,  '0.6',  '24',    '0',    '0', '14.4',  '24',    '0',  '12', '4.8',  False,    '0',  '24',       '0',    False,  '12',    '0',    '7.2', lazy_fixture('fundedRepFixture')),
    (    BID,     NO,  '0.6',  '24',  '24',    '0',    '0',  '24',    '0',  '12', '4.8',  False,    '0',    '0','9.55152',    False,  '12',    '0','7.12728', lazy_fixture('fundedRepFixture')),

    (    BID,     NO,  '0.6',  '24',  '12',    '0', '7.2',  '24',    '0',  '12', '4.8',  False,    '0',  '12','4.75152',    False,  '12',    '0','7.12728', lazy_fixture('fundedRepFixture')),

    (    ASK,    YES,  '0.6',  '12',  '12',    '0',    '0',  '12',    '0',    '0', '7.2',  False,    '0',    '0',    '7.2',    False,  '12',    '0',       '0', lazy_fixture('fundedRepFixture')),
    (    ASK,    YES,  '0.6',  '12',    '0',    '0', '4.8',  '12',    '0',    '0', '7.2',  False,    '0',  '12',       '0',    False,  '12',    '0',       '0', lazy_fixture('fundedRepFixture')),
    (    ASK,    YES,  '0.6',  '12',  '12',    '0',    '0',  '12',    '0',  '12',    '0',  False,    '0',    '0','7.12728',    False,    '0',    '0','4.75152', lazy_fixture('fundedRepFixture')),
    (    ASK,    YES,  '0.6',  '12',    '0',    '0', '4.8',  '12',    '0',  '12',    '0',  False,    '0',  '12',       '0',    False,    '0',    '0',    '4.8', lazy_fixture('fundedRepFixture')),
])
def test_parametrized(type, outcome, displayPrice, orderSize, makerYesShares, makerNoShares, makerTokens, takeSize, takerYesShares, takerNoShares, takerTokens, expectMakeRaise, expectedMakerYesShares, expectedMakerNoShares, expectedMakerTokens, expectTakeRaise, expectedTakerYesShares, expectedTakerNoShares, expectedTakerTokens, fixture):
    # TODO: add support for wider range markets
    displayPrice = fix(displayPrice)
    assert displayPrice < 10**18
    assert displayPrice > 0

    orderSize = int(orderSize)
    makerYesShares = int(makerYesShares)
    makerNoShares = int(makerNoShares)
    makerTokens = fix(makerTokens)

    takeSize = int(takeSize)
    takerYesShares = int(takerYesShares)
    takerNoShares = int(takerNoShares)
    takerTokens = fix(takerTokens)

    expectedMakerYesShares = int(expectedMakerYesShares)
    expectedMakerNoShares = int(expectedMakerNoShares)
    expectedMakerTokens = fix(expectedMakerTokens)

    expectedTakerYesShares = int(expectedTakerYesShares)
    expectedTakerNoShares = int(expectedTakerNoShares)
    expectedTakerTokens = fix(expectedTakerTokens)

    makerAddress = tester.a1
    makerKey = tester.k1
    takerAddress = tester.a2
    takerKey = tester.k2

    cash = fixture.cash
    market = fixture.binaryMarket
    completeSets = fixture.contracts['CompleteSets']
    makeOrder = fixture.contracts['MakeOrder']
    takeOrder = fixture.contracts['TakeOrder']
    yesShareToken = fixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('ShareToken', market.getShareToken(NO))

    def acquireShares(outcome, amount, approvalAddress, sender):
        if amount == 0: return
        assert cash.depositEther(value=fix(amount), sender = sender)
        assert cash.approve(completeSets.address, fix(amount), sender = sender)
        assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender)
        if outcome == YES:
            assert yesShareToken.approve(approvalAddress, amount, sender = sender)
            assert noShareToken.transfer(0, amount, sender = sender)
        if outcome == NO:
            assert yesShareToken.transfer(0, amount, sender = sender)
            assert noShareToken.approve(approvalAddress, amount, sender = sender)

    def acquireTokens(amount, approvalAddress, sender):
        if amount == 0: return
        assert cash.depositEther(value = amount, sender = sender)
        assert cash.approve(approvalAddress, amount, sender = sender)

    # make order
    acquireShares(YES, makerYesShares, makeOrder.address, sender = makerKey)
    acquireShares(NO, makerNoShares, makeOrder.address, sender = makerKey)
    acquireTokens(makerTokens, makeOrder.address, sender = makerKey)
    with raises(TransactionFailed) if expectMakeRaise else placeholder_context():
        orderID = makeOrder.publicMakeOrder(type, orderSize, displayPrice, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), 42, sender = makerKey)

    # take order
    acquireShares(YES, takerYesShares, takeOrder.address, sender = takerKey)
    acquireShares(NO, takerNoShares, takeOrder.address, sender = takerKey)
    acquireTokens(takerTokens, takeOrder.address, sender = takerKey)
    with raises(TransactionFailed) if expectTakeRaise else placeholder_context():
        takeOrder.publicTakeOrder(orderID, takeSize, sender = takerKey)

    # assert final state
    assert cash.balanceOf(makerAddress) == expectedMakerTokens
    assert cash.balanceOf(takerAddress) == expectedTakerTokens
    assert yesShareToken.balanceOf(makerAddress) == expectedMakerYesShares
    assert yesShareToken.balanceOf(takerAddress) == expectedTakerYesShares
    assert noShareToken.balanceOf(makerAddress) == expectedMakerNoShares
    assert noShareToken.balanceOf(takerAddress) == expectedTakerNoShares
