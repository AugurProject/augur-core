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

def execute(fixture, universe, market, orderType, orderSize, orderPrice, orderOutcome, creatorLongShares, creatorShortShares, creatorTokens, fillerLongShares, fillerShortShares, fillerTokens, expectedMakerLongShares, expectedMakerShortShares, expectedMakerTokens, expectedFillerLongShares, expectedFillerShortShares, expectedFillerTokens):
    def acquireLongShares(outcome, amount, approvalAddress, sender):
        if amount == 0: return

        shareToken = fixture.applySignature('ShareToken', market.getShareToken(outcome))
        completeSets = fixture.contracts['CompleteSets']
        createOrder = fixture.contracts['CreateOrder']
        fillOrder = fixture.contracts['FillOrder']

        ethRequired = amount * market.getNumTicks()
        assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender, value = ethRequired)
        assert shareToken.approve(approvalAddress, amount, sender = sender)
        for otherOutcome in range(0, market.getNumberOfOutcomes()):
            if otherOutcome == outcome: continue
            otherShareToken = fixture.applySignature('ShareToken', market.getShareToken(otherOutcome))
            assert otherShareToken.transfer(0, amount, sender = sender)

    def acquireShortShareSet(outcome, amount, approvalAddress, sender):
        if amount == 0: return

        shareToken = fixture.applySignature('ShareToken', market.getShareToken(outcome))
        completeSets = fixture.contracts['CompleteSets']
        createOrder = fixture.contracts['CreateOrder']
        fillOrder = fixture.contracts['FillOrder']

        ethRequired = amount * market.getNumTicks()
        assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender, value = ethRequired)
        assert shareToken.transfer(0, amount, sender = sender)
        for otherOutcome in range(0, market.getNumberOfOutcomes()):
            if otherOutcome == outcome: continue
            otherShareToken = fixture.applySignature('ShareToken', market.getShareToken(otherOutcome))
            assert otherShareToken.approve(approvalAddress, amount, sender = sender)

    legacyReputationToken = fixture.contracts['LegacyReputationToken']
    legacyReputationToken.faucet(long(11 * 10**6 * 10**18))
    fixture.chain.head_state.timestamp += 15000

    # Get the reputation token for this universe and migrate legacy REP to it
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    legacyReputationToken.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyReputationToken()

    orders = fixture.contracts['Orders']
    ordersFetcher = fixture.contracts['OrdersFetcher']
    createOrder = fixture.contracts['CreateOrder']
    fillOrder = fixture.contracts['FillOrder']
    completeSets = fixture.contracts['CompleteSets']

    creatorAddress = tester.a1
    fillerAddress = tester.a2
    creatorKey = tester.k1
    fillerKey = tester.k2

    creatorOriginalBalance = fixture.chain.head_state.get_balance(creatorAddress)
    fillerOriginalBalance = fixture.chain.head_state.get_balance(fillerAddress)

    # create order
    creatorEthRequiredLong = 0 if creatorLongShares == 0 else creatorLongShares * market.getNumTicks()
    creatorEthRequiredShort = 0 if creatorShortShares == 0 else creatorShortShares * market.getNumTicks()
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
    fillerEthRequiredLong = 0 if fillerLongShares == 0 else fillerLongShares * market.getNumTicks()
    fillerEthRequiredShort = 0 if fillerShortShares == 0 else fillerShortShares * market.getNumTicks()
    acquireLongShares(orderOutcome, fillerLongShares, fillOrder.address, sender = fillerKey)
    acquireShortShareSet(orderOutcome, fillerShortShares, fillOrder.address, sender = fillerKey)
    remaining = fillOrder.publicFillOrder(orderID, orderSize, 42, sender = fillerKey, value = fillerTokens)
    assert not remaining

    # assert final state
    assert fixture.chain.head_state.get_balance(creatorAddress) == creatorOriginalBalance - creatorEthRequiredLong - creatorEthRequiredShort - creatorTokens + expectedMakerTokens
    assert fixture.chain.head_state.get_balance(fillerAddress) == fillerOriginalBalance - fillerEthRequiredLong - fillerEthRequiredShort - fillerTokens + expectedFillerTokens
    for outcome in range(0, market.getNumberOfOutcomes()):
        shareToken = fixture.applySignature('ShareToken', market.getShareToken(outcome))
        if outcome == orderOutcome:
            assert shareToken.balanceOf(creatorAddress) == expectedMakerLongShares
            assert shareToken.balanceOf(fillerAddress) == expectedFillerLongShares
        else:
            assert shareToken.balanceOf(creatorAddress) == expectedMakerShortShares
            assert shareToken.balanceOf(fillerAddress) == expectedFillerShortShares

def execute_bidOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice):
    longCost = long(fxpAmount * fxpPrice)
    shortCost = long(fxpAmount * (market.getNumTicks() - fxpPrice))
    completeSetFees = long(fxpAmount * market.getNumTicks() * fix('0.0101') / 10**18)
    shortFee = long((completeSetFees * shortCost) / (longCost + shortCost))
    longFee = completeSetFees - shortFee

    print "creator escrows ETH, filler pays with ETH"
    execute(
        fixture = fixture,
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

    fixture.resetToSnapshot(kitchenSinkSnapshot)

    print "creator escrows shares, filler pays with shares"
    execute(
        fixture = fixture,
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

    fixture.resetToSnapshot(kitchenSinkSnapshot)

    print "creator escrows ETH, filler pays with shares"
    execute(
        fixture = fixture,
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

    fixture.resetToSnapshot(kitchenSinkSnapshot)

    print "creator escrows shares, filler pays with ETH"
    execute(
        fixture = fixture,
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

    fixture.resetToSnapshot(kitchenSinkSnapshot)

def execute_askOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice):
    longCost = long(fxpAmount * fxpPrice)
    shortCost = long(fxpAmount * (market.getNumTicks() - fxpPrice))
    completeSetFees = long(fxpAmount * market.getNumTicks() * fix('0.0101') / 10**18)
    longFee = long((completeSetFees * longCost) / (longCost + shortCost))
    shortFee = completeSetFees - longFee

    print "creator escrows ETH, filler pays with ETH"
    execute(
        fixture = fixture,
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

    fixture.resetToSnapshot(kitchenSinkSnapshot)

    print "creator escrows shares, filler pays with shares"
    execute(
        fixture = fixture,
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

    fixture.resetToSnapshot(kitchenSinkSnapshot)

    print "creator escrows ETH, filler pays with shares"
    execute(
        fixture = fixture,
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

    fixture.resetToSnapshot(kitchenSinkSnapshot)

    print "creator escrows shares, filler pays with ETH"
    execute(
        fixture = fixture,
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

    fixture.resetToSnapshot(kitchenSinkSnapshot)

def test_binary(fixture, kitchenSinkSnapshot, universe, market, randomAmount, randomNormalizedPrice):
    print 'Random amount: ' + str(randomAmount)
    print 'Random price: ' + str(randomNormalizedPrice)
    fxpAmount = fix(randomAmount)
    fxpPrice = long(randomNormalizedPrice * market.getNumTicks())
    print "Start Fuzzy WCL tests - Binary Market - bidOrders."
    print ""
    execute_bidOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Binary Market - bidOrders."
    print ""
    print "Start Fuzzy WCL tests - Binary Market - askOrders."
    print ""
    execute_askOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Binary Market - askOrders."
    print ""

def test_categorical(fixture, kitchenSinkSnapshot, universe, market, randomAmount, randomNormalizedPrice):
    print 'Random amount: ' + str(randomAmount)
    print 'Random price: ' + str(randomNormalizedPrice)
    fxpAmount = fix(randomAmount)
    fxpPrice = long(randomNormalizedPrice * market.getNumTicks())
    print "Start Fuzzy WCL tests - Categorical Market - bidOrders."
    print ""
    execute_bidOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Categorical Market - bidOrders."
    print ""
    print "Start Fuzzy WCL tests - Categorical Market - askOrders."
    print ""
    execute_askOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Categorical Market - askOrders."
    print ""

def test_scalar(fixture, kitchenSinkSnapshot, universe, market, randomAmount, randomNormalizedPrice):
    print 'Random amount: ' + str(randomAmount)
    print 'Random price: ' + str(randomNormalizedPrice)
    fxpAmount = fix(randomAmount)
    fxpPrice = long(randomNormalizedPrice * market.getNumTicks())
    print "Start Fuzzy WCL tests - Scalar Market - bidOrders."
    print ""
    execute_bidOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice)
    print ""
    print "Finished Fuzzy WCL tests - Scalar Market - bidOrders."
    print ""
    print "Start Fuzzy WCL tests - Scalar Market - askOrders."
    print ""
    execute_askOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice)
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
