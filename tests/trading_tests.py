#!/usr/bin/env python
"""
Trading tests:
+ functions/createEvent.se
+ functions/createMarket.se
+ functions/cash.se
+ functions/makeOrder.se
+ functions/completeSets.se
+ functions/cancelOrder.se
+ functions/shareTokens.se
+ functions/wallet.se
+ functions/takeAskOrder.se
+ functions/takeBidOrder.se
+ functions/takeOrder.se
+ functions/decreaseTradingFee.se
+ functions/binaryOrCategoricalPayouts.se
+ functions/scalarPayouts.se
+ functions/claimMarketProceeds.se

"""
from __future__ import division
import os
import sys
import json
import ethereum
import iocapture
from decimal import *

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))

from upload_contracts import ContractLoader

contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])

shareTokenContractTranslator = ethereum.abi.ContractTranslator('[{"constant": false, "type": "function", "name": "allowance(address,address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "address", "name": "spender"}]}, {"constant": false, "type": "function", "name": "approve(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "balanceOf(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "address"}]}, {"constant": false, "type": "function", "name": "changeTokens(int256,int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "trader"}, {"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "createShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "destroyShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "getDecimals()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getName()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getSymbol()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "modifySupply(int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "setController(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "newController"}]}, {"constant": false, "type": "function", "name": "suicideFunds(address)", "outputs": [], "inputs": [{"type": "address", "name": "to"}]}, {"constant": false, "type": "function", "name": "totalSupply()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "transfer(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "transferFrom(address,address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "from"}, {"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval(address,address,uint256)"}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer(address,address,uint256)"}, {"inputs": [{"indexed": false, "type": "int256", "name": "from"}, {"indexed": false, "type": "int256", "name": "to"}, {"indexed": false, "type": "int256", "name": "value"}, {"indexed": false, "type": "int256", "name": "senderBalance"}, {"indexed": false, "type": "int256", "name": "sender"}, {"indexed": false, "type": "int256", "name": "spenderMaxValue"}], "type": "event", "name": "echo(int256,int256,int256,int256,int256,int256)"}]')

outcomeShareContractWrapper = contracts._ContractLoader__state.abi_contract("""
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

def createBinaryEvent():
    global eventCreationCounter
    global contracts
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

def createCategoricalEvent(numOutcomes=8):
    global eventCreationCounter
    global contracts
    t = contracts._ContractLoader__tester
    contracts.cash.publicDepositEther(value=fix(100), sender=t.k1)
    contracts.cash.approve(contracts.createEvent.address, fix(100), sender=t.k1)
    branch = 1010101
    contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1)
    description = "test categorical event"
    expDate = 3000000002 + eventCreationCounter
    eventCreationCounter += 1
    fxpMinValue = fix(1)
    fxpMaxValue = fix(7)
    resolution = "http://lmgtfy.com"
    resolutionAddress = t.a2
    currency = contracts.cash.address
    forkResolveAddress = contracts.forkResolution.address
    return contracts.createEvent.publicCreateEvent(branch, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)

def createScalarEvent(fxpMinValue=fix(1), fxpMaxValue=fix(10)):
    global eventCreationCounter
    global contracts
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

def createEventType(eventType):
    if eventType == "binary":
        eventID = createBinaryEvent()
    elif eventType == "scalar":
        eventID = createScalarEvent()
    else:
        eventID = createCategoricalEvent()
    return eventID

def createMarket(eventID):
    global contracts
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

def buyCompleteSets(marketID, fxpAmount, sender=None):
    global contracts
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

def test_Cash():
    global contracts
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    initialEtherBalance2 = contracts._ContractLoader__state.block.get_balance(t.a2)
    def test_init():
        assert(hex2str(contracts.cash.getName()) == '4361736800000000000000000000000000000000000000000000000000000000'), "currency name"
        assert(contracts.cash.getDecimals() == 18), "number of decimals"
        assert(hex2str(contracts.cash.getSymbol()) == '4341534800000000000000000000000000000000000000000000000000000000'), "currency symbol"
    def test_publicDepositEther():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.publicDepositEther(value=100, sender=t.k1) == 1), "deposit ether"
        assert(contracts.cash.balanceOf(t.a1) == 100), "balance equal to deposit"
        assert(contracts.cash.totalSupply() == 100), "totalSupply equal to deposit"
    def test_publicWithdrawEther():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.getInitiated(sender=t.k1) == 0), "withdraw not initiated"
        try:
            raise Exception(contracts.cash.publicWithdrawEther(t.a2, 110, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdraw should throw due to insufficient funds"
        assert(contracts.cash.publicWithdrawEther(t.a2, 30, sender=t.k1)), "initiate withdrawal"
        assert(contracts.cash.getInitiated(sender=t.k1) == contracts._ContractLoader__state.block.timestamp), "withdraw initiated"
        try:
            raise Exception(contracts.cash.publicWithdrawEther(t.a2, 30, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdraw should throw (3 days haven't passed)"
        contracts._ContractLoader__state.block.timestamp += 259199
        try:
            raise Exception(contracts.cash.publicWithdrawEther(t.a2, 30, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdraw should throw (3 days still haven't passed)"
        contracts._ContractLoader__state.block.timestamp += 1
        assert(contracts.cash.publicWithdrawEther(t.a2, 30, sender=t.k1)), "withdraw should succeed"
        assert(contracts.cash.balanceOf(t.a1) == 70), "decrease sender's balance by 30"
        assert(contracts.cash.balanceOf(t.a2) == 0), "receiver's cash balance still equals 0"
        assert(contracts._ContractLoader__state.block.get_balance(t.a2) - initialEtherBalance2 == 30), "receiver's ether balance increased by 30"
        assert(contracts.cash.totalSupply() == 70), "total supply decreased by 30"
        try:
            raise Exception(contracts.cash.publicWithdrawEther(t.a2, -10, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative withdraw should throw"
        assert(contracts.cash.getInitiated(sender=t.k1) == 0), "withdraw no longer initiated"
    def test_transfer():
        contracts._ContractLoader__state.mine(1)
        with iocapture.capture() as captured:
            retval = contracts.cash.transfer(t.a2, 5, sender=t.k1)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transfer 5 cash to a2"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == 5)
        assert(contracts.cash.balanceOf(t.a1) == 65), "balance of a1 decreased by 5"
        assert(contracts.cash.balanceOf(t.a2) == 5), "balance of a2 increased by 5"
        assert(contracts.cash.totalSupply() == 70), "totalSupply unchanged"
        try:
            raise Exception(contracts.cash.transfer(t.a2, 70, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should throw if insufficient funds"
        try:
            raise Exception(contracts.cash.transfer(t.a2, -5, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative transfer should throw"
        with iocapture.capture() as captured:
            retval = contracts.cash.transfer(t.a2, 0, sender=t.k1)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transfer should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == 0)
        assert(contracts.cash.balanceOf(t.a1) == 65), "balance of a1 unchanged"
        assert(contracts.cash.balanceOf(t.a2) == 5), "balance of a2 unchanged"
        assert(contracts.cash.totalSupply() == 70), "totalSupply unchanged"
    def test_transferFrom():
        try:
            raise Exception(contracts.cash.transferFrom(t.a1, t.a2, 7, sender=t.k2))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transferFrom should throw, msg.sender is not approved"
    def test_approve():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.allowance(t.a1, t.a2) == 0), "initial allowance is 0"
        with iocapture.capture() as captured:
            retval = contracts.cash.approve(t.a2, 10, sender=t.k1)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "approve a2 to spend 10 cash from a1"
        assert(logged["_event_type"] == "Approval")
        assert(long(logged["owner"], 16) == address1)
        assert(long(logged["spender"], 16) == address2)
        assert(logged["value"] == 10)
        assert(contracts.cash.allowance(t.a1, t.a2) == 10), "allowance is 10 after approval"
        with iocapture.capture() as captured:
            retval = contracts.cash.transferFrom(t.a1, t.a2, 7, sender=t.k2)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transferFrom should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == 7)
    def test_setController():
        try:
            raise Exception(contracts.wallet.setController(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "setController should fail when attempted by non-controller address"
    def test_suicideFunds():
        try:
            raise Exception(contracts.cash.suicideFunds(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "suicideFunds should fail when attempted by non-controller address"
    def test_exceptions():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = fix(10)
        fxpWithdrawAmount = fix(2)
        try:
            raise Exception(contracts.cash.depositEther(t.a1, value=fxpAmount, sender=t.k1), "deposit ether")
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "depositEther should fail if called from a non-whitelisted account (account 1)"
        assert(contracts.cash.publicDepositEther(value=fxpAmount, sender=t.k1) == 1), "publicDepositEther should succeed"
        try:
            raise Exception(contracts.cash.withdrawEther(t.a1, t.a1, fxpWithdrawAmount, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdrawEther should fail if called from a non-whitelisted account (account 1)"
    test_publicDepositEther()
    test_publicWithdrawEther()
    test_transfer()
    test_transferFrom()
    test_approve()
    test_setController()
    test_suicideFunds()
    test_exceptions()

def test_ShareTokens():
    global contracts
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    def test_init():
        assert(hex2str(contracts.shareTokens.getName()) == '5368617265730000000000000000000000000000000000000000000000000000'), "currency name"
        assert(contracts.shareTokens.getDecimals() == 18), "number of decimals"
        assert(hex2str(contracts.shareTokens.getSymbol()) == '5348415245000000000000000000000000000000000000000000000000000000'), "currency symbol"
    def test_createShares():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = fix(10)
        initialTotalSupply = contracts.shareTokens.totalSupply()
        initialBalance = contracts.shareTokens.balanceOf(t.a1)
        assert(contracts.shareTokens.createShares(t.a1, fxpAmount, sender=t.k0) == 1), "Create share tokens for address 1"
        assert(contracts.shareTokens.totalSupply() - initialTotalSupply == fxpAmount), "Total supply increase should equal the number of tokens created"
        assert(contracts.shareTokens.balanceOf(t.a1) - initialBalance == fxpAmount), "Address 1 token balance increase should equal the number of tokens created"
    def test_destroyShares():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = fix(10)
        initialTotalSupply = contracts.shareTokens.totalSupply()
        initialBalance = contracts.shareTokens.balanceOf(t.a1)
        assert(contracts.shareTokens.destroyShares(t.a1, fxpAmount, sender=t.k0) == 1), "Destroy share tokens owned by address 1"
        assert(initialTotalSupply - contracts.shareTokens.totalSupply() == fxpAmount), "Total supply decrease should equal the number of tokens destroyed"
        assert(initialBalance - contracts.shareTokens.balanceOf(t.a1) == fxpAmount), "Address 1 token balance decrease should equal the number of tokens destroyed"
    def test_transfer():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = fix(10)
        fxpTransferAmount = fix(2)
        assert(contracts.shareTokens.createShares(t.a1, fxpAmount, sender=t.k0) == 1), "Create share tokens for address 1"
        initialTotalSupply = contracts.shareTokens.totalSupply()
        initialBalance1 = contracts.shareTokens.balanceOf(t.a1)
        initialBalance2 = contracts.shareTokens.balanceOf(t.a2)
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.transfer(t.a2, fxpTransferAmount, sender=t.k1)
            logged = captured.stdout
        logged = parseCapturedLogs(logged)[-1]
        assert(retval == 1), "transfer should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == fxpTransferAmount)
        afterTransferBalance1 = contracts.shareTokens.balanceOf(t.a1)
        afterTransferBalance2 = contracts.shareTokens.balanceOf(t.a2)
        assert(initialBalance1 - afterTransferBalance1 == fxpTransferAmount), "Decrease in address 1's balance should equal amount transferred"
        assert(afterTransferBalance2 - initialBalance2 == fxpTransferAmount), "Increase in address 2's balance should equal amount transferred"
        assert(contracts.shareTokens.totalSupply() == initialTotalSupply), "Total supply should be unchanged"
        try:
            raise Exception(contracts.shareTokens.transfer(t.a2, fix(70), sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should throw if insufficient funds"
        try:
            raise Exception(contracts.shareTokens.transfer(t.a2, -5, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative transfer should throw"
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.transfer(t.a2, 0, sender=t.k1)
            logged = captured.stdout
        logged = parseCapturedLogs(logged)[-1]
        assert(retval == 1), "transfer with 0 value should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == 0)
        assert(contracts.shareTokens.balanceOf(t.a1) == afterTransferBalance1), "Balance of a1 should be unchanged"
        assert(contracts.shareTokens.balanceOf(t.a2) == afterTransferBalance2), "Balance of a2 should be unchanged"
        assert(contracts.shareTokens.totalSupply() == initialTotalSupply), "Total supply should be unchanged"
    def test_transferFrom():
        try:
            raise Exception(contracts.shareTokens.transferFrom(t.a1, t.a2, 7, sender=t.k2))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transferFrom should throw, msg.sender is not approved"
    def test_approve():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.shareTokens.allowance(t.a1, t.a2) == 0), "initial allowance is 0"
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.approve(t.a2, 10, sender=t.k1)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "approve a2 to spend 10 cash from a1"
        assert(logged["_event_type"] == "Approval")
        assert(long(logged["owner"], 16) == address1)
        assert(long(logged["spender"], 16) == address2)
        assert(logged["value"] == 10)
        assert(contracts.shareTokens.allowance(t.a1, t.a2) == 10), "allowance is 10 after approval"
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.transferFrom(t.a1, t.a2, 7, sender=t.k2)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transferFrom should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(long(logged["to"], 16) == address2)
        assert(long(logged["from"], 16) == address1)
        assert(logged["value"] == 7)
    def test_setController():
        try:
            raise Exception(contracts.wallet.setController(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "setController should fail when attempted by non-controller address"
    def test_suicideFunds():
        try:
            raise Exception(contracts.shareTokens.suicideFunds(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "suicideFunds should fail when attempted by non-controller address"
    def test_exceptions():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = fix(10)
        fxpTransferAmount = fix(2)
        assert(contracts.shareTokens.createShares(t.a1, fxpAmount, sender=t.k0) == 1), "Create share tokens for address 1"
        try:
            raise Exception(contracts.shareTokens.createShares(t.a1, fxpTransferAmount, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "createShares should fail if called from a non-whitelisted account (account 1)"
        try:
            raise Exception(contracts.shareTokens.destroyShares(t.a1, fxpTransferAmount, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "destroyShares should fail if called from a non-whitelisted account (account 1)"
    test_init()
    test_createShares()
    test_destroyShares()
    test_transfer()
    test_transferFrom()
    test_approve()
    test_setController()
    test_suicideFunds()
    test_exceptions()

def test_Wallet():
    global contracts
    t = contracts._ContractLoader__tester
    def test_initialize():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.wallet.initialize(contracts.cash.address, sender=t.k1) == 1), "Should initialize wallet with cash currency"
    def test_transfer():
        contracts._ContractLoader__state.mine(1)
        fxpValue = fix(100)
        assert(contracts.wallet.initialize(contracts.cash.address, sender=t.k1) == 1), "Should initialize wallet with cash currency"
        initialBalanceWallet = contracts.cash.balanceOf(contracts.wallet.address)
        initialBalance2 = contracts.cash.balanceOf(t.a2)
        assert(contracts.cash.publicDepositEther(value=fxpValue, sender=t.k2) == 1), "Should deposit ether to account 2"
        assert(contracts.cash.balanceOf(contracts.wallet.address) == initialBalanceWallet), "Wallet balance unchanged"
        assert(contracts.cash.balanceOf(t.a2) - initialBalance2 == fxpValue), "Account 2 balance increase equal to deposit"
        assert(contracts.cash.transfer(contracts.wallet.address, fxpValue, sender=t.k2) == 1), "Should transfer ether to wallet address"
        assert(contracts.cash.balanceOf(contracts.wallet.address) - initialBalanceWallet == fxpValue), "Wallet balance increase equal to deposit"
        assert(contracts.cash.balanceOf(t.a2) == initialBalance2), "Account 2 balance unchanged"
        fxpTransferValue = contracts.cash.balanceOf(contracts.wallet.address)
        try:
            raise Exception(contracts.wallet.transfer(t.a2, fxpTransferValue, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should fail when attempted by non-whitelisted address"
        try:
            raise Exception(contracts.wallet.transfer(t.a2, 0, sender=t.k0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should fail if value is zero"
        try:
            raise Exception(contracts.wallet.transfer(t.a2, -1, sender=t.k0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "transfer should fail if value is negative"
        try:
            raise Exception(contracts.wallet.transfer(0, fxpTransferValue, sender=t.k0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should fail if receiver address is zero"
        assert(contracts.wallet.transfer(t.a1, fxpTransferValue, sender=t.k0) == 1), "transfer should succeed"
        try:
            raise Exception(contracts.wallet.transfer(t.a2, fxpTransferValue, sender=t.k0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should fail if insufficient balance"
    def test_setController():
        try:
            raise Exception(contracts.wallet.setController(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "setController should fail when attempted by non-controller address"
    def test_suicideFunds():
        try:
            raise Exception(contracts.wallet.suicideFunds(t.a1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "suicideFunds should fail when attempted by non-controller address"
    test_initialize()
    test_transfer()
    test_setController()
    test_suicideFunds()

# TODO update create event tests pending final review of contract
def test_CreateEvent():
    global contracts
    t = contracts._ContractLoader__tester
    def test_checkEventCreationPreconditions():
        contracts._ContractLoader__state.mine(1)
        branch = 1010101
        periodLength = 9000
        description = "test binary event"
        expDate = 3000000000
        fxpMinValue = fix(1)
        fxpMaxValue = fix(2)
        numOutcomes = 2
        resolution = "http://lmgtfy.com"
        resolutionAddress = t.a2
        currency = contracts.cash.address
        forkResolveAddress = contracts.forkResolution.address
        try:
            contracts.createEvent.checkEventCreationPreconditions(branch, periodLength, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "checkEventCreationPreconditions should throw when createEvent contract is not the caller"
    def test_publicCreateEvent():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.publicDepositEther(value=fix(10000), sender=t.k1) == 1), "Convert ether to cash"
        assert(contracts.cash.approve(contracts.createEvent.address, fix(10000), sender=t.k1) == 1), "Approve createEvent contract to spend cash (for validity bond)"
        branch = 1010101
        assert(contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1) == 1), "Hit Reputation faucet"
        description = "test binary event"
        expDate = 3000000000
        fxpMinValue = fix(1)
        fxpMaxValue = fix(2)
        numOutcomes = 2
        resolution = "http://lmgtfy.com"
        resolutionAddress = t.a2
        currency = contracts.cash.address
        forkResolveAddress = contracts.forkResolution.address
        eventID = contracts.createEvent.publicCreateEvent(branch, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)
        assert(eventID != 0), "Event created"
        assert(contracts.info.getDescription(eventID) == description), "Description matches input"
        assert(contracts.events.getExpiration(eventID) == expDate), "Expiration date matches input"
        assert(contracts.events.getMinValue(eventID) == fxpMinValue), "Min value matches input"
        assert(contracts.events.getMaxValue(eventID) == fxpMaxValue), "Max value matches input"
        assert(contracts.events.getNumOutcomes(eventID) == numOutcomes), "Number of outcomes matches input"
        assert(contracts.events.getEventResolution(eventID) == resolution), "Resolution matches input"
        assert(hex2str(contracts.events.getEventType(eventID)) == "62696e6172790000000000000000000000000000000000000000000000000000"), "Event type is binary"
    test_checkEventCreationPreconditions()
    test_publicCreateEvent()

# TODO update create market tests pending final review of contract
def test_CreateMarket():
    global contracts
    t = contracts._ContractLoader__tester
    def test_publicCreateMarket():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.publicDepositEther(value=fix(10000), sender=t.k1) == 1), "Convert ether to cash"
        assert(contracts.cash.approve(contracts.createEvent.address, fix(10000), sender=t.k1) == 1), "Approve createEvent contract to spend cash (for validity bond)"
        assert(contracts.cash.approve(contracts.createMarket.address, fix(10000), sender=t.k1) == 1), "Approve createMarket contract to spend cash"
        branch = 1010101
        assert(contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1) == 1), "Hit Reputation faucet"
        description = "test binary event"
        expDate = 3000000001
        fxpMinValue = fix(1)
        fxpMaxValue = fix(2)
        numOutcomes = 2
        resolution = "http://lmgtfy.com"
        resolutionAddress = t.a2
        currency = contracts.cash.address
        forkResolveAddress = contracts.forkResolution.address
        eventID = contracts.createEvent.publicCreateEvent(branch, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)
        fxpTradingFee = 20000000000000001
        tag1 = 123
        tag2 = 456
        tag3 = 789
        extraInfo = "rabble rabble rabble"
        marketID = contracts.createMarket.publicCreateMarket(branch, fxpTradingFee, eventID, tag1, tag2, tag3, extraInfo, currency, 0, 0, sender=t.k1, value=fix(10000))
        assert(marketID != 0)
        assert(contracts.markets.getTradingFee(marketID) == fxpTradingFee), "Trading fee matches input"
        assert(contracts.markets.getMarketEvent(marketID) == eventID), "Market event matches input"
        assert(contracts.markets.getTags(marketID) == [tag1, tag2, tag3]), "Tags array matches input"
        assert(contracts.markets.getTopic(marketID)), "Topic matches input tag1"
        assert(contracts.markets.getExtraInfo(marketID) == extraInfo), "Extra info matches input"
        assert(contracts.cash.publicDepositEther(value=fix(10000), sender=t.k1) == 1), "Convert ether to cash"
        assert(contracts.cash.approve(contracts.createEvent.address, fix(10000), sender=t.k1) == 1), "Approve createEvent contract to spend cash (for validity bond)"
        assert(contracts.cash.approve(contracts.createMarket.address, fix(10000), sender=t.k1) == 1), "Approve createMarket contract to spend cash"
        marketID2 = contracts.createMarket.publicCreateMarket(branch, 0, eventID, tag1, tag2, tag3, extraInfo, contracts.markets.getOutcomeShareContract(marketID, 1), marketID, 1, sender=t.k1, value=fix(10000))
    test_publicCreateMarket()

def test_CompleteSets():
    global contracts
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    def test_publicBuyCompleteSets():
        contracts._ContractLoader__state.mine(1)
        eventID = createBinaryEvent()
        marketID = createMarket(eventID)
        fxpAmount = fix(10)
        senderInitialCash = contracts.cash.balanceOf(t.a1)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
        assert(contracts.cash.approve(contracts.completeSets.address, fix(10000), sender=t.k1) == 1), "Approve completeSets contract to spend cash"
        with iocapture.capture() as captured:
            result = contracts.completeSets.publicBuyCompleteSets(marketID, fxpAmount, sender=t.k1)
            logged = captured.stdout
        logCompleteSets = parseCapturedLogs(logged)[-1]
        assert(logCompleteSets["_event_type"] == "CompleteSets"), "Should emit a CompleteSets event"
        assert(logCompleteSets["sender"] == address1), "Logged sender should match input"
        assert(logCompleteSets["type"] == 1), "Logged type should be 1 (buy)"
        assert(logCompleteSets["fxpAmount"] == fxpAmount), "Logged fxpAmount should match input"
        assert(logCompleteSets["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match input"
        assert(logCompleteSets["numOutcomes"] == contracts.events.getNumOutcomes(eventID)), "Logged numOutcomes should match event's number of outcomes"
        assert(logCompleteSets["fxpFee"] == 0), "Logged fee should be 0"
        assert(logCompleteSets["market"] == marketID), "Logged market should match input"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1) == fxpAmount), "Should have 10 shares of outcome 1"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2) == fxpAmount), "Should have 10 shares of outcome 2"
        assert(senderInitialCash - contracts.cash.balanceOf(t.a1) == fxpAmount), "Decrease in sender's cash should equal 10"
        assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == fxpAmount), "Increase in market's cash should equal 10"
        assert(contracts.markets.getTotalSharesPurchased(marketID) - marketInitialTotalShares == 2*fxpAmount), "Increase in total shares purchased for this market should be 18"
        def test_exceptions():
            contracts._ContractLoader__state.mine(1)
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            fxpAmount = fix(10)
            assert(contracts.cash.approve(contracts.completeSets.address, fxpAmount, sender=t.k1) == 1), "Approve completeSets contract to spend cash"

            # Permissions exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.completeSets.buyCompleteSets(t.a1, marketID, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "buyCompleteSets should fail if called from a non-whitelisted account (account 1)"

            # buyCompleteSets exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.completeSets.publicBuyCompleteSets(marketID + 1, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicBuyCompleteSets should fail if market ID is invalid"
            try:
                raise Exception(contracts.completeSets.publicBuyCompleteSets(marketID, fix(-10), sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "publicBuyCompleteSets should throw ValueOutOfBounds exception if fxpAmount is negative"
            try:
                raise Exception(contracts.completeSets.publicBuyCompleteSets(marketID, 0, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicBuyCompleteSets should fail if fxpAmount is zero"
            assert(contracts.cash.approve(contracts.completeSets.address, fxpAmount - 1, sender=t.k1) == 1), "Approve completeSets contract to spend slightly less cash than needed"
            try:
                raise Exception(contracts.completeSets.publicBuyCompleteSets(marketID, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicBuyCompleteSets should fail if the completeSets contract is not approved for the full amount needed"
        test_exceptions()
    def test_publicSellCompleteSets():
        contracts._ContractLoader__state.mine(1)
        eventID = createBinaryEvent()
        marketID = createMarket(eventID)
        buyCompleteSets(marketID, fix(10))
        fxpAmount = fix(9)
        senderInitialCash = contracts.cash.balanceOf(t.a1)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
        with iocapture.capture() as captured:
            result = contracts.completeSets.publicSellCompleteSets(marketID, fxpAmount, sender=t.k1)
            logged = captured.stdout
        logCompleteSets = parseCapturedLogs(logged)[-1]
        assert(logCompleteSets["_event_type"] == "CompleteSets"), "Should emit a CompleteSets event"
        assert(logCompleteSets["sender"] == address1), "Logged sender should match input"
        assert(logCompleteSets["type"] == 2), "Logged type should be 2 (sell)"
        assert(logCompleteSets["fxpAmount"] == fxpAmount), "Logged fxpAmount should match input"
        assert(logCompleteSets["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match input"
        assert(logCompleteSets["numOutcomes"] == contracts.events.getNumOutcomes(eventID)), "Logged numOutcomes should match event's number of outcomes"
        assert(logCompleteSets["fxpFee"] > 0), "Logged fees should be > 0"
        assert(logCompleteSets["market"] == marketID), "Logged market should match input"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1) == fix(1)), "Should have 1 share of outcome 1"
        assert(contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2) == fix(1)), "Should have 1 share of outcome 2"
        assert(marketInitialTotalShares - contracts.markets.getTotalSharesPurchased(marketID) == 2*fxpAmount), "Decrease in total shares purchased for this market should be 18"
        def test_exceptions():
            contracts._ContractLoader__state.mine(1)
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            fxpAmount = fix(10)
            buyCompleteSets(marketID, fxpAmount)

            # Permissions exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.completeSets.sellCompleteSets(t.a1, marketID, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "sellCompleteSets should fail if called from a non-whitelisted account (account 1)"

            # sellCompleteSets exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.completeSets.publicSellCompleteSets(marketID + 1, fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicSellCompleteSets should fail if market ID is invalid"
            try:
                raise Exception(contracts.completeSets.publicSellCompleteSets(marketID, fix(-10), sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "publicSellCompleteSets should throw ValueOutOfBounds exception if fxpAmount is negative"
            try:
                raise Exception(contracts.completeSets.publicSellCompleteSets(marketID, 0, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicSellCompleteSets should fail if fxpAmount is zero"
            try:
                raise Exception(contracts.completeSets.publicSellCompleteSets(marketID, fxpAmount + 1, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicSellCompleteSets should fail if the sender has insufficient shares in any outcome"
        test_exceptions()
    test_publicBuyCompleteSets()
    test_publicSellCompleteSets()

def test_MakeOrder():
    global contracts
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    def test_usingMarketType(marketType):
        def test_publicMakeOrder():
            def test_bid():
                contracts._ContractLoader__state.mine(1)
                orderType = 1 # bid
                fxpAmount = fix(1)
                fxpPrice = fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = createEventType(marketType)
                marketID = createMarket(eventID)
                assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
                makerInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                with iocapture.capture() as captured:
                    orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
                    logged = captured.stdout
                logMakeOrder = parseCapturedLogs(logged)[-1]
                assert(orderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(orderID)
                assert(len(order) == 10), "Order array length should be 10"
                assert(order[0] == orderID), "order[0] should be the order ID"
                assert(order[1] == orderType), "order[1] should be the order type"
                assert(order[2] == marketID), "order[2] should be the market ID"
                assert(order[3] == fxpAmount), "order[3] should be the amount of the order"
                assert(order[4] == fxpPrice), "order[4] should be the order's price"
                assert(order[5] == address1), "order[5] should be the sender's address"
                assert(order[6] == contracts._ContractLoader__state.block.number), "order[6] should be the current block number"
                assert(order[7] == outcomeID), "order[6] should be the outcome ID"
                assert(order[8] == int(unfix(fxpAmount*(fxpPrice - contracts.events.getMinValue(eventID))))), "order[8] should be the amount of money escrowed"
                assert(order[9] == 0), "order[9] should be the number of shares escrowed"
                assert(makerInitialCash - contracts.cash.balanceOf(t.a1) == order[8]), "Decrease in maker's cash balance should equal money escrowed"
                assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
                assert(logMakeOrder["_event_type"] == "MakeOrder"), "Should emit a MakeOrder event"
                assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
                assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
                assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
                assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
                assert(logMakeOrder["orderID"] == orderID), "Logged orderID should match returned orderID"
                assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
                assert(logMakeOrder["market"] == marketID), "Logged market should match input"
                assert(logMakeOrder["sender"] == address1), "Logged sender should match input"
            def test_bid_allButOneOutcome():
                # 1. Account 1: buy complete sets
                # 2. Account 1: make ask order for a single outcome (outcome 2)
                # 3. Account 2: take account 1's ask order for outcome 2
                # 4. Account 1: make bid order for outcome 2
                global shareTokenContractTranslator
                global outcomeShareContractWrapper
                contracts._ContractLoader__state.mine(1)
                assert(contracts.cash.publicDepositEther(value=fix(100), sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
                assert(contracts.cash.publicDepositEther(value=fix(100), sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
                orderType = 1 # bid
                fxpAmount = 1200000000000000000 # fixed-point 1.2
                fxpPrice = fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = createEventType(marketType)
                marketID = createMarket(eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                # 1. Account 1: buy complete sets
                contracts._ContractLoader__state.mine(1)
                buyCompleteSets(marketID, fxpAmount)
                assert(outcomeShareContractWrapper.balanceOf(outcomeOneShareContract, t.a1) == fxpAmount), "Account 1 should have fxpAmount shares of outcome 1"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a1) == fxpAmount), "Account 1 should have fxpAmount shares of outcome 2"
                assert(outcomeShareContractWrapper.balanceOf(outcomeOneShareContract, t.a2) == 0), "Account 2 should have 0 shares of outcome 2"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a2) == 0), "Account 2 should have 0 shares of outcome 2"
                # 2. Account 1: make ask order for a single outcome (outcome 2)
                contracts._ContractLoader__state.mine(1)
                fxpAllowance = fix(12)
                abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend outcome 2 shares from account 1"
                assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"
                contracts._ContractLoader__state.mine(1)
                askOrderID = contracts.makeOrder.publicMakeOrder(2, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
                assert(askOrderID != 0), "Order ID should be non-zero"
                # 3. Account 2: take account 1's ask order for outcome 2
                contracts._ContractLoader__state.mine(1)
                assert(contracts.cash.approve(contracts.takeOrder.address, fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
                contracts._ContractLoader__state.mine(1)
                fxpAmountTakerWants = fxpAmount
                orderHash = contracts.orders.makeOrderHash(marketID, outcomeID, 2, sender=t.k2)
                assert(contracts.orders.commitOrder(orderHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
                contracts._ContractLoader__state.mine(1)
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a1) == 0), "Account 1 should have 0 shares of outcome 2"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a2) == 0), "Account 2 should have 0 shares of outcome 2"
                assert(contracts.cash.approve(contracts.takeOrder.address, fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
                contracts._ContractLoader__state.mine(1)
                fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(askOrderID, fxpAmountTakerWants, sender=t.k2)
                assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a1) == 0), "Account 1 should have 0 shares of outcome 2"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a2) == fxpAmount), "Account 2 should have fxpAmount shares of outcome 2"
                # 4. Account 1: make bid order for outcome 2
                contracts._ContractLoader__state.mine(1)
                fxpBidAmount = 900000000000000000 # fixed-point 0.9
                assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
                makerInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                makerInitialShares = outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a1)
                marketOutcomeOneInitialShares = outcomeShareContractWrapper.balanceOf(outcomeOneShareContract, outcomeOneShareWallet)
                marketOutcomeTwoInitialShares = outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, outcomeTwoShareWallet)
                abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend outcome 1 shares from account 1"
                assert(outcomeShareContractWrapper.allowance(outcomeOneShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"
                with iocapture.capture() as captured:
                    bidOrderID = contracts.makeOrder.publicMakeOrder(1, fxpBidAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
                    logged = captured.stdout
                logMakeOrder = parseCapturedLogs(logged)[-1]
                assert(bidOrderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(bidOrderID)
                assert(len(order) == 10), "Order array length should be 10"
                assert(order[0] == bidOrderID), "order[0] should be the order ID"
                assert(order[1] == orderType), "order[1] should be the order type"
                assert(order[2] == marketID), "order[2] should be the market ID"
                assert(order[3] == fxpBidAmount), "order[3] should be the amount of the order"
                assert(order[4] == fxpPrice), "order[4] should be the order's price"
                assert(order[5] == address1), "order[5] should be the sender's address"
                assert(order[6] == contracts._ContractLoader__state.block.number), "order[6] should be the current block number"
                assert(order[7] == outcomeID), "order[6] should be the outcome ID"
                assert(order[8] == 0), "order[8] should be the amount of money escrowed"
                assert(order[9] == fxpBidAmount), "order[9] should be the number of shares escrowed"
                assert(contracts.cash.balanceOf(t.a1) == makerInitialCash), "Account 1's cash balance should not change"
                assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == marketInitialCash), "Market's cash balance should not change"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, outcomeTwoShareWallet) == marketOutcomeTwoInitialShares), "Market's outcome 2 share balance should not change"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a1) == makerInitialShares), "Account 1's outcome 2 share balance should not change"
                assert(outcomeShareContractWrapper.balanceOf(outcomeOneShareContract, outcomeOneShareWallet) - marketOutcomeOneInitialShares == fxpBidAmount), "Increase in market's outcome 1 share balance should be equal to the amount of the bid"
                assert(logMakeOrder["_event_type"] == "MakeOrder"), "Should emit a MakeOrder event"
                assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
                assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
                assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
                assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
                assert(logMakeOrder["orderID"] == bidOrderID), "Logged orderID should match returned orderID"
                assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
                assert(logMakeOrder["market"] == marketID), "Logged market should match input"
                assert(logMakeOrder["sender"] == address1), "Logged sender should match input"
            def test_ask_withoutShares():
                contracts._ContractLoader__state.mine(1)
                orderType = 2                   # ask
                fxpAmount = fix(1)
                fxpPrice = fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = createEventType(marketType)
                marketID = createMarket(eventID)
                assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
                makerInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                with iocapture.capture() as captured:
                    orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
                    logged = captured.stdout
                logMakeOrder = parseCapturedLogs(logged)[-1]
                assert(orderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(orderID)
                assert(len(order) == 10), "Order array length should be 10"
                assert(order[0] == orderID), "order[0] should be the order ID"
                assert(order[1] == orderType), "order[1] should be the order type"
                assert(order[2] == marketID), "order[2] should be the market ID"
                assert(order[3] == fxpAmount), "order[3] should be the amount of the order"
                assert(order[4] == fxpPrice), "order[4] should be the order's price"
                assert(order[5] == address1), "order[5] should be the sender's address"
                assert(order[6] == contracts._ContractLoader__state.block.number), "order[6] should be the current block number"
                assert(order[7] == outcomeID), "order[6] should be the outcome ID"
                assert(order[8] == int(unfix(fxpAmount*(contracts.events.getMaxValue(eventID) - fxpPrice)))), "order[8] should be the amount of money escrowed"
                assert(order[9] == 0), "order[9] should be the number of shares escrowed"
                assert(makerInitialCash - contracts.cash.balanceOf(t.a1) == order[8]), "Decrease in maker's cash balance should equal money escrowed"
                assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
                assert(logMakeOrder["_event_type"] == "MakeOrder"), "Should emit a MakeOrder event"
                assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
                assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
                assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
                assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
                assert(logMakeOrder["orderID"] == orderID), "Logged orderID should match returned orderID"
                assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
                assert(logMakeOrder["market"] == marketID), "Logged market should match input"
                assert(logMakeOrder["sender"] == address1), "Logged sender should match input"
            def test_ask_withShares():
                global shareTokenContractTranslator
                global outcomeShareContractWrapper
                contracts._ContractLoader__state.mine(1)
                orderType = 2                   # ask
                fxpAmount = fix(1)
                fxpPrice = fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = createEventType(marketType)
                marketID = createMarket(eventID)
                buyCompleteSets(marketID, fix(10))
                fxpAmount = fix(9)
                fxpAllowance = fix(12)
                makerInitialCash = contracts.cash.balanceOf(t.a1)
                makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
                outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
                abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 1)"
                assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"
                with iocapture.capture() as captured:
                    orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
                    logged = captured.stdout
                logMakeOrder = parseCapturedLogs(logged)[-1]
                assert(orderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(orderID)
                assert(len(order) == 10), "Order array length should be 10"
                assert(order[0] == orderID), "order[0] should be the order ID"
                assert(order[1] == orderType), "order[1] should be the order type"
                assert(order[2] == marketID), "order[2] should be the market ID"
                assert(order[3] == fxpAmount), "order[3] should be the amount of the order"
                assert(order[4] == fxpPrice), "order[4] should be the order's price"
                assert(order[5] == address1), "order[5] should be the sender's address"
                assert(order[6] == contracts._ContractLoader__state.block.number), "order[6] should be the current block number"
                assert(order[7] == outcomeID), "order[6] should be the outcome ID"
                assert(order[8] == 0), "order[8] should be the amount of money escrowed"
                assert(order[9] == fxpAmount), "order[9] should be the number of shares escrowed"
                assert(makerInitialCash == contracts.cash.balanceOf(t.a1)), "Maker's cash balance should be unchanged"
                assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == marketInitialCash), "Market's cash balance should be unchanged"
                assert(makerInitialShares - contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID) == fxpAmount), "Decrease in participant shares purchased should be equal to order amount"
                assert(marketInitialTotalShares == contracts.markets.getTotalSharesPurchased(marketID)), "Market's total shares purchased should be unchanged"
                assert(logMakeOrder["_event_type"] == "MakeOrder"), "Should emit a MakeOrder event"
                assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
                assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
                assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
                assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
                assert(logMakeOrder["orderID"] == orderID), "Logged orderID should match returned orderID"
                assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
                assert(logMakeOrder["market"] == marketID), "Logged market should match input"
                assert(logMakeOrder["sender"] == address1), "Logged sender should match input"
            def test_ask_withPartialShares():
                global shareTokenContractTranslator
                global outcomeShareContractWrapper
                contracts._ContractLoader__state.mine(1)
                orderType = 2                   # ask
                fxpAmount = fix(1)
                fxpPrice = fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = createEventType(marketType)
                marketID = createMarket(eventID)
                buyCompleteSets(marketID, fix(10))
                fxpAmount = fix(12)
                fxpAllowance = fix(120)
                makerInitialCash = contracts.cash.balanceOf(t.a1)
                makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
                outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
                abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 1)"
                assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"
                assert(contracts.cash.approve(contracts.makeOrder.address, fxpAllowance, sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
                with iocapture.capture() as captured:
                    orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
                    logged = captured.stdout
                logMakeOrder = parseCapturedLogs(logged)[-1]
                assert(orderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(orderID)
                assert(len(order) == 10), "Order array length should be 10"
                assert(order[0] == orderID), "order[0] should be the order ID"
                assert(order[1] == orderType), "order[1] should be the order type"
                assert(order[2] == marketID), "order[2] should be the market ID"
                assert(order[3] == fxpAmount), "order[3] should be the amount of the order"
                assert(order[4] == fxpPrice), "order[4] should be the order's price"
                assert(order[5] == address1), "order[5] should be the sender's address"
                assert(order[6] == contracts._ContractLoader__state.block.number), "order[6] should be the current block number"
                assert(order[7] == outcomeID), "order[6] should be the outcome ID"
                assert(order[8] == int(unfix(fix(2)*(contracts.events.getMaxValue(eventID) - fxpPrice)))), "order[8] should be the amount of money escrowed"
                assert(order[9] == fix(10)), "order[9] should be the number of shares escrowed"
                assert(makerInitialCash - contracts.cash.balanceOf(t.a1) == order[8]), "Decrease in maker's cash balance should equal money escrowed"
                assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) - marketInitialCash == order[8]), "Increase in market's cash balance should equal money escrowed"
                assert(logMakeOrder["_event_type"] == "MakeOrder"), "Should emit a MakeOrder event"
                assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
                assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
                assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
                assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
                assert(logMakeOrder["orderID"] == orderID), "Logged orderID should match returned orderID"
                assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
                assert(logMakeOrder["market"] == marketID), "Logged market should match input"
                assert(logMakeOrder["sender"] == address1), "Logged sender should match input"
            def test_exceptions():
                global shareTokenContractTranslator
                global outcomeShareContractWrapper
                contracts._ContractLoader__state.mine(1)
                orderType = 1 # bid
                fxpAmount = fix(1)
                fxpPrice = fix("1.6")
                outcomeID = 1
                tradeGroupID = 42
                eventID = createBinaryEvent()
                marketID = createMarket(eventID)
                makerInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))

                # Permissions exceptions
                contracts._ContractLoader__state.mine(1)
                try:
                    raise Exception(contracts.makeOrder.makeOrder(t.a1, orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "makeOrder should fail if called from a non-whitelisted account (account 1)"
                try:
                    raise Exception(contracts.makeOrder.placeAsk(t.a1, fxpAmount, fxpPrice, marketID, outcomeID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "placeAsk should fail if called directly"
                try:
                    raise Exception(contracts.makeOrder.placeBid(t.a1, fxpAmount, fxpPrice, marketID, outcomeID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "placeBid should fail if called directly"

                # makeOrder exceptions (pre-placeBid/placeAsk)
                contracts._ContractLoader__state.mine(1)
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID - 1, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder should fail if market ID is not valid"
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(3, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder should fail if order type is not 1 (bid) or 2 (ask)"

                # placeBid exceptions
                contracts._ContractLoader__state.mine(1)
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(1, fxpAmount, fix(3), marketID, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder bid should fail if order cost per share is greater than the market's range"
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(1, 1, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder bid should fail if order cost is below than the minimum order value"

                # placeAsk exceptions
                contracts._ContractLoader__state.mine(1)
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(2, fxpAmount, 1, marketID, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (without shares) should fail if order cost per share (maxValue - price) is greater than the market's range"
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(2, 1, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (without shares) should fail if order cost is below than the minimum order value"
                buyCompleteSets(marketID, fix(2))
                contracts._ContractLoader__state.mine(1)
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(2, fxpAmount, fix(3), marketID, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (with shares held) should fail if cost per share (price - minValue) is greater than the market's range"
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(2, 1, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (with shares held) should fail if order cost is below than the minimum order value"

                contracts._ContractLoader__state.mine(1)
                assert(contracts.cash.approve(contracts.makeOrder.address, fix(100), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
                fxpAllowance = fix(12)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 1)"
                assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"
                contracts._ContractLoader__state.mine(1)
                assert(contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1) != 0), "Order ID should be non-zero"

                # makeOrder exceptions (post-placeBid/Ask)
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder should fail if duplicate orders are placed in the same block (should combine into a single order instead)"
            test_bid()
            test_bid_allButOneOutcome()
            test_ask_withoutShares()
            test_ask_withShares()
            test_ask_withPartialShares()
            test_exceptions()
        test_publicMakeOrder()
    test_usingMarketType("binary")
    test_usingMarketType("scalar")

def test_CancelOrder():
    global contracts
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    def test_publicCancelOrder():
        def test_cancelBid():
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount = fix(1)
            fxpPrice = fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10000), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            assert(contracts.orders.getOrder(orderID) != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "Order should have non-zero elements"
            assert(contracts.cancelOrder.publicCancelOrder(orderID, sender=t.k1) == 1), "publicCancelOrder should succeed"
            assert(contracts.orders.getOrder(orderID) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "Canceled order elements should all be zero"
            assert(makerInitialCash == contracts.cash.balanceOf(t.a1)), "Maker's cash should be the same as before the order was placed"
            assert(marketInitialCash == contracts.cash.balanceOf(contracts.info.getWallet(marketID))), "Market's cash balance should be the same as before the order was placed"
            assert(makerInitialShares == contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)), "Maker's shares should be unchanged"
            assert(marketInitialTotalShares == contracts.markets.getTotalSharesPurchased(marketID)), "Market's total shares should be unchanged"
        def test_cancelAsk():
            contracts._ContractLoader__state.mine(1)
            orderType = 2                   # ask
            fxpAmount = fix(1)
            fxpPrice = fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10000), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            assert(contracts.orders.getOrder(orderID) != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "Order should have non-zero elements"
            assert(contracts.cancelOrder.publicCancelOrder(orderID, sender=t.k1) == 1), "publicCancelOrder should succeed"
            assert(contracts.orders.getOrder(orderID) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "Canceled order elements should all be zero"
            assert(makerInitialCash == contracts.cash.balanceOf(t.a1)), "Maker's cash should be the same as before the order was placed"
            assert(marketInitialCash == contracts.cash.balanceOf(contracts.info.getWallet(marketID))), "Market's cash balance should be the same as before the order was placed"
            assert(makerInitialShares == contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)), "Maker's shares should be unchanged"
            assert(marketInitialTotalShares == contracts.markets.getTotalSharesPurchased(marketID)), "Market's total shares should be unchanged"
        def test_exceptions():
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount = fix(1)
            fxpPrice = fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10000), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"

            # Permissions exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.cancelOrder.cancelOrder(t.a1, orderID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "cancelOrder should fail if called from a non-whitelisted account (account 1)"
            try:
                raise Exception(contracts.cancelOrder.refundOrder(t.a1, orderType, 0, fxpAmount, marketID, outcomeID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "refundOrder should fail if called directly"

            # cancelOrder exceptions
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.cancelOrder.publicCancelOrder(0, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicCancelOrder should fail if order ID is zero"
            try:
                raise Exception(contracts.cancelOrder.publicCancelOrder(orderID + 1, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicCancelOrder should fail if order does not exist"
            try:
                raise Exception(contracts.cancelOrder.publicCancelOrder(orderID, sender=t.k2))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicCancelOrder should fail if sender does not own the order"
            assert(contracts.cancelOrder.publicCancelOrder(orderID, sender=t.k1) == 1), "publicCancelOrder should succeed"
            try:
                raise Exception(contracts.cancelOrder.publicCancelOrder(orderID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicCancelOrder should fail if the order has already been cancelled"
        test_cancelBid()
        test_cancelAsk()
        test_exceptions()
    test_publicCancelOrder()

def test_TakeAskOrder():
    global contracts
    t = contracts._ContractLoader__tester
    def test_usingMarketType(marketType):
        def test_takeAskOrder_makerEscrowedCash():
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            outcomeID = 2
            eventID = createEventType(marketType)
            marketID = createMarket(eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeAskOrder.address, fix(10), sender=t.k2) == 1), "Approve takeAskOrder contract to spend cash from account 2"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            assert(makerInitialCash >= fxpEtherDepositValue), "Maker's initial cash balance should be at least fxpEtherDepositValue"
            assert(takerInitialCash >= fxpEtherDepositValue), "Taker's initial cash balance should be at least fxpEtherDepositValue"
            assert(marketInitialCash == 0), "Market's initial cash balance should be 0"
            makerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerInitialOutcomeOneShares == 0), "Maker's initial outcome 1 shares balance should be 0"
            assert(makerInitialOutcomeTwoShares == 0), "Maker's initial outcome 2 shares balance should be 0"
            assert(takerInitialOutcomeOneShares == 0), "Taker's initial outcome 1 shares balance should be 0"
            assert(takerInitialOutcomeTwoShares == 0), "Taker's initial outcome 2 shares balance should be 0"
            assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
            assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"

            # 1. Maker places ask order for outcome 2 on order book. Cash (maxValue - price) is escrowed from maker.
            contracts._ContractLoader__state.mine(1)
            fxpOrderAmount = fix(1)
            fxpPrice = fix("1.6")
            tradeGroupID = 42
            orderID = contracts.makeOrder.publicMakeOrder(2, fxpOrderAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            makerIntermediateCash = contracts.cash.balanceOf(t.a1)
            takerIntermediateCash = contracts.cash.balanceOf(t.a2)
            marketIntermediateCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpMaxValue = contracts.events.getMaxValue(eventID)
            fxpExpectedCashEscrowed = int((Decimal(fxpMaxValue) - Decimal(fxpPrice)) * Decimal(fxpOrderAmount) / Decimal(10)**Decimal(18))
            assert(makerIntermediateCash == makerInitialCash - fxpExpectedCashEscrowed), "Maker's intermediate cash balance should be decreased by (fxpMaxValue - fxpPrice)*fxpOrderAmount"
            assert(takerIntermediateCash == takerInitialCash), "Taker's intermediate cash balance should be unchanged from the initial cash balance"
            assert(marketIntermediateCash == fxpExpectedCashEscrowed), "Market's intermediate cash balance should be (fxpMaxValue - fxpPrice)*fxpOrderAmount"
            makerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerIntermediateOutcomeOneShares == 0), "Maker's intermediate outcome 1 shares balance should be 0"
            assert(makerIntermediateOutcomeTwoShares == 0), "Maker's intermediate outcome 2 shares balance should be 0"
            assert(takerIntermediateOutcomeOneShares == 0), "Taker's intermediate outcome 1 shares balance should be 0"
            assert(takerIntermediateOutcomeTwoShares == 0), "Taker's intermediate outcome 2 shares balance should be 0"
            assert(marketIntermediateOutcomeOneShares == 0), "Market's intermediate outcome 1 shares balance should be 0"
            assert(marketIntermediateOutcomeTwoShares == 0), "Market's intermediate outcome 2 shares balance should be 0"

            # 2. Taker fills ask order. Complete sets are created and split between taker (receives outcome 2) and maker (receives other outcomes).
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = fix(7)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 2, sender=t.k2)
            assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
            contracts._ContractLoader__state.mine(1)
            fxpAmountRemaining = contracts.takeAskOrder.takeAskOrder(t.a2, orderID, fxpAmountTakerWants, sender=t.k0)
            assert(fxpAmountRemaining == fxpAmountTakerWants - fxpOrderAmount), "Amount remaining of taker's request should be fxpAmountTakerWants - fxpOrderAmount"
            makerFinalCash = contracts.cash.balanceOf(t.a1)
            takerFinalCash = contracts.cash.balanceOf(t.a2)
            marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpMinValue = contracts.events.getMinValue(eventID)
            fxpExpectedCostPaidByTaker = int(Decimal(fxpOrderAmount) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
            assert(makerFinalCash == makerIntermediateCash), "Maker's final cash balance should be equal to makerIntermediateCash"
            assert(takerFinalCash == takerIntermediateCash - fxpExpectedCostPaidByTaker), "Taker's final cash balance should be takerIntermediateCash - fxpAmountTakerWants*(fxpPrice - fxpMinValue)"
            assert(marketFinalCash == marketIntermediateCash + fxpExpectedCostPaidByTaker), "Market's final cash balance should be equal to marketIntermediateCash + fxpExpectedCostPaidByTaker"
            makerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerFinalOutcomeOneShares == fxpOrderAmount), "Maker's final outcome 1 shares balance should be fxpOrderAmount"
            assert(makerFinalOutcomeTwoShares == 0), "Maker's final outcome 2 shares balance should be 0"
            assert(takerFinalOutcomeOneShares == 0), "Taker's final outcome 1 shares balance should be 0"
            assert(takerFinalOutcomeTwoShares == fxpOrderAmount), "Taker's final outcome 2 shares balance should be fxpOrderAmount"
            assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
            assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"

        def test_takeAskOrder_makerEscrowedShares():
            global shareTokenContractTranslator
            global outcomeShareContractWrapper
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            eventID = createEventType(marketType)
            marketID = createMarket(eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)

            # 1. Maker buys complete sets
            fxpNumCompleteSets = fix(10)
            buyCompleteSets(marketID, fxpNumCompleteSets)
            fxpAllowance = fix(12)
            outcomeID = 2
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
            contracts._ContractLoader__state.mine(1)
            outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
            assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 1)"
            assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            fxpCumulativeScale = Decimal(contracts.markets.getCumulativeScale(marketID))
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            assert(makerInitialCash >= fxpEtherDepositValue), "Maker's initial cash balance should be at least fxpEtherDepositValue"
            assert(takerInitialCash >= fxpEtherDepositValue), "Taker's initial cash balance should be at least fxpEtherDepositValue"
            assert(marketInitialCash == Decimal(fxpNumCompleteSets) * fxpCumulativeScale / Decimal(10)**Decimal(18)), "Market's initial cash balance should be fxpNumCompleteSets*fxpCumulativeScale"
            makerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerInitialOutcomeOneShares == fxpNumCompleteSets), "Maker's initial outcome 1 shares balance should be fxpNumCompleteSets"
            assert(makerInitialOutcomeTwoShares == fxpNumCompleteSets), "Maker's initial outcome 2 shares balance should be fxpNumCompleteSets"
            assert(takerInitialOutcomeOneShares == 0), "Taker's initial outcome 1 shares balance should be 0"
            assert(takerInitialOutcomeTwoShares == 0), "Taker's initial outcome 2 shares balance should be 0"
            assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
            assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"

            # 2. Maker places ask order for outcome 2 on order book. Maker's shares of outcome 2 are escrowed.
            contracts._ContractLoader__state.mine(1)
            fxpOrderAmount = fix(9)
            fxpPrice = fix("1.6")
            tradeGroupID = 42
            orderID = contracts.makeOrder.publicMakeOrder(2, fxpOrderAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            makerIntermediateCash = contracts.cash.balanceOf(t.a1)
            takerIntermediateCash = contracts.cash.balanceOf(t.a2)
            marketIntermediateCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            assert(makerIntermediateCash == makerInitialCash), "Maker's intermediate cash balance should be unchanged from the initial cash balance"
            assert(takerIntermediateCash == takerInitialCash), "Taker's intermediate cash balance should be unchanged from the initial cash balance"
            assert(marketIntermediateCash == marketInitialCash), "Market's intermediate cash balance should be unchanged from the initial cash balance"
            makerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerIntermediateOutcomeOneShares == fxpNumCompleteSets), "Maker's intermediate outcome 1 shares balance should be fxpNumCompleteSets"
            assert(makerIntermediateOutcomeTwoShares == fxpNumCompleteSets - fxpOrderAmount), "Maker's intermediate outcome 2 shares balance should be fxpNumCompleteSets - fxpOrderAmount"
            assert(takerIntermediateOutcomeOneShares == 0), "Taker's intermediate outcome 1 shares balance should be 0"
            assert(takerIntermediateOutcomeTwoShares == 0), "Taker's intermediate outcome 2 shares balance should be 0"
            assert(marketIntermediateOutcomeOneShares == 0), "Market's intermediate outcome 1 shares balance should be 0"
            assert(marketIntermediateOutcomeTwoShares == fxpOrderAmount), "Market's intermediate outcome 2 shares balance should be fxpOrderAmount"

            # 3. Taker fills ask order. Taker receives maker's escrowed shares. Maker receives cash.
            contracts._ContractLoader__state.mine(1)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 2, sender=t.k2)
            assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = fix(7)
            assert(contracts.cash.approve(contracts.takeAskOrder.address, fix(10), sender=t.k2) == 1), "Approve takeAskOrder contract to spend cash from account 2"
            contracts._ContractLoader__state.mine(1)
            fxpAmountRemaining = contracts.takeAskOrder.takeAskOrder(t.a2, orderID, fxpAmountTakerWants, sender=t.k0)
            assert(fxpAmountRemaining == 0), "Number of shares remaining in taker's request should be 0"
            makerFinalCash = contracts.cash.balanceOf(t.a1)
            takerFinalCash = contracts.cash.balanceOf(t.a2)
            marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpMinValue = contracts.events.getMinValue(eventID)
            fxpExpectedCostPaidByTaker = int(Decimal(fxpAmountTakerWants) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
            # addr 2: 10 shares both outcomes
            # addr 2 ask order 9 shares -> 9 shares escrowed @ market, 1 share remaining @ addr 2
            # addr 1 buy 7 shares
            # addr 2: 2 shares escrowed @ market, 1 share remaining @ addr 2
            # => addr 2 should have 1 complete set to auto-sell
            fxpSharesHeld = Decimal(fxpNumCompleteSets) - Decimal(fxpOrderAmount)
            fxpMoneyFromSellCompleteSets = fxpSharesHeld * fxpCumulativeScale / Decimal(10)**Decimal(18)
            fxpExpectedFee = int(Decimal(contracts.markets.getTradingFee(marketID)) * fxpSharesHeld / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
            fxpExpectedCashTransferToMaker = int(fxpMoneyFromSellCompleteSets - Decimal(fxpExpectedFee))
            # note: creator is also maker in this case
            fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
            assert(makerFinalCash == makerInitialCash + fxpExpectedCostPaidByTaker + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator), "Maker's final cash balance should be makerInitialCash + fxpAmountTakerWants*fxpPrice + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator"
            assert(takerFinalCash == takerInitialCash - fxpExpectedCostPaidByTaker), "Taker's final cash balance should be takerInitialCash - fxpAmountTakerWants*fxpPrice"
            assert(marketFinalCash == marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator), "Market's final cash balance should be marketInitialCash - fxpExpectedCostPaidByTaker - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator"
            makerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerFinalOutcomeOneShares == int(Decimal(fxpNumCompleteSets) - fxpSharesHeld)), "Maker's final outcome 1 shares balance should be fxpNumCompleteSets - fxpSharesHeld"
            assert(makerFinalOutcomeTwoShares == 0), "Maker's final outcome 2 shares balance should be 0"
            assert(takerFinalOutcomeOneShares == 0), "Taker's final outcome 1 shares balance should be 0"
            assert(takerFinalOutcomeTwoShares == fxpAmountTakerWants), "Taker's final outcome 2 shares balance should be fxpAmountTakerWants"
            assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
            assert(marketFinalOutcomeTwoShares == fxpOrderAmount - fxpAmountTakerWants), "Market's final outcome 2 shares balance should be fxpOrderAmount - fxpAmountTakerWants"

        test_takeAskOrder_makerEscrowedCash()
        test_takeAskOrder_makerEscrowedShares()
    test_usingMarketType("binary")
    test_usingMarketType("scalar")

def test_TakeBidOrder():
    global contracts
    t = contracts._ContractLoader__tester
    def test_usingMarketType(marketType):
        def test_takeBidOrder_makerEscrowedCash_takerWithoutShares():
            global shareTokenContractTranslator
            global outcomeShareContractWrapper
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            fxpOrderAmount = fix(2)
            fxpPrice = fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            fxpAllowance = fix(10)
            abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeBidOrder.address, fxpAllowance])
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeTwoShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeBidOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a2, contracts.takeBidOrder.address) == fxpAllowance), "takeBidOrder contract's allowance should be equal to the amount approved"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            assert(makerInitialCash >= fxpEtherDepositValue), "Maker's initial cash balance should be at least fxpEtherDepositValue"
            assert(takerInitialCash >= fxpEtherDepositValue), "Taker's initial cash balance should be at least fxpEtherDepositValue"
            assert(marketInitialCash == 0), "Market's initial cash balance should be 0"
            makerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerInitialOutcomeOneShares == 0), "Maker's initial outcome 1 shares balance should be 0"
            assert(makerInitialOutcomeTwoShares == 0), "Maker's initial outcome 2 shares balance should be 0"
            assert(takerInitialOutcomeOneShares == 0), "Taker's initial outcome 1 shares balance should be 0"
            assert(takerInitialOutcomeTwoShares == 0), "Taker's initial outcome 2 shares balance should be 0"
            assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
            assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"

            # 1. Maker places a bid order. Cash sent from maker to market.
            contracts._ContractLoader__state.mine(1)
            orderID = contracts.makeOrder.publicMakeOrder(1, fxpOrderAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            makerIntermediateCash = contracts.cash.balanceOf(t.a1)
            takerIntermediateCash = contracts.cash.balanceOf(t.a2)
            marketIntermediateCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpMinValue = contracts.events.getMinValue(eventID)
            fxpCashPaidByMaker = int(Decimal(fxpOrderAmount) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
            assert(makerIntermediateCash == makerInitialCash - fxpCashPaidByMaker), "Maker's cash balance should be decreased by fxpCashPaidByMaker"
            assert(takerIntermediateCash == takerInitialCash), "Taker's cash balance should be unchanged"
            assert(marketIntermediateCash == fxpCashPaidByMaker), "Market's intermediate cash balance should be equal to fxpCashPaidByMaker"
            makerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerIntermediateOutcomeOneShares == 0), "Maker's intermediate outcome 1 shares balance should be 0"
            assert(makerIntermediateOutcomeTwoShares == 0), "Maker's intermediate outcome 2 shares balance should be 0"
            assert(takerIntermediateOutcomeOneShares == 0), "Taker's intermediate outcome 1 shares balance should be 0"
            assert(takerIntermediateOutcomeTwoShares == 0), "Taker's intermediate outcome 2 shares balance should be 0"
            assert(marketIntermediateOutcomeOneShares == 0), "Market's intermediate outcome 1 shares balance should be 0"
            assert(marketIntermediateOutcomeTwoShares == 0), "Market's intermediate outcome 2 shares balance should be 0"

            # 2. Taker fills bid order. Taker is short selling: taker buys a complete set then sells a single outcome.
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = fix(3)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 1, sender=t.k2)
            assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, fix(10), sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
            contracts._ContractLoader__state.mine(1)
            fxpAmountRemaining = contracts.takeBidOrder.takeBidOrder(t.a2, orderID, fxpAmountTakerWants, sender=t.k0)
            assert(fxpAmountRemaining == fxpAmountTakerWants - fxpOrderAmount), "Amount remaining should be fxpAmountTakerWants - fxpOrderAmount"
            makerFinalCash = contracts.cash.balanceOf(t.a1)
            takerFinalCash = contracts.cash.balanceOf(t.a2)
            marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpAmountFilled = min(fxpAmountTakerWants, fxpOrderAmount)
            fxpCompleteSetsCostPaidByTaker = fxpAmountFilled
            assert(makerFinalCash == makerIntermediateCash), "Maker's final cash balance should be unchanged from intermediate cash balance"
            assert(takerFinalCash == takerInitialCash + fxpCashPaidByMaker - fxpCompleteSetsCostPaidByTaker), "Taker's cash balance should be increased by fxpCashPaidByMaker - fxpCompleteSetsCostPaidByTaker"
            assert(marketFinalCash == fxpAmountFilled), "Market's final cash balance should be equal to fxpAmountFilled"
            makerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerFinalOutcomeOneShares == 0), "Maker's final outcome 1 shares balance should be 0"
            assert(makerFinalOutcomeTwoShares == fxpAmountFilled), "Maker's final outcome 2 shares balance should be equal to fxpAmountFilled"
            assert(takerFinalOutcomeOneShares == fxpAmountFilled), "Taker's final outcome 1 shares balance should be equal to fxpAmountFilled"
            assert(takerFinalOutcomeTwoShares == 0), "Taker's final outcome 2 shares balance should be 0"
            assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
            assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"

        def test_takeBidOrder_makerEscrowedShares_takerWithoutShares():
            global shareTokenContractTranslator
            global outcomeShareContractWrapper
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)

            # 1. Maker buys complete sets, then transfers shares of outcome 2.
            contracts._ContractLoader__state.mine(1)
            fxpNumCompleteSets = fix(10)
            buyCompleteSets(marketID, fxpNumCompleteSets)
            contracts._ContractLoader__state.mine(1)
            transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
            assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            assert(makerInitialCash >= fxpEtherDepositValue - fxpNumCompleteSets), "Maker's initial cash balance should be at least fxpEtherDepositValue - fxpNumCompleteSets"
            assert(takerInitialCash >= fxpEtherDepositValue), "Taker's initial cash balance should be at least fxpEtherDepositValue"
            assert(marketInitialCash == fxpNumCompleteSets), "Market's initial cash balance should be equal to fxpNumCompleteSets"
            makerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerInitialOutcomeOneShares == fxpNumCompleteSets), "Maker's initial outcome 1 shares balance should be equal to fxpNumCompleteSets"
            assert(makerInitialOutcomeTwoShares == 0), "Maker's initial outcome 2 shares balance should be 0"
            assert(takerInitialOutcomeOneShares == 0), "Taker's initial outcome 1 shares balance should be 0"
            assert(takerInitialOutcomeTwoShares == 0), "Taker's initial outcome 2 shares balance should be 0"
            assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
            assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"

            # 2. Maker places a bid order. Shares of other outcome(s) sent from maker to market.
            contracts._ContractLoader__state.mine(1)
            fxpOrderAmount = fix(2)
            fxpPrice = fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            fxpAllowance = fix(10)
            assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares of outcome 1 from account 1 (maker)"
            assert(outcomeShareContractWrapper.allowance(outcomeOneShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance for outcome 1 on account 1 (maker) should be equal to the amount approved"
            orderID = contracts.makeOrder.publicMakeOrder(1, fxpOrderAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            makerIntermediateCash = contracts.cash.balanceOf(t.a1)
            takerIntermediateCash = contracts.cash.balanceOf(t.a2)
            marketIntermediateCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpCumulativeScale = Decimal(contracts.markets.getCumulativeScale(marketID))
            fxpMinValue = contracts.events.getMinValue(eventID)
            assert(makerIntermediateCash == makerInitialCash), "Maker's cash balance should be unchanged"
            assert(takerIntermediateCash == takerInitialCash), "Taker's cash balance should be unchanged"
            assert(marketIntermediateCash == marketInitialCash), "Market's cash balance should be unchanged"
            makerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerIntermediateOutcomeOneShares == fxpNumCompleteSets - fxpOrderAmount), "Maker's intermediate outcome 1 shares balance should be fxpNumCompleteSets - fxpOrderAmount"
            assert(makerIntermediateOutcomeTwoShares == 0), "Maker's intermediate outcome 2 shares balance should be 0"
            assert(takerIntermediateOutcomeOneShares == 0), "Taker's intermediate outcome 1 shares balance should be 0"
            assert(takerIntermediateOutcomeTwoShares == 0), "Taker's intermediate outcome 2 shares balance should be 0"
            assert(marketIntermediateOutcomeOneShares == fxpOrderAmount), "Market's intermediate outcome 1 shares balance should be equal to fxpOrderAmount"
            assert(marketIntermediateOutcomeTwoShares == 0), "Market's intermediate outcome 2 shares balance should be 0"

            # 3. Taker fills bid order:
            #    - Taker is short selling: taker buys a complete set then sells a single outcome.
            #    - Maker has a complete set once bid is filled; takeBidOrder auto-sells this complete set.
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = fix(3)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 1, sender=t.k2)
            assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
            contracts._ContractLoader__state.mine(1)
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeTwoShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.takeBidOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve takeBidOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a2, contracts.takeBidOrder.address) == fxpAllowance), "takeBidOrder contract's allowance should be equal to the amount approved"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, fix(10), sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, fix(10), sender=t.k1) == 1), "Approve takeBidOrder contract to spend cash from account 1"
            contracts._ContractLoader__state.mine(1)
            fxpAmountRemaining = contracts.takeBidOrder.takeBidOrder(t.a2, orderID, fxpAmountTakerWants, sender=t.k0)
            assert(fxpAmountRemaining == fxpAmountTakerWants - fxpOrderAmount), "Amount remaining should be fxpAmountTakerWants - fxpOrderAmount"
            makerFinalCash = contracts.cash.balanceOf(t.a1)
            takerFinalCash = contracts.cash.balanceOf(t.a2)
            marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpAmountFilled = min(fxpAmountTakerWants, fxpOrderAmount)
            fxpCashTransferFromMarketToTaker = int(Decimal(fxpAmountFilled) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
            fxpBuyCompleteSetsCashTransferFromTakerToMarket = int(Decimal(fxpAmountFilled) * fxpCumulativeScale / Decimal(10)**Decimal(18))
            fxpSharesHeld = Decimal(min(fxpNumCompleteSets, fxpAmountFilled))
            fxpSellCompleteSetsCashTransferFromMarketToMaker = fxpSharesHeld * fxpCumulativeScale / Decimal(10)**Decimal(18)
            fxpExpectedFee = int(Decimal(contracts.markets.getTradingFee(marketID)) * fxpSharesHeld / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
            fxpCashTransferFromMakerToMarket = int((Decimal(fxpPrice) - Decimal(fxpMinValue)) * Decimal(fxpOrderAmount) / Decimal(10)**Decimal(18))
            fxpExpectedCashTransferToMaker = int(fxpSellCompleteSetsCashTransferFromMarketToMaker - Decimal(fxpExpectedFee))
            # note: creator is also maker in this case
            fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
            assert(makerFinalCash == makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket), "Maker's final cash balance should be makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket"
            assert(takerFinalCash == takerInitialCash - fxpBuyCompleteSetsCashTransferFromTakerToMarket + fxpCashTransferFromMarketToTaker), "Taker's final cash balance takerInitialCash - fxpBuyCompleteSetsCashTransferFromTakerToMarket + fxpCashTransferFromMarketToTaker"
            assert(marketFinalCash == marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket + fxpBuyCompleteSetsCashTransferFromTakerToMarket), "Market's final cash balance should be marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket + fxpBuyCompleteSetsCashTransferFromTakerToMarket"
            makerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerFinalOutcomeOneShares == makerIntermediateOutcomeOneShares), "Maker's final outcome 1 shares balance should be unchanged"
            assert(makerFinalOutcomeTwoShares == 0), "Maker's final outcome 2 shares balance should be 0"
            assert(takerFinalOutcomeOneShares == fxpAmountFilled), "Taker's final outcome 1 shares balance should be equal to fxpAmountFilled"
            assert(takerFinalOutcomeTwoShares == 0), "Taker's final outcome 2 shares balance should be 0"
            assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
            assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"

        def test_takeBidOrder_makerEscrowedCash_takerWithShares():
            global shareTokenContractTranslator
            global outcomeShareContractWrapper
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            fxpOrderAmount = fix(2)
            fxpPrice = fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)

            # 1. Taker buys a complete set, then transfers outcome 1, leaving taker with shares of outcome 2 only.
            contracts._ContractLoader__state.mine(1)
            fxpOutcomeTwoShares = fix(10)
            buyCompleteSets(marketID, fxpOutcomeTwoShares, sender=t.k2)
            contracts._ContractLoader__state.mine(1)
            transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpOutcomeTwoShares])
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"

            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            fxpAllowance = fix(10)
            abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeBidOrder.address, fxpAllowance])
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeTwoShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeBidOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a2, contracts.takeBidOrder.address) == fxpAllowance), "takeBidOrder contract's allowance should be equal to the amount approved"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            assert(makerInitialCash >= fxpEtherDepositValue), "Maker's initial cash balance should be at least fxpEtherDepositValue"
            assert(takerInitialCash >= fxpEtherDepositValue - fxpOutcomeTwoShares), "Taker's initial cash balance should be at least fxpEtherDepositValue - fxpOutcomeTwoShares"
            assert(marketInitialCash == fxpOutcomeTwoShares), "Market's initial cash balance should be equal to fxpOutcomeTwoShares"
            makerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerInitialOutcomeOneShares == 0), "Maker's initial outcome 1 shares balance should be 0"
            assert(makerInitialOutcomeTwoShares == 0), "Maker's initial outcome 2 shares balance should be 0"
            assert(takerInitialOutcomeOneShares == 0), "Taker's initial outcome 1 shares balance should be 0"
            assert(takerInitialOutcomeTwoShares == fxpOutcomeTwoShares), "Taker's initial outcome 2 shares balance should be fxpOutcomeTwoShares"
            assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
            assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"

            # 2. Maker places a bid order. Cash sent from maker to market.
            contracts._ContractLoader__state.mine(1)
            orderID = contracts.makeOrder.publicMakeOrder(1, fxpOrderAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            makerIntermediateCash = contracts.cash.balanceOf(t.a1)
            takerIntermediateCash = contracts.cash.balanceOf(t.a2)
            marketIntermediateCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpMinValue = contracts.events.getMinValue(eventID)
            fxpCashPaidByMaker = int(Decimal(fxpOrderAmount) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
            assert(makerIntermediateCash == makerInitialCash - fxpCashPaidByMaker), "Maker's cash balance should be decreased by fxpCashPaidByMaker"
            assert(takerIntermediateCash == takerInitialCash), "Taker's cash balance should be unchanged"
            assert(marketIntermediateCash == marketInitialCash + fxpCashPaidByMaker), "Market's intermediate cash balance should be equal to fxpCashPaidByMaker"
            makerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerIntermediateOutcomeOneShares == 0), "Maker's intermediate outcome 1 shares balance should be 0"
            assert(makerIntermediateOutcomeTwoShares == 0), "Maker's intermediate outcome 2 shares balance should be 0"
            assert(takerIntermediateOutcomeOneShares == 0), "Taker's intermediate outcome 1 shares balance should be 0"
            assert(takerIntermediateOutcomeTwoShares == fxpOutcomeTwoShares), "Taker's intermediate outcome 2 shares balance should be fxpOutcomeTwoShares"
            assert(marketIntermediateOutcomeOneShares == 0), "Market's intermediate outcome 1 shares balance should be 0"
            assert(marketIntermediateOutcomeTwoShares == 0), "Market's intermediate outcome 2 shares balance should be 0"

            # 3. Taker fills bid order. Taker is short selling: taker buys a complete set then sells a single outcome.
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = fix(3)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 1, sender=t.k2)
            assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, fix(10), sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
            contracts._ContractLoader__state.mine(1)
            fxpAmountRemaining = contracts.takeBidOrder.takeBidOrder(t.a2, orderID, fxpAmountTakerWants, sender=t.k0)
            assert(fxpAmountRemaining == fxpAmountTakerWants - fxpOrderAmount), "Amount remaining should be fxpAmountTakerWants - fxpOrderAmount"
            makerFinalCash = contracts.cash.balanceOf(t.a1)
            takerFinalCash = contracts.cash.balanceOf(t.a2)
            marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpAmountFilled = min(fxpAmountTakerWants, fxpOrderAmount)
            assert(makerFinalCash == makerIntermediateCash), "Maker's final cash balance should be unchanged from intermediate cash balance"
            assert(takerFinalCash == takerInitialCash + fxpCashPaidByMaker), "Taker's cash balance should be increased by fxpCashPaidByMaker"
            assert(marketFinalCash == marketInitialCash), "Market's final cash balance should be equal to its initial cash balance"
            makerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerFinalOutcomeOneShares == 0), "Maker's final outcome 1 shares balance should be 0"
            assert(makerFinalOutcomeTwoShares == fxpAmountFilled), "Maker's final outcome 2 shares balance should be equal to fxpAmountFilled"
            assert(takerFinalOutcomeOneShares == 0), "Taker's final outcome 1 shares balance should be 0"
            assert(takerFinalOutcomeTwoShares == fxpOutcomeTwoShares - fxpAmountFilled), "Taker's final outcome 2 shares balance should be 0"
            assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
            assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"

        def test_takeBidOrder_makerEscrowedShares_takerWithShares():
            global shareTokenContractTranslator
            global outcomeShareContractWrapper
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)

            # 1. Taker buys a complete set, then transfers outcome 1, leaving taker with shares of outcome 2 only.
            contracts._ContractLoader__state.mine(1)
            fxpOutcomeTwoShares = fix(10)
            buyCompleteSets(marketID, fxpOutcomeTwoShares, sender=t.k2)
            contracts._ContractLoader__state.mine(1)
            transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpOutcomeTwoShares])
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer taker's shares of outcome 1 to address 0"

            # 2. Maker buys complete sets, then transfers shares of outcome 2.
            contracts._ContractLoader__state.mine(1)
            fxpNumCompleteSets = fix(10)
            buyCompleteSets(marketID, fxpNumCompleteSets)
            contracts._ContractLoader__state.mine(1)
            transferSharesAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
            assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, transferSharesAbiEncodedData).encode("hex"), 16) == 1), "Transfer maker's shares of outcome 2 to address 0"
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            assert(makerInitialCash >= fxpEtherDepositValue - fxpNumCompleteSets), "Maker's initial cash balance should be at least fxpEtherDepositValue - fxpNumCompleteSets"
            assert(takerInitialCash >= fxpEtherDepositValue - fxpOutcomeTwoShares), "Taker's initial cash balance should be at least fxpEtherDepositValue"
            assert(marketInitialCash == fxpNumCompleteSets + fxpOutcomeTwoShares), "Market's initial cash balance should be equal to fxpNumCompleteSets + fxpOutcomeTwoShares"
            makerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerInitialOutcomeOneShares == fxpNumCompleteSets), "Maker's initial outcome 1 shares balance should be equal to fxpNumCompleteSets"
            assert(makerInitialOutcomeTwoShares == 0), "Maker's initial outcome 2 shares balance should be 0"
            assert(takerInitialOutcomeOneShares == 0), "Taker's initial outcome 1 shares balance should be 0"
            assert(takerInitialOutcomeTwoShares == fxpOutcomeTwoShares), "Taker's initial outcome 2 shares balance should be equal to fxpOutcomeTwoShares"
            assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
            assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"

            # 3. Maker places a bid order. Shares of other outcome(s) sent from maker to market.
            contracts._ContractLoader__state.mine(1)
            fxpOrderAmount = fix(2)
            fxpPrice = fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            fxpAllowance = fix(10)
            assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares of outcome 1 from account 1 (maker)"
            assert(outcomeShareContractWrapper.allowance(outcomeOneShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance for outcome 1 on account 1 (maker) should be equal to the amount approved"
            orderID = contracts.makeOrder.publicMakeOrder(1, fxpOrderAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            makerIntermediateCash = contracts.cash.balanceOf(t.a1)
            takerIntermediateCash = contracts.cash.balanceOf(t.a2)
            marketIntermediateCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpCumulativeScale = Decimal(contracts.markets.getCumulativeScale(marketID))
            fxpMinValue = contracts.events.getMinValue(eventID)
            assert(makerIntermediateCash == makerInitialCash), "Maker's cash balance should be unchanged"
            assert(takerIntermediateCash == takerInitialCash), "Taker's cash balance should be unchanged"
            assert(marketIntermediateCash == marketInitialCash), "Market's cash balance should be unchanged"
            makerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketIntermediateOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketIntermediateOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerIntermediateOutcomeOneShares == fxpNumCompleteSets - fxpOrderAmount), "Maker's intermediate outcome 1 shares balance should be fxpNumCompleteSets - fxpOrderAmount"
            assert(makerIntermediateOutcomeTwoShares == 0), "Maker's intermediate outcome 2 shares balance should be 0"
            assert(takerIntermediateOutcomeOneShares == 0), "Taker's intermediate outcome 1 shares balance should be 0"
            assert(takerIntermediateOutcomeTwoShares == takerInitialOutcomeTwoShares), "Taker's intermediate outcome 2 shares balance should be unchanged"
            assert(marketIntermediateOutcomeOneShares == fxpOrderAmount), "Market's intermediate outcome 1 shares balance should be equal to fxpOrderAmount"
            assert(marketIntermediateOutcomeTwoShares == 0), "Market's intermediate outcome 2 shares balance should be 0"

            # 4. Taker fills bid order:
            #    - Maker has a complete set once bid is filled; takeBidOrder auto-sells this complete set.
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = fix(3)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 1, sender=t.k2)
            assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
            contracts._ContractLoader__state.mine(1)
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeTwoShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.takeBidOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve takeBidOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a2, contracts.takeBidOrder.address) == fxpAllowance), "takeBidOrder contract's allowance should be equal to the amount approved"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, fix(10), sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, fix(10), sender=t.k1) == 1), "Approve takeBidOrder contract to spend cash from account 1"
            contracts._ContractLoader__state.mine(1)
            fxpAmountRemaining = contracts.takeBidOrder.takeBidOrder(t.a2, orderID, fxpAmountTakerWants, sender=t.k0)
            assert(fxpAmountRemaining == fxpAmountTakerWants - fxpOrderAmount), "Amount remaining should be fxpAmountTakerWants - fxpOrderAmount"
            makerFinalCash = contracts.cash.balanceOf(t.a1)
            takerFinalCash = contracts.cash.balanceOf(t.a2)
            marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            fxpAmountFilled = min(fxpAmountTakerWants, fxpOrderAmount)
            fxpCashTransferFromMarketToTaker = int(Decimal(fxpAmountFilled) * (Decimal(fxpPrice) - Decimal(fxpMinValue)) / Decimal(10)**Decimal(18))
            fxpSharesHeld = Decimal(min(fxpNumCompleteSets, fxpAmountFilled))
            fxpSellCompleteSetsCashTransferFromMarketToMaker = fxpSharesHeld * fxpCumulativeScale / Decimal(10)**Decimal(18)
            fxpExpectedFee = int(Decimal(contracts.markets.getTradingFee(marketID)) * fxpSharesHeld / Decimal(10)**Decimal(18) * fxpCumulativeScale / Decimal(10)**Decimal(18))
            fxpCashTransferFromMakerToMarket = int((Decimal(fxpPrice) - Decimal(fxpMinValue)) * Decimal(fxpOrderAmount) / Decimal(10)**Decimal(18))
            fxpExpectedCashTransferToMaker = int(fxpSellCompleteSetsCashTransferFromMarketToMaker - Decimal(fxpExpectedFee))
            # note: creator is also maker in this case
            fxpExpectedFeePaidToCreator = int(Decimal(fxpExpectedFee) / Decimal(2))
            assert(makerFinalCash == makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket), "Maker's final cash balance should be makerInitialCash + fxpExpectedCashTransferToMaker + fxpExpectedFeePaidToCreator - fxpCashTransferFromMakerToMarket"
            assert(takerFinalCash == takerInitialCash + fxpCashTransferFromMarketToTaker), "Taker's final cash balance takerInitialCash + fxpCashTransferFromMarketToTaker"
            assert(marketFinalCash == marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket), "Market's final cash balance should be marketInitialCash - fxpExpectedCashTransferToMaker - fxpExpectedFeePaidToCreator - fxpCashTransferFromMarketToTaker + fxpCashTransferFromMakerToMarket"
            makerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
            makerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
            takerFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 1)
            takerFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a2, 2)
            marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
            marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
            assert(makerFinalOutcomeOneShares == makerIntermediateOutcomeOneShares), "Maker's final outcome 1 shares balance should be unchanged"
            assert(makerFinalOutcomeTwoShares == 0), "Maker's final outcome 2 shares balance should be 0"
            assert(takerFinalOutcomeOneShares == 0), "Taker's final outcome 1 shares balance should be 0"
            assert(takerFinalOutcomeTwoShares == fxpOutcomeTwoShares - fxpAmountFilled), "Taker's final outcome 2 shares balance should be fxpOutcomeTwoShares - fxpAmountFilled"
            assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
            assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"

        test_takeBidOrder_makerEscrowedCash_takerWithoutShares()
        test_takeBidOrder_makerEscrowedShares_takerWithoutShares()
        test_takeBidOrder_makerEscrowedCash_takerWithShares()
        test_takeBidOrder_makerEscrowedShares_takerWithShares()
    test_usingMarketType("binary")
    test_usingMarketType("scalar")

def test_TakeOrder():
    global contracts
    t = contracts._ContractLoader__tester
    def test_publicTakeOrder():
        def test_takeAskOrder():
            global shareTokenContractTranslator
            global outcomeShareContractWrapper
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 2                   # ask
            fxpAmount = fix(1)
            fxpPrice = fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeOrder.address, fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = int(fxpAmount / 10)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=t.k2)
            assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
            contracts._ContractLoader__state.mine(1)
            fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=t.k2)
            assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        def test_takeBidOrder():
            global shareTokenContractTranslator
            global outcomeShareContractWrapper
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount = fix(1)
            fxpPrice = fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createMarket(eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeOrder.address, fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            fxpAllowance = fix(10)
            outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
            abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            # place a bid order (escrow cash)
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = int(fxpAmount / 10)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, orderType, sender=t.k2)
            assert(contracts.orders.commitOrder(tradeHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
            contracts._ContractLoader__state.mine(1)
            assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == fix("0.6")), "Market's cash balance should be (price - 1)*amount"
            fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(orderID, fxpAmountTakerWants, sender=t.k2)
            assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        test_takeAskOrder()
        test_takeBidOrder()
    test_publicTakeOrder()

def test_DecreaseTradingFee():
    global contracts
    t = contracts._ContractLoader__tester
    def test_publicDecreaseTradingFee():
        contracts._ContractLoader__state.mine(1)
        eventID = createBinaryEvent()
        marketID = createMarket(eventID)
        assert(contracts.cash.approve(contracts.decreaseTradingFee.address, fix(10), sender=t.k1) == 1), "Approve decreaseTradingFee contract to spend cash from account 1"
        fxpInitialTradingFee = contracts.markets.getTradingFee(marketID)
        assert(fxpInitialTradingFee == fix("0.020000000000000001")), "Initial trading fee should be 20000000000000001"
        fxpNewTradingFee = fix("0.02")
        result = contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, fxpNewTradingFee, sender=t.k1)
        assert(contracts.markets.getTradingFee(marketID) == fxpNewTradingFee), "Updated trading fee should be equal to fxpNewTradingFee"
    def test_exceptions():
        contracts._ContractLoader__state.mine(1)
        eventID = createBinaryEvent()
        marketID = createMarket(eventID)
        assert(contracts.cash.approve(contracts.decreaseTradingFee.address, fix(10), sender=t.k1) == 1), "Approve decreaseTradingFee contract to spend cash from account 1"
        assert(contracts.cash.approve(contracts.decreaseTradingFee.address, fix(10), sender=t.k2) == 1), "Approve decreaseTradingFee contract to spend cash from account 2"
        fxpInitialTradingFee = contracts.markets.getTradingFee(marketID)
        assert(fxpInitialTradingFee == fix("0.020000000000000001")), "Initial trading fee should be 20000000000000001"
        fxpNewTradingFee = fix("0.02")

        # Permissions exceptions
        contracts._ContractLoader__state.mine(1)
        try:
            raise Exception(contracts.decreaseTradingFee.decreaseTradingFee(t.a1, marketID, fxpNewTradingFee, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "decreaseTradingFee should fail if called from a non-whitelisted account (account 1)"

        # decreaseTradingFee exceptions
        contracts._ContractLoader__state.mine(1)
        try:
            raise Exception(contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, fxpNewTradingFee, sender=t.k2))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicDecreaseTradingFee should fail if sender is not the market creator"
        try:
            raise Exception(contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, contracts.branches.getMinTradingFee(1010101) - 1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicDecreaseTradingFee should fail if new trading fee is below the minimum fee for the branch"
        try:
            raise Exception(contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, fix("0.020000000000000002"), sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicDecreaseTradingFee should fail if new trading fee is higher than the old trading fee"
        contracts._ContractLoader__state.mine(1)
        result = contracts.decreaseTradingFee.publicDecreaseTradingFee(marketID, fxpNewTradingFee, sender=t.k1)
        assert(contracts.markets.getTradingFee(marketID) == fxpNewTradingFee), "Updated trading fee should be equal to fxpNewTradingFee"
    test_publicDecreaseTradingFee()
    test_exceptions()

def test_ClaimProceeds():
    def test_BinaryOrCategoricalPayouts():
        global contracts
        t = contracts._ContractLoader__tester
        def test_payoutBinaryOrCategoricalMarket():
            def test_binary():
                def test_userWithoutShares():
                    contracts._ContractLoader__state.mine(1)
                    eventID = createBinaryEvent()
                    marketID = createMarket(eventID)
                    outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                    outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                    outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                    outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                    contracts._ContractLoader__state.mine(1)
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                    outcomeID = 2
                    assert(contracts.events.setOutcome(eventID, fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
                    assert(contracts.markets.setMarketResolved(marketID, sender=t.k0) == 1), "Should manually set market resolved"
                    contracts._ContractLoader__state.mine(1)
                    userInitialCash = contracts.cash.balanceOf(t.a1)
                    marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                    assert(marketInitialCash == 0), "Market's initial cash balance should be equal to 0"
                    userInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                    userInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                    marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                    marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                    assert(userInitialOutcomeOneShares == 0), "User's initial outcome 1 shares balance should be equal to 0"
                    assert(userInitialOutcomeTwoShares == 0), "User's initial outcome 2 shares balance should be 0"
                    assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
                    assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"
                    assert(contracts.claimProceeds.publicClaimProceeds(marketID, sender=t.k1) == 1), "publicClaimProceeds should complete successfully"
                    userFinalCash = contracts.cash.balanceOf(t.a1)
                    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                    assert(userFinalCash == userInitialCash), "User's cash balance should be unchanged"
                    assert(marketFinalCash == 0), "Market's final cash balance should be equal to 0"
                    userFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                    userFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                    marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                    marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                    assert(userFinalOutcomeOneShares == 0), "User's final outcome 1 shares balance should be equal to 0"
                    assert(userFinalOutcomeTwoShares == 0), "User's final outcome 2 shares balance should be 0"
                    assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
                    assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) - 259201
                def test_userWithWinningShares():
                    global shareTokenContractTranslator
                    global outcomeShareContractWrapper
                    contracts._ContractLoader__state.mine(1)
                    fxpEtherDepositValue = fix(100)
                    assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                    contracts._ContractLoader__state.mine(1)
                    eventID = createBinaryEvent()
                    marketID = createMarket(eventID)
                    outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                    outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                    outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                    outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                    contracts._ContractLoader__state.mine(1)
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                    fxpNumCompleteSets = fix(3)
                    buyCompleteSets(marketID, fxpNumCompleteSets)
                    contracts._ContractLoader__state.mine(1)
                    transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                    assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                    outcomeID = 2
                    assert(contracts.events.setOutcome(eventID, fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
                    assert(contracts.markets.setMarketResolved(marketID, sender=t.k0) == 1), "Should manually set market resolved"
                    contracts._ContractLoader__state.mine(1)
                    userInitialCash = contracts.cash.balanceOf(t.a1)
                    marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                    assert(marketInitialCash == fxpNumCompleteSets), "Market's initial cash balance should be equal to fxpNumCompleteSets"
                    userInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                    userInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                    marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                    marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                    assert(userInitialOutcomeOneShares == 0), "User's initial outcome 1 shares balance should be 0"
                    assert(userInitialOutcomeTwoShares == fxpNumCompleteSets), "User's initial outcome 2 shares balance should be fxpNumCompleteSets"
                    assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
                    assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"
                    assert(contracts.claimProceeds.publicClaimProceeds(marketID, sender=t.k1) == 1), "publicClaimProceeds should complete successfully"
                    userFinalCash = contracts.cash.balanceOf(t.a1)
                    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                    fxpTradingFee = contracts.markets.getTradingFee(marketID)
                    fxpFee = int(Decimal(userInitialOutcomeTwoShares) * Decimal(fxpTradingFee) / Decimal(10)**Decimal(18))
                    fxpFeeSentToMarketCreator = int(Decimal(fxpFee) / Decimal(2))
                    assert(userFinalCash == userInitialCash + userInitialOutcomeTwoShares - fxpFee + fxpFeeSentToMarketCreator), "User's final cash balance should be userInitialCash + userInitialOutcomeTwoShares - fxpFee + fxpFeeSentToMarketCreator"
                    assert(marketFinalCash == 0), "Market's final cash balance should be equal to 0"
                    userFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                    userFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                    marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                    marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                    assert(userFinalOutcomeOneShares == 0), "User's final outcome 1 shares balance should be equal to 0"
                    assert(userFinalOutcomeTwoShares == 0), "User's final outcome 2 shares balance should be 0"
                    assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
                    assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) - 259201
                test_userWithoutShares()
                test_userWithWinningShares()
            def test_categorical():
                def test_userWithoutShares():
                    contracts._ContractLoader__state.mine(1)
                    numOutcomes = 3
                    eventID = createCategoricalEvent(numOutcomes)
                    marketID = createMarket(eventID)
                    outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                    outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                    outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                    outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                    contracts._ContractLoader__state.mine(1)
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                    outcomeID = 2
                    assert(contracts.events.setOutcome(eventID, fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
                    assert(contracts.markets.setMarketResolved(marketID, sender=t.k0) == 1), "Should manually set market resolved"
                    contracts._ContractLoader__state.mine(1)
                    userInitialCash = contracts.cash.balanceOf(t.a1)
                    marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                    assert(marketInitialCash == 0), "Market's initial cash balance should be equal to 0"
                    userInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                    userInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                    marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                    marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                    assert(userInitialOutcomeOneShares == 0), "User's initial outcome 1 shares balance should be equal to 0"
                    assert(userInitialOutcomeTwoShares == 0), "User's initial outcome 2 shares balance should be 0"
                    assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
                    assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"
                    assert(contracts.claimProceeds.publicClaimProceeds(marketID, sender=t.k1) == 1), "publicClaimProceeds should complete successfully"
                    userFinalCash = contracts.cash.balanceOf(t.a1)
                    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                    assert(userFinalCash == userInitialCash), "User's cash balance should be unchanged"
                    assert(marketFinalCash == 0), "Market's final cash balance should be equal to 0"
                    userFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                    userFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                    marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                    marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                    assert(userFinalOutcomeOneShares == 0), "User's final outcome 1 shares balance should be equal to 0"
                    assert(userFinalOutcomeTwoShares == 0), "User's final outcome 2 shares balance should be 0"
                    assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
                    assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) - 259201
                def test_userWithWinningShares():
                    global shareTokenContractTranslator
                    global outcomeShareContractWrapper
                    contracts._ContractLoader__state.mine(1)
                    fxpEtherDepositValue = fix(100)
                    assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                    contracts._ContractLoader__state.mine(1)
                    numOutcomes = 3
                    eventID = createCategoricalEvent(numOutcomes)
                    marketID = createMarket(eventID)
                    outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                    outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                    outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                    outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                    contracts._ContractLoader__state.mine(1)
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                    fxpNumCompleteSets = fix(3)
                    buyCompleteSets(marketID, fxpNumCompleteSets)
                    contracts._ContractLoader__state.mine(1)
                    transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                    assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                    outcomeID = 2
                    assert(contracts.events.setOutcome(eventID, fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
                    assert(contracts.markets.setMarketResolved(marketID, sender=t.k0) == 1), "Should manually set market resolved"
                    contracts._ContractLoader__state.mine(1)
                    userInitialCash = contracts.cash.balanceOf(t.a1)
                    marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                    assert(marketInitialCash == fxpNumCompleteSets), "Market's initial cash balance should be equal to fxpNumCompleteSets"
                    userInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                    userInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                    marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                    marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                    assert(userInitialOutcomeOneShares == 0), "User's initial outcome 1 shares balance should be 0"
                    assert(userInitialOutcomeTwoShares == fxpNumCompleteSets), "User's initial outcome 2 shares balance should be fxpNumCompleteSets"
                    assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
                    assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"
                    assert(contracts.claimProceeds.publicClaimProceeds(marketID, sender=t.k1) == 1), "publicClaimProceeds should complete successfully"
                    userFinalCash = contracts.cash.balanceOf(t.a1)
                    marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                    fxpTradingFee = contracts.markets.getTradingFee(marketID)
                    fxpFee = int(Decimal(userInitialOutcomeTwoShares) * Decimal(fxpTradingFee) / Decimal(10)**Decimal(18))
                    fxpFeeSentToMarketCreator = int(Decimal(fxpFee) / Decimal(2))
                    assert(userFinalCash == userInitialCash + userInitialOutcomeTwoShares - fxpFee + fxpFeeSentToMarketCreator), "User's final cash balance should be userInitialCash + userInitialOutcomeTwoShares - fxpFee + fxpFeeSentToMarketCreator"
                    assert(marketFinalCash == 0), "Market's final cash balance should be equal to 0"
                    userFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                    userFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                    marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                    marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                    assert(userFinalOutcomeOneShares == 0), "User's final outcome 1 shares balance should be equal to 0"
                    assert(userFinalOutcomeTwoShares == 0), "User's final outcome 2 shares balance should be 0"
                    assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
                    assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) - 259201
                test_userWithoutShares()
                test_userWithWinningShares()
            test_binary()
            test_categorical()
        def test_payoutIndeterminateBinaryOrCategoricalMarket():
            def test_binary():
                global shareTokenContractTranslator
                global outcomeShareContractWrapper
                contracts._ContractLoader__state.mine(1)
                fxpEtherDepositValue = fix(100)
                assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                contracts._ContractLoader__state.mine(1)
                eventID = createBinaryEvent()
                marketID = createMarket(eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                fxpNumCompleteSets = fix(3)
                buyCompleteSets(marketID, fxpNumCompleteSets)
                contracts._ContractLoader__state.mine(1)
                transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                assert(contracts.events.setOutcome(eventID, fix("0.5"), sender=t.k0) == 1), "Should manually set event outcome"
                assert(contracts.markets.setMarketResolved(marketID, sender=t.k0) == 1), "Should manually set market resolved"
                contracts._ContractLoader__state.mine(1)
                userInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                assert(marketInitialCash == fxpNumCompleteSets), "Market's initial cash balance should be equal to fxpNumCompleteSets"
                userInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                assert(userInitialOutcomeOneShares == 0), "User's initial outcome 1 shares balance should be 0"
                assert(userInitialOutcomeTwoShares == fxpNumCompleteSets), "User's initial outcome 2 shares balance should be fxpNumCompleteSets"
                assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
                assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"
                assert(contracts.claimProceeds.publicClaimProceeds(marketID, sender=t.k1) == 1), "publicClaimProceeds should complete successfully"
                userFinalCash = contracts.cash.balanceOf(t.a1)
                marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                fxpTradingFee = contracts.markets.getTradingFee(marketID)
                fxpShareValue = int(Decimal(userInitialOutcomeTwoShares) / Decimal(2))
                fxpFee = int(Decimal(fxpShareValue) * Decimal(fxpTradingFee) / Decimal(10)**Decimal(18))
                fxpFeeSentToMarketCreator = int(Decimal(fxpFee) / Decimal(2))
                assert(userFinalCash == userInitialCash + fxpShareValue - fxpFee + fxpFeeSentToMarketCreator), "User's final cash balance should be userInitialCash + userInitialOutcomeTwoShares - fxpFee + fxpFeeSentToMarketCreator"
                assert(marketFinalCash == int(Decimal(marketInitialCash) / Decimal(2))), "Market's final cash balance should be equal to 0"
                userFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                assert(userFinalOutcomeOneShares == 0), "User's final outcome 1 shares balance should be equal to 0"
                assert(userFinalOutcomeTwoShares == 0), "User's final outcome 2 shares balance should be 0"
                assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
                assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) - 259201
            def test_categorical():
                global shareTokenContractTranslator
                global outcomeShareContractWrapper
                contracts._ContractLoader__state.mine(1)
                fxpEtherDepositValue = fix(100)
                assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                contracts._ContractLoader__state.mine(1)
                numOutcomes = 3
                eventID = createCategoricalEvent(numOutcomes)
                marketID = createMarket(eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeThreeShareContract = contracts.markets.getOutcomeShareContract(marketID, 3)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                outcomeThreeShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 3)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                fxpNumCompleteSets = fix(3)
                buyCompleteSets(marketID, fxpNumCompleteSets)
                contracts._ContractLoader__state.mine(1)
                transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                assert(contracts.events.setOutcome(eventID, fix("0.5"), sender=t.k0) == 1), "Should manually set event outcome"
                assert(contracts.markets.setMarketResolved(marketID, sender=t.k0) == 1), "Should manually set market resolved"
                contracts._ContractLoader__state.mine(1)
                userInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                assert(marketInitialCash == fxpNumCompleteSets), "Market's initial cash balance should be equal to fxpNumCompleteSets"
                userInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                userInitialOutcomeThreeShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 3)
                marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                marketInitialOutcomeThreeShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 3)
                assert(userInitialOutcomeOneShares == 0), "User's initial outcome 1 shares balance should be 0"
                assert(userInitialOutcomeTwoShares == fxpNumCompleteSets), "User's initial outcome 2 shares balance should be fxpNumCompleteSets"
                assert(userInitialOutcomeThreeShares == fxpNumCompleteSets), "User's initial outcome 3 shares balance should be 0"
                assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
                assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"
                assert(marketInitialOutcomeThreeShares == 0), "Market's initial outcome 3 shares balance should be 0"
                assert(contracts.claimProceeds.publicClaimProceeds(marketID, sender=t.k1) == 1), "publicClaimProceeds should complete successfully"
                userFinalCash = contracts.cash.balanceOf(t.a1)
                marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                fxpTradingFee = contracts.markets.getTradingFee(marketID)
                fxpShareValue = int(Decimal(userInitialOutcomeTwoShares) / Decimal(numOutcomes) * Decimal(2))
                fxpFee = int(Decimal(fxpShareValue) * Decimal(fxpTradingFee) / Decimal(10)**Decimal(18))
                fxpFeeSentToMarketCreator = int(Decimal(fxpFee) / Decimal(2))
                assert(userFinalCash == userInitialCash + fxpShareValue - fxpFee + fxpFeeSentToMarketCreator - 1), "User's final cash balance should be userInitialCash + userInitialOutcomeTwoShares - fxpFee + fxpFeeSentToMarketCreator - 1 (rounding)"
                assert(marketFinalCash == int(Decimal(marketInitialCash) / Decimal(3))), "Market's final cash balance should be equal to marketInitialCash / 3"
                userFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                userFinalOutcomeThreeShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 3)
                marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                marketFinalOutcomeThreeShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeThreeShareWallet, 2)
                assert(userFinalOutcomeOneShares == 0), "User's final outcome 1 shares balance should be equal to 0"
                assert(userFinalOutcomeTwoShares == 0), "User's final outcome 2 shares balance should be 0"
                assert(userFinalOutcomeThreeShares == 0), "User's final outcome 3 shares balance should be 0"
                assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
                assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
                assert(marketFinalOutcomeThreeShares == 0), "Market's final outcome 3 shares balance should be 0"
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) - 259201
            test_binary()
            test_categorical()
        test_payoutBinaryOrCategoricalMarket()
        test_payoutIndeterminateBinaryOrCategoricalMarket()
    def test_ScalarPayouts():
        global contracts
        t = contracts._ContractLoader__tester
        def test_payoutScalarMarket():
            def test_userWithoutShares():
                contracts._ContractLoader__state.mine(1)
                fxpMinValue = fix(5)
                fxpMaxValue = fix(15)
                eventID = createScalarEvent(fxpMinValue, fxpMaxValue)
                marketID = createMarket(eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                outcomeID = "12.5"
                assert(contracts.events.setOutcome(eventID, fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
                assert(contracts.markets.setMarketResolved(marketID, sender=t.k0) == 1), "Should manually set market resolved"
                contracts._ContractLoader__state.mine(1)
                userInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                assert(marketInitialCash == 0), "Market's initial cash balance should be equal to 0"
                userInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                assert(userInitialOutcomeOneShares == 0), "User's initial outcome 1 shares balance should be equal to 0"
                assert(userInitialOutcomeTwoShares == 0), "User's initial outcome 2 shares balance should be 0"
                assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
                assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"
                assert(contracts.claimProceeds.publicClaimProceeds(marketID, sender=t.k1) == 1), "publicClaimProceeds should complete successfully"
                userFinalCash = contracts.cash.balanceOf(t.a1)
                marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                assert(userFinalCash == userInitialCash), "User's cash balance should be unchanged"
                assert(marketFinalCash == 0), "Market's final cash balance should be equal to 0"
                userFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                assert(userFinalOutcomeOneShares == 0), "User's final outcome 1 shares balance should be equal to 0"
                assert(userFinalOutcomeTwoShares == 0), "User's final outcome 2 shares balance should be 0"
                assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
                assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) - 259201
            def test_userWithHighSideShares():
                global shareTokenContractTranslator
                global outcomeShareContractWrapper
                contracts._ContractLoader__state.mine(1)
                fxpEtherDepositValue = fix(100)
                assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                contracts._ContractLoader__state.mine(1)
                fxpMinValue = fix(5)
                fxpMaxValue = fix(15)
                eventID = createScalarEvent(fxpMinValue, fxpMaxValue)
                marketID = createMarket(eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                fxpNumCompleteSets = fix(3)
                buyCompleteSets(marketID, fxpNumCompleteSets)
                contracts._ContractLoader__state.mine(1)
                transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                outcomeID = "12.5"
                assert(contracts.events.setOutcome(eventID, fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
                assert(contracts.events.getOutcome(eventID) == fix(outcomeID)), "Event outcome should be equal to value set"
                assert(contracts.markets.setMarketResolved(marketID, sender=t.k0) == 1), "Should manually set market resolved"
                contracts._ContractLoader__state.mine(1)
                fxpCompleteSetsCost = int(Decimal(fxpNumCompleteSets) * Decimal(contracts.markets.getCumulativeScale(marketID)) / Decimal(10)**Decimal(18))
                userInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                assert(marketInitialCash == fxpCompleteSetsCost), "Market's initial cash balance should be equal to fxpNumCompleteSets"
                userInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                assert(userInitialOutcomeOneShares == 0), "User's initial outcome 1 shares balance should be 0"
                assert(userInitialOutcomeTwoShares == fxpNumCompleteSets), "User's initial outcome 2 shares balance should be fxpNumCompleteSets"
                assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
                assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"
                assert(contracts.claimProceeds.publicClaimProceeds(marketID, sender=t.k1) == 1), "publicClaimProceeds should complete successfully"
                # assert(contracts.scalarPayouts.payoutScalarMarket(t.a1, marketID, eventID, sender=t.k0) == 1), "payoutScalarMarket should complete successfully"
                userFinalCash = contracts.cash.balanceOf(t.a1)
                marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                fxpShare1Value = fxpMaxValue - fix(outcomeID)
                fxpShare2Value = fix(outcomeID) - fxpMinValue
                fxpTradingFee = contracts.markets.getTradingFee(marketID)
                fxpShareValue = int(Decimal(fxpShare2Value) * Decimal(userInitialOutcomeTwoShares) / Decimal(10)**Decimal(18))
                fxpFee = int(Decimal(fxpShareValue) * Decimal(fxpTradingFee) / Decimal(10)**Decimal(18))
                fxpFeeSentToBranch = int(Decimal(fxpFee) - Decimal(fxpFee) / Decimal(2))
                fxpFeeSentToMarketCreator = int(Decimal(fxpFee) / Decimal(2))
                assert(userFinalCash == userInitialCash + fxpShareValue - fxpFee + fxpFeeSentToMarketCreator), "User's final cash balance should be userInitialCash + fxpShareValue - fxpFee + fxpFeeSentToMarketCreator"
                assert(marketFinalCash == marketInitialCash - fxpShareValue), "Market's final cash balance should be equal to 0"
                userFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                assert(userFinalOutcomeOneShares == 0), "User's final outcome 1 shares balance should be equal to 0"
                assert(userFinalOutcomeTwoShares == 0), "User's final outcome 2 shares balance should be 0"
                assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
                assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) - 259201
            def test_userWithLowSideShares():
                global shareTokenContractTranslator
                global outcomeShareContractWrapper
                contracts._ContractLoader__state.mine(1)
                fxpEtherDepositValue = fix(100)
                assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                contracts._ContractLoader__state.mine(1)
                fxpMinValue = fix(5)
                fxpMaxValue = fix(15)
                eventID = createScalarEvent(fxpMinValue, fxpMaxValue)
                marketID = createMarket(eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                fxpNumCompleteSets = fix(3)
                buyCompleteSets(marketID, fxpNumCompleteSets)
                contracts._ContractLoader__state.mine(1)
                transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 2 to address 0"
                outcomeID = "12.5"
                assert(contracts.events.setOutcome(eventID, fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
                assert(contracts.events.getOutcome(eventID) == fix(outcomeID)), "Event outcome should be equal to value set"
                assert(contracts.markets.setMarketResolved(marketID, sender=t.k0) == 1), "Should manually set market resolved"
                contracts._ContractLoader__state.mine(1)
                fxpCompleteSetsCost = int(Decimal(fxpNumCompleteSets) * Decimal(contracts.markets.getCumulativeScale(marketID)) / Decimal(10)**Decimal(18))
                userInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                assert(marketInitialCash == fxpCompleteSetsCost), "Market's initial cash balance should be equal to fxpNumCompleteSets"
                userInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                marketInitialOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketInitialOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                assert(userInitialOutcomeOneShares == fxpNumCompleteSets), "User's initial outcome 1 shares balance should be fxpNumCompleteSets"
                assert(userInitialOutcomeTwoShares == 0), "User's initial outcome 2 shares balance should be 0"
                assert(marketInitialOutcomeOneShares == 0), "Market's initial outcome 1 shares balance should be 0"
                assert(marketInitialOutcomeTwoShares == 0), "Market's initial outcome 2 shares balance should be 0"
                assert(contracts.claimProceeds.publicClaimProceeds(marketID, sender=t.k1) == 1), "publicClaimProceeds should complete successfully"
                # assert(contracts.scalarPayouts.payoutScalarMarket(t.a1, marketID, eventID, sender=t.k0) == 1), "payoutScalarMarket should complete successfully"
                userFinalCash = contracts.cash.balanceOf(t.a1)
                marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                fxpShare1Value = fxpMaxValue - fix(outcomeID)
                fxpTradingFee = contracts.markets.getTradingFee(marketID)
                fxpShareValue = int(Decimal(fxpShare1Value) * Decimal(userInitialOutcomeOneShares) / Decimal(10)**Decimal(18))
                fxpFee = int(Decimal(fxpShareValue) * Decimal(fxpTradingFee) / Decimal(10)**Decimal(18))
                fxpFeeSentToBranch = int(Decimal(fxpFee) - Decimal(fxpFee) / Decimal(2))
                fxpFeeSentToMarketCreator = int(Decimal(fxpFee) / Decimal(2))
                assert(userFinalCash == userInitialCash + fxpShareValue - fxpFee + fxpFeeSentToMarketCreator), "User's final cash balance should be userInitialCash + fxpShareValue - fxpFee + fxpFeeSentToMarketCreator"
                assert(marketFinalCash == marketInitialCash - fxpShareValue), "Market's final cash balance should be equal to 0"
                userFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 1)
                userFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, 2)
                marketFinalOutcomeOneShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeOneShareWallet, 1)
                marketFinalOutcomeTwoShares = contracts.markets.getParticipantSharesPurchased(marketID, outcomeTwoShareWallet, 2)
                assert(userFinalOutcomeOneShares == 0), "User's final outcome 1 shares balance should be equal to 0"
                assert(userFinalOutcomeTwoShares == 0), "User's final outcome 2 shares balance should be 0"
                assert(marketFinalOutcomeOneShares == 0), "Market's final outcome 1 shares balance should be 0"
                assert(marketFinalOutcomeTwoShares == 0), "Market's final outcome 2 shares balance should be 0"
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) - 259201
            test_userWithoutShares()
            test_userWithHighSideShares()
            test_userWithLowSideShares()
        test_payoutScalarMarket()
    test_BinaryOrCategoricalPayouts()
    test_ScalarPayouts()

def runtests():
    test_Cash()
    test_ShareTokens()
    test_Wallet()
    test_CreateEvent()
    test_CreateMarket()
    test_CompleteSets()
    test_MakeOrder()
    test_CancelOrder()
    test_TakeAskOrder()
    test_TakeBidOrder()
    test_TakeOrder()
    test_DecreaseTradingFee()
    test_ClaimProceeds()

if __name__ == '__main__':
    runtests()
