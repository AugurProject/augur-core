#!/usr/bin/env python

from ethereum import tester
from ethereum.tester import TransactionFailed
from pytest import raises, fixture, mark, lazy_fixture
from utils import bytesToLong, longToHexString, bytesToHexString, fix, unfix

tester.gas_limit = long(4.2 * 10**6)

YES = 1
NO = 0

BID = 1
ASK = 2

def test_make_ask_with_shares_take_with_shares(contractsFixture):
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket

    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))
    completeSetFees = fix('1.2', '0.01') + fix('1.2', '0.0001')

    # 1. both accounts buy a complete set
    assert cash.publicDepositEther(value=fix('1.2'), sender = tester.k1)
    assert cash.publicDepositEther(value=fix('1.2'), sender = tester.k2)
    assert cash.approve(completeSets.address, fix('1.2'), sender = tester.k1)
    assert cash.approve(completeSets.address, fix('1.2'), sender = tester.k2)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender = tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender = tester.k2)
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2')
    assert yesShareToken.balanceOf(tester.a2) == fix('1.2')
    assert noShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a2) == fix('1.2')

    # 2. make ASK order for YES with YES shares for escrow
    assert yesShareToken.approve(makeOrder.address, fix('1.2'), sender = tester.k1)
    askOrderID = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    assert askOrderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('1.2')

    # 3. take ASK order for YES with NO shares
    assert noShareToken.approve(takeOrder.address, fix('1.2'), sender = tester.k2)
    fxpAmountRemaining = takeOrder.publicTakeOrder(askOrderID, ASK, market.address, YES, fix('1.2'), sender = tester.k2)
    makerFee = completeSetFees * 0.6
    takerFee = completeSetFees * 0.4
    assert fxpAmountRemaining == 0
    assert cash.balanceOf(tester.a1) == fix('1.2', '0.6') - makerFee
    assert cash.balanceOf(tester.a2) == fix('1.2', '0.4') - takerFee
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix('1.2')
    assert noShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a2) == fix('0')

def test_make_ask_with_shares_take_with_cash(contractsFixture):
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket

    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))

    # 1. buy a complete set with account 1
    assert cash.publicDepositEther(value=fix('1.2'), sender = tester.k1)
    assert cash.approve(completeSets.address, fix('1.2'), sender = tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender = tester.k1)
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2'), "Account 1 should have fxpAmount shares of outcome 1"
    assert noShareToken.balanceOf(tester.a1) == fix('1.2'), "Account 1 should have fxpAmount shares of outcome 2"

    # 2. make ASK order for YES with YES shares for escrow
    assert yesShareToken.approve(makeOrder.address, fix('1.2'), sender = tester.k1)
    askOrderID = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    assert askOrderID, "Order ID should be non-zero"
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('1.2')

    # 3. take ASK order for YES with cash
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    fxpAmountRemaining = takeOrder.publicTakeOrder(askOrderID, ASK, market.address, YES, fix('1.2'), sender = tester.k2)
    assert fxpAmountRemaining == 0
    assert cash.balanceOf(tester.a1) == fix('1.2', '0.6')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix('1.2')
    assert noShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a2) == fix('0')

def test_make_ask_with_cash_take_with_shares(contractsFixture):
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket

    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 2
    assert cash.publicDepositEther(value=fix('1.2'), sender = tester.k2)
    assert cash.approve(completeSets.address, fix('1.2'), sender = tester.k2)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender = tester.k2)
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix('1.2')
    assert noShareToken.balanceOf(tester.a2) == fix('1.2')

    # 2. make ASK order for YES with cash escrowed
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    askOrderID = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    assert askOrderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('0')

    # 3. take ASK order for YES with shares of NO
    assert noShareToken.approve(takeOrder.address, fix('1.2'), sender = tester.k2)
    fxpAmountRemaining = takeOrder.publicTakeOrder(askOrderID, ASK, market.address, YES, fix('1.2'), sender = tester.k2)
    assert fxpAmountRemaining == 0, "Amount remaining should be 0"
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('1.2', '0.4')
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix('1.2')
    assert noShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a2) == fix('0')

def test_make_ask_with_cash_take_with_cash(contractsFixture):
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket

    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))

    # 1. make ASK order for YES with cash escrowed
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.4'), sender = tester.k1)
    askOrderID = makeOrder.publicMakeOrder(ASK, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    assert askOrderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('0')

    # 2. take ASK order for YES with cash
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.6'), sender = tester.k2)
    fxpAmountRemaining = takeOrder.publicTakeOrder(askOrderID, ASK, market.address, YES, fix('1.2'), sender = tester.k2)
    assert fxpAmountRemaining == 0
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix('1.2')
    assert noShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a2) == fix('0')

def test_make_bid_with_shares_take_with_shares(contractsFixture):
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket

    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))
    completeSetFees = fix('1.2', '0.01') + fix('1.2', '0.0001')

    # 1. buy complete sets with both accounts
    assert cash.publicDepositEther(value=fix('1.2'), sender = tester.k1) == 1
    assert cash.publicDepositEther(value=fix('1.2'), sender = tester.k2) == 1
    assert cash.approve(completeSets.address, fix('1.2'), sender = tester.k1)
    assert cash.approve(completeSets.address, fix('1.2'), sender = tester.k2)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender = tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender = tester.k2)
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix('1.2')
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a2) == fix('1.2')

    # 2. make BID order for YES with NO shares escrowed
    assert noShareToken.approve(makeOrder.address, fix('1.2'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a1) == fix('0')

    # 3. take BID order for YES with shares of YES
    assert yesShareToken.approve(takeOrder.address, fix('1.2'), sender = tester.k2)
    leftoverInOrder = takeOrder.publicTakeOrder(orderID, BID, market.address, YES, fix('1.2'), sender = tester.k2)
    makerFee = completeSetFees * 0.4
    takerFee = completeSetFees * 0.6
    assert leftoverInOrder == 0
    makerBalance = fix('1.2', '0.4') - makerFee
    takerBalance = fix('1.2', '0.6') - takerFee
    assert cash.balanceOf(tester.a1) == makerBalance
    assert cash.balanceOf(tester.a2) == takerBalance
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2')
    assert yesShareToken.balanceOf(tester.a2) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a2) == fix('1.2')

def test_make_bid_with_shares_take_with_cash(contractsFixture):
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket

    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 1
    assert cash.publicDepositEther(value=fix('1.2'), sender = tester.k1) == 1
    assert cash.approve(completeSets.address, fix('1.2'), sender = tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender = tester.k1)
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a1) == fix('1.2')

    # 2. make BID order for YES with NO shares escrowed
    assert noShareToken.approve(makeOrder.address, fix('1.2'), sender = tester.k1)
    orderID = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2')
    assert noShareToken.balanceOf(tester.a1) == fix('0')

    # 3. take BID order for YES with cash
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k2) == 1
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    leftoverInOrder = takeOrder.publicTakeOrder(orderID, BID, market.address, YES, fix('1.2'), sender = tester.k2)
    assert leftoverInOrder == 0
    assert cash.balanceOf(tester.a1) == fix('1.2', '0.4')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2')
    assert yesShareToken.balanceOf(tester.a2) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a2) == fix('1.2')

def test_make_bid_with_cash_take_with_shares(contractsFixture):
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket

    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 2
    assert cash.publicDepositEther(value=fix('1.2'), sender = tester.k2)
    assert cash.approve(completeSets.address, fix('1.2'), sender = tester.k2)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender = tester.k2)
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix('1.2')
    assert noShareToken.balanceOf(tester.a2) == fix('1.2')

    # 2. make BID order for YES with cash escrowed
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1) == 1
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1) == 1
    orderID = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('0')

    # 3. take BID order for YES with shares of YES
    assert yesShareToken.approve(takeOrder.address, fix('1.2'), sender = tester.k2)
    leftoverInOrder = takeOrder.publicTakeOrder(orderID, BID, market.address, YES, fix('1.2'), sender = tester.k2)
    assert leftoverInOrder == 0
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('1.2', '0.6')
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2')
    assert yesShareToken.balanceOf(tester.a2) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a2) == fix('1.2')

def test_make_bid_with_cash_take_with_cash(contractsFixture):
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket

    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))

    # 1. make BID order for YES with cash escrowed
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1) == 1
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1) == 1
    orderID = makeOrder.publicMakeOrder(BID, fix('1.2'), fix('0.6'), market.address, YES, 0, 0, 42, sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('0')

    # 2. take BID order for YES with cash
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k2) == 1
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    leftoverInOrder = takeOrder.publicTakeOrder(orderID, BID, market.address, YES, fix('1.2'), sender = tester.k2)
    assert leftoverInOrder == 0
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix('1.2')
    assert yesShareToken.balanceOf(tester.a2) == fix('0')
    assert noShareToken.balanceOf(tester.a1) == fix('0')
    assert noShareToken.balanceOf(tester.a2) == fix('1.2')

import contextlib
@contextlib.contextmanager
def placeholder_context():
    yield None

@mark.parametrize('type,outcome,displayPrice,orderSize,makerYesShares,makerNoShares,makerTokens,takeSize,takerYesShares,takerNoShares,takerTokens,expectMakeRaise,expectedMakerYesShares,expectedMakerNoShares,expectedMakerTokens,expectTakeRaise,expectedTakerYesShares,expectedTakerNoShares,expectedTakerTokens,fixture', [
    # | ------ ORDER ------ |   | ------ MAKER START ------ |   | ------ TAKER START ------ |  | ------- MAKER FINISH -------  |    | ------- TAKER FINISH -------  |
    #   type,outcome,  price,   size,    yes,     no,   tkns,   size,    yes,     no,   tkns,  raise,    yes,     no,      tkns,    raise,    yes,     no,      tkns,
    (    BID,    YES,  '0.6',  '1.2',    '0',    '0', '0.72',  '1.2',  '1.2',    '0',    '0',  False,  '1.2',    '0',       '0',    False,    '0',    '0',    '0.72', lazy_fixture('contractsFixture')),
    (    BID,    YES,  '0.6',  '1.2',    '0',  '1.2',    '0',  '1.2',  '1.2',    '0',    '0',  False,    '0',    '0','0.475152',    False,    '0',    '0','0.712728', lazy_fixture('contractsFixture')),
    (    BID,    YES,  '0.6',  '1.2',    '0',    '0', '0.72',  '1.2',    '0',    '0', '0.48',  False,  '1.2',    '0',       '0',    False,    '0',  '1.2',       '0', lazy_fixture('contractsFixture')),
    (    BID,    YES,  '0.6',  '1.2',    '0',  '1.2',    '0',  '1.2',    '0',    '0', '0.48',  False,    '0',    '0',    '0.48',    False,    '0',  '1.2',       '0', lazy_fixture('contractsFixture')),

    (    BID,    YES,  '0.6',  '2.4',    '0',  '1.2', '0.72',  '2.4',  '2.4',    '0',    '0',  False,  '1.2',    '0','0.475152',    False,    '0',    '0','1.432728', lazy_fixture('contractsFixture')),
    (    BID,    YES,  '0.6',  '2.4',    '0',  '1.2', '0.72',  '2.4',    '0',    '0', '0.96',  False,  '1.2',    '0',    '0.48',    False,    '0',  '2.4',       '0', lazy_fixture('contractsFixture')),
    (    BID,    YES,  '0.6',  '2.4',    '0',    '0', '1.44',  '2.4',  '1.2',    '0', '0.48',  False,  '2.4',    '0',       '0',    False,    '0',  '1.2',    '0.72', lazy_fixture('contractsFixture')),
    (    BID,    YES,  '0.6',  '2.4',    '0',  '2.4',    '0',  '2.4',  '1.2',    '0', '0.48',  False,    '0',    '0','0.955152',    False,    '0',  '1.2','0.712728', lazy_fixture('contractsFixture')),

    (    BID,    YES,  '0.6',  '2.4',    '0',  '1.2', '0.72',  '2.4',  '1.2',    '0', '0.48',  False,  '1.2',    '0','0.475152',    False,    '0',  '1.2','0.712728', lazy_fixture('contractsFixture')),

    (    BID,     NO,  '0.6',  '1.2',    '0',    '0', '0.72',  '1.2',    '0',  '1.2',    '0',  False,    '0',  '1.2',       '0',    False,    '0',    '0',    '0.72', lazy_fixture('contractsFixture')),
    (    BID,     NO,  '0.6',  '1.2',  '1.2',    '0',    '0',  '1.2',    '0',  '1.2',    '0',  False,    '0',    '0','0.475152',    False,    '0',    '0','0.712728', lazy_fixture('contractsFixture')),
    (    BID,     NO,  '0.6',  '1.2',    '0',    '0', '0.72',  '1.2',    '0',    '0', '0.48',  False,    '0',  '1.2',       '0',    False,  '1.2',    '0',       '0', lazy_fixture('contractsFixture')),
    (    BID,     NO,  '0.6',  '1.2',  '1.2',    '0',    '0',  '1.2',    '0',    '0', '0.48',  False,    '0',    '0',    '0.48',    False,  '1.2',    '0',       '0', lazy_fixture('contractsFixture')),

    (    BID,     NO,  '0.6',  '2.4',  '1.2',    '0', '0.72',  '2.4',    '0',  '2.4',    '0',  False,    '0',  '1.2','0.475152',    False,    '0',    '0','1.432728', lazy_fixture('contractsFixture')),
    (    BID,     NO,  '0.6',  '2.4',  '1.2',    '0', '0.72',  '2.4',    '0',    '0', '0.96',  False,    '0',  '1.2',    '0.48',    False,  '2.4',    '0',       '0', lazy_fixture('contractsFixture')),
    (    BID,     NO,  '0.6',  '2.4',    '0',    '0', '1.44',  '2.4',    '0',  '1.2', '0.48',  False,    '0',  '2.4',       '0',    False,  '1.2',    '0',    '0.72', lazy_fixture('contractsFixture')),
    (    BID,     NO,  '0.6',  '2.4',  '2.4',    '0',    '0',  '2.4',    '0',  '1.2', '0.48',  False,    '0',    '0','0.955152',    False,  '1.2',    '0','0.712728', lazy_fixture('contractsFixture')),

    (    BID,     NO,  '0.6',  '2.4',  '1.2',    '0', '0.72',  '2.4',    '0',  '1.2', '0.48',  False,    '0',  '1.2','0.475152',    False,  '1.2',    '0','0.712728', lazy_fixture('contractsFixture')),

    (    ASK,    YES,  '0.6',  '1.2',  '1.2',    '0',    '0',  '1.2',    '0',    '0', '0.72',  False,    '0',    '0',    '0.72',    False,  '1.2',    '0',       '0', lazy_fixture('contractsFixture')),
    (    ASK,    YES,  '0.6',  '1.2',    '0',    '0', '0.48',  '1.2',    '0',    '0', '0.72',  False,    '0',  '1.2',       '0',    False,  '1.2',    '0',       '0', lazy_fixture('contractsFixture')),
    (    ASK,    YES,  '0.6',  '1.2',  '1.2',    '0',    '0',  '1.2',    '0',  '1.2',    '0',  False,    '0',    '0','0.712728',    False,    '0',    '0','0.475152', lazy_fixture('contractsFixture')),
    (    ASK,    YES,  '0.6',  '1.2',    '0',    '0', '0.48',  '1.2',    '0',  '1.2',    '0',  False,    '0',  '1.2',       '0',    False,    '0',    '0',    '0.48', lazy_fixture('contractsFixture')),
])
def test_parametrized(type, outcome, displayPrice, orderSize, makerYesShares, makerNoShares, makerTokens, takeSize, takerYesShares, takerNoShares, takerTokens, expectMakeRaise, expectedMakerYesShares, expectedMakerNoShares, expectedMakerTokens, expectTakeRaise, expectedTakerYesShares, expectedTakerNoShares, expectedTakerTokens, fixture):
    # TODO: add support for wider range markets
    displayPrice = fix(displayPrice)
    assert displayPrice < 10**18
    assert displayPrice > 0

    orderSize = fix(orderSize)
    makerYesShares = fix(makerYesShares)
    makerNoShares = fix(makerNoShares)
    makerTokens = fix(makerTokens)

    takeSize = fix(takeSize)
    takerYesShares = fix(takerYesShares)
    takerNoShares = fix(takerNoShares)
    takerTokens = fix(takerTokens)

    expectedMakerYesShares = fix(expectedMakerYesShares)
    expectedMakerNoShares = fix(expectedMakerNoShares)
    expectedMakerTokens = fix(expectedMakerTokens)

    expectedTakerYesShares = fix(expectedTakerYesShares)
    expectedTakerNoShares = fix(expectedTakerNoShares)
    expectedTakerTokens = fix(expectedTakerTokens)

    makerAddress = tester.a1
    makerKey = tester.k1
    takerAddress = tester.a2
    takerKey = tester.k2

    cash = fixture.cash
    market = fixture.binaryMarket
    completeSets = fixture.contracts['completeSets']
    makeOrder = fixture.contracts['makeOrder']
    takeOrder = fixture.contracts['takeOrder']
    yesShareToken = fixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('shareToken', market.getShareToken(NO))

    def acquireShares(outcome, amount, approvalAddress, sender):
        if amount == 0: return
        assert cash.publicDepositEther(value=amount, sender = sender)
        assert cash.approve(completeSets.address, amount, sender = sender)
        assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender)
        if outcome == YES:
            assert yesShareToken.approve(approvalAddress, amount, sender = sender)
            assert noShareToken.transfer(0, amount, sender = sender)
        if outcome == NO:
            assert yesShareToken.transfer(0, amount, sender = sender)
            assert noShareToken.approve(approvalAddress, amount, sender = sender)

    def acquireTokens(amount, approvalAddress, sender):
        if amount == 0: return
        assert cash.publicDepositEther(value = amount, sender = sender)
        assert cash.approve(approvalAddress, amount, sender = sender)

    # make order
    acquireShares(YES, makerYesShares, makeOrder.address, sender = makerKey)
    acquireShares(NO, makerNoShares, makeOrder.address, sender = makerKey)
    acquireTokens(makerTokens, makeOrder.address, sender = makerKey)
    with raises(TransactionFailed) if expectMakeRaise else placeholder_context():
        orderID = makeOrder.publicMakeOrder(type, orderSize, displayPrice, market.address, outcome, 0, 0, 42, sender = makerKey)

    # take order
    acquireShares(YES, takerYesShares, takeOrder.address, sender = takerKey)
    acquireShares(NO, takerNoShares, takeOrder.address, sender = takerKey)
    acquireTokens(takerTokens, takeOrder.address, sender = takerKey)
    with raises(TransactionFailed) if expectTakeRaise else placeholder_context():
        takeOrder.publicTakeOrder(orderID, type, market.address, outcome, takeSize, sender = takerKey)

    # assert final state
    assert cash.balanceOf(makerAddress) == expectedMakerTokens
    assert cash.balanceOf(takerAddress) == expectedTakerTokens
    assert yesShareToken.balanceOf(makerAddress) == expectedMakerYesShares
    assert yesShareToken.balanceOf(takerAddress) == expectedTakerYesShares
    assert noShareToken.balanceOf(makerAddress) == expectedMakerNoShares
    assert noShareToken.balanceOf(takerAddress) == expectedTakerNoShares
