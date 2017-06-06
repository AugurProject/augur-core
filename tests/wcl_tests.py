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
    return fix((unfix(fxpAmount)*((unfix(fxpPrice) - unfix(contracts.events.getMinValue(eventID))))))

def calculateHighSide(contracts, eventID, fxpAmount, fxpPrice):
    return fix((unfix(fxpAmount)*((unfix(contracts.events.getMaxValue(eventID)) - unfix(fxpPrice)))))

def test_binary(contracts, i):
    # Test case:
    # binary event market
    t = contracts._ContractLoader__tester
    eventID = createEventType(contracts, 'binary')
    marketID = createMarket(contracts, eventID)
    randomAmount = random.randint(1, 11)
    randomPrice = random.random()
    def test_bid_case_1():
        # maker escrows cash, taker does not have shares of outcome
        contracts._ContractLoader__state.mine(1)
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedCash = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedCash = int(fxpExpectedCash)
        outcomeID = 2
        tradeGroupID = 10
        fxpAllowance = fix(1.1*randomAmount)
        fxpEtherDepositValue = fix(2*randomAmount)
        assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
        assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
        # TODO: create an approval function to automate approvals for tests
        assert(contracts.cash.approve(contracts.makeOrder.address, fxpAllowance, sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
        assert(contracts.cash.approve(contracts.takeOrder.address, fxpAllowance, sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
        outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
        abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
        assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
        # end approvals - Start makeOrder
        takerInitialCash = contracts.cash.balanceOf(t.a2)
        makerInitialCash = contracts.cash.balanceOf(t.a1)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1)
        order = contracts.orders.getOrder(orderID)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=t.k2)
        assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == fxpExpectedCash), "Market's cash balance should be (price - 1)*amount"
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=t.k2)
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(t.a1)
        takerFinalCash = contracts.cash.balanceOf(t.a2)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedCash, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants)
        print ""
        print "fxpAllowance", fxpAllowance, unfix(fxpAllowance)
        print "fxpEtherDepositValue", fxpEtherDepositValue, unfix(fxpEtherDepositValue)
        print ""
        # confirm cash
        assert(marketFinalCash == fxpAmount), "Market's cash balance should be the fxpAmount of the maker's Order"
        assert(makerFinalCash == makerInitialCash - fxpExpectedCash), "maker's cash balance should be maker's initial balance - (price-marketMinValue)*amount"
        assert(takerFinalCash == takerInitialCash - (fxpAmount - fxpExpectedCash)), "taker's cash balance should be taker's initial balance - (price-marketMinValue)*amountTakerWanted"
        # confirm shares
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID) == fxpAmountTakerWants), "shares for outcome 2 for maker should be = to the amount takerWanted"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1) == fxpAmountTakerWants), "shares for outcome 1 for taker should be = to the amount takerWanted"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1) == 0), "maker should have 0 shares in the outcomeID 1"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a2, outcomeID) == 0), "taker should have 0 shares in the outcomeID 2"
    def test_bid_case_4():
        # maker has shares in other outcomes, taker has shares of outcome
        contracts._ContractLoader__state.mine(1)
        orderType = 1 # bid
        fxpAmount = fix(randomAmount)
        fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
        fxpExpectedTakerGain = calculateLowSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedTakerGain = int(fxpExpectedTakerGain)
        fxpExpectedMakerGain = calculateHighSide(contracts, eventID, fxpAmount, fxpPrice)
        expectedMakerGain = int(fxpExpectedMakerGain)
        outcomeID = 1
        tradeGroupID = 10
        fxpAllowance = fix(1.1*randomAmount)
        print ""
        print "fxpAllowance", fxpAllowance, unfix(fxpAllowance)
        print ""
        # fxpEtherDepositValue = fix(1.1*randomAmount)
        # assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
        # assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
        assert(contracts.cash.approve(contracts.makeOrder.address, fxpAllowance, sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
        assert(contracts.cash.approve(contracts.takeOrder.address, fxpAllowance, sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
        # TODO: create an approval function to automate approvals for tests
        outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
        outcome2ShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
        abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 1)"
        assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
        assert(int(contracts._ContractLoader__state.send(t.k1, outcome2ShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 1)"
        assert(int(contracts._ContractLoader__state.send(t.k2, outcome2ShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
        abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])
        assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 1)"
        assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 2)"
        assert(int(contracts._ContractLoader__state.send(t.k1, outcome2ShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 1)"
        assert(int(contracts._ContractLoader__state.send(t.k2, outcome2ShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 2)"
        assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
        # end approvals - Start makeOrder
        takerInitialCash = contracts.cash.balanceOf(t.a2)
        makerInitialCash = contracts.cash.balanceOf(t.a1)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
        orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1)
        order = contracts.orders.getOrder(orderID)
        assert(makerInitialShares == order[9]), "Shares Escrowed should be = to the shares the maker started with"
        assert(makerInitialShares - order[9] == contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)), "maker shouldn't have shares in outcomeID anymore"
        fxpAmountTakerWants = fxpAmount
        tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=t.k2)
        assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
        contracts._ContractLoader__state.mine(1)
        # assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == fxpExpectedCash), "Market's cash balance should be (price - 1)*amount"
        print "taking order.."
        fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=t.k2)
        print "took that order..."
        assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        makerFinalCash = contracts.cash.balanceOf(t.a1)
        takerFinalCash = contracts.cash.balanceOf(t.a2)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        # TODO: remove "print_for_dev" before finishing.
        print_for_dev(contracts, marketID, fxpAmount, fxpPrice, outcomeID, expectedMakerGain, makerInitialCash, takerInitialCash, marketInitialCash, makerFinalCash, takerFinalCash, marketFinalCash, fxpAmountTakerWants, expectedTakerGain)
        # confirm cash
        fxpCumulativeScale = contracts.markets.getCumulativeScale(marketID)
        fxpTradingFee = contracts.markets.getTradingFee(marketID)
        fxpMoneyFromSellCompleteSets = fix(unfix(makerInitialShares)*unfix(fxpCumulativeScale))
        print ""
        print "marketTradingFee", fxpTradingFee, unfix(fxpTradingFee)
        print "expectedMakerGain", expectedMakerGain, unfix(expectedMakerGain)
        print "expectedTakerGain", expectedTakerGain, unfix(expectedTakerGain)
        print "expectedFinalMaker", (makerInitialCash + expectedMakerGain), unfix(makerInitialCash + expectedMakerGain)
        print "expectedFinalTaker", (takerInitialCash + expectedTakerGain), unfix(takerInitialCash + expectedTakerGain)
        print "actualMaker/TakerFinal", makerFinalCash, takerFinalCash
        print "actualUnfixedMaker/TakerFinal", unfix(makerFinalCash), unfix(takerFinalCash)
        print ""
        print "expectedMarketFinal", fix(randomAmount*0.01), randomAmount*0.01
        print marketFinalCash, fix(randomAmount*0.01)
        print unfix(marketFinalCash), randomAmount*0.01
        print ""
        print "makerInitialShares", makerInitialShares, unfix(makerInitialShares)
        fxpFee = fix(((unfix(fxpTradingFee)*unfix(makerInitialShares))*unfix(fxpCumulativeScale)))
        print "fxpFee", fxpFee, unfix(fxpFee)
        print "fxpTesting..", (fxpFee/2), unfix(fxpFee/2)
        print "fxpMoneyFromSellCompleteSets", fxpMoneyFromSellCompleteSets, unfix(fxpMoneyFromSellCompleteSets)
        pretest = unfix(fxpFee) + unfix(fxpExpectedTakerGain)
        print "pretest", pretest, fix(pretest)
        test = fix((unfix(fxpMoneyFromSellCompleteSets) - pretest))
        # test = fix(unfix(fxpMoneyFromSellCompleteSets) - (unfix(fxpFee) + unfix(fxpExpectedTakerGain)))
        print "finally:", test, unfix(test)
        print "another:", ((makerInitialCash - test) + expectedMakerGain), unfix(((makerInitialCash - test) + expectedMakerGain))
        expectedMarketFinal = fix(randomAmount*0.01)
        assert(expectedMarketFinal == marketFinalCash), "expected market's final cash to be = to the amount of shares purchased * .01"
        assert(makerInitialCash + expectedMakerGain == makerFinalCash), "maker's cash balance should be the initial balance + expected Gain"
        assert(takerInitialCash + expectedTakerGain == takerFinalCash), "taker's cash balance should be the initial balance + expected Gain"
        # # confirm shares
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1) == 0), "maker should have 0 shares in the outcomeID 1"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1) == 0), "taker should have 0 shares in the outcomeID 1"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2) == 0), "maker should have 0 shares in the outcomeID 2"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2) == 0), "taker should have 0 shares in the outcomeID 2"
    test_bid_case_1()
    test_bid_case_4()

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
    print "makerInitialCash", unfix(makerInitialCash)
    print "takerInitialCash", unfix(takerInitialCash)
    print "marketInitialCash", unfix(marketInitialCash)
    print ""
    print "fxpAmountTakerWants", fxpAmountTakerWants, unfix(fxpAmountTakerWants)
    print ""
    print "makerFinalCash", unfix(makerFinalCash)
    print "takerFinalCash", unfix(takerFinalCash)
    print "marketFinalCash", unfix(marketFinalCash)
    print ""
    print "account 1:"
    print "outcome 2 Shares:",  unfix(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID))
    print "outcome 1 Shares:", unfix(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1))
    print "account2:"
    print "outcome 2 shares:",  unfix(contracts.markets.getParticipantSharesPurchased(marketID, t.a2, outcomeID))
    print "outcome 1 shares:", unfix(contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1))

def test_wcl(contracts, amountOfTests=1):
    t = contracts._ContractLoader__tester
    contracts.cash.publicDepositEther(value=fix(10000), sender=t.k1)
    contracts.cash.publicDepositEther(value=fix(10000), sender=t.k2)
    def test_fuzzy_wcl():
        for i in range(0, amountOfTests):
            contracts._ContractLoader__state.mine(1)
            test_binary(contracts, i)
    test_fuzzy_wcl()


if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_wcl(contracts)
