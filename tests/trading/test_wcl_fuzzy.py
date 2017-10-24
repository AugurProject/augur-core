#!/usr/bin/env python

from ethereum.tools import tester
from os import getenv
from pytest import fixture, mark
from random import randint, random as randfloat
from utils import bytesToLong, longTo32Bytes, bytesToHexString, fix
from constants import BID, ASK, YES, NO

pytestmark = mark.skipif(not getenv('INCLUDE_FUZZY_TESTS'), reason="take forever to run")


# order fields
ATTOSHARES = 0
DISPLAY_PRICE = 1
OWNER = 2
TOKENS_ESCROWED = 3
SHARES_ESCROWED = 4
BETTER_ORDER_ID = 5
WORSE_ORDER_ID = 6
GAS_PRICE = 7

# TODO: turn these into 24 parameterized tests rather than 3 tests that each execute 8 sub-tests

def execute(contractsFixture, universe, cash, market, orderType, orderSize, orderPrice, orderOutcome, creatorLongShares, creatorShortShares, creatorTokens, fillerLongShares, fillerShortShares, fillerTokens, expectedMakerLongShares, expectedMakerShortShares, expectedMakerTokens, expectedFillerLongShares, expectedFillerShortShares, expectedFillerTokens):
    def acquireLongShares(outcome, amount, approvalAddress, sender):
        if amount == 0: return

        shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(outcome))
        completeSets = contractsFixture.contracts['CompleteSets']
        createOrder = contractsFixture.contracts['CreateOrder']
        fillOrder = contractsFixture.contracts['FillOrder']

        cashRequired = amount * market.getNumTicks() / 10**18
        assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender, value = cashRequired)
        assert shareToken.approve(approvalAddress, amount, sender = sender)
        for otherOutcome in range(0, market.getNumberOfOutcomes()):
            if otherOutcome == outcome: continue
            otherShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(otherOutcome))
            assert otherShareToken.transfer(0, amount, sender = sender)

    def acquireShortShareSet(outcome, amount, approvalAddress, sender):
        if amount == 0: return

        shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(outcome))
        completeSets = contractsFixture.contracts['CompleteSets']
        createOrder = contractsFixture.contracts['CreateOrder']
        fillOrder = contractsFixture.contracts['FillOrder']

        cashRequired = amount * market.getNumTicks() / 10**18
        assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender, value = cashRequired)
        assert shareToken.transfer(0, amount, sender = sender)
        for otherOutcome in range(0, market.getNumberOfOutcomes()):
            if otherOutcome == outcome: continue
            otherShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(otherOutcome))
            assert otherShareToken.approve(approvalAddress, amount, sender = sender)

    legacyReputationToken = contractsFixture.contracts['LegacyReputationToken']
    legacyReputationToken.faucet(long(11 * 10**6 * 10**18))
    contractsFixture.chain.head_state.timestamp += 15000

    # Get the reputation token for this universe and migrate legacy REP to it
    reputationToken = contractsFixture.applySignature('ReputationToken', universe.getReputationToken())
    legacyReputationToken.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyReputationToken()

    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    completeSets = contractsFixture.contracts['CompleteSets']

    creatorAddress = tester.a1
    fillerAddress = tester.a2
    creatorKey = tester.k1
    fillerKey = tester.k2

    # create order
    acquireLongShares(orderOutcome, creatorLongShares, createOrder.address, sender = creatorKey)
    acquireShortShareSet(orderOutcome, creatorShortShares, createOrder.address, sender = creatorKey)
    orderID = createOrder.publicCreateOrder(orderType, orderSize, orderPrice, market.address, orderOutcome, longTo32Bytes(0), longTo32Bytes(0), 42, sender = creatorKey, value = creatorTokens)

    # validate the order
    order = ordersFetcher.getOrder(orderID)
    assert order[ATTOSHARES] == orderSize
    assert order[DISPLAY_PRICE] == orderPrice
    assert order[OWNER] == bytesToHexString(creatorAddress)
    assert order[TOKENS_ESCROWED] == creatorTokens
    assert order[SHARES_ESCROWED] == creatorLongShares or creatorShortShares

    # fill order
    acquireLongShares(orderOutcome, fillerLongShares, fillOrder.address, sender = fillerKey)
    acquireShortShareSet(orderOutcome, fillerShortShares, fillOrder.address, sender = fillerKey)
    remaining = fillOrder.publicFillOrder(orderID, orderSize, 42, sender = fillerKey, value = fillerTokens)
    assert not remaining

    # assert final state
    assert cash.balanceOf(creatorAddress) == expectedMakerTokens
    assert cash.balanceOf(fillerAddress) == expectedFillerTokens
    for outcome in range(0, market.getNumberOfOutcomes()):
        shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(outcome))
        if outcome == orderOutcome:
            assert shareToken.balanceOf(creatorAddress) == expectedMakerLongShares
            assert shareToken.balanceOf(fillerAddress) == expectedFillerLongShares
        else:
            assert shareToken.balanceOf(creatorAddress) == expectedMakerShortShares
            assert shareToken.balanceOf(fillerAddress) == expectedFillerShortShares

def execute_bidOrder_tests(contractsFixture, universe, market, fxpAmount, fxpPrice):
    longCost = long(fxpAmount * fxpPrice / 10**18)
    shortCost = long(fxpAmount * (market.getNumTicks() - fxpPrice) / 10**18)
    completeSetFees = long(fxpAmount * market.getNumTicks() * fix('0.0101') / 10**18 / 10**18)
    shortFee = long((completeSetFees * shortCost) / (longCost + shortCost))
    longFee = completeSetFees - shortFee

    print "creator escrows cash, filler pays with cash"
    execute(
        contractsFixture = contractsFixture,
        universe = universe,
        market = market,
        orderType = BID,
        orderSize = fxpAmount,
        orderPrice = fxpPrice,
        orderOutcome = YES,
        creatorLongShares = 0,
        creatorShortShares = 0,
        creatorTokens = longCost,
        fillerLongShares = 0,
        fillerShortShares = 0,
        fillerTokens = shortCost,
        expectedMakerLongShares = fxpAmount,
        expectedMakerShortShares = 0,
        expectedMakerTokens = 0,
        expectedFillerLongShares = 0,
        expectedFillerShortShares = fxpAmount,
        expectedFillerTokens = 0)

    print "creator escrows shares, filler pays with shares"
    execute(
        contractsFixture = contractsFixture,
        universe = universe,
        market = market,
        orderType = BID,
        orderSize = fxpAmount,
        orderPrice = fxpPrice,
        orderOutcome = YES,
        creatorLongShares = 0,
        creatorShortShares = fxpAmount,
        creatorTokens = 0,
        fillerLongShares = fxpAmount,
        fillerShortShares = 0,
        fillerTokens = 0,
        expectedMakerLongShares = 0,
        expectedMakerShortShares = 0,
        expectedMakerTokens = shortCost - shortFee,
        expectedFillerLongShares = 0,
        expectedFillerShortShares = 0,
        expectedFillerTokens = longCost - longFee)

    print "creator escrows cash, filler pays with shares"
    execute(
        contractsFixture = contractsFixture,
        universe = universe,
        market = market,
        orderType = BID,
        orderSize = fxpAmount,
        orderPrice = fxpPrice,
        orderOutcome = YES,
        creatorLongShares = 0,
        creatorShortShares = 0,
        creatorTokens = longCost,
        fillerLongShares = fxpAmount,
        fillerShortShares = 0,
        fillerTokens = 0,
        expectedMakerLongShares = fxpAmount,
        expectedMakerShortShares = 0,
        expectedMakerTokens = 0,
        expectedFillerLongShares = 0,
        expectedFillerShortShares = 0,
        expectedFillerTokens = longCost)

    print "creator escrows shares, filler pays with cash"
    execute(
        contractsFixture = contractsFixture,
        universe = universe,
        market = market,
        orderType = BID,
        orderSize = fxpAmount,
        orderPrice = fxpPrice,
        orderOutcome = YES,
        creatorLongShares = 0,
        creatorShortShares = fxpAmount,
        creatorTokens = 0,
        fillerLongShares = 0,
        fillerShortShares = 0,
        fillerTokens = shortCost,
        expectedMakerLongShares = 0,
        expectedMakerShortShares = 0,
        expectedMakerTokens = shortCost,
        expectedFillerLongShares = 0,
        expectedFillerShortShares = fxpAmount,
        expectedFillerTokens = 0)

def execute_askOrder_tests(contractsFixture, universe, market, fxpAmount, fxpPrice):
    longCost = long(fxpAmount * fxpPrice / 10**18)
    shortCost = long(fxpAmount * (market.getNumTicks() - fxpPrice) / 10**18)
    completeSetFees = long(fxpAmount * market.getNumTicks() * fix('0.0101') / 10**18 / 10**18)
    longFee = long((completeSetFees * longCost) / (longCost + shortCost))
    shortFee = completeSetFees - longFee

    print "creator escrows cash, filler pays with cash"
    execute(
        contractsFixture = contractsFixture,
        universe = universe,
        market = market,
        orderType = ASK,
        orderSize = fxpAmount,
        orderPrice = fxpPrice,
        orderOutcome = YES,
        creatorLongShares = 0,
        creatorShortShares = 0,
        creatorTokens = shortCost,
        fillerLongShares = 0,
        fillerShortShares = 0,
        fillerTokens = longCost,
        expectedMakerLongShares = 0,
        expectedMakerShortShares = fxpAmount,
        expectedMakerTokens = 0,
        expectedFillerLongShares = fxpAmount,
        expectedFillerShortShares = 0,
        expectedFillerTokens = 0)

    print "creator escrows shares, filler pays with shares"
    execute(
        contractsFixture = contractsFixture,
        universe = universe,
        market = market,
        orderType = ASK,
        orderSize = fxpAmount,
        orderPrice = fxpPrice,
        orderOutcome = YES,
        creatorLongShares = fxpAmount,
        creatorShortShares = 0,
        creatorTokens = 0,
        fillerLongShares = 0,
        fillerShortShares = fxpAmount,
        fillerTokens = 0,
        expectedMakerLongShares = 0,
        expectedMakerShortShares = 0,
        expectedMakerTokens = longCost - longFee,
        expectedFillerLongShares = 0,
        expectedFillerShortShares = 0,
        expectedFillerTokens = shortCost - shortFee)

    print "creator escrows cash, filler pays with shares"
    execute(
        contractsFixture = contractsFixture,
        universe = universe,
        market = market,
        orderType = ASK,
        orderSize = fxpAmount,
        orderPrice = fxpPrice,
        orderOutcome = YES,
        creatorLongShares = 0,
        creatorShortShares = 0,
        creatorTokens = shortCost,
        fillerLongShares = 0,
        fillerShortShares = fxpAmount,
        fillerTokens = 0,
        expectedMakerLongShares = 0,
        expectedMakerShortShares = fxpAmount,
        expectedMakerTokens = 0,
        expectedFillerLongShares = 0,
        expectedFillerShortShares = 0,
        expectedFillerTokens = shortCost)

    print "creator escrows shares, filler pays with cash"
    execute(
        contractsFixture = contractsFixture,
        universe = universe,
        market = market,
        orderType = ASK,
        orderSize = fxpAmount,
        orderPrice = fxpPrice,
        orderOutcome = YES,
        creatorLongShares = fxpAmount,
        creatorShortShares = 0,
        creatorTokens = 0,
        fillerLongShares = 0,
        fillerShortShares = 0,
        fillerTokens = longCost,
        expectedMakerLongShares = 0,
        expectedMakerShortShares = 0,
        expectedMakerTokens = longCost,
        expectedFillerLongShares = fxpAmount,
        expectedFillerShortShares = 0,
        expectedFillerTokens = 0)

def test_binary(contractsFixture, market, randomAmount, randomNormalizedPrice):
    print 'Random amount: ' + str(randomAmount)
    print 'Random price: ' + str(randomNormalizedPrice)
    fxpAmount = fix(randomAmount)
    fxpPrice = long(randomNormalizedPrice * market.getNumTicks())
    print "Start Fuzzy WCL tests - Binary Market - bidOrders."
    print ""
    execute_bidOrder_tests(contractsFixture, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Binary Market - bidOrders."
    print ""
    print "Start Fuzzy WCL tests - Binary Market - askOrders."
    print ""
    execute_askOrder_tests(contractsFixture, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Binary Market - askOrders."
    print ""

def test_categorical(contractsFixture, randomAmount, randomNormalizedPrice):
    market = contractsFixture.categoricalMarket
    print 'Random amount: ' + str(randomAmount)
    print 'Random price: ' + str(randomNormalizedPrice)
    fxpAmount = fix(randomAmount)
    fxpPrice = long(randomNormalizedPrice * market.getNumTicks())
    print "Start Fuzzy WCL tests - Categorical Market - bidOrders."
    print ""
    execute_bidOrder_tests(contractsFixture, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Categorical Market - bidOrders."
    print ""
    print "Start Fuzzy WCL tests - Categorical Market - askOrders."
    print ""
    execute_askOrder_tests(contractsFixture, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Categorical Market - askOrders."
    print ""

def test_scalar(contractsFixture, randomAmount, randomNormalizedPrice):
    market = contractsFixture.scalarMarket
    print 'Random amount: ' + str(randomAmount)
    print 'Random price: ' + str(randomNormalizedPrice)
    fxpAmount = fix(randomAmount)
    fxpPrice = long(randomNormalizedPrice * market.getNumTicks())
    print "Start Fuzzy WCL tests - Scalar Market - bidOrders."
    print ""
    execute_bidOrder_tests(contractsFixture, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Scalar Market - bidOrders."
    print ""
    print "Start Fuzzy WCL tests - Scalar Market - askOrders."
    print ""
    execute_askOrder_tests(contractsFixture, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Scalar Market - askOrders."
    print ""

# check randomly generated numbers to make sure they aren't unreasonable
def check_randoms(market, price):
    fxpPrice = fix(price)
    fxpMaxDisplayPrice = market.getNumTicks()
    fxpTradingFee = fix('0.0101')
    if fxpPrice <= 0:
        return 0
    if fxpPrice >= fxpMaxDisplayPrice:
        return 0
    if fxpTradingFee >= fxpPrice:
        return 0
    if fxpTradingFee >= fxpMaxDisplayPrice - fxpPrice:
        return 0
    return 1

@fixture
def numberOfIterations():
    return 1

@fixture
def creatorAddress():
    return tester.a1

@fixture
def fillerAddress():
    return tester.a2

@fixture
def creatorKey():
    return tester.k1

@fixture
def fillerKey():
    return tester.k2

@fixture
def randomAmount():
    return randint(1, 11)

@fixture
def randomNormalizedPrice():
    price = 0
    while price < 0.0101 or price > 0.9899:
        price = randfloat()
    return price
