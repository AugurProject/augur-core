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
    contracts.cash.publicDepositEther(value=fix(10000), sender=t.k1)
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
    s = contracts._ContractLoader__state
    branch = 1010101
    assert(contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1) == 1), "Hit Reputation faucet"
    contracts._ContractLoader__state.mine(1)
    binaryEventID = createEventType(contracts, 'binary')
    categoricalEventID = createEventType(contracts, 'categorical')
    scalarEventID = createEventType(contracts, 'scalar')
    binaryMarketID = createMarket(contracts, binaryEventID)
    categoricalMarketID = createMarket(contracts, categoricalEventID)
    scalarMarketID = createMarket(contracts, scalarEventID)
    def fuzzyTests():
        print "Start fuzzy tests"
        global shareTokenContractTranslator
        outcomeShareContractWrapper = makeOutcomeShareContractWrapper(contracts)
        contracts._ContractLoader__state.mine(1)
        outcomeOneShareContract = contracts.markets.getOutcomeShareContract(binaryMarketID, 1)
        outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(binaryMarketID, 2)
        outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(binaryMarketID, 1)
        outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(binaryMarketID, 2)
        assert(contracts.orders.getOrderIDs(binaryMarketID) == []), "binary market shouldn't have any orders yet"
        assert(contracts.orders.getOrderIDs(categoricalMarketID) == []), "categorical market shouldn't have any orders yet"
        assert(contracts.orders.getOrderIDs(scalarMarketID) == []), "scalar market shouldn't have any orders yet"
        assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
        fxpAllowance = fix(100)
        abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeBidOrder.address, fxpAllowance])
        contracts.cash.publicDepositEther(value=fix(10000), sender=t.k2)
        assert(int(contracts._ContractLoader__state.send(t.k2, outcomeTwoShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeBidOrder contract to spend shares from the user's account (account 2)"
        assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a2, contracts.takeBidOrder.address) == fxpAllowance), "takeBidOrder contract's allowance should be equal to the amount approved"
        makerInitialCash = contracts.cash.balanceOf(t.a1)
        takerInitialCash = contracts.cash.balanceOf(t.a2)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(binaryMarketID))
        makerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a1, 1)
        makerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a1, 2)
        takerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a2, 1)
        takerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a2, 2)
        marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, outcomeOneShareWallet, 1)
        marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, outcomeTwoShareWallet, 2)
        print('makerInitialCash', unfix(makerInitialCash))
        print('takerInitialCash', unfix(takerInitialCash))
        print('marketInitialCash', unfix(marketInitialCash))
        print('marketInitialOutcomeOneShares', marketInitialOutcomeOneShares)
        print('marketInitialOutcomeTwoShares', marketInitialOutcomeTwoShares)
        # 1. Maker places a bid order. Cash sent from maker to market.
        contracts._ContractLoader__state.mine(1)
        with iocapture.capture() as captured:
            # types: 1 bid, 2 sell
            orderID = contracts.makeOrder.publicMakeOrder(1, fix(1), fix('1.5'), binaryMarketID, 1, 1, sender=t.k1)
            logged = captured.stdout
        logMakeOrder = parseCapturedLogs(logged)[-1]
        contracts._ContractLoader__state.mine(1)
        print ''
        makerIntermediateCash = contracts.cash.balanceOf(t.a1)
        takerIntermediateCash = contracts.cash.balanceOf(t.a2)
        marketIntermediateCash = contracts.cash.balanceOf(contracts.info.getWallet(binaryMarketID))
        print('maker, taker, market', makerIntermediateCash, takerIntermediateCash, marketIntermediateCash)
        print('logMakeOrder:', logMakeOrder)
        print ""
        print('orderID:', orderID)
        print ""
        fxpMinValue = contracts.events.getMinValue(binaryEventID)
        fxpCashPaidByMaker = int(Decimal(fix(1)) * (Decimal(fix('1.5')) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
        contracts._ContractLoader__state.mine(1)
        assert(makerIntermediateCash == makerInitialCash - fxpCashPaidByMaker), "Maker's cash balance should be decreased by fxpCashPaidByMaker"
        assert(takerIntermediateCash == takerInitialCash), "Taker's cash balance should be unchanged"
        assert(marketIntermediateCash == fxpCashPaidByMaker), "Market's intermediate cash balance should be equal to fxpCashPaidByMaker"
        makerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a1, 1)
        makerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a1, 2)
        takerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a2, 1)
        takerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a2, 2)
        marketIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, outcomeOneShareWallet, 1)
        marketIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, outcomeTwoShareWallet, 2)
        # 2. Taker fills bid order. Taker is short selling: taker buys a complete set then sells a single outcome.
        contracts._ContractLoader__state.mine(1)
        fxpAmountTakerWants = fix(1)
        assert(contracts.cash.approve(contracts.completeSets.address, fix(10), sender=t.k1) == 1), "Approve completeSets contract to spend cash from account 1"
        assert(contracts.cash.approve(contracts.completeSets.address, fix(10), sender=t.k2) == 1), "Approve completeSets contract to spend cash from account 1"
        tradeHash = contracts.orders.makeOrderHash(binaryMarketID, 1, 1, sender=t.k2)
        assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
        assert(contracts.cash.approve(contracts.takeBidOrder.address, fix(10), sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
        contracts._ContractLoader__state.mine(1)
        fxpAmountRemaining = contracts.takeBidOrder.takeBidOrder(t.a2, orderID, fxpAmountTakerWants, sender=t.k0)
        assert(fxpAmountRemaining == fxpAmountTakerWants - fxpOrderAmount), "Amount remaining should be fxpAmountTakerWants - fxpOrderAmount"
        makerFinalCash = contracts.cash.balanceOf(t.a1)
        takerFinalCash = contracts.cash.balanceOf(t.a2)
        marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(binaryMarketID))
        fxpAmountFilled = min(fxpAmountTakerWants, fxpOrderAmount)
        fxpCompleteSetsCostPaidByTaker = fxpAmountFilled
        print('maker, taker, market', makerFinalCash, takerFinalCash, marketFinalCash)
        assert(makerFinalCash == makerIntermediateCash), "Maker's final cash balance should be unchanged from intermediate cash balance"
        assert(takerFinalCash == takerInitialCash + fxpCashPaidByMaker - fxpCompleteSetsCostPaidByTaker), "Taker's cash balance should be increased by fxpCashPaidByMaker - fxpCompleteSetsCostPaidByTaker"
        assert(marketFinalCash == fxpAmountFilled), "Market's final cash balance should be equal to fxpAmountFilled"
        makerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a1, 1)
        makerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a1, 2)
        takerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a2, 1)
        takerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, t.a2, 2)
        marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, outcomeOneShareWallet, 1)
        marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(binaryMarketID, outcomeTwoShareWallet, 2)
        assert(makerFinalOutcomeOneShares == 0), "Maker's final outcome 1 shares balance should be 0"
        assert(makerFinalOutcomeTwoShares == fxpAmountFilled), "Maker's final outcome 2 shares balance should be equal to fxpAmountFilled"
        assert(takerFinalOutcomeOneShares == fxpAmountFilled), "Taker's final outcome 1 shares balance should be equal to fxpAmountFilled"
        assert(takerFinalOutcomeTwoShares == 0), "Taker's final outcome 2 shares balance should be 0"
        assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
        assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
        print "End fuzzy tests"
    fuzzyTests()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_wcl(contracts)
