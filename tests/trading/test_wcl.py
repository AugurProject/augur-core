#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, mark
from utils import longTo32Bytes, fix, AssertLog
from constants import BID, ASK, YES, NO

tester.STARTGAS = long(6.7 * 10**6)


def test_create_ask_with_shares_fill_with_shares(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    completeSetFees = fix('12', '0.02') * market.getNumTicks()

    # 1. both accounts buy a complete set
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k1, value=fix('12', market.getNumTicks()))
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k2, value=fix('12', market.getNumTicks()))
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert yesShareToken.balanceOf(tester.a2) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a2) == fix(12)

    # 2. create ASK order for YES with YES shares for escrow
    assert yesShareToken.approve(createOrder.address, fix(12), sender = tester.k1)
    askOrderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1)
    assert askOrderID
    assert cash.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == fix(12)

    # 3. fill ASK order for YES with NO shares
    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    assert noShareToken.approve(fillOrder.address, fix(12), sender = tester.k2)
    fxpAmountRemaining = fillOrder.publicFillOrder(askOrderID, fix(12), sender = tester.k2)
    creatorFee = completeSetFees * 0.6
    fillerFee = completeSetFees * 0.4
    assert fxpAmountRemaining == 0
    assert cash.balanceOf(tester.a1) == 0
    assert cash.balanceOf(tester.a2) == 0
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH + fix('12', '6000') - long(creatorFee)
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH + fix('12', '4000') - long(fillerFee)
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a2) == 0

def test_create_ask_with_shares_fill_with_cash(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy a complete set with account 1
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k1, value=fix('12', market.getNumTicks()))
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix(12), "Account 1 should have 12 shares of outcome 1"
    assert noShareToken.balanceOf(tester.a1) == fix(12), "Account 1 should have 12 shares of outcome 2"

    # 2. create ASK order for YES with YES shares for escrow
    assert yesShareToken.approve(createOrder.address, fix(12), sender = tester.k1)
    askOrderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1)
    assert askOrderID, "Order ID should be non-zero"
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == fix(12)

    # 3. fill ASK order for YES with cash
    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    fxpAmountRemaining = fillOrder.publicFillOrder(askOrderID, fix(12), sender = tester.k2, value=fix('12', '6000'))
    assert fxpAmountRemaining == 0
    assert cash.balanceOf(tester.a1) == 0
    assert cash.balanceOf(tester.a2) == 0
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH + fix('12', '6000')
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH - fix('12', '6000')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a2) == 0

def test_create_ask_with_cash_fill_with_shares(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 2
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k2, value=fix('12', market.getNumTicks()))
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix(12)
    assert noShareToken.balanceOf(tester.a2) == fix(12)

    # 2. create ASK order for YES with cash escrowed
    askOrderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1, value=fix('12', '4000'))
    assert askOrderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 0

    # 3. fill ASK order for YES with shares of NO
    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    assert noShareToken.approve(fillOrder.address, fix(12), sender = tester.k2)
    amountRemaining = fillOrder.publicFillOrder(askOrderID, fix(12), sender = tester.k2)
    assert amountRemaining == 0, "Amount remaining should be 0"
    assert cash.balanceOf(tester.a1) == 0
    assert cash.balanceOf(tester.a2) == 0
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH + fix('12', '4000')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a2) == 0

def test_create_ask_with_cash_fill_with_cash(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. create ASK order for YES with cash escrowed
    askOrderID = createOrder.publicCreateOrder(ASK, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1, value=fix('12', '4000'))
    assert askOrderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 0

    # 2. fill ASK order for YES with cash
    fxpAmountRemaining = fillOrder.publicFillOrder(askOrderID, fix(12), sender = tester.k2, value=fix('12', '6000'))
    assert fxpAmountRemaining == 0
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a2) == 0

def test_create_bid_with_shares_fill_with_shares(contractsFixture, cash, market, universe):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    totalProceeds = fix('12', market.getNumTicks())
    marketCreatorFee = totalProceeds / market.getMarketCreatorSettlementFeeDivisor()
    reporterFee = totalProceeds / universe.getOrCacheReportingFeeDivisor()
    completeSetFees = marketCreatorFee + reporterFee

    # 1. buy complete sets with both accounts
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k1, value=fix('12', market.getNumTicks()))
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k2, value=fix('12', market.getNumTicks()))
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix(12)
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a2) == fix(12)

    # 2. create BID order for YES with NO shares escrowed
    assert noShareToken.approve(createOrder.address, fix(12), sender = tester.k1)
    orderID = createOrder.publicCreateOrder(BID, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == 0

    # 3. fill BID order for YES with shares of YES
    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    assert yesShareToken.approve(fillOrder.address, fix(12), sender = tester.k2)

    orderFilledLog = {
        'marketCreatorFees': marketCreatorFee,
        'reporterFees': reporterFee,
    }
    with AssertLog(contractsFixture, 'OrderFilled', orderFilledLog):
        leftoverInOrder = fillOrder.publicFillOrder(orderID, fix(12), sender = tester.k2)
        assert leftoverInOrder == 0

    creatorFee = completeSetFees * 0.4
    fillerFee = completeSetFees * 0.6
    creatorPayment = fix('12', '4000') - long(creatorFee)
    fillerPayment = fix('12', '6000') - long(fillerFee)
    assert cash.balanceOf(tester.a1) == 0
    assert cash.balanceOf(tester.a2) == 0
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH + long(creatorPayment)
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH + long(fillerPayment)
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == fix(12)

def test_create_bid_with_shares_fill_with_cash(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 1
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k1, value=fix('12', market.getNumTicks()))
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == fix(12)

    # 2. create BID order for YES with NO shares escrowed
    assert noShareToken.approve(createOrder.address, fix(12), sender = tester.k1)
    orderID = createOrder.publicCreateOrder(BID, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1)
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert noShareToken.balanceOf(tester.a1) == 0

    # 3. fill BID order for YES with cash
    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    leftoverInOrder = fillOrder.publicFillOrder(orderID, fix(12), sender = tester.k2, value=fix('12', '4000'))
    assert leftoverInOrder == 0
    assert cash.balanceOf(tester.a1) == 0
    assert cash.balanceOf(tester.a2) == 0
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH + fix('12', '4000')
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH - fix('12', '4000')
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == fix(12)

def test_create_bid_with_cash_fill_with_shares(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. buy complete sets with account 2
    assert completeSets.publicBuyCompleteSets(market.address, fix(12), sender = tester.k2, value=fix('12', market.getNumTicks()))
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a2) == fix(12)
    assert noShareToken.balanceOf(tester.a2) == fix(12)

    # 2. create BID order for YES with cash escrowed
    orderID = createOrder.publicCreateOrder(BID, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1, value=fix('12', '6000'))
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 0

    # 3. fill BID order for YES with shares of YES
    initialMakerETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialFillerETH = contractsFixture.chain.head_state.get_balance(tester.a2)
    assert yesShareToken.approve(fillOrder.address, fix(12), sender = tester.k2)
    leftoverInOrder = fillOrder.publicFillOrder(orderID, fix(12), sender = tester.k2)
    assert leftoverInOrder == 0
    assert cash.balanceOf(tester.a1) == 0
    assert cash.balanceOf(tester.a2) == 0
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialMakerETH
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialFillerETH + fix('12', '6000')
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == fix(12)

def test_create_bid_with_cash_fill_with_cash(contractsFixture, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']

    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # 1. create BID order for YES with cash escrowed
    orderID = createOrder.publicCreateOrder(BID, fix(12), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender = tester.k1, value=fix('12', '6000'))
    assert orderID
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 0

    # 2. fill BID order for YES with cash
    leftoverInOrder = fillOrder.publicFillOrder(orderID, fix(12), sender = tester.k2, value=fix('12', '4000'))
    assert leftoverInOrder == 0
    assert cash.balanceOf(tester.a1) == fix('0')
    assert cash.balanceOf(tester.a2) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == fix(12)
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == fix(12)

import contextlib
@contextlib.contextmanager
def placeholder_context():
    yield None

@mark.parametrize('type,outcome,displayPrice,orderSize,creatorYesShares,creatorNoShares,creatorCost,fillSize,fillerYesShares,fillerNoShares,fillerCost,expectMakeRaise,expectedMakerYesShares,expectedMakerNoShares,expectedMakerPayout,expectTakeRaise,expectedFillerYesShares,expectedFillerNoShares,expectedFillerPayout', [
    # | ------ ORDER ------ |   | ------ CREATOR START ------ |   | ------ FILLER START ------ |  | ------- CREATOR FINISH -------  |    | ------- FILLER FINISH -------  |
    #   type,outcome,  price,   size,    yes,     no,   cost,   size,    yes,     no,   cost,  raise,    yes,     no,      pay,    raise,    yes,     no,      pay,
    (    BID,    YES,  '0.6',  '12',    '0',    '0',  '7.2',  '12',   '12',    '0',    '0',  False,   '12',    '0',       '0',    False,    '0',    '0',     '7.2'),
    (    BID,    YES,  '0.6',  '12',    '0',   '12',    '0',  '12',   '12',    '0',    '0',  False,    '0',    '0',   '4.704',    False,    '0',    '0',   '7.056'),
    (    BID,    YES,  '0.6',  '12',    '0',    '0',  '7.2',  '12',    '0',    '0',  '4.8',  False,   '12',    '0',       '0',    False,    '0',   '12',       '0'),
    (    BID,    YES,  '0.6',  '12',    '0',   '12',    '0',  '12',    '0',    '0',  '4.8',  False,    '0',    '0',     '4.8',    False,    '0',   '12',       '0'),

    (    BID,    YES,  '0.6',  '24',    '0',   '12',  '7.2',  '24',   '24',    '0',    '0',  False,   '12',    '0',   '4.704',    False,    '0',    '0',  '14.256'),
    (    BID,    YES,  '0.6',  '24',    '0',   '12',  '7.2',  '24',    '0',    '0',  '9.6',  False,   '12',    '0',     '4.8',    False,    '0',   '24',       '0'),
    (    BID,    YES,  '0.6',  '24',    '0',    '0', '14.4',  '24',   '12',    '0',  '4.8',  False,   '24',    '0',       '0',    False,    '0',   '12',     '7.2'),
    (    BID,    YES,  '0.6',  '24',    '0',   '24',    '0',  '24',   '12',    '0',  '4.8',  False,    '0',    '0',   '9.504',    False,    '0',   '12',   '7.056'),

    (    BID,    YES,  '0.6',  '24',    '0',   '12',  '7.2',  '24',   '12',    '0',  '4.8',  False,   '12',    '0',   '4.704',    False,    '0',   '12',   '7.056'),

    (    BID,     NO,  '0.6',  '12',    '0',    '0',  '7.2',  '12',    '0',   '12',    '0',  False,    '0',   '12',       '0',    False,    '0',    '0',     '7.2'),
    (    BID,     NO,  '0.6',  '12',   '12',    '0',    '0',  '12',    '0',   '12',    '0',  False,    '0',    '0',   '4.704',    False,    '0',    '0',   '7.056'),
    (    BID,     NO,  '0.6',  '12',    '0',    '0',  '7.2',  '12',    '0',    '0',  '4.8',  False,    '0',   '12',       '0',    False,   '12',    '0',       '0'),
    (    BID,     NO,  '0.6',  '12',   '12',    '0',    '0',  '12',    '0',    '0',  '4.8',  False,    '0',    '0',     '4.8',    False,   '12',    '0',       '0'),

    (    BID,     NO,  '0.6',  '24',   '12',    '0',  '7.2',  '24',    '0',   '24',    '0',  False,    '0',   '12',   '4.704',    False,    '0',    '0',  '14.256'),
    (    BID,     NO,  '0.6',  '24',   '12',    '0',  '7.2',  '24',    '0',    '0',  '9.6',  False,    '0',   '12',     '4.8',    False,   '24',    '0',       '0'),
    (    BID,     NO,  '0.6',  '24',    '0',    '0', '14.4',  '24',    '0',   '12',  '4.8',  False,    '0',   '24',       '0',    False,   '12',    '0',     '7.2'),
    (    BID,     NO,  '0.6',  '24',   '24',    '0',    '0',  '24',    '0',   '12',  '4.8',  False,    '0',    '0',   '9.504',    False,   '12',    '0',   '7.056'),

    (    BID,     NO,  '0.6',  '24',   '12',    '0',  '7.2',  '24',    '0',   '12',  '4.8',  False,    '0',   '12',   '4.704',    False,   '12',    '0',   '7.056'),

    (    ASK,    YES,  '0.6',  '12',   '12',    '0',    '0',  '12',    '0',    '0',  '7.2',  False,    '0',    '0',     '7.2',    False,   '12',    '0',       '0'),
    (    ASK,    YES,  '0.6',  '12',    '0',    '0',  '4.8',  '12',    '0',    '0',  '7.2',  False,    '0',   '12',       '0',    False,   '12',    '0',       '0'),
    (    ASK,    YES,  '0.6',  '12',   '12',    '0',    '0',  '12',    '0',   '12',    '0',  False,    '0',    '0',   '7.056',    False,    '0',    '0',   '4.704'),
    (    ASK,    YES,  '0.6',  '12',    '0',    '0',  '4.8',  '12',    '0',   '12',    '0',  False,    '0',   '12',       '0',    False,    '0',    '0',     '4.8'),
])
def test_parametrized(type, outcome, displayPrice, orderSize, creatorYesShares, creatorNoShares, creatorCost, fillSize, fillerYesShares, fillerNoShares, fillerCost, expectMakeRaise, expectedMakerYesShares, expectedMakerNoShares, expectedMakerPayout, expectTakeRaise, expectedFillerYesShares, expectedFillerNoShares, expectedFillerPayout, contractsFixture, cash, market):
    fixture = contractsFixture
    # TODO: add support for wider range markets
    displayPrice = int(float(displayPrice) * market.getNumTicks())
    assert displayPrice < market.getNumTicks()
    assert displayPrice > 0

    orderSize = fix(orderSize)
    creatorYesShares = fix(creatorYesShares)
    creatorNoShares = fix(creatorNoShares)
    creatorCost = fix(creatorCost, market.getNumTicks())

    fillSize = fix(fillSize)
    fillerYesShares = fix(fillerYesShares)
    fillerNoShares = fix(fillerNoShares)
    fillerCost = fix(fillerCost, market.getNumTicks())

    expectedMakerYesShares = fix(expectedMakerYesShares)
    expectedMakerNoShares = fix(expectedMakerNoShares)
    expectedMakerPayout = fix(expectedMakerPayout, market.getNumTicks())

    expectedFillerYesShares = fix(expectedFillerYesShares)
    expectedFillerNoShares = fix(expectedFillerNoShares)
    expectedFillerPayout = fix(expectedFillerPayout, market.getNumTicks())

    creatorAddress = tester.a1
    creatorKey = tester.k1
    fillerAddress = tester.a2
    fillerKey = tester.k2

    completeSets = fixture.contracts['CompleteSets']
    createOrder = fixture.contracts['CreateOrder']
    fillOrder = fixture.contracts['FillOrder']
    yesShareToken = fixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('ShareToken', market.getShareToken(NO))

    def acquireShares(outcome, amount, approvalAddress, sender):
        if amount == 0: return
        assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender, value=amount * market.getNumTicks())
        if outcome == YES:
            assert yesShareToken.approve(approvalAddress, amount, sender = sender)
            assert noShareToken.transfer(0, amount, sender = sender)
        if outcome == NO:
            assert yesShareToken.transfer(0, amount, sender = sender)
            assert noShareToken.approve(approvalAddress, amount, sender = sender)

    # create order
    acquireShares(YES, creatorYesShares, createOrder.address, sender = creatorKey)
    acquireShares(NO, creatorNoShares, createOrder.address, sender = creatorKey)
    with raises(TransactionFailed) if expectMakeRaise else placeholder_context():
        orderID = createOrder.publicCreateOrder(type, orderSize, displayPrice, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "42", sender = creatorKey, value = creatorCost)

    # fill order
    acquireShares(YES, fillerYesShares, fillOrder.address, sender = fillerKey)
    acquireShares(NO, fillerNoShares, fillOrder.address, sender = fillerKey)
    initialMakerETH = fixture.chain.head_state.get_balance(creatorAddress)
    initialFillerETH = fixture.chain.head_state.get_balance(fillerAddress)
    with raises(TransactionFailed) if expectTakeRaise else placeholder_context():
        fillOrder.publicFillOrder(orderID, fillSize, sender = fillerKey, value = fillerCost)

    # assert final state
    assert cash.balanceOf(creatorAddress) == 0
    assert cash.balanceOf(fillerAddress) == 0
    assert fixture.chain.head_state.get_balance(creatorAddress) == initialMakerETH + expectedMakerPayout
    assert fixture.chain.head_state.get_balance(fillerAddress) == initialFillerETH + expectedFillerPayout - fillerCost
    assert yesShareToken.balanceOf(creatorAddress) == expectedMakerYesShares
    assert yesShareToken.balanceOf(fillerAddress) == expectedFillerYesShares
    assert noShareToken.balanceOf(creatorAddress) == expectedMakerNoShares
    assert noShareToken.balanceOf(fillerAddress) == expectedFillerNoShares
