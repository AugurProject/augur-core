#!/usr/bin/env python
'''
Trading tests:
functions/bidAndAsk.se -> makeOrder.se + cancelOrder.se
functions/cash.se
functions/claimMarketProceeds.se
functions/completeSets.se
functions/createEvent.se
functions/createMarket.se
functions/fillAskLibrary.se
functions/fillBidLibrary.se
functions/marketModifiers.se
functions/offChainTrades.se
functions/oneWinningOutcomePayouts.se
functions/shareTokens.se
functions/trade.se
functions/tradeAvailableOrders.se
functions/twoWinningOutcomePayouts.se
functions/wallet.se
'''

from __future__ import division
import ethereum
import os
import json
import iocapture
from load_contracts import ContractLoader

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

def createBinaryEvent(contracts, s, t):
    global eventCreationCounter
    contracts.cash.depositEther(value=fix(10000), sender=t.k1)
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

def createBinaryMarket(contracts, s, t, eventID):
    contracts.cash.approve(contracts.createMarket.address, fix(10000), sender=t.k1)
    branch = 1010101
    fxpTradingFee = 20000000000000001
    tag1 = 123
    tag2 = 456
    tag3 = 789
    extraInfo = "rabble rabble rabble"
    currency = contracts.cash.address
    return contracts.createMarket.publicCreateMarket(branch, fxpTradingFee, eventID, tag1, tag2, tag3, extraInfo, currency, sender=t.k1, value=fix(10000))

def test_Cash(path):
    t = ethereum.tester
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract(path)
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    initialEtherBalance2 = s.block.get_balance(t.a2)
    def test_init():
        assert(hex2str(c.getName()) == '4361736800000000000000000000000000000000000000000000000000000000'), "currency name"
        assert(c.getDecimals() == 18), "number of decimals"
        assert(hex2str(c.getSymbol()) == '4341534800000000000000000000000000000000000000000000000000000000'), "currency symbol"
    def test_depositEther():
        s.mine(1)
        assert(c.depositEther(value=100, sender=t.k1) == 1), "deposit ether"
        assert(c.balanceOf(t.a1) == 100), "balance equal to deposit"
        assert(c.totalSupply() == 100), "totalSupply equal to deposit"
    def test_withdrawEther():
        s.mine(1)
        assert(c.getInitiated(sender=t.k1) == 0), "withdraw not initiated"
        assert(c.withdrawEther(t.a2, 110, sender=t.k1) == 0), "withdraw fails, insufficient funds"
        assert(c.withdrawEther(t.a2, 30, sender=t.k1)), "initiate withdrawal"
        assert(c.getInitiated(sender=t.k1) == s.block.timestamp), "withdraw initiated"
        try:
            raise Exception(c.withdrawEther(t.a2, 30, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "withdraw should throw (3 days haven't passed)"
        s.block.timestamp += 259199
        try:
            raise Exception(c.withdrawEther(t.a2, 30, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdraw should throw (3 days still haven't passed)"
        s.block.timestamp += 1
        assert(c.withdrawEther(t.a2, 30, sender=t.k1)), "withdraw should succeed"
        assert(c.balanceOf(t.a1) == 70), "decrease sender's balance by 30"
        assert(c.balanceOf(t.a2) == 0), "receiver's cash balance still equals 0"
        assert(s.block.get_balance(t.a2) - initialEtherBalance2 == 30), "receiver's ether balance increased by 30"
        assert(c.totalSupply() == 70), "total supply decreased by 30"
        try:
            raise Exception(c.withdrawEther(t.a2, -10, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative withdraw should throw"
        assert(c.getInitiated(sender=t.k1) == 0), "withdraw no longer initiated"
    def test_transfer():
        s.mine(1)
        with iocapture.capture() as captured:
            retval = c.transfer(t.a2, 5, sender=t.k1)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transfer 5 cash to a2"
        assert(logged["_event_type"] == "Transfer")
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
        assert(logged["value"] == 5)
        assert(c.balanceOf(t.a1) == 65), "balance of a1 decreased by 5"
        assert(c.balanceOf(t.a2) == 5), "balance of a2 increased by 5"
        assert(c.totalSupply() == 70), "totalSupply unchanged"
        try:
            raise Exception(c.transfer(t.a2, 70, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should throw if insufficient funds"
        try:
            raise Exception(c.transfer(t.a2, -5, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative transfer should throw"
        with iocapture.capture() as captured:
            retval = c.transfer(t.a2, 0, sender=t.k1)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transferFrom should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
        assert(logged["value"] == 0)
        assert(c.balanceOf(t.a1) == 65), "balance of a1 unchanged"
        assert(c.balanceOf(t.a2) == 5), "balance of a2 unchanged"
        assert(c.totalSupply() == 70), "totalSupply unchanged"
    def test_transferFrom():
        try:
            raise Exception(c.transferFrom(t.a1, t.a2, 7, sender=t.k2))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transferFrom should throw, msg.sender is not approved"
    def test_approve():
        s.mine(1)
        assert(c.allowance(t.a1, t.a2) == 0), "initial allowance is 0"
        with iocapture.capture() as captured:
            retval = c.approve(t.a2, 10, sender=t.k1)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "approve a2 to spend 10 cash from a1"
        assert(logged["_event_type"] == "Approval")
        assert(logged["owner"] == address1)
        assert(logged["spender"] == address2)
        assert(logged["value"] == 10)
        assert(c.allowance(t.a1, t.a2) == 10), "allowance is 10 after approval"
        with iocapture.capture() as captured:
            retval = c.transferFrom(t.a1, t.a2, 7, sender=t.k2)
            logged = parseCapturedLogs(captured.stdout)[-1]
        assert(retval == 1), "transferFrom should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
        assert(logged["value"] == 7)
    def test_commitSuicide():
        try:
            raise Exception(c.commitSuicide(sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "commit suicide should fail from non-whitelisted address"
    test_init()
    test_depositEther()
    test_withdrawEther()
    test_transfer()
    test_transferFrom()
    test_approve()
    test_commitSuicide()

# TODO update create event tests pending final review of contract
def test_CreateEvent(contracts, s, t):
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
        assert(contracts.cash.depositEther(value=fix(10000), sender=t.k1) == 1), "Convert ether to cash"
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
        assert(eventID > 0), "Event created"
        assert(contracts.info.getDescription(eventID) == description), "Description matches input"
        assert(contracts.events.getExpiration(eventID) == expDate), "Expiration date matches input"
        assert(contracts.events.getMinValue(eventID) == fxpMinValue), "Min value matches input"
        assert(contracts.events.getMaxValue(eventID) == fxpMaxValue), "Max value matches input"
        assert(contracts.events.getNumOutcomes(eventID) == numOutcomes), "Number of outcomes matches input"
        assert(contracts.events.getEventResolution(eventID) == resolution), "Resolution matches input"
    test_checkEventCreationPreconditions()
    test_publicCreateEvent()

# TODO update create market tests pending final review of contract
def test_CreateMarket(contracts, s, t):
    def test_publicCreateMarket():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.depositEther(value=fix(10000), sender=t.k1) == 1), "Convert ether to cash"
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
        assert(marketID > 0)
        assert(contracts.markets.getTradingFee(marketID) == fxpTradingFee), "Trading fee matches input"
        assert(contracts.markets.getMarketEvent(marketID) == eventID), "Market event matches input"
        assert(contracts.markets.getTags(marketID) == [tag1, tag2, tag3]), "Tags array matches input"
        assert(contracts.markets.getTopic(marketID)), "Topic matches input tag1"
        assert(contracts.markets.getExtraInfo(marketID) == extraInfo), "Extra info matches input"
    test_publicCreateMarket()

def buyCompleteSets(contracts, s, t, marketID, fxpAmount):
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

def test_CompleteSets(contracts, s, t):
    address1 = long(t.a1.encode("hex"), 16)
    def test_publicBuyCompleteSets():
        contracts._ContractLoader__state.mine(1)
        eventID = createBinaryEvent(contracts, s, t)
        marketID = createBinaryMarket(contracts, s, t, eventID)
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
            eventID = createBinaryEvent(contracts, s, t)
            marketID = createBinaryMarket(contracts, s, t, eventID)
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
                raise Exception(contracts.completeSets.publicBuyCompleteSets(marketID, -1*fxpAmount, sender=t.k1))
            except Exception as exc:
                assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicBuyCompleteSets should fail if fxpAmount is negative"
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
        eventID = createBinaryEvent(contracts, s, t)
        marketID = createBinaryMarket(contracts, s, t, eventID)
        buyCompleteSets(contracts, s, t, marketID, fix(10))
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
    test_publicBuyCompleteSets()
    test_publicSellCompleteSets()

def test_MakeOrder(contracts, s, t):
    address1 = long(t.a1.encode("hex"), 16)
    def test_publicMakeOrder():
        def test_bid():
            contracts._ContractLoader__state.mine(1)
            orderType = 1                   # bid
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent(contracts, s, t)
            marketID = createBinaryMarket(contracts, s, t, eventID)
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
            eventID = createBinaryEvent(contracts, s, t)
            marketID = createBinaryMarket(contracts, s, t, eventID)
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
            eventID = createBinaryEvent(contracts, s, t)
            marketID = createBinaryMarket(contracts, s, t, eventID)
            buyCompleteSets(contracts, s, t, marketID, fix(10))
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
            eventID = createBinaryEvent(contracts, s, t)
            marketID = createBinaryMarket(contracts, s, t, eventID)
            buyCompleteSets(contracts, s, t, marketID, fix(10))
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
            eventID = createBinaryEvent(contracts, s, t)
            marketID = createBinaryMarket(contracts, s, t, eventID)
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
            buyCompleteSets(contracts, s, t, marketID, fix(1))
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
            assert(contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1) > 0), "Order ID should be non-zero"
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

def test_CancelOrder(contracts, s, t):
    address1 = long(t.a1.encode("hex"), 16)
    def test_publicCancelOrder():
        def test_cancelBid():
            contracts._ContractLoader__state.mine(1)
            orderType = 1                   # bid
            fxpAmount = 1000000000000000000 # fixed-point 1
            fxpPrice = 1600000000000000000  # fixed-point 1.6
            outcomeID = 2
            tradeGroupID = 42
            eventID = createBinaryEvent(contracts, s, t)
            marketID = createBinaryMarket(contracts, s, t, eventID)
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
            eventID = createBinaryEvent(contracts, s, t)
            marketID = createBinaryMarket(contracts, s, t, eventID)
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
            eventID = createBinaryEvent(contracts, s, t)
            marketID = createBinaryMarket(contracts, s, t, eventID)
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
    src = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'src')
    contracts = ContractLoader(src, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'])
    state = contracts._ContractLoader__state
    t = contracts._ContractLoader__tester
    test_Cash(os.path.join(src, 'functions', 'cash.se'))
    test_CreateEvent(contracts, state, t)
    test_CreateMarket(contracts, state, t)
    test_CompleteSets(contracts, state, t)
    test_MakeOrder(contracts, state, t)
    test_CancelOrder(contracts, state, t)

if __name__ == '__main__':
    runtests()
