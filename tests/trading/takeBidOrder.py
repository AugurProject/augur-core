#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

shareTokenContractTranslator = ethereum.abi.ContractTranslator('[{"constant": false, "type": "function", "name": "allowance(address,address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "address", "name": "spender"}]}, {"constant": false, "type": "function", "name": "approve(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "balanceOf(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "address"}]}, {"constant": false, "type": "function", "name": "changeTokens(int256,int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "trader"}, {"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "createShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "destroyShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "getDecimals()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getName()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getSymbol()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "modifySupply(int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "setController(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "newController"}]}, {"constant": false, "type": "function", "name": "suicideFunds(address)", "outputs": [], "inputs": [{"type": "address", "name": "to"}]}, {"constant": false, "type": "function", "name": "totalSupply()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "transfer(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "transferFrom(address,address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "from"}, {"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval(address,address,uint256)"}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer(address,address,uint256)"}, {"inputs": [{"indexed": false, "type": "int256", "name": "from"}, {"indexed": false, "type": "int256", "name": "to"}, {"indexed": false, "type": "int256", "name": "value"}, {"indexed": false, "type": "int256", "name": "senderBalance"}, {"indexed": false, "type": "int256", "name": "sender"}, {"indexed": false, "type": "int256", "name": "spenderMaxValue"}], "type": "event", "name": "echo(int256,int256,int256,int256,int256,int256)"}]')

def test_TakeBidOrder(contracts):
    t = contracts._ContractLoader__tester
    def test_usingMarketType(marketType):
        def test_takeBidOrder_makerEscrowedCash_takerWithoutShares():
            global shareTokenContractTranslator
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            fxpOrderAmount = utils.fix(2)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            fxpAllowance = utils.fix(10)
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
            fxpAmountTakerWants = utils.fix(3)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 1, sender=t.k2)
            assert(contracts.cash.approve(contracts.takeBidOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
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
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)

            # 1. Maker buys complete sets, then transfers shares of outcome 2.
            contracts._ContractLoader__state.mine(1)
            fxpNumCompleteSets = utils.fix(10)
            utils.buyCompleteSets(contracts, marketID, fxpNumCompleteSets)
            contracts._ContractLoader__state.mine(1)
            transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
            assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
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
            fxpOrderAmount = utils.fix(2)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            fxpAllowance = utils.fix(10)
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
            fxpAmountTakerWants = utils.fix(3)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 1, sender=t.k2)
            contracts._ContractLoader__state.mine(1)
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeTwoShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.takeBidOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve takeBidOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a2, contracts.takeBidOrder.address) == fxpAllowance), "takeBidOrder contract's allowance should be equal to the amount approved"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve takeBidOrder contract to spend cash from account 1"
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
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            fxpOrderAmount = utils.fix(2)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)

            # 1. Taker buys a complete set, then transfers outcome 1, leaving taker with shares of outcome 2 only.
            contracts._ContractLoader__state.mine(1)
            fxpOutcomeTwoShares = utils.fix(10)
            utils.buyCompleteSets(contracts, marketID, fxpOutcomeTwoShares, sender=t.k2)
            contracts._ContractLoader__state.mine(1)
            transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpOutcomeTwoShares])
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"

            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            fxpAllowance = utils.fix(10)
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
            fxpAmountTakerWants = utils.fix(3)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 1, sender=t.k2)
            assert(contracts.cash.approve(contracts.takeBidOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
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
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            eventID = utils.createBinaryEvent(contracts)
            marketID = utils.createMarket(contracts, eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)

            # 1. Taker buys a complete set, then transfers outcome 1, leaving taker with shares of outcome 2 only.
            contracts._ContractLoader__state.mine(1)
            fxpOutcomeTwoShares = utils.fix(10)
            utils.buyCompleteSets(contracts, marketID, fxpOutcomeTwoShares, sender=t.k2)
            contracts._ContractLoader__state.mine(1)
            transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpOutcomeTwoShares])
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer taker's shares of outcome 1 to address 0"

            # 2. Maker buys complete sets, then transfers shares of outcome 2.
            contracts._ContractLoader__state.mine(1)
            fxpNumCompleteSets = utils.fix(10)
            utils.buyCompleteSets(contracts, marketID, fxpNumCompleteSets)
            contracts._ContractLoader__state.mine(1)
            transferSharesAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
            assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, transferSharesAbiEncodedData).encode("hex"), 16) == 1), "Transfer maker's shares of outcome 2 to address 0"
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
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
            fxpOrderAmount = utils.fix(2)
            fxpPrice = utils.fix("1.6")
            outcomeID = 2
            tradeGroupID = 42
            fxpAllowance = utils.fix(10)
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
            fxpAmountTakerWants = utils.fix(3)
            tradeHash = contracts.orders.makeOrderHash(marketID, outcomeID, 1, sender=t.k2)
            contracts._ContractLoader__state.mine(1)
            assert(int(contracts._ContractLoader__state.send(t.k2, outcomeTwoShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.takeBidOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve takeBidOrder contract to spend shares from the user's account (account 2)"
            assert(outcomeShareContractWrapper.allowance(outcomeTwoShareContract, t.a2, contracts.takeBidOrder.address) == fxpAllowance), "takeBidOrder contract's allowance should be equal to the amount approved"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeBidOrder contract to spend cash from account 2"
            assert(contracts.cash.approve(contracts.takeBidOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve takeBidOrder contract to spend cash from account 1"
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

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_TakeBidOrder(contracts)
