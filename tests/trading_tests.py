#!/usr/bin/env python
"""Trading tests:
+ functions/createEvent.se
+ functions/createMarket.se
+ functions/cash.se
+ functions/makeOrder.se
+ functions/completeSets.se
+ functions/cancelOrder.se
+ functions/shareTokens.se
+ functions/wallet.se
- functions/fillAskLibrary.se
- functions/fillBidLibrary.se
- functions/trade.se
- functions/tradeAvailableOrders.se
- functions/marketModifiers.se
- functions/offChainTrades.se
- functions/claimMarketProceeds.se
- functions/oneWinningOutcomePayouts.se
- functions/twoWinningOutcomePayouts.se

"""
from __future__ import division
import ethereum
import os
import sys
import json
import iocapture

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))

from upload_contracts import ContractLoader

contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])

eventCreationCounter = 0

def fix(n):
    return n * 10**18

def unfix(n):
    return n / 10**18

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
    contracts.cash.publicDepositEther(value=fix(10000), sender=t.k1)
    contracts.cash.approve(contracts.createEvent.address, fix(10000), sender=t.k1)
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

def createBinaryMarket(eventID):
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
    return contracts.createMarket.publicCreateMarket(branch, fxpTradingFee, eventID, tag1, tag2, tag3, extraInfo, currency, sender=t.k1, value=fix(10000))

def buyCompleteSets(marketID, fxpAmount):
    global contracts
    t = contracts._ContractLoader__tester
    assert(contracts.cash.approve(contracts.completeSets.address, fix(10000), sender=t.k1) == 1), "Approve completeSets contract to spend cash"
    with iocapture.capture() as captured:
        result = contracts.completeSets.publicBuyCompleteSets(marketID, fxpAmount, sender=t.k1)
        logged = captured.stdout
    logCompleteSets = parseCapturedLogs(logged)[-1]
    assert(logCompleteSets["_event_type"] == "logCompleteSets"), "Should emit a logCompleteSets event"
    assert(logCompleteSets["sender"] == long(t.a1.encode("hex"), 16)), "Logged sender should match input"
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
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
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
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
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
        assert(logged["owner"] == address1)
        assert(logged["spender"] == address2)
        assert(logged["value"] == 10)
        assert(contracts.cash.allowance(t.a1, t.a2) == 10), "allowance is 10 after approval"
        with iocapture.capture() as captured:
            retval = contracts.cash.transferFrom(t.a1, t.a2, 7, sender=t.k2)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transferFrom should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
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
    def test_createTokens():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = fix(10)
        initialTotalSupply = contracts.shareTokens.totalSupply()
        initialBalance = contracts.shareTokens.balanceOf(t.a1)
        assert(contracts.shareTokens.createTokens(t.a1, fxpAmount, sender=t.k0) == 1), "Create share tokens for address 1"
        assert(contracts.shareTokens.totalSupply() - initialTotalSupply == fxpAmount), "Total supply increase should equal the number of tokens created"
        assert(contracts.shareTokens.balanceOf(t.a1) - initialBalance == fxpAmount), "Address 1 token balance increase should equal the number of tokens created"
    def test_destroyTokens():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = fix(10)
        initialTotalSupply = contracts.shareTokens.totalSupply()
        initialBalance = contracts.shareTokens.balanceOf(t.a1)
        assert(contracts.shareTokens.destroyTokens(t.a1, fxpAmount, sender=t.k0) == 1), "Destroy share tokens owned by address 1"
        assert(initialTotalSupply - contracts.shareTokens.totalSupply() == fxpAmount), "Total supply decrease should equal the number of tokens destroyed"
        assert(initialBalance - contracts.shareTokens.balanceOf(t.a1) == fxpAmount), "Address 1 token balance decrease should equal the number of tokens destroyed"
    def test_transfer():
        contracts._ContractLoader__state.mine(1)
        fxpAmount = fix(10)
        fxpTransferAmount = fix(2)
        assert(contracts.shareTokens.createTokens(t.a1, fxpAmount, sender=t.k0) == 1), "Create share tokens for address 1"
        initialTotalSupply = contracts.shareTokens.totalSupply()
        initialBalance1 = contracts.shareTokens.balanceOf(t.a1)
        initialBalance2 = contracts.shareTokens.balanceOf(t.a2)
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.transfer(t.a2, fxpTransferAmount, sender=t.k1)
            logged = captured.stdout
        logged = parseCapturedLogs(logged)[-1]
        assert(retval == 1), "transfer should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
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
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
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
        assert(logged["owner"] == address1)
        assert(logged["spender"] == address2)
        assert(logged["value"] == 10)
        print "allowance:", contracts.shareTokens.allowance(t.a1, t.a2)
        assert(contracts.shareTokens.allowance(t.a1, t.a2) == 10), "allowance is 10 after approval"
        with iocapture.capture() as captured:
            retval = contracts.shareTokens.transferFrom(t.a1, t.a2, 7, sender=t.k2)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transferFrom should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
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
        assert(contracts.shareTokens.createTokens(t.a1, fxpAmount, sender=t.k0) == 1), "Create share tokens for address 1"
        try:
            raise Exception(contracts.shareTokens.createTokens(t.a1, fxpTransferAmount, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "createTokens should fail if called from a non-whitelisted account (account 1)"
        try:
            raise Exception(contracts.shareTokens.destroyTokens(t.a1, fxpTransferAmount, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "destroyTokens should fail if called from a non-whitelisted account (account 1)"
    test_init()
    test_createTokens()
    test_destroyTokens()
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
        marketID = contracts.createMarket.publicCreateMarket(branch, fxpTradingFee, eventID, tag1, tag2, tag3, extraInfo, currency, sender=t.k1, value=fix(10000))
        assert(marketID != 0)
        assert(contracts.markets.getTradingFee(marketID) == fxpTradingFee), "Trading fee matches input"
        assert(contracts.markets.getMarketEvent(marketID) == eventID), "Market event matches input"
        assert(contracts.markets.getTags(marketID) == [tag1, tag2, tag3]), "Tags array matches input"
        assert(contracts.markets.getTopic(marketID)), "Topic matches input tag1"
        assert(contracts.markets.getExtraInfo(marketID) == extraInfo), "Extra info matches input"
    test_publicCreateMarket()

def test_CompleteSets():
    global contracts
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    def test_publicBuyCompleteSets():
        contracts._ContractLoader__state.mine(1)
        eventID = createBinaryEvent()
        marketID = createBinaryMarket(eventID)
        fxpAmount = fix(10)
        senderInitialCash = contracts.cash.balanceOf(t.a1)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
        assert(contracts.cash.approve(contracts.completeSets.address, fix(10000), sender=t.k1) == 1), "Approve completeSets contract to spend cash"
        with iocapture.capture() as captured:
            result = contracts.completeSets.publicBuyCompleteSets(marketID, fxpAmount, sender=t.k1)
            logged = captured.stdout
        logCompleteSets = parseCapturedLogs(logged)[-1]
        assert(logCompleteSets["_event_type"] == "logCompleteSets"), "Should emit a logCompleteSets event"
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
            marketID = createBinaryMarket(eventID)
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
        marketID = createBinaryMarket(eventID)
        buyCompleteSets(marketID, fix(10))
        fxpAmount = fix(9)
        senderInitialCash = contracts.cash.balanceOf(t.a1)
        marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
        marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
        with iocapture.capture() as captured:
            result = contracts.completeSets.publicSellCompleteSets(marketID, fxpAmount, sender=t.k1)
            logged = captured.stdout
        logCompleteSets = parseCapturedLogs(logged)[-1]
        assert(logCompleteSets["_event_type"] == "logCompleteSets"), "Should emit a logCompleteSets event"
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
            marketID = createBinaryMarket(eventID)
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
    def test_publicMakeOrder():
        def test_bid():
            contracts._ContractLoader__state.mine(1)
            orderType = 1                   # bid
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createBinaryMarket(eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10000), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
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
            assert(logMakeOrder["_event_type"] == "logMakeOrder"), "Should emit a logMakeOrder event"
            assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
            assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
            assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
            assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
            assert(logMakeOrder["orderID"] == orderID), "Logged orderID should match returned orderID"
            assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
            assert(logMakeOrder["market"] == marketID), "Logged market should match input"
            assert(logMakeOrder["sender"] == address1), "Logged sender should match input"
        def test_bid_allButOneOutcome():
            pass # needs trade
        def test_ask_withoutShares():
            contracts._ContractLoader__state.mine(1)
            orderType = 2                   # ask
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createBinaryMarket(eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10000), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
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
            assert(logMakeOrder["_event_type"] == "logMakeOrder"), "Should emit a logMakeOrder event"
            assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
            assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
            assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
            assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
            assert(logMakeOrder["orderID"] == orderID), "Logged orderID should match returned orderID"
            assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
            assert(logMakeOrder["market"] == marketID), "Logged market should match input"
            assert(logMakeOrder["sender"] == address1), "Logged sender should match input"
        def test_ask_withShares():
            contracts._ContractLoader__state.mine(1)
            orderType = 2                   # ask
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createBinaryMarket(eventID)
            buyCompleteSets(marketID, fix(10))
            fxpAmount = fix(9)
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
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
            assert(logMakeOrder["_event_type"] == "logMakeOrder"), "Should emit a logMakeOrder event"
            assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
            assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
            assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
            assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
            assert(logMakeOrder["orderID"] == orderID), "Logged orderID should match returned orderID"
            assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
            assert(logMakeOrder["market"] == marketID), "Logged market should match input"
            assert(logMakeOrder["sender"] == address1), "Logged sender should match input"
        def test_ask_withPartialShares():
            contracts._ContractLoader__state.mine(1)
            orderType = 2                   # ask
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createBinaryMarket(eventID)
            buyCompleteSets(marketID, fix(10))
            fxpAmount = fix(12)
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
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
            assert(logMakeOrder["_event_type"] == "logMakeOrder"), "Should emit a logMakeOrder event"
            assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
            assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
            assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
            assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
            assert(logMakeOrder["orderID"] == orderID), "Logged orderID should match returned orderID"
            assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
            assert(logMakeOrder["market"] == marketID), "Logged market should match input"
            assert(logMakeOrder["sender"] == address1), "Logged sender should match input"
        def test_exceptions():
            contracts._ContractLoader__state.mine(1)
            orderType = 1                   # bid
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 1
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createBinaryMarket(eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, fix(10000), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
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
            buyCompleteSets(marketID, fix(1))
            contracts._ContractLoader__state.mine(1)
            try:
                raise Exception(contracts.makeOrder.publicMakeOrder(2, fxpAmount, fix(3), marketID, outcomeID, tradeGroupID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (with shares held) should fail if cost per share (price - minValue) is greater than the market's range"
            try:
                raise Exception(contracts.makeOrder.publicMakeOrder(2, 1, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (with shares held) should fail if order cost is below than the minimum order value"

            # makeOrder exceptions (post-placeBid/Ask)
            contracts._ContractLoader__state.mine(1)
            assert(contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1) != 0), "Order ID should be non-zero"
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

def test_CancelOrder():
    global contracts
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    def test_publicCancelOrder():
        def test_cancelBid():
            contracts._ContractLoader__state.mine(1)
            orderType = 1                   # bid
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createBinaryMarket(eventID)
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
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createBinaryMarket(eventID)
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
            orderType = 1                   # bid
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent()
            marketID = createBinaryMarket(eventID)
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

def runtests():
    test_Cash()
    test_ShareTokens()
    test_CreateEvent()
    test_CreateMarket()
    test_CompleteSets()
    test_MakeOrder()
    test_CancelOrder()
    test_Wallet()

if __name__ == '__main__':
    runtests()
