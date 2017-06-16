#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

shareTokenContractTranslator = ethereum.abi.ContractTranslator('[{"constant": false, "type": "function", "name": "allowance(address,address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "address", "name": "spender"}]}, {"constant": false, "type": "function", "name": "approve(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "balanceOf(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "address"}]}, {"constant": false, "type": "function", "name": "changeTokens(int256,int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "trader"}, {"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "createShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "destroyShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "getDecimals()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getName()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getSymbol()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "modifySupply(int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "setController(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "newController"}]}, {"constant": false, "type": "function", "name": "suicideFunds(address)", "outputs": [], "inputs": [{"type": "address", "name": "to"}]}, {"constant": false, "type": "function", "name": "totalSupply()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "transfer(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "transferFrom(address,address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "from"}, {"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval(address,address,uint256)"}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer(address,address,uint256)"}, {"inputs": [{"indexed": false, "type": "int256", "name": "from"}, {"indexed": false, "type": "int256", "name": "to"}, {"indexed": false, "type": "int256", "name": "value"}, {"indexed": false, "type": "int256", "name": "senderBalance"}, {"indexed": false, "type": "int256", "name": "sender"}, {"indexed": false, "type": "int256", "name": "spenderMaxValue"}], "type": "event", "name": "echo(int256,int256,int256,int256,int256,int256)"}]')

def test_Trade(contracts):
    t = contracts._ContractLoader__tester
    def test_publicTakeBestOrder():
        def test_takeBestAskOrder():
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(20)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 2 # ask
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = int(fxpAmount / 10)
            fxpAmountRemaining = contracts.trade.publicTakeBestOrder(orderType, marketID, outcomeID, fxpAmountTakerWants, fxpPrice, sender=t.k2)
            assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        def test_takeBestBidOrder():
            global shareTokenContractTranslator
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(20)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            fxpAllowance = utils.fix(10)
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
            assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == utils.fix("0.6")), "Market's cash balance should be (price - 1)*amount"
            fxpAmountRemaining = contracts.trade.publicTakeBestOrder(orderType, marketID, outcomeID, fxpAmountTakerWants, fxpPrice, sender=t.k2)
            assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        test_takeBestAskOrder()
        test_takeBestBidOrder()

    def test_publicBuy():
        def test_publicBuy_takeOrder():
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(20)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 2 # ask
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = int(fxpAmount / 10)
            fxpAmountRemaining = contracts.trade.publicBuy(marketID, outcomeID, fxpAmountTakerWants, fxpPrice, tradeGroupID, sender=t.k2)
            assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        def test_publicBuy_makeOrder():
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            with iocapture.capture() as captured:
                fxpAmountRemaining = contracts.trade.publicBuy(marketID, outcomeID, fxpAmount, fxpPrice, tradeGroupID, sender=t.k1)
                logged = captured.stdout
            logMakeOrder = utils.parseCapturedLogs(logged)[-1]
            assert(fxpAmountRemaining == 0), "fxpAmountRemaining should be 0"
            orderID = logMakeOrder["orderID"]
            assert(orderID != 0), "Order ID should be non-zero"
            order = contracts.orders.getOrder(orderID, orderType, marketID, outcomeID)
            assert(len(order) == 13), "Order array length should be 13"
            assert(order[0] == orderID), "order[0] should be the order ID"
            assert(order[1] == orderType), "order[1] should be the order type"
            assert(order[2] == marketID), "order[2] should be the market ID"
            assert(order[3] == fxpAmount), "order[3] should be the amount of the order"
            assert(order[4] == fxpPrice), "order[4] should be the order's price"
            assert(order[5] == long(t.a1.encode("hex"), 16)), "order[5] should be the sender's address"
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
            assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
            assert(logMakeOrder["market"] == marketID), "Logged market should match input"
            assert(logMakeOrder["sender"] == long(t.a1.encode("hex"), 16)), "Logged sender should match input"
        def test_publicBuy_takeThenMakeOrder():
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(20)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 2 # ask
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve makeOrder contract to spend cash from account 2"
            assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            takerInitialCash = contracts.cash.balanceOf(t.a2)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            makeOrderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(makeOrderID != 0), "Order ID should be non-zero"
            assert(contracts.orders.getAmount(makeOrderID, orderType, marketID, outcomeID) == fxpAmount), "Ask order amount should be fxpAmount"
            contracts._ContractLoader__state.mine(1)
            fxpAmountToBuy = utils.fix("1.2")
            with iocapture.capture() as captured:
                fxpAmountRemaining = contracts.trade.publicBuy(marketID, outcomeID, fxpAmountToBuy, fxpPrice, tradeGroupID, sender=t.k2)
                logged = captured.stdout
            assert(contracts.orders.getAmount(makeOrderID, orderType, marketID, outcomeID) == 0), "Ask order amount should be zero"
            logMakeOrder = utils.parseCapturedLogs(logged)[-1]
            assert(fxpAmountRemaining == 0), "fxpAmountRemaining should be 0"
            orderID = logMakeOrder["orderID"]
            assert(orderID != 0), "Order ID should be non-zero"
            order = contracts.orders.getOrder(orderID, 1, marketID, outcomeID)
            assert(len(order) == 13), "Order array length should be 13"
            assert(order[0] == orderID), "order[0] should be the order ID"
            assert(order[1] == 1), "order[1] should be the order type"
            assert(order[2] == marketID), "order[2] should be the market ID"
            assert(order[3] == fxpAmountToBuy - fxpAmount), "order[3] should be the amount of the order"
            assert(order[4] == fxpPrice), "order[4] should be the order's price"
            assert(order[5] == long(t.a2.encode("hex"), 16)), "order[5] should be the sender's address"
            assert(order[7] == outcomeID), "order[6] should be the outcome ID"
            assert(order[8] == int(utils.unfix((fxpAmountToBuy - fxpAmount)*(fxpPrice - contracts.events.getMinValue(eventID))))), "order[8] should be the amount of money escrowed"
            assert(order[9] == 0), "order[9] should be the number of shares escrowed"
            assert(logMakeOrder["_event_type"] == "MakeOrder"), "Should emit a MakeOrder event"
            assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
            assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
            assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
            assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
            assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
            assert(logMakeOrder["market"] == marketID), "Logged market should match input"
            assert(logMakeOrder["sender"] == long(t.a2.encode("hex"), 16)), "Logged sender should match input"
        def test_publicBuy_takeTwoOrders():
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(20)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 2 # ask
            fxpAmount1 = utils.fix(1)
            fxpAmount2 = utils.fix("0.4")
            fxpPrice1 = utils.fix("1.5")
            fxpPrice2 = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            orderID1 = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount1, fxpPrice1, marketID, outcomeID, tradeGroupID, sender=t.k1)
            contracts._ContractLoader__state.mine(1)
            orderID2 = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount2, fxpPrice2, marketID, outcomeID, tradeGroupID, sender=t.k1)
            contracts._ContractLoader__state.mine(1)
            assert(orderID1 != 0), "Order ID should be non-zero"
            assert(orderID2 != 0), "Order ID should be non-zero"
            fxpAmountToBuy = utils.fix("1.1")
            # should take all of the first order and 0.1 of the second order (0.3 remaining in 2nd order)
            fxpAmountRemaining = contracts.trade.publicBuy(marketID, outcomeID, fxpAmountToBuy, fxpPrice2, tradeGroupID, sender=t.k2)
            assert(fxpAmountRemaining == 0), "fxpAmountRemaining should be zero"
            assert(contracts.orders.getAmount(orderID1, orderType, marketID, outcomeID) == 0), "Order 1 amount should be zero"
            assert(contracts.orders.getAmount(orderID2, orderType, marketID, outcomeID) == utils.fix("0.3")), "Order 2 amount should be 0.3"
        test_publicBuy_takeOrder()
        test_publicBuy_makeOrder()
        test_publicBuy_takeThenMakeOrder()
        test_publicBuy_takeTwoOrders()

    def test_publicSell():
        def test_publicSell_takeOrder():
            global shareTokenContractTranslator
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(20)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            fxpAllowance = utils.fix(10)
            outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
            abiEncodedData = shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeShareContract, 0, abiEncodedData).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
            # place a bid order (escrow cash)
            orderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(orderID != 0), "Order ID should be non-zero"
            contracts._ContractLoader__state.mine(1)
            fxpAmountTakerWants = int(fxpAmount / 10)
            assert(contracts.cash.balanceOf(contracts.info.getWallet(marketID)) == utils.fix("0.6")), "Market's cash balance should be (price - 1)*amount"
            fxpAmountRemaining = contracts.trade.publicSell(marketID, outcomeID, fxpAmountTakerWants, fxpPrice, sender=t.k2)
            assert(fxpAmountRemaining == 0), "Amount remaining should be 0"
        def test_publicSell_makeOrder():
            contracts._ContractLoader__state.mine(1)
            orderType = 2 # ask
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash"
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            with iocapture.capture() as captured:
                fxpAmountRemaining = contracts.trade.publicSell(marketID, outcomeID, fxpAmount, fxpPrice, tradeGroupID, sender=t.k1)
                logged = captured.stdout
            logMakeOrder = utils.parseCapturedLogs(logged)[-1]
            assert(fxpAmountRemaining == 0), "fxpAmountRemaining should be 0"
            orderID = logMakeOrder["orderID"]
            assert(orderID != 0), "Order ID should be non-zero"
            order = contracts.orders.getOrder(orderID, orderType, marketID, outcomeID)
            assert(len(order) == 13), "Order array length should be 13"
            assert(order[0] == orderID), "order[0] should be the order ID"
            assert(order[1] == orderType), "order[1] should be the order type"
            assert(order[2] == marketID), "order[2] should be the market ID"
            assert(order[3] == fxpAmount), "order[3] should be the amount of the order"
            assert(order[4] == fxpPrice), "order[4] should be the order's price"
            assert(order[5] == long(t.a1.encode("hex"), 16)), "order[5] should be the sender's address"
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
            assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
            assert(logMakeOrder["market"] == marketID), "Logged market should match input"
            assert(logMakeOrder["sender"] == long(t.a1.encode("hex"), 16)), "Logged sender should match input"
        def test_publicSell_takeThenMakeOrder():
            global shareTokenContractTranslator
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(20)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve makeOrder contract to spend cash from account 2"
            assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            fxpAllowance = utils.fix(20)
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeOneShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeTwoShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeOneShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
            assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
            makeOrderID = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount, fxpPrice, marketID, outcomeID, tradeGroupID, sender=t.k1)
            assert(makeOrderID != 0), "Order ID should be non-zero"
            assert(contracts.orders.getAmount(makeOrderID, orderType, marketID, outcomeID) == fxpAmount), "Bid order amount should be fxpAmount"
            contracts._ContractLoader__state.mine(1)
            fxpAmountToSell = utils.fix("1.2")
            with iocapture.capture() as captured:
                fxpAmountRemaining = contracts.trade.publicSell(marketID, outcomeID, fxpAmountToSell, fxpPrice, tradeGroupID, sender=t.k2)
                logged = captured.stdout
            assert(contracts.orders.getAmount(makeOrderID, orderType, marketID, outcomeID) == 0), "Bid order amount should be zero"
            logMakeOrder = utils.parseCapturedLogs(logged)[-1]
            assert(fxpAmountRemaining == 0), "fxpAmountRemaining should be 0"
            orderID = logMakeOrder["orderID"]
            assert(orderID != 0), "Order ID should be non-zero"
            order = contracts.orders.getOrder(orderID, 2, marketID, outcomeID)
            assert(len(order) == 13), "Order array length should be 13"
            assert(order[0] == orderID), "order[0] should be the order ID"
            assert(order[1] == 2), "order[1] should be the order type"
            assert(order[2] == marketID), "order[2] should be the market ID"
            assert(order[3] == fxpAmountToSell - fxpAmount), "order[3] should be the amount of the order"
            assert(order[4] == fxpPrice), "order[4] should be the order's price"
            assert(order[5] == long(t.a2.encode("hex"), 16)), "order[5] should be the sender's address"
            assert(order[7] == outcomeID), "order[6] should be the outcome ID"
            assert(logMakeOrder["_event_type"] == "MakeOrder"), "Should emit a MakeOrder event"
            assert(logMakeOrder["tradeGroupID"] == tradeGroupID), "Logged tradeGroupID should match input"
            assert(logMakeOrder["fxpMoneyEscrowed"] == order[8]), "Logged fxpMoneyEscrowed should match amount in order"
            assert(logMakeOrder["fxpSharesEscrowed"] == order[9]), "Logged fxpSharesEscrowed should match amount in order"
            assert(logMakeOrder["timestamp"] == contracts._ContractLoader__state.block.timestamp), "Logged timestamp should match the current block timestamp"
            assert(logMakeOrder["outcome"] == outcomeID), "Logged outcome should match input"
            assert(logMakeOrder["market"] == marketID), "Logged market should match input"
            assert(logMakeOrder["sender"] == long(t.a2.encode("hex"), 16)), "Logged sender should match input"
        def test_publicSell_takeTwoOrders():
            global shareTokenContractTranslator
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(20)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            orderType = 1 # bid
            fxpAmount1 = utils.fix(1)
            fxpAmount2 = utils.fix("0.4")
            fxpPrice1 = utils.fix("1.5")
            fxpPrice2 = utils.fix("1.4")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeOrder contract to spend cash from account 2"
            fxpAllowance = utils.fix(20)
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeOneShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeTwoShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.takeOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve takeOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeOneShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
            assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a2, contracts.takeOrder.address) == fxpAllowance), "takeOrder contract's allowance should be equal to the amount approved"
            orderID1 = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount1, fxpPrice1, marketID, outcomeID, tradeGroupID, sender=t.k1)
            contracts._ContractLoader__state.mine(1)
            orderID2 = contracts.makeOrder.publicMakeOrder(orderType, fxpAmount2, fxpPrice2, marketID, outcomeID, tradeGroupID, sender=t.k1)
            contracts._ContractLoader__state.mine(1)
            assert(orderID1 != 0), "Order ID should be non-zero"
            assert(orderID2 != 0), "Order ID should be non-zero"
            fxpAmountToSell = utils.fix("1.1")
            # should take all of the first order and 0.1 of the second order (0.3 remaining in 2nd order)
            fxpAmountRemaining = contracts.trade.publicSell(marketID, outcomeID, fxpAmountToSell, fxpPrice2, tradeGroupID, sender=t.k2)
            assert(fxpAmountRemaining == 0), "fxpAmountRemaining should be zero"
            assert(contracts.orders.getAmount(orderID1, orderType, marketID, outcomeID) == 0), "Order 1 amount should be zero"
            assert(contracts.orders.getAmount(orderID2, orderType, marketID, outcomeID) == utils.fix("0.3")), "Order 2 amount should be 0.3"
        test_publicSell_takeOrder()
        test_publicSell_makeOrder()
        test_publicSell_takeThenMakeOrder()
        test_publicSell_takeTwoOrders()

    test_publicTakeBestOrder()
    test_publicBuy()
    test_publicSell()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_Trade(contracts)
