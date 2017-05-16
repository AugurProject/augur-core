#!/usr/bin/env python

from ContractsFixture import ContractsFixture
from ethereum import tester
from ethereum.tester import TransactionFailed
from iocapture import capture
from pytest import raises, fixture
from utils import parseCapturedLogs, bytesToLong, longToHexString, bytesToHexString, fix, unfix

tester.gas_limit = long(4.2 * 10**6)

YES = 1
NO = 0

BID = 1
ASK = 2

ATTOSHARES = 0
DISPLAY_PRICE = 1
OWNER = 2
OUTCOME = 3
TOKENS_ESCROWED = 4
SHARES_ESCROWED = 5
BETTER_ORDER_ID = 6
WORSE_ORDER_ID = 7
GAS_PRICE = 8

def test_initialize():
    fixture = ContractsFixture()
    makeOrder = fixture.uploadAndAddToController('../src/trading/makeOrder.se')

    makeOrder.initialize(tester.a0)

    assert makeOrder.setController(tester.a1)

def test_initialize_failure():
    fixture = ContractsFixture()
    makeOrder = fixture.uploadAndAddToController('../src/trading/makeOrder.se')

    with raises(TransactionFailed):
        makeOrder.initialize(tester.a0, sender = tester.k1)
    with raises(TransactionFailed):
        # NOTE: must be last since it changes contract state
        makeOrder.initialize(tester.a0)
        makeOrder.initialize(tester.a1)

def test_setController_failure():
    fixture = ContractsFixture()
    makeOrder = fixture.uploadAndAddToController('../src/trading/makeOrder.se')
    makeOrder.initialize(tester.a0)

    with raises(TransactionFailed):
        makeOrder.setController(tester.a1, sender = tester.k1)

def test_publicMakeOrder_bid():
    fixture = ContractsFixture()
    (_, cash, market, orders, makeOrder, _) = fixture.prepOrders()
    cash.publicDepositEther(value = 10**17)
    cash.approve(makeOrder.address, 10**17)

    orderId = makeOrder.publicMakeOrder(BID, 10**18, 10**17, market.address, 1, 0, 0, 7)
    assert orderId

    order = orders.getOrder(orderId, BID, market.address, 1)
    assert order[ATTOSHARES] == 10**18
    assert order[DISPLAY_PRICE] == 10**17
    assert order[OWNER] == bytesToLong(tester.a0)
    assert order[OUTCOME] == 1
    assert order[TOKENS_ESCROWED] == 10**17
    assert order[SHARES_ESCROWED] == 0
    assert order[BETTER_ORDER_ID] == 0
    assert order[WORSE_ORDER_ID] == 0
    assert order[GAS_PRICE] == 1

def test_publicMakeOrder_ask():
    fixture = ContractsFixture()
    (_, cash, market, orders, makeOrder, _) = fixture.prepOrders()
    cash.publicDepositEther(value = 10**18)
    cash.approve(makeOrder.address, 10**18)

    orderId = makeOrder.publicMakeOrder(ASK, 10**18, 10**17, market.address, 0, 0, 0, 7)

    order = orders.getOrder(orderId, ASK, market.address, 0)
    assert order[ATTOSHARES] == 10**18
    assert order[DISPLAY_PRICE] == 10**17
    assert order[OWNER] == bytesToLong(tester.a0)
    assert order[OUTCOME] == 0
    assert order[TOKENS_ESCROWED] == 10**18 - 10**17
    assert order[SHARES_ESCROWED] == 0
    assert order[BETTER_ORDER_ID] == 0
    assert order[WORSE_ORDER_ID] == 0
    assert order[GAS_PRICE] == 1
    assert cash.balanceOf(market.address) == 10**18 - 10**17

def test_publicMakeOrder_bid2():
    fixture = ContractsFixture()
    (_, cash, market, orders, makeOrder, _) = fixture.prepOrders()

    orderType = BID
    fxpAmount = fix(1)
    fxpPrice = fix("0.6")
    outcome = 0
    tradeGroupID = 42

    assert cash.publicDepositEther(value = fix(10), sender = tester.k1) == 1, "Deposit cash"
    assert cash.approve(makeOrder.address, fix(10), sender = tester.k1) == 1, "Approve makeOrder contract to spend cash"
    makerInitialCash = cash.balanceOf(tester.a1)
    marketInitialCash = cash.balanceOf(market.address)
    with capture() as captured:
        orderID = makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, market.address, outcome, 0, 0, tradeGroupID, sender=tester.k1)
        logged = captured.stdout
    logMakeOrder = parseCapturedLogs(logged)[-1]
    assert orderID != 0, "Order ID should be non-zero"
    order = orders.getOrder(orderID, orderType, market.address, outcome)
    assert len(order) == 9, "Order array length should be 13"
    assert order[ATTOSHARES] == fxpAmount, "order[ATTOSHARES] should be the amount of the order"
    assert order[DISPLAY_PRICE] == fxpPrice, "order[DISPLAY_PRICE] should be the order's price"
    assert order[OWNER] == bytesToLong(tester.a1), "order[OWNER] should be the sender's address"
    assert order[OUTCOME] == outcome, "order[OUTCOME] should be the outcome ID"
    assert order[TOKENS_ESCROWED] == 0.6 * 10**18, "order[TOKENS_ESCROWED] should be the amount of money escrowed"
    assert order[SHARES_ESCROWED] == 0, "order[SHARES_ESCROWED] should be the number of shares escrowed"
    assert makerInitialCash - cash.balanceOf(tester.a1) == order[TOKENS_ESCROWED], "Decrease in maker's cash balance should equal money escrowed"
    assert cash.balanceOf(market.address) - marketInitialCash == order[TOKENS_ESCROWED], "Increase in market's cash balance should equal money escrowed"
    assert logMakeOrder["_event_type"] == "MakeOrder", "Should emit a MakeOrder event"
    assert logMakeOrder["tradeGroupID"] == tradeGroupID, "Logged tradeGroupID should match input"
    assert logMakeOrder["fxpMoneyEscrowed"] == order[TOKENS_ESCROWED], "Logged fxpMoneyEscrowed should match amount in order"
    assert logMakeOrder["fxpSharesEscrowed"] == order[SHARES_ESCROWED], "Logged fxpSharesEscrowed should match amount in order"
    assert logMakeOrder["timestamp"] == fixture.state.block.timestamp, "Logged timestamp should match the current block timestamp"
    assert logMakeOrder["orderID"] == longToHexString(orderID), "Logged orderID should match returned orderID"
    assert logMakeOrder["outcome"] == outcome, "Logged outcome should match input"
    assert logMakeOrder["market"] == longToHexString(market.address), "Logged market should match input"
    assert logMakeOrder["sender"] == bytesToHexString(tester.a1), "Logged sender should match input"

def test_makeOrder_failure():
    fixture = ContractsFixture()
    orders = fixture.initializeOrders()
    makeOrder = fixture.initializeMakeOrder()
    takeOrder = fixture.initializeTakeOrder()
    completeSets = fixture.initializeCompleteSets()
    branch = fixture.createBranch(0, 0)
    cash = fixture.getSeededCash()
    market = fixture.createReasonableBinaryMarket(branch, cash)
    yesShareToken = fixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('shareToken', market.getShareToken(NO))

    with raises(TransactionFailed):
        makeOrder.makeOrder(tester.a1, ASK, fix(1), fix(0.6), market.address, YES, 0, 0, 42, sender=tester.k1)
    with raises(TransactionFailed):
        makeOrder.placeAsk(tester.a1, fix(1), fix(0.6), market.address, YES, sender=tester.k1)
    with raises(TransactionFailed):
        makeOrder.placeBid(tester.a1, fix(1), fix(0.6), market.address, YES, sender=tester.k1)

    # makeOrder exceptions (pre-placeBid/placeAsk)
    with raises(TransactionFailed):
        makeOrder.publicMakeOrder(ASK, fix(1), fix(0.6), market.address - 1, YES, 0, 0, 42, sender=tester.k1)
    with raises(TransactionFailed):
        makeOrder.publicMakeOrder(3, fix(1), fix(0.6), market.address, YES, 0, 0, 42, sender=tester.k1)

    # placeBid exceptions
    with raises(TransactionFailed):
        makeOrder.publicMakeOrder(BID, fix(1), fix(3), market.address, YES, 0, 0, 42, sender=tester.k1)
    with raises(TransactionFailed):
        makeOrder.publicMakeOrder(BID, 1, fix(0.6), market.address, YES, 0, 0, 42, sender=tester.k1)

    # placeAsk exceptions
    with raises(TransactionFailed):
        makeOrder.publicMakeOrder(ASK, fix(1), 1, market.address, YES, 0, 0, 42, sender=tester.k1)
    with raises(TransactionFailed):
        makeOrder.publicMakeOrder(ASK, 1, fix(0.6), market.address, YES, 0, 0, 42, sender=tester.k1)
    assert cash.publicDepositEther(value=fix(2), sender=tester.k1)
    assert cash.approve(completeSets.address, fix(2), sender=tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, fix(2), sender=tester.k1)
    with raises(TransactionFailed):
        makeOrder.publicMakeOrder(ASK, fix(1), fix(3), market.address, YES, 0, 0, 42, sender=tester.k1)
    with raises(TransactionFailed):
        makeOrder.publicMakeOrder(ASK, 1, fix(0.6), market.address, YES, 0, 0, 42, sender=tester.k1)

    assert cash.approve(makeOrder.address, fix(100), sender=tester.k1) == 1, "Approve makeOrder contract to spend cash from account 1"
    assert yesShareToken.approve(makeOrder.address, fix(12), sender=tester.k1) == 1, "Approve makeOrder contract to spend shares from the user's account (account 1)"
    assert yesShareToken.allowance(tester.a1, makeOrder.address) == fix(12), "makeOrder contract's allowance should be equal to the amount approved"
    assert makeOrder.publicMakeOrder(ASK, fix(1), fix(0.6), market.address, YES, 0, 0, 42, sender=tester.k1) != 0, "Order ID should be non-zero"

    # makeOrder exceptions (post-placeBid/Ask)
    with raises(TransactionFailed):
        makeOrder.publicMakeOrder(ASK, fix(1), fix(0.6), market.address, YES, 0, 0, 42, sender=tester.k1)

def test_ask_withPartialShares():
    fixture = ContractsFixture()
    orders = fixture.initializeOrders()
    makeOrder = fixture.initializeMakeOrder()
    takeOrder = fixture.initializeTakeOrder()
    completeSets = fixture.initializeCompleteSets()
    branch = fixture.createBranch(0, 0)
    cash = fixture.getSeededCash()
    market = fixture.createReasonableBinaryMarket(branch, cash)
    yesShareToken = fixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('shareToken', market.getShareToken(NO))

    # buy 1.2 complete sets
    assert cash.publicDepositEther(value=fix(1.2), sender = tester.k1)
    assert cash.approve(completeSets.address, fix(1.2), sender = tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, fix(1.2), sender = tester.k1)
    assert cash.balanceOf(tester.a1) == fix(0)
    assert yesShareToken.balanceOf(tester.a1) == fix(1.2)
    assert noShareToken.balanceOf(tester.a1) == fix(1.2)

    # get enough cash to cover shorting 0.8 more shares
    assert cash.publicDepositEther(value=long(fix(0.8) * 0.4), sender = tester.k1)
    assert cash.balanceOf(tester.a1) == fix(0.32)

    # create ASK order for 2 shares with a mix of shares and cash
    assert yesShareToken.approve(makeOrder.address, fix(1.2), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix(0.32), sender = tester.k1)
    with capture() as captured:
        orderID = makeOrder.publicMakeOrder(ASK, fix(2), fix(0.6), market.address, YES, 0, 0, 42, sender=tester.k1)
        logMakeOrder = parseCapturedLogs(captured.stdout)[-1]
    assert cash.balanceOf(tester.a1) == fix(0)
    assert yesShareToken.balanceOf(tester.a1) == fix(0)
    assert noShareToken.balanceOf(tester.a1) == fix(1.2)

    # validate the order contains expected results
    assert orderID != 0, "Order ID should be non-zero"
    order = orders.getOrder(orderID, ASK, market.address, YES)
    assert len(order) == 9, "Order array length should be 13"
    assert order[ATTOSHARES] == fix(2), "order[ATTOSHARES] should be the amount of the order"
    assert order[DISPLAY_PRICE] == fix(0.6), "order[DISPLAY_PRICE] should be the order's price"
    assert order[OWNER] == bytesToLong(tester.a1), "order[OWNER] should be the sender's address"
    assert order[OUTCOME] == YES, "order[6] should be the outcome ID"
    assert order[TOKENS_ESCROWED] == fix(0.32), "order[TOKENS_ESCROWED] should be the amount of money escrowed"
    assert order[SHARES_ESCROWED] == fix(1.2), "order[SHARES_ESCROWED] should be the number of shares escrowed"

    # validate the log output of the order
    assert logMakeOrder["_event_type"] == "MakeOrder", "Should emit a MakeOrder event"
    assert logMakeOrder["tradeGroupID"] == 42, "Logged tradeGroupID should match input"
    assert logMakeOrder["fxpMoneyEscrowed"] == order[TOKENS_ESCROWED], "Logged fxpMoneyEscrowed should match amount in order"
    assert logMakeOrder["fxpSharesEscrowed"] == order[SHARES_ESCROWED], "Logged fxpSharesEscrowed should match amount in order"
    assert logMakeOrder["timestamp"] == fixture.state.block.timestamp, "Logged timestamp should match the current block timestamp"
    assert logMakeOrder["orderID"] == longToHexString(orderID), "Logged orderID should match returned orderID"
    assert logMakeOrder["outcome"] == YES, "Logged outcome should match input"
    assert logMakeOrder["market"] == longToHexString(market.address), "Logged market should match input"
    assert logMakeOrder["sender"] == bytesToHexString(tester.a1), "Logged sender should match input"
