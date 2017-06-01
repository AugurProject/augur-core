#!/usr/bin/env python
from __future__ import division
import math
import random
import os
import sys
import json
import iocapture
import ethereum.tester
from decimal import *

eventCreationCounter = 0
def fix(n):
    return int((Decimal(str(n)) * Decimal(10)**Decimal(18)).quantize(0))

def unfix(n):
    return n / 10**18
    # return str(Decimal(str(n)) / Decimal(10)**Decimal(18))

def hex2str(h):
    return hex(h)[2:-1]

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
    fxpMaxValue = fix(3)
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
    contracts.cash.publicDepositEther(value=fix(10000), sender=t.k1)
    contracts.cash.approve(contracts.createMarket.address, fix(10000), sender=t.k1)
    branch = 1010101
    fxpTradingFee = 20000000000000001
    tag1 = 123
    tag2 = 456
    tag3 = 789
    extraInfo = "rabble rabble rabble"
    currency = contracts.cash.address
    print 'we are getting here fine...'
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
# money:      500000000000000000
# amount:     1000000000000000000
# price:      1500000000000000000
 # contracts.markets.getMarketShareContracts(998373807722627158989243220182876893797878151823)
# [189109708458247235150114606012016580118456428437L, 1368626844341501049932299104410892120609773474330L]
def test_wcl(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
    branch = 1010101
    assert(contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1) == 1), "Hit Reputation faucet"
    binaryEventID = createEventType(contracts, 'binary')
    categoricalEventID = createEventType(contracts, 'categorical')
    scalarEventID = createEventType(contracts, 'scalar')
    binaryMarketID = createMarket(contracts, binaryEventID)
    categoricalMarketID = createMarket(contracts, categoricalEventID)
    scalarMarketID = createMarket(contracts, scalarEventID)
    print ""
    def fuzzyTests():
        print "Start fuzzy tests"
        # print ""
        # print "eventIDs: (bin, cat, sca)"
        # print binaryEventID
        # print categoricalEventID
        # print scalarEventID
        # print "marketIDs: (bin, cat, sca)"
        # print binaryMarketID
        # print categoricalMarketID
        # print scalarMarketID
        # print ""
        contracts._ContractLoader__state.mine(1)
        assert(contracts.orders.getOrderIDs(binaryMarketID) == []), "binary market shouldn't have any orders yet"
        assert(contracts.orders.getOrderIDs(categoricalMarketID) == []), "categorical market shouldn't have any orders yet"
        assert(contracts.orders.getOrderIDs(scalarMarketID) == []), "scalar market shouldn't have any orders yet"
        assert(contracts.cash.approve(contracts.makeOrder.address, fix(100), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
        makerInitialCash = contracts.cash.balanceOf(t.a1)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(binaryMarketID))
        # print(makerInitialCash)
        # print(marketInitialCash)
        with iocapture.capture() as captured:
            # types: 1 bid, 2 sell
            orderID = contracts.makeOrder.publicMakeOrder(1, fix(1), fix('1.5'), binaryMarketID, 1, 1, sender=t.k1)
            logged = captured.stdout
        logMakeOrder = parseCapturedLogs(logged)[-1]
        # print 'logMakeOrder:'
        # print(logMakeOrder)
        # print 'cash post order'
        # print(contracts.cash.balanceOf(t.a1))
        # print(contracts.cash.balanceOf(contracts.info.getWallet(binaryMarketID)))
        # print(contracts.orders.getLastOrder(binaryMarketID))
        # print(contracts.orders.getOrder(contracts.orders.getLastOrder(binaryMarketID)))
        print "End fuzzy tests"
    fuzzyTests()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_wcl(contracts)
