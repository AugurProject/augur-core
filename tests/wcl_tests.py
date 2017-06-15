#!/usr/bin/env python
from __future__ import division
import math
import random
import os
import sys
import json
import iocapture
import ethereum.tester
import utils
from decimal import *

eventCreationCounter = 0
MIN_ORDER_VALUE = 10**14
MAX_INT256_VALUE = 2**255 - 1
shareTokenContractTranslator = ethereum.abi.ContractTranslator('[{"constant": false, "type": "function", "name": "allowance(address,address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "address", "name": "spender"}]}, {"constant": false, "type": "function", "name": "approve(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "balanceOf(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "address"}]}, {"constant": false, "type": "function", "name": "changeTokens(int256,int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "trader"}, {"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "createShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "destroyShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "getDecimals()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getName()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getSymbol()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "modifySupply(int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "setController(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "newController"}]}, {"constant": false, "type": "function", "name": "suicideFunds(address)", "outputs": [], "inputs": [{"type": "address", "name": "to"}]}, {"constant": false, "type": "function", "name": "totalSupply()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "transfer(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "transferFrom(address,address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "from"}, {"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval(address,address,uint256)"}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer(address,address,uint256)"}, {"inputs": [{"indexed": false, "type": "int256", "name": "from"}, {"indexed": false, "type": "int256", "name": "to"}, {"indexed": false, "type": "int256", "name": "value"}, {"indexed": false, "type": "int256", "name": "senderBalance"}, {"indexed": false, "type": "int256", "name": "sender"}, {"indexed": false, "type": "int256", "name": "spenderMaxValue"}], "type": "event", "name": "echo(int256,int256,int256,int256,int256,int256)"}]')

def makeOutcomeShareContractWrapper(contracts):
    return contracts._ContractLoader__state.abi_contract("""
extern shareTokens: [allowance:[address,address]:int256, approve:[address,uint256]:int256, balanceOf:[address]:int256, changeTokens:[int256,int256]:int256, createShares:[address,uint256]:int256, destroyShares:[address,uint256]:int256, getDecimals:[]:int256, getName:[]:int256, getSymbol:[]:int256, modifySupply:[int256]:int256, setController:[address]:int256, suicideFunds:[address]:_, totalSupply:[]:int256, transfer:[address,uint256]:int256, transferFrom:[address,address,uint256]:int256]

def approve(shareContract: address, spender: address, value: uint256):
    return(shareContract.approve(spender, value))

def allowance(shareContract: address, owner: address, spender: address):
    return(shareContract.allowance(owner, spender))

def transferFrom(shareContract: address, from: address, to: address, value: uint256):
    return(shareContract.transferFrom(from, to, value))

def totalSupply(shareContract: address):
    return(shareContract.totalSupply())

def balanceOf(shareContract: address, address: address):
    return(shareContract.balanceOf(address))
""")

def fix(n):
    return int((Decimal(str(n)) * Decimal(10)**Decimal(18)).quantize(0))

def unfix(n):
    return n / 10**18
    # return str(Decimal(str(n)) / Decimal(10)**Decimal(18))

def parseCapturedLogs(logs):
    arrayOfLogs = logs.strip().split("\n")
    arrayOfParsedLogs = []
    for log in arrayOfLogs:
        parsedLog = json.loads(log.replace("'", '"').replace("L", "").replace('u"', '"'))
        arrayOfParsedLogs.append(parsedLog)
    if len(arrayOfParsedLogs) == 0:
        return arrayOfParsedLogs[0]
    return arrayOfParsedLogs

def createBinaryEvent(contracts):
    global eventCreationCounter
    t = contracts._ContractLoader__tester
    contracts.cash.publicDepositEther(value=fix(100), sender=t.k1)
    contracts.cash.approve(contracts.createEvent.address, fix(100), sender=t.k1)
    branch = 1010101
    contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1)
    description = "test binary event"
    expDate = 3000000002 + eventCreationCounter
    eventCreationCounter += 1
    fxpMinValue = fix(1)
    fxpMaxValue = fix(2)
    numOutcomes = 2
    resolution = "http://lmgtfy.com"
    resolutionAddress = t.a2
    currency = contracts.cash.address
    forkResolveAddress = contracts.forkResolution.address
    return contracts.createEvent.publicCreateEvent(branch, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)

def createCategoricalEvent(contracts, numOutcomes=3):
    global eventCreationCounter
    t = contracts._ContractLoader__tester
    contracts.cash.publicDepositEther(value=fix(100), sender=t.k1)
    contracts.cash.approve(contracts.createEvent.address, fix(100), sender=t.k1)
    branch = 1010101
    contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1)
    description = "test categorical event"
    expDate = 3000000002 + eventCreationCounter
    eventCreationCounter += 1
    fxpMinValue = fix(1)
    fxpMaxValue = fix(numOutcomes)
    resolution = "http://lmgtfy.com"
    resolutionAddress = t.a2
    currency = contracts.cash.address
    forkResolveAddress = contracts.forkResolution.address
    return contracts.createEvent.publicCreateEvent(branch, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)

def createScalarEvent(contracts, fxpMinValue=fix(1), fxpMaxValue=fix(10)):
    global eventCreationCounter
    t = contracts._ContractLoader__tester
    contracts.cash.publicDepositEther(value=fix(100), sender=t.k1)
    contracts.cash.approve(contracts.createEvent.address, fix(100), sender=t.k1)
    branch = 1010101
    contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1)
    description = "test scalar event"
    expDate = 3000000002 + eventCreationCounter
    eventCreationCounter += 1
    numOutcomes = 2
    resolution = "http://lmgtfy.com"
    resolutionAddress = t.a2
    currency = contracts.cash.address
    forkResolveAddress = contracts.forkResolution.address
    return contracts.createEvent.publicCreateEvent(branch, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)

def createEventType(contracts, eventType):
    if eventType == "binary":
        eventID = createBinaryEvent(contracts)
    elif eventType == "scalar":
        eventID = createScalarEvent(contracts)
    else:
        eventID = createCategoricalEvent(contracts)
    return eventID

def createMarket(contracts, eventID):
    t = contracts._ContractLoader__tester
    contracts.cash.approve(contracts.createMarket.address, fix(10000), sender=t.k1)
    branch = 1010101
    fxpTradingFee = 20000000000000001
    tag1 = 123
    tag2 = 456
    tag3 = 789
    extraInfo = "rabble rabble rabble"
    currency = contracts.cash.address
    return contracts.createMarket.publicCreateMarket(branch, fxpTradingFee, eventID, tag1, tag2, tag3, extraInfo, currency, 0, 0, sender=t.k1, value=fix(10000))

def buyCompleteSets(contracts, marketID, fxpAmount, sender=None):
    t = contracts._ContractLoader__tester
    if sender is None: sender = t.k1
    assert(contracts.cash.approve(contracts.completeSets.address, fix(10000), sender=sender) == 1), "Approve completeSets contract to spend cash"
    with iocapture.capture() as captured:
        result = contracts.completeSets.publicBuyCompleteSets(marketID, fxpAmount, sender=sender)
        logged = captured.stdout
    logCompleteSets = parseCapturedLogs(logged)[-1]
    assert(logCompleteSets["_event_type"] == "CompleteSets"), "Should emit a CompleteSets event"
    assert(logCompleteSets["type"] == 1), "Logged type should be 1 (buy)"
    assert(logCompleteSets["fxpAmount"] == fxpAmount), "Logged fxpAmount should match input"
    assert(logCompleteSets["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match input"
    assert(logCompleteSets["numOutcomes"] == contracts.markets.getMarketNumOutcomes(marketID)), "Logged numOutcomes should market's number of outcomes"
    assert(logCompleteSets["market"] == marketID), "Logged market should match input"

def calculateLowSide(contracts, eventID, fxpAmount, fxpPrice):
    return int(Decimal(fxpAmount) * (Decimal(fxpPrice) - Decimal(contracts.events.getMinValue(eventID))) / Decimal(10)**Decimal(18))

def calculateHighSide(contracts, eventID, fxpAmount, fxpPrice):
    maxValue = contracts.events.getMaxValue(eventID)
    numOutcomes = contracts.events.getNumOutcomes(eventID)
    if numOutcomes > 2:
        # this is categorical, we should have fix(2) as the max value
        maxValue = fix(2)
    return int(Decimal(fxpAmount) * (Decimal(maxValue) - Decimal(fxpPrice)) / Decimal(10)**Decimal(18))

def check_cash_bid_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash):
    fxpMinValue = contracts.events.getMinValue(eventID)
    fxpMaxValue = contracts.events.getMaxValue(eventID)
    numOutcomes = contracts.events.getNumOutcomes(eventID)
    makerFinalCash = contracts.cash.balanceOf(MAKER)
    takerFinalCash = contracts.cash.balanceOf(TAKER)
    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
    if numOutcomes > 2:
        # categorical, max is forced to 2 for calculations
        fxpMaxValue = fix(2)
    # Low Side = (price - min)*amount
    expectedMakerCost = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
    # High Side = (max - price)*amount
    expectedTakerCost = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
    assert(marketFinalCash == (marketInitialCash + ((fxpMaxValue - fxpMinValue)*unfix(fxpAmount)))), "Market's cash balance should be the marketInitialCash + (max - min)*amount of the maker's Order"
    assert(makerFinalCash == makerInitialCash - expectedMakerCost), "maker's cash balance should be maker's initial balance - (price-min)*amount"
    assert(takerFinalCash == takerInitialCash - expectedTakerCost), "taker's cash balance should be taker's initial balance - (max-price)*amountTakerWanted"

def check_cash_bid_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash):
    fxpMinValue = contracts.events.getMinValue(eventID)
    fxpMaxValue = contracts.events.getMaxValue(eventID)
    numOutcomes = contracts.events.getNumOutcomes(eventID)
    makerFinalCash = contracts.cash.balanceOf(MAKER)
    takerFinalCash = contracts.cash.balanceOf(TAKER)
    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
    if numOutcomes > 2:
        # categorical, max is forced to 2 for calculations
        fxpMaxValue = fix(2)
    # Low Side = (price - min)*amount
    fxpExpectedMakerCost = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
    # High Side = (max - price)*amount
    fxpExpectedTakerCost = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
    fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
    fxpTradingFee = contracts.markets.getTradingFee(marketID)
    fxpExpectedFee = int(Decimal(fxpTradingFee) * fxpAmount / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
    fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
    assert(makerFinalCash == makerInitialCash + fxpExpectedTakerCost - fxpExpectedFee + fxpExpectedFeePaidToCreator), "Maker's final cash balance should be makerInitialCash + (max-price)*amount + ((fxpTradingFee*amount*marketCumlativeScale) / 2)"
    assert(takerFinalCash == takerInitialCash + fxpExpectedMakerCost), "Taker's final cash balance takerInitialCash + (price - min)*amount"
    assert(marketFinalCash == marketInitialCash - (fxpExpectedTakerCost + fxpExpectedMakerCost) + (fxpExpectedFee - fxpExpectedFeePaidToCreator)), "Market's final cash balance should be marketInitialCash - ((max - min)*amount) + ((fxpTradingFee*amount*marketCumlativeScale) / 2)"

def check_cash_bid_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash):
    fxpMinValue = contracts.events.getMinValue(eventID)
    fxpMaxValue = contracts.events.getMaxValue(eventID)
    numOutcomes = contracts.events.getNumOutcomes(eventID)
    makerFinalCash = contracts.cash.balanceOf(MAKER)
    takerFinalCash = contracts.cash.balanceOf(TAKER)
    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
    if numOutcomes > 2:
        # categorical, max is forced to 2 for calculations
        fxpMaxValue = fix(2)
    # Low Side = (price - min)*amount
    fxpExpectedTakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
    assert(makerFinalCash == makerInitialCash - fxpExpectedTakerGain), "Maker's Final cash balance should be makerInitialCash - ((price - min)*amount)"
    assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain), "Taker's Final cash balance should be makerInitialCash + ((price - min)*amount)"
    assert(marketFinalCash == marketInitialCash), "Market's Final cash balance should be marketInitialCash. (unchanged balance)"

def check_cash_bid_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash):
    fxpMinValue = contracts.events.getMinValue(eventID)
    fxpMaxValue = contracts.events.getMaxValue(eventID)
    numOutcomes = contracts.events.getNumOutcomes(eventID)
    makerFinalCash = contracts.cash.balanceOf(MAKER)
    takerFinalCash = contracts.cash.balanceOf(TAKER)
    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
    if numOutcomes > 2:
        # categorical, max is forced to 2 for calculations
        fxpMaxValue = fix(2)
    # High Side = (max - price)*amount
    fxpExpectedTakerCost = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
    fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
    fxpTradingFee = contracts.markets.getTradingFee(marketID)
    fxpExpectedFee = int(Decimal(fxpTradingFee) * fxpAmount / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
    # note: creator is also maker in this case
    fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
    assert(makerFinalCash == makerInitialCash + fxpExpectedTakerCost - fxpExpectedFee + fxpExpectedFeePaidToCreator), "Maker's final cash balance should be makerInitialCash + ((max*price)*amount) + ((fxpTradingFee*amount*marketCumlativeScale) / 2)"
    assert(takerFinalCash == takerInitialCash - fxpExpectedTakerCost), "Taker's final cash balance takerInitialCash - ((max-price)*amount)"
    assert(marketFinalCash == marketInitialCash + (fxpExpectedFee - fxpExpectedFeePaidToCreator)), "Market's final cash balance should be marketInitialCash + ((fxpTradingFee*amount*marketCumlativeScale) / 2)"


def check_cash_ask_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash):
    fxpMinValue = contracts.events.getMinValue(eventID)
    fxpMaxValue = contracts.events.getMaxValue(eventID)
    numOutcomes = contracts.events.getNumOutcomes(eventID)
    makerFinalCash = contracts.cash.balanceOf(MAKER)
    takerFinalCash = contracts.cash.balanceOf(TAKER)
    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
    if numOutcomes > 2:
        # categorical, max is forced to 2 for calculations
        fxpMaxValue = fix(2)
    # Low Side = (price - min)*amount
    expectedTakerCost = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
    # High Side = (max - price)*amount
    expectedMakerCost = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
    assert(marketFinalCash == marketInitialCash + fxpAmount), "Market's cash balance should be the marketInitialCash + fxpAmount of the maker's Order"
    assert(makerFinalCash == makerInitialCash - expectedMakerCost), "maker's cash balance should be maker's initial balance - (max - price)*amount"
    assert(takerFinalCash == takerInitialCash - expectedTakerCost), "taker's cash balance should be taker's initial balance - (max - price)*amountTakerWanted"

def check_cash_ask_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash):
    fxpMinValue = contracts.events.getMinValue(eventID)
    fxpMaxValue = contracts.events.getMaxValue(eventID)
    numOutcomes = contracts.events.getNumOutcomes(eventID)
    makerFinalCash = contracts.cash.balanceOf(MAKER)
    takerFinalCash = contracts.cash.balanceOf(TAKER)
    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
    if numOutcomes > 2:
        # categorical, max is forced to 2 for calculations
        fxpMaxValue = fix(2)
    # Low Side = (price - min)*amount
    fxpExpectedMakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
    # High Side = (max - price)*amount
    fxpExpectedTakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
    fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
    fxpTradingFee = contracts.markets.getTradingFee(marketID)
    fxpExpectedFee = int(Decimal(fxpTradingFee) * fxpAmount / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
    fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
    assert(makerFinalCash == makerInitialCash + fxpExpectedMakerGain + fxpExpectedFeePaidToCreator), "Maker's final cash balance should be makerInitialCash + (price - min)*amount + ((fxpTradingFee*amount) / 2)"
    assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain - fxpExpectedFee), "Taker's final cash balance takerInitialCash + (max-price)*amount - fxpTradingFee*amount"
    assert(marketFinalCash == (marketInitialCash - ((fxpExpectedMakerGain + fxpExpectedTakerGain) - (fxpExpectedFee - fxpExpectedFeePaidToCreator)))), "Market's final cash balance should be marketInitialCash - ((max-min)*amount - ((fxpTradingFee*amount) / 2))"

def check_cash_ask_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash):
    fxpMinValue = contracts.events.getMinValue(eventID)
    fxpMaxValue = contracts.events.getMaxValue(eventID)
    numOutcomes = contracts.events.getNumOutcomes(eventID)
    makerFinalCash = contracts.cash.balanceOf(MAKER)
    takerFinalCash = contracts.cash.balanceOf(TAKER)
    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
    if numOutcomes > 2:
        # categorical, max is forced to 2 for calculations
        fxpMaxValue = fix(2)
    # High Side = (max - price)*amount
    fxpExpectedTakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
    fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
    fxpTradingFee = contracts.markets.getTradingFee(marketID)
    fxpExpectedFee = int(Decimal(fxpTradingFee) * fxpAmount / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
    fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
    assert(makerFinalCash == makerInitialCash - fxpExpectedTakerGain + fxpExpectedFeePaidToCreator), "maker final cash should be equal to makerInitialCash - (max - price)*amount + ((fxpTradingFee*amount) / 2))."
    assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain - fxpExpectedFee), "taker final cash should be equal to takerInitialCash + (max - price)*amount - (fxpTradingFee*amount)"
    assert(marketFinalCash == marketInitialCash + fxpExpectedFee - fxpExpectedFeePaidToCreator), "market final cash should be equal to marketInitialCash + ((fxpTradingFee*amount) / 2))"

def check_cash_ask_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash):
    fxpMinValue = contracts.events.getMinValue(eventID)
    fxpMaxValue = contracts.events.getMaxValue(eventID)
    numOutcomes = contracts.events.getNumOutcomes(eventID)
    makerFinalCash = contracts.cash.balanceOf(MAKER)
    takerFinalCash = contracts.cash.balanceOf(TAKER)
    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
    if numOutcomes > 2:
        # categorical, max is forced to 2 for calculations
        fxpMaxValue = fix(2)
    # Low Side = (price - min)*amount
    fxpExpectedMakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
    assert(makerFinalCash == makerInitialCash + fxpExpectedMakerGain), "Maker's final cash balance should be makerInitialCash + fxpExpectedMakerGain"
    assert(takerFinalCash == takerInitialCash - fxpExpectedMakerGain), "Taker's final cash balance takerInitialCash - fxpExpectedMakerGain"
    assert(marketFinalCash == marketInitialCash), "Market's final cash balance should be marketInitialCash"

def test_bidOrders_binary(contracts, eventID, marketID, randomAmount, randomPrice):
    def test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker escrows cash, taker does not have shares of anything
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedMakerCost = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        # Start makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == fxpExpectedMakerCost), "Market's cash balance should be (price - min)*amount"
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedCash, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        # confirm cash
        check_cash_bid_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, fxpAmountTakerWants])
        check_shares(contracts, marketID, TAKER, [fxpAmountTakerWants, 0])
    def test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in other outcomes, taker has shares of outcome
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedTakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedTakerGain = int(fxpExpectedTakerGain)
        fxpExpectedMakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedMakerGain = int(fxpExpectedMakerGain)
        outcomeID = 1
        tradeGroupID = 10
        # place bid order
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, expectedTakerGain)
        fxpMinValue = contracts.events.getMinValue(eventID)
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * makerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpCashTransferFromMarketToTaker = int(Decimal(fxpAmountTakerWants) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
        fxpSellCompleteSetsCashTransferFromMarketToMaker = makerInitialShares * fxpCumulativeScale / Decimal(10)**Decimal(18)
        fxpCashTransferFromMakerToMarket = int((Decimal(fxpPrice) - Decimal(fxpMinValue)) * Decimal(fxpAmount) / Decimal(10)**Decimal(18))
        fxpExpectedCashTransferToMaker = int(fxpSellCompleteSetsCashTransferFromMarketToMaker - Decimal(fxpExpectedFee))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0])
        check_shares(contracts, marketID, TAKER, [0, 0])
        # confirm cash
        assert(makerFinalCash == makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket), "Maker's final cash balance should be makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket"
        assert(takerFinalCash == takerInitialCash + fxpCashTransferFromMarketToTaker), "Taker's final cash balance takerInitialCash + fxpCashTransferFromMarketToTaker"
        assert(marketFinalCash == marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket), "Market's final cash balance should be marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket"
    def test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker escrows cash, taker has complete set
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedTakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        # taker first buys a complete set
        # buy the amount the taker plans to take from the order
        contracts._ContractLoader__state.mine(1)
        buyCompleteSets(contracts, marketID, fxpAmountTakerWants, sender=TAKER_KEY)
        contracts._ContractLoader__state.mine(1)
        # makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedTakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        # check shares
        check_shares(contracts, marketID, MAKER, [0, fxpAmountTakerWants])
        check_shares(contracts, marketID, TAKER, [fxpAmountTakerWants, 0])
        # check cash
        assert(makerFinalCash == makerInitialCash - fxpExpectedTakerGain)
        assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain)
        assert(marketFinalCash == marketInitialCash)
    def test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in other outcome, taker has shares in outcome
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        outcomeID = 1
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        # transfer shares from taker to account 0 if taker has any shares
        # this is done because there should be shares from previous tests
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
        # make order
        contracts._ContractLoader__state.mine(1)
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        # finish make order
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # finish take order
        # begin assertions
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, fxpExpectedTakerGain)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0])
        check_shares(contracts, marketID, TAKER, [0, fxpAmountTakerWants])
        # confirm cash
        fxpMinValue = contracts.events.getMinValue(eventID)
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpCashTransferFromMarketToTaker = int(Decimal(fxpAmountTakerWants) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
        fxpBuyCompleteSetsCashTransferFromTakerToMarket = int(Decimal(fxpAmountTakerWants) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpSharesHeld = Decimal(min(makerInitialShares, fxpAmountTakerWants))
        fxpSellCompleteSetsCashTransferFromMarketToMaker = fxpSharesHeld * fxpCumulativeScale / Decimal(10)**Decimal(18)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * fxpSharesHeld / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpCashTransferFromMakerToMarket = int((Decimal(fxpPrice) - Decimal(fxpMinValue)) * Decimal(fxpAmount) / Decimal(10)**Decimal(18))
        fxpExpectedCashTransferToMaker = int(fxpSellCompleteSetsCashTransferFromMarketToMaker - Decimal(fxpExpectedFee))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        assert(makerFinalCash == makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket), "Maker's final cash balance should be makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket"
        assert(takerFinalCash == takerInitialCash - fxpBuyCompleteSetsCashTransferFromTakerToMarket + fxpCashTransferFromMarketToTaker), "Taker's final cash balance takerInitialCash - fxpBuyCompleteSetsCashTransferFromTakerToMarket + fxpCashTransferFromMarketToTaker"
        assert(marketFinalCash == marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket + fxpBuyCompleteSetsCashTransferFromTakerToMarket), "Market's final cash balance should be marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket + fxpBuyCompleteSetsCashTransferFromTakerToMarket"
        # finally, transfer all shares to account 0 to close out or bid tests
        send_shares(contracts, marketID, MAKER, MAKER_KEY)
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
    test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)
    # test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    # test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    # test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)

def test_askOrders_binary(contracts, eventID, marketID, randomAmount, randomPrice):
    def test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has cash, taker has cash
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedCash = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedCash = int(fxpExpectedCash)
        outcomeID = 2
        tradeGroupID = 10
        # Start makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == marketInitialCash + fxpExpectedCash), "Market's cash balance should be market Initial balance + (max - price)*amount"
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedCash, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        # confirm cash
        assert(marketFinalCash == marketInitialCash + fxpAmount), "Market's cash balance should be the marketInitialCash + fxpAmount of the maker's Order"
        assert(makerFinalCash == makerInitialCash - fxpExpectedCash), "maker's cash balance should be maker's initial balance - (max - price)*amount"
        assert(takerFinalCash == takerInitialCash - (fxpAmount - fxpExpectedCash)), "taker's cash balance should be taker's initial balance - (max - price)*amountTakerWanted"
        # confirm shares
        check_shares(contracts, marketID, MAKER, [fxpAmountTakerWants, 0])
        check_shares(contracts, marketID, TAKER, [0, fxpAmountTakerWants])
    def test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in outcome, taker has shares of other outcomes
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedTakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedTakerGain = int(fxpExpectedTakerGain)
        fxpExpectedMakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedMakerGain = int(fxpExpectedMakerGain)
        outcomeID = 1
        tradeGroupID = 10
        # place bid order
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, outcomeID)
        makerTakerShares = contracts.markets.getParticipantSharesPurchased(marketID, TAKER, outcomeID)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, expectedTakerGain)
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * makerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0])
        check_shares(contracts, marketID, TAKER, [0, 0])
        # confirm cash
        assert(makerFinalCash == makerInitialCash + fxpExpectedMakerGain + fxpExpectedFeePaidToCreator), "Maker's final cash balance should be makerInitialCash + fxpExpectedMakerGain + fxpExpectedFeePaidToCreator"
        assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain - fxpExpectedFee), "Taker's final cash balance takerInitialCash + fxpExpectedTakerGain"
        assert(marketFinalCash == (marketInitialCash - (fxpExpectedMakerGain + fxpExpectedTakerGain) + fxpExpectedFee - fxpExpectedFeePaidToCreator)), "Market's final cash balance should be marketInitialCash - ((fxpExpectedMakerGain + fxpExpectedTakerGain) + fxpExpectedFee - fxpExpectedFeePaidToCreator)"
    def test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker escrows cash, taker has complete set (shares of outcome)
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedTakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        # taker first buys a complete set
        # buy the amount the taker plans to take from the order
        contracts._ContractLoader__state.mine(1)
        buyCompleteSets(contracts, marketID, fxpAmountTakerWants, sender=TAKER_KEY)
        contracts._ContractLoader__state.mine(1)
        # makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        takerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, TAKER, outcomeID)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedTakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        # check shares
        check_shares(contracts, marketID, MAKER, [fxpAmountTakerWants, 0])
        check_shares(contracts, marketID, TAKER, [0, fxpAmountTakerWants])
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * takerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        # check cash
        assert(makerFinalCash == makerInitialCash - fxpExpectedTakerGain + fxpExpectedFeePaidToCreator), "maker final cash should be equal to makerInitialCash - expectedTakerGain + expectedFeePaidToCreator because maker is also market maker."
        assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain - fxpExpectedFee), "taker final cash should be equal to takerInitialCash + expectedTakerGain - expectedFee"
        assert(marketFinalCash == marketInitialCash + fxpExpectedFee - fxpExpectedFeePaidToCreator), "market final cash should be equal to marketInitialCash + expectedFee - expectedFeePaidToCreator"
    def test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in other outcome, taker has no shares
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # Ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        outcomeID = 1
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        fxpExpectedMakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        # transfer shares from taker to account 0 if taker has any shares
        # this is done because there should be shares from previous tests
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
        # make order
        contracts._ContractLoader__state.mine(1)
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, outcomeID)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        # finish make order
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # finish take order
        # begin assertions
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, 0)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0])
        check_shares(contracts, marketID, TAKER, [fxpAmountTakerWants, 0])
        # confirm cash
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * makerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        assert(makerFinalCash == makerInitialCash + fxpExpectedMakerGain), "Maker's final cash balance should be makerInitialCash + fxpExpectedMakerGain"
        assert(takerFinalCash == takerInitialCash - fxpExpectedMakerGain), "Taker's final cash balance takerInitialCash - fxpExpectedMakerGain"
        assert(marketFinalCash == marketInitialCash), "Market's final cash balance should be marketInitialCash + fxpExpectedFee - fxpExpectedFeePaidToCreator"
        # finally, transfer all shares to account 0 to close out or bid tests
        send_shares(contracts, marketID, MAKER, MAKER_KEY)
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
    test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)

def test_bidOrders_categorical(contracts, eventID, marketID, randomAmount, randomPrice):
    def test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker escrows cash, taker does not have shares of anything
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedCash = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedCash = int(fxpExpectedCash)
        outcomeID = 2
        tradeGroupID = 10
        # Start makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == fxpExpectedCash), "Market's cash balance should be (price - 1)*amount"
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedCash, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        # confirm cash
        check_cash_bid_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, fxpAmountTakerWants, 0])
        check_shares(contracts, marketID, TAKER, [fxpAmountTakerWants, 0, fxpAmountTakerWants])
    def test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in other outcomes, taker has shares of outcome
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedTakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedTakerGain = int(fxpExpectedTakerGain)
        fxpExpectedMakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedMakerGain = int(fxpExpectedMakerGain)
        outcomeID = 1
        tradeGroupID = 10
        numOutcomes = contracts.markets.getMarketNumOutcomes(marketID)
        # place bid order
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # send outcome shares of outcome 3 to maker so maker will have outcomes 2 and 3 and will be making a bid to buy outcome 1.
        send_shares(contracts, marketID, TAKER, TAKER_KEY, 3, MAKER)
        contracts._ContractLoader__state.mine(1)
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)
        makerInitialSharesOutcome3 = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 3)
        assert(makerInitialShares == makerInitialSharesOutcome3), "maker should have shares in outcomes 2 and 3, and they should be of an equal amount"
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        takerIntermediateCash = contracts.cash.balanceOf(TAKER)
        makerIntermediateCash = contracts.cash.balanceOf(MAKER)
        marketIntermediateCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 1)), "maker shouldn't have shares in outcomeID anymore"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, expectedTakerGain)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0, 0])
        check_shares(contracts, marketID, TAKER, [0, 0, 0])
        # confirm cash
        check_cash_bid_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
    def test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker escrows cash, taker has complete set
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedTakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        # taker first buys a complete set
        # buy the amount the taker plans to take from the order
        contracts._ContractLoader__state.mine(1)
        buyCompleteSets(contracts, marketID, fxpAmountTakerWants, sender=TAKER_KEY)
        contracts._ContractLoader__state.mine(1)
        # makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedTakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        # check shares
        check_shares(contracts, marketID, MAKER, [0, fxpAmountTakerWants, 0])
        check_shares(contracts, marketID, TAKER, [fxpAmountTakerWants, 0, fxpAmountTakerWants])
        # check cash
        check_cash_bid_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
    def test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in other outcome, taker has shares in outcome
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        outcomeID = 1
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        numOutcomes = contracts.markets.getMarketNumOutcomes(marketID)
        # send shares of outcome 3 to MAKER so that MAKER has shares in outcomes 2 and 3.
        send_shares(contracts, marketID, TAKER, TAKER_KEY, 3, MAKER)
        # transfer shares from taker to account 0 if taker has any shares
        # this is done because there should be shares from previous tests
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
        # make order
        contracts._ContractLoader__state.mine(1)
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        # finish make order
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # finish take order
        # begin assertions
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, fxpExpectedTakerGain)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0, 0])
        check_shares(contracts, marketID, TAKER, [0, fxpAmountTakerWants, fxpAmountTakerWants])
        # confirm cash
        fxpMinValue = contracts.events.getMinValue(eventID)
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpAmountFilled = min(fxpAmountTakerWants, fxpAmount)
        fxpCashTransferFromMarketToTaker = int(Decimal(fxpAmountFilled) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
        fxpBuyCompleteSetsCashTransferFromTakerToMarket = int(Decimal(fxpAmountFilled) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpSharesHeld = Decimal(min(makerInitialShares, fxpAmountFilled))
        fxpSellCompleteSetsCashTransferFromMarketToMaker = fxpSharesHeld * fxpCumulativeScale / Decimal(10)**Decimal(18)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * fxpSharesHeld / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpCashTransferFromMakerToMarket = int((Decimal(fxpPrice) - Decimal(fxpMinValue)) * Decimal(fxpAmount) / Decimal(10)**Decimal(18))
        fxpExpectedCashTransferToMaker = int(fxpSellCompleteSetsCashTransferFromMarketToMaker - Decimal(fxpExpectedFee))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        check_cash_bid_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
        assert(makerFinalCash == makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket), "Maker's final cash balance should be makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket"
        assert(takerFinalCash == takerInitialCash - fxpBuyCompleteSetsCashTransferFromTakerToMarket + fxpCashTransferFromMarketToTaker), "Taker's final cash balance takerInitialCash - fxpBuyCompleteSetsCashTransferFromTakerToMarket + fxpCashTransferFromMarketToTaker"
        assert(marketFinalCash == marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket + fxpBuyCompleteSetsCashTransferFromTakerToMarket), "Market's final cash balance should be marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket + fxpBuyCompleteSetsCashTransferFromTakerToMarket"
        # finally, transfer all shares to account 0 to close out or bid tests
        send_shares(contracts, marketID, MAKER, MAKER_KEY)
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
    test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)

def test_askOrders_categorical(contracts, eventID, marketID, randomAmount, randomPrice):
    def test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has cash, taker has cash
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedMakerOrderCost = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        fxpExpectedTakerCost = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        # Start makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == marketInitialCash + fxpExpectedMakerOrderCost), "Market's cash balance should be market Initial balance + (max - price)*amount"
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # makerFinalCash = contracts.cash.balanceOf(MAKER)
        # takerFinalCash = contracts.cash.balanceOf(TAKER)
        # marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedMakerOrderCost, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        # confirm cash
        check_cash_ask_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [fxpAmountTakerWants, 0, fxpAmountTakerWants])
        check_shares(contracts, marketID, TAKER, [0, fxpAmountTakerWants, 0])
    def test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in outcome, taker has shares of other outcomes
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedTakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedTakerGain = int(fxpExpectedTakerGain)
        fxpExpectedMakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedMakerGain = int(fxpExpectedMakerGain)
        outcomeID = 1
        tradeGroupID = 10
        # transfer shares from outcome 3 to Taker, Maker starts this test with Outcome 1 and Outcome 3 shares, Taker starts with only outcome 2 shares.
        send_shares(contracts, marketID, MAKER, MAKER_KEY, 3, TAKER)
        # place bid order
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, outcomeID)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, expectedTakerGain)
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * makerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpSellCompleteSetsCashTransferFromTakerToMarket = makerInitialShares * fxpCumulativeScale / Decimal(10)**Decimal(18)
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0, 0])
        check_shares(contracts, marketID, TAKER, [0, 0, 0])
        # confirm cash
        check_cash_ask_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
        # assert(makerFinalCash == makerInitialCash + fxpExpectedMakerGain + fxpExpectedFeePaidToCreator), "Maker's final cash balance should be makerInitialCash + (price - min)*amount + ((fxpTradingFee*amount) / 2)"
        # assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain - fxpExpectedFee), "Taker's final cash balance takerInitialCash + (max-price)*amount - fxpTradingFee*amount"
        # assert(marketFinalCash == (marketInitialCash - (fxpExpectedMakerGain + fxpExpectedTakerGain - fxpExpectedFeePaidToCreator))), "Market's final cash balance should be marketInitialCash - ((max-min)*amount - ((fxpTradingFee*amount) / 2))"
    def test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker escrows cash, taker has complete set (shares of outcome)
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedTakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        fxpExpectedMakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        # taker first buys a complete set
        # buy the amount the taker plans to take from the order
        contracts._ContractLoader__state.mine(1)
        buyCompleteSets(contracts, marketID, fxpAmountTakerWants, sender=TAKER_KEY)
        contracts._ContractLoader__state.mine(1)
        # makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        takerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, TAKER, outcomeID)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedTakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        fxpAmountFilled = min(fxpAmountTakerWants, fxpAmount)
        # check shares
        check_shares(contracts, marketID, MAKER, [fxpAmountFilled, 0, fxpAmountFilled])
        check_shares(contracts, marketID, TAKER, [0, fxpAmountFilled, 0])
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * takerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpSellCompleteSetsCash = takerInitialShares * fxpCumulativeScale / Decimal(10)**Decimal(18)
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        # check cash
        check_cash_ask_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
        # assert(makerFinalCash == makerInitialCash - fxpExpectedTakerGain + fxpExpectedFeePaidToCreator), "maker final cash should be equal to makerInitialCash - (max - price)*amount + ((fxpTradingFee*amount) / 2))."
        # assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain - fxpExpectedFee), "taker final cash should be equal to takerInitialCash + (max - price)*amount - (fxpTradingFee*amount)"
        # assert(marketFinalCash == marketInitialCash + fxpExpectedFeePaidToCreator), "market final cash should be equal to marketInitialCash + ((fxpTradingFee*amount) / 2))"
    def test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in outcome, taker has no shares
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # Ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        outcomeID = 1
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        fxpExpectedMakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        # transfer shares from taker to account 0 if taker has any shares
        # this is done because there should be shares from previous tests
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
        # now send outcome 3 shares to account 0 from maker so maker only has outcome 1 shares (the shares they intend to sell)
        send_shares(contracts, marketID, MAKER, MAKER_KEY, 3)
        # make order
        contracts._ContractLoader__state.mine(1)
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, outcomeID)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        # finish make order
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # finish take order
        # makerFinalCash = contracts.cash.balanceOf(MAKER)
        # takerFinalCash = contracts.cash.balanceOf(TAKER)
        # marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, 0)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0, 0])
        check_shares(contracts, marketID, TAKER, [fxpAmountTakerWants, 0, 0])
        # confirm cash
        check_cash_ask_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
        # finally, transfer all shares to account 0 to close out or bid tests
        send_shares(contracts, marketID, MAKER, MAKER_KEY)
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
    test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)

def test_bidOrders_scalar(contracts, eventID, marketID, randomAmount, randomPrice):
    def test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker escrows cash, taker does not have shares of anything
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice)
        fxpExpectedMakerCost = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        fxpExpectedTakerCost = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        # Start makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == fxpExpectedMakerCost), "Market's cash balance should be (price - 1)*amount"
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedMakerCost, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, fxpExpectedTakerCost)
        # confirm cash
        check_cash_bid_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, fxpAmount, fxpPrice, MAKER, TAKER, marketInitialCash, makerInitialCash, takerInitialCash)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, fxpAmountTakerWants])
        check_shares(contracts, marketID, TAKER, [fxpAmountTakerWants, 0])
    def test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in other outcomes, taker has shares of outcome
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice)
        fxpExpectedTakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedTakerGain = int(fxpExpectedTakerGain)
        fxpExpectedMakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedMakerGain = int(fxpExpectedMakerGain)
        outcomeID = 1
        tradeGroupID = 10
        # place bid order
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, expectedTakerGain)
        fxpMinValue = contracts.events.getMinValue(eventID)
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * makerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpCashTransferFromMarketToTaker = int(Decimal(fxpAmountTakerWants) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
        fxpSellCompleteSetsCashTransferFromMarketToMaker = makerInitialShares * fxpCumulativeScale / Decimal(10)**Decimal(18)
        fxpCashTransferFromMakerToMarket = int((Decimal(fxpPrice) - Decimal(fxpMinValue)) * Decimal(fxpAmount) / Decimal(10)**Decimal(18))
        fxpExpectedCashTransferToMaker = int(fxpSellCompleteSetsCashTransferFromMarketToMaker - Decimal(fxpExpectedFee))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0])
        check_shares(contracts, marketID, TAKER, [0, 0])
        # confirm cash
        assert(makerFinalCash == makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket), "Maker's final cash balance should be makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket"
        assert(takerFinalCash == takerInitialCash + fxpCashTransferFromMarketToTaker), "Taker's final cash balance takerInitialCash + fxpCashTransferFromMarketToTaker"
        assert(marketFinalCash == marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket), "Market's final cash balance should be marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket"
    def test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker escrows cash, taker has complete set
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice)
        fxpExpectedTakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        # taker first buys a complete set
        # buy the amount the taker plans to take from the order
        contracts._ContractLoader__state.mine(1)
        buyCompleteSets(contracts, marketID, fxpAmountTakerWants, sender=TAKER_KEY)
        contracts._ContractLoader__state.mine(1)
        # makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedTakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        # check shares
        check_shares(contracts, marketID, MAKER, [0, fxpAmountTakerWants])
        check_shares(contracts, marketID, TAKER, [fxpAmountTakerWants, 0])
        # check cash
        assert(makerFinalCash == makerInitialCash - fxpExpectedTakerGain)
        assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain)
        assert(marketFinalCash == marketInitialCash)
    def test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in other outcome, taker has shares in outcome
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice)
        outcomeID = 1
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        # transfer shares from taker to account 0 if taker has any shares
        # this is done because there should be shares from previous tests
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
        # make order
        contracts._ContractLoader__state.mine(1)
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        # finish make order
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # finish take order
        # begin assertions
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, 0, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, 0)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0])
        check_shares(contracts, marketID, TAKER, [0, fxpAmountTakerWants])
        # confirm cash
        fxpMinValue = contracts.events.getMinValue(eventID)
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpCashTransferFromMarketToTaker = int(Decimal(fxpAmountTakerWants) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
        fxpBuyCompleteSetsCashTransferFromTakerToMarket = int(Decimal(fxpAmountTakerWants) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpSharesHeld = Decimal(min(makerInitialShares, fxpAmountTakerWants))
        fxpSellCompleteSetsCashTransferFromMarketToMaker = fxpSharesHeld * fxpCumulativeScale / Decimal(10)**Decimal(18)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * fxpSharesHeld / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        fxpCashTransferFromMakerToMarket = int((Decimal(fxpPrice) - Decimal(fxpMinValue)) * Decimal(fxpAmount) / Decimal(10)**Decimal(18))
        fxpExpectedCashTransferToMaker = int(fxpSellCompleteSetsCashTransferFromMarketToMaker - Decimal(fxpExpectedFee))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        assert(makerFinalCash == makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket), "Maker's final cash balance should be makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket"
        assert(takerFinalCash == takerInitialCash - fxpBuyCompleteSetsCashTransferFromTakerToMarket + fxpCashTransferFromMarketToTaker), "Taker's final cash balance takerInitialCash - fxpBuyCompleteSetsCashTransferFromTakerToMarket + fxpCashTransferFromMarketToTaker"
        assert(marketFinalCash == marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket + fxpBuyCompleteSetsCashTransferFromTakerToMarket), "Market's final cash balance should be marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket + fxpBuyCompleteSetsCashTransferFromTakerToMarket"
        # finally, transfer all shares to account 0 to close out or bid tests
        send_shares(contracts, marketID, MAKER, MAKER_KEY)
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
    test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)
    # test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    # test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    # test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)

def test_askOrders_scalar(contracts, eventID, marketID, randomAmount, randomPrice):
    def test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has cash, taker has cash
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice)
        fxpExpectedMakerCost = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        fxpExpectedTakerCost = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        # Start makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == marketInitialCash + fxpExpectedMakerCost), "Market's cash balance should be market Initial balance + (max - price)*amount"
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedMakerCost, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, fxpExpectedTakerCost)
        # confirm cash
        assert(marketFinalCash == marketInitialCash + fxpExpectedMakerCost + fxpExpectedTakerCost), "Market's cash balance should be the marketInitialCash + fxpExpectedMakerCost + fxpExpectedTakerCost"
        assert(makerFinalCash == makerInitialCash - fxpExpectedMakerCost), "maker's cash balance should be maker's initial balance - (max - price)*amount"
        assert(takerFinalCash == takerInitialCash - fxpExpectedTakerCost), "taker's cash balance should be taker's initial balance - (max - price)*amountTakerWanted"
        # confirm shares
        check_shares(contracts, marketID, MAKER, [fxpAmountTakerWants, 0])
        check_shares(contracts, marketID, TAKER, [0, fxpAmountTakerWants])
    def test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in outcome, taker has shares of other outcomes
        t = contracts._ContractLoader__tester
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice)
        fxpExpectedTakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedTakerGain = int(fxpExpectedTakerGain)
        fxpExpectedMakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedMakerGain = int(fxpExpectedMakerGain)
        outcomeID = 1
        tradeGroupID = 10
        # place bid order
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, outcomeID)
        takerInitalShares = contracts.markets.getParticipantSharesPurchased(marketID, TAKER, outcomeID)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, expectedTakerGain)
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * makerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0])
        check_shares(contracts, marketID, TAKER, [0, 0])
        # confirm cash
        assert(makerFinalCash == makerInitialCash + fxpExpectedMakerGain + fxpExpectedFeePaidToCreator), "Maker's final cash balance should be makerInitialCash + fxpExpectedMakerGain + fxpExpectedFeePaidToCreator"
        assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain - fxpExpectedFee), "Taker's final cash balance takerInitialCash + fxpExpectedTakerGain"
        assert(marketFinalCash == (marketInitialCash - (fxpExpectedMakerGain + fxpExpectedTakerGain) + fxpExpectedFee - fxpExpectedFeePaidToCreator)), "Market's final cash balance should be marketInitialCash - ((fxpExpectedMakerGain + fxpExpectedTakerGain) + fxpExpectedFee - fxpExpectedFeePaidToCreator)"
    def test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker escrows cash, taker has complete set (shares of outcome)
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice)
        fxpExpectedTakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        outcomeID = 2
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        # taker first buys a complete set
        # buy the amount the taker plans to take from the order
        contracts._ContractLoader__state.mine(1)
        buyCompleteSets(contracts, marketID, fxpAmountTakerWants, sender=TAKER_KEY)
        contracts._ContractLoader__state.mine(1)
        # makeOrder
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        takerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, TAKER, outcomeID)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedTakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        # check shares
        check_shares(contracts, marketID, MAKER, [fxpAmountTakerWants, 0])
        check_shares(contracts, marketID, TAKER, [0, fxpAmountTakerWants])
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * takerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        # check cash
        assert(makerFinalCash == makerInitialCash - fxpExpectedTakerGain + fxpExpectedFeePaidToCreator), "maker final cash should be equal to makerInitialCash - expectedTakerGain + expectedFeePaidToCreator because maker is also market maker."
        assert(takerFinalCash == takerInitialCash + fxpExpectedTakerGain - fxpExpectedFee), "taker final cash should be equal to takerInitialCash + expectedTakerGain - expectedFee"
        assert(marketFinalCash == marketInitialCash + fxpExpectedFee - fxpExpectedFeePaidToCreator), "market final cash should be equal to marketInitialCash + expectedFee - expectedFeePaidToCreator"
    def test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice):
        # maker has shares in other outcome, taker has no shares
        t = contracts._ContractLoader__tester
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        MAKER = t.a1
        TAKER = t.a2
        MAKER_KEY = t.k1
        TAKER_KEY = t.k2
        orderType = 2 # Ask
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice)
        outcomeID = 1
        tradeGroupID = 10
        fxpAmountTakerWants = fxpAmount
        fxpExpectedMakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        # transfer shares from taker to account 0 if taker has any shares
        # this is done because there should be shares from previous tests
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
        # make order
        contracts._ContractLoader__state.mine(1)
        makerInitialCash = contracts.cash.balanceOf(MAKER)
        takerInitialCash = contracts.cash.balanceOf(TAKER)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, MAKER, outcomeID)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=MAKER_KEY)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, MAKER, 2)), "maker shouldn't have shares in outcomeID anymore"
        # finish make order
        contracts._ContractLoader__state.mine(1)
        # take order
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=TAKER_KEY)
        assert(contracts.orders.commitOrder(tradeHash, sender=TAKER_KEY) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=TAKER_KEY)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        # finish take order
        # begin assertions
        makerFinalCash = contracts.cash.balanceOf(MAKER)
        takerFinalCash = contracts.cash.balanceOf(TAKER)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        # print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, fxpExpectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, 0)
        # confirm shares
        check_shares(contracts, marketID, MAKER, [0, 0])
        check_shares(contracts, marketID, TAKER, [fxpAmountTakerWants, 0])
        # confirm cash
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpExpectedFee = int(Decimal(fxpTradingFee) * makerInitialShares / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
        # note: creator is also maker in this case
        fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
        assert(makerFinalCash == makerInitialCash + fxpExpectedMakerGain), "Maker's final cash balance should be makerInitialCash + fxpExpectedMakerGain"
        assert(takerFinalCash == takerInitialCash - fxpExpectedMakerGain), "Taker's final cash balance takerInitialCash - fxpExpectedMakerGain"
        assert(marketFinalCash == marketInitialCash), "Market's final cash balance should be marketInitialCash + fxpExpectedFee - fxpExpectedFeePaidToCreator"
        # finally, transfer all shares to account 0 to close out or bid tests
        send_shares(contracts, marketID, MAKER, MAKER_KEY)
        send_shares(contracts, marketID, TAKER, TAKER_KEY)
    test_makerEscrowedCash_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedShares_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedCash_takerWithShares(contracts, eventID, marketID, randomAmount, randomPrice)
    test_makerEscrowedShares_takerWithoutShares(contracts, eventID, marketID, randomAmount, randomPrice)

def test_binary(contracts, i):
    # Test case:
    # binary event market
    t = contracts._ContractLoader__tester
    eventID = createEventType(contracts, 'binary')
    marketID = createMarket(contracts, eventID)
    randomAmount = random.randint(1, 11)
    randomPrice = random.random()
    # run all possible approvals now so that we don't need to do it in each test case
    approvals(contracts, eventID, marketID, randomAmount, randomPrice)
    print "Start Fuzzy WCL tests - Binary Market - bidOrders. loop count:", i + 1
    test_bidOrders_binary(contracts, eventID, marketID, randomAmount, randomPrice)
    print "Finished Fuzzy WCL tests - Binary Market - bidOrders. loop count:", i + 1
    print ""
    # print "Start Fuzzy WCL tests - Binary Market - askOrders. loop count:", i + 1
    # test_askOrders_binary(contracts, eventID, marketID, randomAmount, randomPrice)
    # print "Finished Fuzzy WCL tests - Binary Market - askOrders. loop count:", i + 1

def test_categorical(contracts, i):
    # Test case:
    # categorical event market
    t = contracts._ContractLoader__tester
    eventID = createEventType(contracts, 'categorical')
    marketID = createMarket(contracts, eventID)
    randomAmount = random.randint(1, 11)
    randomPrice = random.random()
    # run all possible approvals now so that we don't need to do it in each test case
    approvals(contracts, eventID, marketID, randomAmount, randomPrice)
    print "Start Fuzzy WCL tests - Categorical Market - bidOrders. loop count:", i + 1
    test_bidOrders_categorical(contracts, eventID, marketID, randomAmount, randomPrice)
    print "Finished Fuzzy WCL tests - Categorical Market - bidOrders. loop count:", i + 1
    print ""
    # print "Start Fuzzy WCL tests - Categorical Market - askOrders. loop count:", i + 1
    # test_askOrders_categorical(contracts, eventID, marketID, randomAmount, randomPrice)
    # print "Finished Fuzzy WCL tests - Categorical Market - askOrders. loop count:", i + 1

def test_scalar(contracts, i):
    # Test case:
    # scalar event market
    t = contracts._ContractLoader__tester
    # TODO: it seems like createScalar doesn't handle - numbers, like a scale between -20 and 200 will always throw because 200 + - 20 = 180 < 200 which throws in the validator for a new event. I thought the scalar scaling was getting moved to contracts but maybe that hasn't happened yet.
    eventID = createScalarEvent(contracts, fix(10), fix(60))
    marketID = createMarket(contracts, eventID)
    randomAmount = random.randint(1, 10)
    randomPrice = random.randrange(10, 61, 1)
    # run all possible approvals now so that we don't need to do it in each test case
    approvals(contracts, eventID, marketID, randomAmount, randomPrice)
    print "Start Fuzzy WCL tests - Scalar Market - bidOrders. loop count:", i + 1
    test_bidOrders_scalar(contracts, eventID, marketID, randomAmount, randomPrice)
    print "Finished Fuzzy WCL tests - Scalar Market - bidOrders. loop count:", i + 1
    print ""
    # print "Start Fuzzy WCL tests - Scalar Market - askOrders. loop count:", i + 1
    # test_askOrders_scalar(contracts, eventID, marketID, randomAmount, randomPrice)
    # print "Finished Fuzzy WCL tests - Scalar Market - askOrders. loop count:", i + 1

def test_cash(contracts, eventID, marketID, MAKER, TAKER):
    t = contracts._ContractLoader__tester
    print "Maker:"
    print "makeOrder", contracts.cash.allowance(MAKER, contracts.makeOrder.address), unfix(contracts.cash.allowance(MAKER, contracts.makeOrder.address))
    print "takeOrder", contracts.cash.allowance(MAKER, contracts.takeOrder.address), unfix(contracts.cash.allowance(MAKER, contracts.takeOrder.address))
    print "takeBidOrder", contracts.cash.allowance(MAKER, contracts.takeBidOrder.address), unfix(contracts.cash.allowance(MAKER, contracts.takeBidOrder.address))
    print "takeAskOrder", contracts.cash.allowance(MAKER, contracts.takeAskOrder.address), unfix(contracts.cash.allowance(MAKER, contracts.takeAskOrder.address))
    numOutcomes = contracts.markets.getMarketNumOutcomes(marketID)
    outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
    contracts._ContractLoader__state.mine(1)
    for i in range(0, numOutcomes):
        outcomeID = i + 1
        print "outcome", outcomeID
        outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
        abiEncodedData = shareTokenContractTranslator.encode("allowance", [MAKER, contracts.makeOrder.address])
        print "makeOrder", int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16), unfix(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16))
        abiEncodedData = shareTokenContractTranslator.encode("allowance", [MAKER, contracts.takeOrder.address])
        print "takeOrder", int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16), unfix(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16))
        abiEncodedData = shareTokenContractTranslator.encode("allowance", [MAKER, contracts.takeBidOrder.address])
        print "takeBidOrder", int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16), unfix(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16))
        abiEncodedData = shareTokenContractTranslator.encode("allowance", [MAKER, contracts.takeAskOrder.address])
        print "takeAskOrder", int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16), unfix(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16))
    print ""
    print "Taker:"
    print "makeOrder", contracts.cash.allowance(TAKER, contracts.makeOrder.address), unfix(contracts.cash.allowance(TAKER, contracts.makeOrder.address))
    print "takeOrder", contracts.cash.allowance(TAKER, contracts.takeOrder.address), unfix(contracts.cash.allowance(TAKER, contracts.takeOrder.address))
    print "takeBidOrder", contracts.cash.allowance(TAKER, contracts.takeBidOrder.address), unfix(contracts.cash.allowance(TAKER, contracts.takeBidOrder.address))
    print "takeAskOrder", contracts.cash.allowance(TAKER, contracts.takeAskOrder.address), unfix(contracts.cash.allowance(TAKER, contracts.takeAskOrder.address))
    numOutcomes = contracts.markets.getMarketNumOutcomes(marketID)
    outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
    contracts._ContractLoader__state.mine(1)
    for i in range(0, numOutcomes):
        outcomeID = i + 1
        print "outcome", outcomeID
        outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
        abiEncodedData = shareTokenContractTranslator.encode("allowance", [TAKER, contracts.makeOrder.address])
        print "makeOrder", int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16), unfix(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16))
        abiEncodedData = shareTokenContractTranslator.encode("allowance", [TAKER, contracts.takeOrder.address])
        print "takeOrder", int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16), unfix(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16))
        abiEncodedData = shareTokenContractTranslator.encode("allowance", [TAKER, contracts.takeBidOrder.address])
        print "takeBidOrder", int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16), unfix(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16))
        abiEncodedData = shareTokenContractTranslator.encode("allowance", [TAKER, contracts.takeAskOrder.address])
        print "takeAskOrder", int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16), unfix(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16))

def approvals(contracts, eventID, marketID, amount, price):
    t = contracts._ContractLoader__tester
    fxpAllowance = fix(100*amount)
    fxpEtherDepositValue = fix(101*price)
    # if scalar, we need to allocate more ether than usual
    if price > 1:
        fxpEtherDepositValue = fix(50*amount*price)
        fxpAllowance = fix(50*amount*price)
    # print "APPROVING FUNDS..."
    # print "Allowance", fxpAllowance, unfix(fxpAllowance)
    # print "DepositValue", fxpEtherDepositValue, unfix(fxpEtherDepositValue)
    # deposit ETH to cash contract
    assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
    assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
    # begin approval process for all possible contracts
    assert(contracts.cash.approve(contracts.makeOrder.address, fxpAllowance, sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
    assert(contracts.cash.approve(contracts.makeOrder.address, fxpAllowance, sender=t.k2) == 1), "Approve makeOrder contract to spend cash from account 2"
    assert(contracts.cash.approve(contracts.takeOrder.address, fxpAllowance, sender=t.k1) == 1), "Approve takeOrder contract to spend cash from account 1"
    assert(contracts.cash.approve(contracts.takeOrder.address, fxpAllowance, sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
    assert(contracts.cash.approve(contracts.takeBidOrder.address, fxpAllowance, sender=t.k1) == 1), "Approve takeBidOrder contract to spend cash from account 1"
    assert(contracts.cash.approve(contracts.takeBidOrder.address, fxpAllowance, sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
    assert(contracts.cash.approve(contracts.takeAskOrder.address, fxpAllowance, sender=t.k1) == 1), "Approve takeAskOrder contract to spend cash from account 1"
    assert(contracts.cash.approve(contracts.takeAskOrder.address, fxpAllowance, sender=t.k2) == 1), "Approve takeAskOrder contract to spend cash from account 2"
    numOutcomes = contracts.markets.getMarketNumOutcomes(marketID)
    outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
    contracts._ContractLoader__state.mine(1)
    for i in range(0, numOutcomes):
        outcomeID = i + 1
        outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
        abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])
        assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 1)"
        assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
        abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeBidOrder.address, fxpAllowance])
        assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeBidOrder contract to spend shares from the user's account (account 1)"
        assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeBidOrder contract to spend shares from the user's account (account 2)"
        abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeAskOrder.address, fxpAllowance])
        assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeAskOrder contract to spend shares from the user's account (account 1)"
        assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeAskOrder contract to spend shares from the user's account (account 2)"
        abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])
        assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 1)"
        assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 2)"
        assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
        assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a1, contracts.takeBidOrder.address) == fxpAllowance), "takeBidOrder contract's allowance should be equal to the amount approved"
        assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a1, contracts.takeAskOrder.address) == fxpAllowance), "takeAskOrder contract's allowance should be equal to the amount approved"
        assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a2, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"

def send_shares(contracts, marketID, address, key, outcome=0, toAddress=0):
    # address is the account we plan to take shares away from (e.g. t.a2)
    t = contracts._ContractLoader__tester
    if toAddress == 0:
        toAddress = t.a0
    if outcome == 0:
        for i in range(0, contracts.markets.getMarketNumOutcomes(marketID)):
            outcome = i + 1
            shares = contracts.markets.getParticipantSharesPurchased(marketID, address, outcome)
            if shares != 0:
                outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcome)
                transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [toAddress, shares])
                assert(int(contracts._ContractLoader__state.send(key, outcomeShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome to address 0"
    else:
        shares = contracts.markets.getParticipantSharesPurchased(marketID, address, outcome)
        if shares != 0:
            outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcome)
            transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [toAddress, shares])
            assert(int(contracts._ContractLoader__state.send(key, outcomeShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome to address 0"

def check_shares(contracts, marketID, owner, expectedArray):
    t = contracts._ContractLoader__tester
    numOutcomes = contracts.markets.getMarketNumOutcomes(marketID)
    for i in range(0, numOutcomes):
        outcome = i + 1
        assert(contracts.markets.getParticipantSharesPurchased(marketID, owner, outcome) == expectedArray[i]), "Shares haven't been assigned as expected"

# TODO: remove "print_shares" before finishing
def print_shares(contracts, marketID, MAKER, TAKER):
    numOutcomes = contracts.markets.getMarketNumOutcomes(marketID)
    print "Maker Shares:"
    for i in range(0, numOutcomes):
        outcome = i + 1
        print "outcome", outcome, contracts.markets.getParticipantSharesPurchased(marketID, MAKER, outcome), unfix(contracts.markets.getParticipantSharesPurchased(marketID, MAKER, outcome))
    print ""
    print "Taker Shares:"
    for i in range(0, numOutcomes):
        outcome = i + 1
        print "outcome", outcome, contracts.markets.getParticipantSharesPurchased(marketID, TAKER, outcome), unfix(contracts.markets.getParticipantSharesPurchased(marketID, TAKER, outcome))
    print ""

# TODO: remove "print_for_dev" before finishing
def print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedCash, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, expectedCash2=0):
    t = contracts._ContractLoader__tester
    print ""
    print "randomized info:"
    print "fxpAmount:", fxpAmount, unfix(fxpAmount)
    print "fxpPrice:", fxpPrice, unfix(fxpPrice)
    print "expectedCash:", expectedCash, unfix(expectedCash)
    print "2nd expectedCash", expectedCash2, unfix(expectedCash2)
    print ""
    print "makerInitialCash", makerInitialCash, unfix(makerInitialCash)
    print "takerInitialCash", takerInitialCash, unfix(takerInitialCash)
    print "marketInitialCash", marketInitialCash, unfix(marketInitialCash)
    print ""
    print "fxpAmountTakerWants", fxpAmountTakerWants, unfix(fxpAmountTakerWants)
    print ""
    print "makerFinalCash", makerFinalCash, unfix(makerFinalCash)
    print "takerFinalCash", takerFinalCash, unfix(takerFinalCash)
    print "marketFinalCash", marketFinalCash, unfix(marketFinalCash)
    print ""
    numOutcomes = contracts.markets.getMarketNumOutcomes(marketID)
    print "Maker:"
    for i in range(0, numOutcomes):
        curOutcome = i + 1
        print "outcome", curOutcome, "Shares:", contracts.markets.getParticipantSharesPurchased(marketID, t.a1, curOutcome),  unfix(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, curOutcome))
    print "Taker:"
    for i in range(0, numOutcomes):
        curOutcome = i + 1
        print "outcome", curOutcome, "Shares:", contracts.markets.getParticipantSharesPurchased(marketID, t.a2, curOutcome),  unfix(contracts.markets.getParticipantSharesPurchased(marketID, t.a2, curOutcome))

def test_wcl(contracts, amountOfTests=1):
    t = contracts._ContractLoader__tester
    print "Initiating Fuzzy WCL Tests"
    print "Amount of times looping through tests:", amountOfTests
    print ""
    def test_fuzzy_wcl():
        for i in range(0, amountOfTests):
            contracts._ContractLoader__state.mine(1)
            # test_binary(contracts, i)
            contracts._ContractLoader__state.mine(1)
            test_categorical(contracts, i)
            contracts._ContractLoader__state.mine(1)
            # test_scalar(contracts, i)
    test_fuzzy_wcl()
    print ""
    print "Fuzzy WCL Tests Complete"
    print "Amount of times looped through tests:", amountOfTests

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_wcl(contracts)
