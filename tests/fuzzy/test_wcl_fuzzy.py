#!/usr/bin/env python

from decimal import Decimal, ROUND_UP, ROUND_DOWN
from ethereum.tools import tester
from os import getenv
from pytest import fixture, mark
from random import randint, random as randfloat
from utils import bytesToLong, longTo32Bytes, bytesToHexString, fix
from constants import BID, ASK, YES, NO

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

def execute(fixture, snapshot, universe, market, orderType, orderSize, orderPrice, orderOutcome, creatorLongShares, creatorShortShares, creatorTokens, fillerLongShares, fillerShortShares, fillerTokens, expectedMakerLongShares, expectedMakerShortShares, expectedMakerTokens, expectedFillerLongShares, expectedFillerShortShares, expectedFillerTokens, numTicks):
    def acquireLongShares(outcome, amount, approvalAddress, sender):
        if amount == 0: return

        shareToken = fixture.applySignature('ShareToken', market.getShareToken(outcome))
        completeSets = fixture.contracts['CompleteSets']
        createOrder = fixture.contracts['CreateOrder']
        fillOrder = fixture.contracts['FillOrder']

        ethRequired = amount * numTicks
        assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender, value = ethRequired)
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

        ethRequired = amount * numTicks
        assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender, value = ethRequired)
        assert shareToken.transfer(0, amount, sender = sender)
        for otherOutcome in range(0, market.getNumberOfOutcomes()):
            if otherOutcome == outcome: continue
            otherShareToken = fixture.applySignature('ShareToken', market.getShareToken(otherOutcome))

    fixture.resetToSnapshot(snapshot)

    legacyReputationToken = fixture.contracts['LegacyReputationToken']
    legacyReputationToken.faucet(long(11 * 10**6 * 10**18))
    fixture.chain.head_state.timestamp += 15000

    orders = fixture.contracts['Orders']
    createOrder = fixture.contracts['CreateOrder']
    fillOrder = fixture.contracts['FillOrder']
    completeSets = fixture.contracts['CompleteSets']

    creatorAddress = tester.a1
    fillerAddress = tester.a2
    creatorKey = tester.k1
    fillerKey = tester.k2

    # Set creator/filler balances
    creatorBalance = fixture.chain.head_state.get_balance(creatorAddress)
    fillerBalance = fixture.chain.head_state.get_balance(fillerAddress)

    # Acquire shares for creator
    creatorEthRequiredLong = 0 if creatorLongShares == 0 else creatorLongShares * numTicks
    creatorEthRequiredShort = 0 if creatorShortShares == 0 else creatorShortShares * numTicks
    acquireLongShares(orderOutcome, creatorLongShares, createOrder.address, sender = creatorKey)
    acquireShortShareSet(orderOutcome, creatorShortShares, createOrder.address, sender = creatorKey)
    assert fixture.chain.head_state.get_balance(creatorAddress) == creatorBalance - creatorEthRequiredLong - creatorEthRequiredShort
    assert fixture.chain.head_state.get_balance(fillerAddress) == fillerBalance

    creatorBalance = fixture.chain.head_state.get_balance(creatorAddress)
    fillerBalance = fixture.chain.head_state.get_balance(fillerAddress)

    # Create order
    orderId = createOrder.publicCreateOrder(orderType, orderSize, orderPrice, market.address, orderOutcome, longTo32Bytes(0), longTo32Bytes(0), "42", sender = creatorKey, value = creatorTokens)
    assert fixture.chain.head_state.get_balance(creatorAddress) == creatorBalance - creatorTokens
    assert fixture.chain.head_state.get_balance(fillerAddress) == fillerBalance

    creatorBalance = fixture.chain.head_state.get_balance(creatorAddress)
    fillerBalance = fixture.chain.head_state.get_balance(fillerAddress)

    # Validate order
    assert orders.getAmount(orderId) == orderSize
    assert orders.getPrice(orderId) == orderPrice
    assert orders.getOrderCreator(orderId) == bytesToHexString(creatorAddress)
    assert orders.getOrderMoneyEscrowed(orderId) == creatorTokens
    assert orders.getOrderSharesEscrowed(orderId) == creatorLongShares or creatorShortShares

    # Acquire shares for filler
    fillerEthRequiredLong = 0 if fillerLongShares == 0 else fillerLongShares * numTicks
    fillerEthRequiredShort = 0 if fillerShortShares == 0 else fillerShortShares * numTicks
    acquireLongShares(orderOutcome, fillerLongShares, fillOrder.address, sender = fillerKey)
    acquireShortShareSet(orderOutcome, fillerShortShares, fillOrder.address, sender = fillerKey)
    assert fixture.chain.head_state.get_balance(creatorAddress) == creatorBalance
    assert fixture.chain.head_state.get_balance(fillerAddress) == fillerBalance - fillerEthRequiredLong - fillerEthRequiredShort

    creatorBalance = fixture.chain.head_state.get_balance(creatorAddress)
    fillerBalance = fixture.chain.head_state.get_balance(fillerAddress)

    # Fill order
    remaining = fillOrder.publicFillOrder(orderId, orderSize, "42", sender = fillerKey, value = fillerTokens)
    assert not remaining

    # Assert final state
    assert fixture.chain.head_state.get_balance(creatorAddress) == creatorBalance + expectedMakerTokens
    assert fixture.chain.head_state.get_balance(fillerAddress) == fillerBalance - fillerTokens + expectedFillerTokens
    for outcome in range(0, market.getNumberOfOutcomes()):
        shareToken = fixture.applySignature('ShareToken', market.getShareToken(outcome))
        if outcome == orderOutcome:
            assert shareToken.balanceOf(creatorAddress) == expectedMakerLongShares
            assert shareToken.balanceOf(fillerAddress) == expectedFillerLongShares
        else:
            assert shareToken.balanceOf(creatorAddress) == expectedMakerShortShares
            assert shareToken.balanceOf(fillerAddress) == expectedFillerShortShares

def execute_bidOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice, numTicks):
    longCost = long(fxpAmount * fxpPrice)
    shortCost = long(fxpAmount * (numTicks - fxpPrice))
    totalProceeds = long(fxpAmount * numTicks)
    completeSetFees = totalProceeds / 100 + totalProceeds / 100
    shortFee = Decimal(completeSetFees * shortCost) / Decimal(longCost + shortCost)
    longFee = completeSetFees - shortFee

    print "creator escrows ETH, filler pays with ETH"
    execute(
        fixture = fixture,
        snapshot = kitchenSinkSnapshot,
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
        expectedFillerTokens = 0,
        numTicks = numTicks)

    print "creator escrows shares, filler pays with shares"
    execute(
        fixture = fixture,
        snapshot = kitchenSinkSnapshot,
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
        expectedMakerTokens = (shortCost - shortFee).quantize(Decimal('1.'), rounding=ROUND_UP),
        expectedFillerLongShares = 0,
        expectedFillerShortShares = 0,
        expectedFillerTokens = (longCost - longFee).quantize(Decimal('1.'), rounding=ROUND_DOWN),
        numTicks = numTicks)

    print "creator escrows ETH, filler pays with shares"
    execute(
        fixture = fixture,
        snapshot = kitchenSinkSnapshot,
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
        expectedFillerTokens = longCost,
        numTicks = numTicks)

    print "creator escrows shares, filler pays with ETH"
    execute(
        fixture = fixture,
        snapshot = kitchenSinkSnapshot,
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
        expectedFillerTokens = 0,
        numTicks = numTicks)

def execute_askOrder_tests(fixture, kitchenSinkSnapshot, universe, market, fxpAmount, fxpPrice, numTicks):
    longCost = long(fxpAmount * fxpPrice)
    shortCost = long(fxpAmount * (numTicks - fxpPrice))
    totalProceeds = long(fxpAmount * numTicks)
    completeSetFees = totalProceeds / 100 + totalProceeds / 100
    longFee = Decimal(completeSetFees * longCost) / Decimal(longCost + shortCost)
    shortFee = completeSetFees - longFee

    print "creator escrows ETH, filler pays with ETH"
    execute(
        fixture = fixture,
        snapshot = kitchenSinkSnapshot,
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
        expectedFillerTokens = 0,
        numTicks = numTicks)

    print "creator escrows shares, filler pays with shares"
    execute(
        fixture = fixture,
        snapshot = kitchenSinkSnapshot,
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
        expectedMakerTokens = (longCost - longFee).quantize(Decimal('1.'), rounding=ROUND_DOWN),
        expectedFillerLongShares = 0,
        expectedFillerShortShares = 0,
        expectedFillerTokens = (shortCost - shortFee).quantize(Decimal('1.'), rounding=ROUND_UP),
        numTicks = numTicks)

    print "creator escrows ETH, filler pays with shares"
    execute(
        fixture = fixture,
        snapshot = kitchenSinkSnapshot,
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
        expectedFillerTokens = shortCost,
        numTicks = numTicks)

    print "creator escrows shares, filler pays with ETH"
    execute(
        fixture = fixture,
        snapshot = kitchenSinkSnapshot,
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
        expectedFillerTokens = 0,
        numTicks = numTicks)

def test_yesNo(fixture, kitchenSinkSnapshot, universe, yesNoMarket, randomAmount, randomNormalizedPrice):
    print ""
    print 'Random amount: ' + str(randomAmount)
    print 'Random price: ' + str(randomNormalizedPrice)
    print ""
    fxpAmount = randomAmount
    numTicks = yesNoMarket.getNumTicks()
    fxpPrice = long(randomNormalizedPrice * numTicks)
    print "Start Fuzzy WCL tests - YesNo Market - bidOrders."
    execute_bidOrder_tests(fixture, kitchenSinkSnapshot, universe, yesNoMarket, fxpAmount, fxpPrice, numTicks)
    print "Finished Fuzzy WCL tests - YesNo Market - bidOrders."
    print ""
    print "Start Fuzzy WCL tests - YesNo Market - askOrders."
    execute_askOrder_tests(fixture, kitchenSinkSnapshot, universe, yesNoMarket, fxpAmount, fxpPrice, numTicks)
    print "Finished Fuzzy WCL tests - YesNo Market - askOrders."
    print ""

def test_categorical(fixture, kitchenSinkSnapshot, universe, categoricalMarket, randomAmount, randomNormalizedPrice):
    print ""
    print 'Random amount: ' + str(randomAmount)
    print 'Random price: ' + str(randomNormalizedPrice)
    print ""
    fxpAmount = randomAmount
    numTicks = categoricalMarket.getNumTicks()
    fxpPrice = long(randomNormalizedPrice * numTicks)
    print "Start Fuzzy WCL tests - Categorical Market - bidOrders."
    execute_bidOrder_tests(fixture, kitchenSinkSnapshot, universe, categoricalMarket, fxpAmount, fxpPrice, numTicks)
    print "Finished Fuzzy WCL tests - Categorical Market - bidOrders."
    print ""
    print "Start Fuzzy WCL tests - Categorical Market - askOrders."
    execute_askOrder_tests(fixture, kitchenSinkSnapshot, universe, categoricalMarket, fxpAmount, fxpPrice, numTicks)
    print "Finished Fuzzy WCL tests - Categorical Market - askOrders."
    print ""

def test_scalar(fixture, kitchenSinkSnapshot, universe, scalarMarket, randomAmount, randomNormalizedPrice):
    print ""
    print 'Random amount: ' + str(randomAmount)
    print 'Random price: ' + str(randomNormalizedPrice)
    print ""
    fxpAmount = randomAmount / 40
    numTicks = scalarMarket.getNumTicks()
    fxpPrice = long(randomNormalizedPrice * numTicks)
    print "Start Fuzzy WCL tests - Scalar Market - bidOrders."
    execute_bidOrder_tests(fixture, kitchenSinkSnapshot, universe, scalarMarket, fxpAmount, fxpPrice, numTicks)
    print "Finished Fuzzy WCL tests - Scalar Market - bidOrders."
    print ""
    print "Start Fuzzy WCL tests - Scalar Market - askOrders."
    execute_askOrder_tests(fixture, kitchenSinkSnapshot, universe, scalarMarket, fxpAmount, fxpPrice, numTicks)
    print "Finished Fuzzy WCL tests - Scalar Market - askOrders."
    print ""

# Check randomly generated numbers to make sure they aren't unreasonable
def check_randoms(market, price, numTicks):
    fxpPrice = fix(price)
    fxpMaxDisplayPrice = numTicks
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
    return fix(randint(1, 11))

@fixture
def randomNormalizedPrice():
    price = 0
    while price < 0.0101 or price > 0.9899:
        price = randfloat()
    return price
