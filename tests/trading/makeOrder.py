#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

shareTokenContractTranslator = ethereum.abi.ContractTranslator('[{"constant": false, "type": "function", "name": "allowance(address,address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "address", "name": "spender"}]}, {"constant": false, "type": "function", "name": "approve(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "balanceOf(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "address"}]}, {"constant": false, "type": "function", "name": "changeTokens(int256,int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "trader"}, {"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "createShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "destroyShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "getDecimals()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getName()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getSymbol()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "modifySupply(int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "setController(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "newController"}]}, {"constant": false, "type": "function", "name": "suicideFunds(address)", "outputs": [], "inputs": [{"type": "address", "name": "to"}]}, {"constant": false, "type": "function", "name": "totalSupply()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "transfer(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "transferFrom(address,address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "from"}, {"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval(address,address,uint256)"}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer(address,address,uint256)"}, {"inputs": [{"indexed": false, "type": "int256", "name": "from"}, {"indexed": false, "type": "int256", "name": "to"}, {"indexed": false, "type": "int256", "name": "value"}, {"indexed": false, "type": "int256", "name": "senderBalance"}, {"indexed": false, "type": "int256", "name": "sender"}, {"indexed": false, "type": "int256", "name": "spenderMaxValue"}], "type": "event", "name": "echo(int256,int256,int256,int256,int256,int256)"}]')

def test_MakeOrder(contracts):
    t = contracts._ContractLoader__tester
    address1 = long(t.a1.encode("hex"), 16)
    def test_usingMarketType(marketType):
        def test_publicMakeOrder():
            def test_bid():
                contracts._ContractLoader__state.mine(1)
                orderType = 1 # bid
                fxpAmount = utils.fix(1)
                fxpPrice = utils.fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = utils.createEventType(contracts, marketType)
                marketID = utils.createMarket(contracts, eventID)
                assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
                makerInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                with iocapture.capture() as captured:
                    orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
                    logged = captured.stdout
                logMakeOrder = utils.parseCapturedLogs(logged)[-1]
                assert(orderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(orderID)
                assert(len(order) == 12), "Order array length should be 12"
                assert(order[0] == orderID), "order[0] should be the order ID"
                assert(order[1] == orderType), "order[1] should be the order type"
                assert(order[2] == marketID), "order[2] should be the market ID"
                assert(order[3] == fxpAmount), "order[3] should be the amount of the order"
                assert(order[4] == fxpPrice), "order[4] should be the order's price"
                assert(order[5] == address1), "order[5] should be the sender's address"
                assert(order[6] == contracts._ContractLoader__state.block.number), "order[6] should be the current block number"
                assert(order[7] == outcomeID), "order[6] should be the outcome ID"
                assert(order[8] == int(utils.unfix(fxpAmount*(fxpPrice - contracts.events.getMinValue(eventID))))), "order[8] should be the amount of money escrowed"
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
                outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                contracts._ContractLoader__state.mine(1)
                assert(contracts.cash.publicDepositEther(value=utils.fix(100), sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
                assert(contracts.cash.publicDepositEther(value=utils.fix(100), sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
                orderType = 1 # bid
                fxpAmount = 1200000000000000000 # fixed-point 1.2
                fxpPrice = utils.fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = utils.createEventType(contracts, marketType)
                marketID = utils.createMarket(contracts, eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                # 1. Account 1: buy complete sets
                contracts._ContractLoader__state.mine(1)
                utils.buyCompleteSets(contracts, marketID, fxpAmount)
                assert(outcomeShareContractWrapper.balanceOf(outcomeOneShareContract, t.a1) == fxpAmount), "Account 1 should have fxpAmount shares of outcome 1"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a1) == fxpAmount), "Account 1 should have fxpAmount shares of outcome 2"
                assert(outcomeShareContractWrapper.balanceOf(outcomeOneShareContract, t.a2) == 0), "Account 2 should have 0 shares of outcome 2"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a2) == 0), "Account 2 should have 0 shares of outcome 2"
                # 2. Account 1: make ask order for a single outcome (outcome 2)
                contracts._ContractLoader__state.mine(1)
                fxpAllowance = utils.fix(12)
                abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend outcome 2 shares from account 1"
                assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"
                contracts._ContractLoader__state.mine(1)
                askOrderID = contracts.makeOrder.publicMakeOrder(2, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
                assert(askOrderID != 0), "Order ID should be non-zero"
                # 3. Account 2: take account 1's ask order for outcome 2
                contracts._ContractLoader__state.mine(1)
                assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
                contracts._ContractLoader__state.mine(1)
                fxpAmountTakerWants = fxpAmount
                orderHash = contracts.orders.makeOrderHash(marketID, outcomeID, 2, sender=t.k2)
                assert(contracts.orders.commitOrder(orderHash, sender=t.k2) == 1), "Commit to market/outcome/direction"
                contracts._ContractLoader__state.mine(1)
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a1) == 0), "Account 1 should have 0 shares of outcome 2"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a2) == 0), "Account 2 should have 0 shares of outcome 2"
                assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
                contracts._ContractLoader__state.mine(1)
                fxpAmountRemaining = contracts.takeOrder.publicTakeOrder(askOrderID, fxpAmountTakerWants, sender=t.k2)
                assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a1) == 0), "Account 1 should have 0 shares of outcome 2"
                assert(outcomeShareContractWrapper.balanceOf(outcomeTwoShareContract, t.a2) == fxpAmount), "Account 2 should have fxpAmount shares of outcome 2"
                # 4. Account 1: make bid order for outcome 2
                contracts._ContractLoader__state.mine(1)
                fxpBidAmount = 900000000000000000 # fixed-point 0.9
                assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
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
                logMakeOrder = utils.parseCapturedLogs(logged)[-1]
                assert(bidOrderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(bidOrderID)
                assert(len(order) == 12), "Order array length should be 12"
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
                fxpAmount = utils.fix(1)
                fxpPrice = utils.fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = utils.createEventType(contracts, marketType)
                marketID = utils.createMarket(contracts, eventID)
                assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
                makerInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                with iocapture.capture() as captured:
                    orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
                    logged = captured.stdout
                logMakeOrder = utils.parseCapturedLogs(logged)[-1]
                assert(orderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(orderID)
                assert(len(order) == 12), "Order array length should be 12"
                assert(order[0] == orderID), "order[0] should be the order ID"
                assert(order[1] == orderType), "order[1] should be the order type"
                assert(order[2] == marketID), "order[2] should be the market ID"
                assert(order[3] == fxpAmount), "order[3] should be the amount of the order"
                assert(order[4] == fxpPrice), "order[4] should be the order's price"
                assert(order[5] == address1), "order[5] should be the sender's address"
                assert(order[6] == contracts._ContractLoader__state.block.number), "order[6] should be the current block number"
                assert(order[7] == outcomeID), "order[6] should be the outcome ID"
                assert(order[8] == int(utils.unfix(fxpAmount*(contracts.events.getMaxValue(eventID) - fxpPrice)))), "order[8] should be the amount of money escrowed"
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
                outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                contracts._ContractLoader__state.mine(1)
                orderType = 2                   # ask
                fxpAmount = utils.fix(1)
                fxpPrice = utils.fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = utils.createEventType(contracts, marketType)
                marketID = utils.createMarket(contracts, eventID)
                utils.buyCompleteSets(contracts, marketID, utils.fix(10))
                fxpAmount = utils.fix(9)
                fxpAllowance = utils.fix(12)
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
                logMakeOrder = utils.parseCapturedLogs(logged)[-1]
                assert(orderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(orderID)
                assert(len(order) == 12), "Order array length should be 12"
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
                outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                contracts._ContractLoader__state.mine(1)
                orderType = 2                   # ask
                fxpAmount = utils.fix(1)
                fxpPrice = utils.fix("1.6")
                outcomeID = 2
                tradeGroupID = 42
                eventID = utils.createEventType(contracts, marketType)
                marketID = utils.createMarket(contracts, eventID)
                utils.buyCompleteSets(contracts, marketID, utils.fix(10))
                fxpAmount = utils.fix(12)
                fxpAllowance = utils.fix(120)
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
                logMakeOrder = utils.parseCapturedLogs(logged)[-1]
                assert(orderID != 0), "Order ID should be non-zero"
                order = contracts.orders.getOrder(orderID)
                assert(len(order) == 12), "Order array length should be 12"
                assert(order[0] == orderID), "order[0] should be the order ID"
                assert(order[1] == orderType), "order[1] should be the order type"
                assert(order[2] == marketID), "order[2] should be the market ID"
                assert(order[3] == fxpAmount), "order[3] should be the amount of the order"
                assert(order[4] == fxpPrice), "order[4] should be the order's price"
                assert(order[5] == address1), "order[5] should be the sender's address"
                assert(order[6] == contracts._ContractLoader__state.block.number), "order[6] should be the current block number"
                assert(order[7] == outcomeID), "order[6] should be the outcome ID"
                assert(order[8] == int(utils.unfix(utils.fix(2)*(contracts.events.getMaxValue(eventID) - fxpPrice)))), "order[8] should be the amount of money escrowed"
                assert(order[9] == utils.fix(10)), "order[9] should be the number of shares escrowed"
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
                outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                contracts._ContractLoader__state.mine(1)
                orderType = 1 # bid
                fxpAmount = utils.fix(1)
                fxpPrice = utils.fix("1.6")
                outcomeID = 1
                tradeGroupID = 42
                eventID = utils.createBinaryEvent(contracts)
                marketID = utils.createMarket(contracts, eventID)
                makerInitialCash = contracts.cash.balanceOf(t.a1)
                marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))

                # Permissions exceptions
                contracts._ContractLoader__state.mine(1)
                try:
                    raise Exception(contracts.makeOrder.makeOrder(t.a1, orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
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
                    raise Exception(contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID - 1, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder should fail if market ID is not valid"
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(3, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder should fail if order type is not 1 (bid) or 2 (ask)"

                # placeBid exceptions
                contracts._ContractLoader__state.mine(1)
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(1, fxpAmount, utils.fix(3), marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder bid should fail if order cost per share is greater than the market's range"
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(1, 1, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder bid should fail if order cost is below than the minimum order value"

                # placeAsk exceptions
                contracts._ContractLoader__state.mine(1)
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(2, fxpAmount, 1, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (without shares) should fail if order cost per share (maxValue - price) is greater than the market's range"
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(2, 1, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (without shares) should fail if order cost is below than the minimum order value"
                utils.buyCompleteSets(contracts, marketID, utils.fix(2))
                contracts._ContractLoader__state.mine(1)
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(2, fxpAmount, utils.fix(3), marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (with shares held) should fail if cost per share (price - minValue) is greater than the market's range"
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(2, 1, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
                except Exception as exc:
                    assert(isinstance(exc, ethereum.tester.TransactionFailed)), "publicMakeOrder ask (with shares held) should fail if order cost is below than the minimum order value"

                contracts._ContractLoader__state.mine(1)
                assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(100), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
                fxpAllowance = utils.fix(12)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 1)"
                assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"
                contracts._ContractLoader__state.mine(1)
                assert(contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1) != 0), "Order ID should be non-zero"

                # makeOrder exceptions (post-placeBid/Ask)
                try:
                    raise Exception(contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, 0, 0, tradeGroupID, sender=t.k1))
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

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_MakeOrder(contracts)
