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

def test_wcl(contracts):
    t = contracts._ContractLoader__tester
    branch = 1010101
    contracts.cash.publicDepositEther(value=fix(10000), sender=t.k1)
    contracts.cash.publicDepositEther(value=fix(10000), sender=t.k2)
    def test_fill_bid():
        # Test case:
        # binary event market
        # maker escrows cash, taker does not have shares of outcome
        for i in range(0, 11):
            contracts._ContractLoader__state.mine(1)
            eventID = createEventType(contracts, 'binary')
            marketID = createMarket(contracts, eventID)
            contracts._ContractLoader__state.mine(1)
            randomAmount = random.randint(1, 11)
            randomPrice = random.random()
            # randomAmount = 2
            # randomPrice = 0.5
            orderType = 1 # bid
            fxpAmount = fix(randomAmount)
            fxpPrice = fix(randomPrice + unfix(contracts.events.getMinValue(eventID)))
            expectedCash = int(unfix(fxpAmount*(fxpPrice - contracts.events.getMinValue(eventID))))
            fxpExpectedCash = fix((unfix(fxpAmount)*((unfix(fxpPrice) - unfix(contracts.events.getMinValue(eventID))))))
            outcomeID = 2
            tradeGroupID = 10
            fxpAllowance = fix(10) + expectedCash
            # print ""
            # print "random info:"
            # print "fxpAmount:", fxpAmount, unfix(fxpAmount)
            # print "fxpPrice:", fxpPrice, unfix(fxpPrice)
            # print "expectedCash:", expectedCash, unfix(expectedCash)
            # print ""
            # approvals
            fxpEtherDepositValue = fix(10) + expectedCash
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            assert(contracts.cash.approve(contracts.makeOrder.address, fxpAllowance, sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
            assert(contracts.cash.approve(contracts.takeOrder.address, fxpAllowance, sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
            abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])
            outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
            # end approvals - Start makeOrder
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            # print ""
            # print "About to makeOrder..."
            # print "makerInitialCash", unfix(makerInitialCash)
            # print "takerInitialCash", unfix(takerInitialCash)
            # print "marketInitialCash", unfix(marketInitialCash)
            # print ""
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1)
            order = contracts.orders.getOrder(orderID)
            assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
            makerIntermediateCash = contracts.cash.balanceOf(t.a1)
            takerIntermediateCash = contracts.cash.balanceOf(t.a2)
            marketIntermediateCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            # print "makerIntermediateCash", unfix(makerIntermediateCash)
            # print "takerIntermediateCash", unfix(takerIntermediateCash)
            # print "marketIntermediateCash", unfix(marketIntermediateCash)
            # print ""
            # print "starting take order section"
            # print ""
            fxpAmountTakerWants = fxpAmount
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=t.k2)
            assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
            contracts._ContractLoader__state.mine(1)
            # print 'just before market balance check...'
            # print contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            # print 'expectedCash:', expectedCash
            # print 'fxpExpectedCash:', fxpExpectedCash
            assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == fxpExpectedCash), "Market's cash balance should be (price - 1)*amount"
            # print ""
            # print "About to TakeOrder..."
            # print ""
            fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=t.k2)
            assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
            makerFinalCash = contracts.cash.balanceOf(t.a1)
            takerFinalCash = contracts.cash.balanceOf(t.a2)
            marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            print ""
            print "random info:"
            print "fxpAmount:", fxpAmount, unfix(fxpAmount)
            print "fxpPrice:", fxpPrice, unfix(fxpPrice)
            print "expectedCash:", expectedCash, unfix(expectedCash)
            print ""
            print "makerInitialCash", unfix(makerInitialCash)
            print "takerInitialCash", unfix(takerInitialCash)
            print "marketInitialCash", unfix(marketInitialCash)
            print ""
            print "makerIntermediateCash", unfix(makerIntermediateCash)
            print "takerIntermediateCash", unfix(takerIntermediateCash)
            print "marketIntermediateCash", unfix(marketIntermediateCash)
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
            assert(marketFinalCash == fxpAmount), "Market's cash balance should be the fxpAmount of the maker's Order"
            assert(makerFinalCash == makerInitialCash - fxpExpectedCash), "maker's cash balance should be maker's initial balance - (price-marketMinValue)*amount"
            assert(takerFinalCash == takerInitialCash - (fxpAmount - fxpExpectedCash)), "taker's cash balance should be taker's initial balance - (price-marketMinValue)*amountTakerWanted"
            assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID) == fxpAmountTakerWants), "shares for outcome 2 for maker should be = to the amount takerWanted"
            assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1) == fxpAmountTakerWants), "shares for outcome 1 for taker should be = to the amount takerWanted"
            assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1) == 0), "maker should have 0 shares in the outcomeID 1"
            assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a2, outcomeID) == 0), "taker should have 0 shares in the outcomeID 2"
    test_fill_bid()


if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_wcl(contracts)
