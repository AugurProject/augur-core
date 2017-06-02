#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

shareTokenContractTranslator = ethereum.abi.ContractTranslator('[{"constant": false, "type": "function", "name": "allowance(address,address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "address", "name": "spender"}]}, {"constant": false, "type": "function", "name": "approve(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "balanceOf(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "address"}]}, {"constant": false, "type": "function", "name": "changeTokens(int256,int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "trader"}, {"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "createShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "destroyShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "getDecimals()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getName()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getSymbol()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "modifySupply(int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "setController(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "newController"}]}, {"constant": false, "type": "function", "name": "suicideFunds(address)", "outputs": [], "inputs": [{"type": "address", "name": "to"}]}, {"constant": false, "type": "function", "name": "totalSupply()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "transfer(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "transferFrom(address,address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "from"}, {"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval(address,address,uint256)"}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer(address,address,uint256)"}, {"inputs": [{"indexed": false, "type": "int256", "name": "from"}, {"indexed": false, "type": "int256", "name": "to"}, {"indexed": false, "type": "int256", "name": "value"}, {"indexed": false, "type": "int256", "name": "senderBalance"}, {"indexed": false, "type": "int256", "name": "sender"}, {"indexed": false, "type": "int256", "name": "spenderMaxValue"}], "type": "event", "name": "echo(int256,int256,int256,int256,int256,int256)"}]')

def test_TakeAskOrder(contracts):
    t = contracts._ContractLoader__tester
    def test_usingMarketType(marketType):
        def test_takeAskOrder_makerEscrowedCash():
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            outcomeID = 2
            eventID = utils.createEventType(contracts, marketType)
            marketID = utils.createMarket(contracts, eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
            assert(contracts.cash.approve(contracts.takeAskOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeAskOrder contract to spend cash from account 2"
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
            fxpOrderAmount = utils.fix(1)
            fxpPrice = utils.fix("1.6")
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
            fxpAmountTakerWants = utils.fix(7)
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
            outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
            contracts._ContractLoader__state.mine(1)
            fxpEtherDepositValue = utils.fix(100)
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to account 1 should succeed"
            assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k2) == 1), "publicDepositEther to account 2 should succeed"
            contracts._ContractLoader__state.mine(1)
            eventID = utils.createEventType(contracts, marketType)
            marketID = utils.createMarket(contracts, eventID)
            outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
            outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
            outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
            outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)

            # 1. Maker buys complete sets
            fxpNumCompleteSets = utils.fix(10)
            utils.buyCompleteSets(contracts, marketID, fxpNumCompleteSets)
            fxpAllowance = utils.fix(12)
            outcomeID = 2
            makerInitialCash = contracts.cash.balanceOf(t.a1)
            makerInitialShares = contracts.markets.getParticipantSharesPurchased(marketID, t.a1, outcomeID)
            marketInitialCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
            marketInitialTotalShares = contracts.markets.getTotalSharesPurchased(marketID)
            contracts._ContractLoader__state.mine(1)
            outcomeShareContract = contracts.markets.getOutcomeShareContract(marketID, outcomeID)
            assert(int(contracts._ContractLoader__state.send(t.k1, outcomeShareContract, 0, shareTokenContractTranslator.encode("approve", [contracts.makeOrder.address, fxpAllowance])).encode("hex"), 16) == 1), "Approve makeOrder contract to spend shares from the user's account (account 1)"
            assert(outcomeShareContractWrapper.allowance(outcomeShareContract, t.a1, contracts.makeOrder.address) == fxpAllowance), "makeOrder contract's allowance should be equal to the amount approved"
            assert(contracts.cash.approve(contracts.makeOrder.address, utils.fix(10), sender=t.k1) == 1), "Approve makeOrder contract to spend cash from account 1"
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
            fxpOrderAmount = utils.fix(9)
            fxpPrice = utils.fix("1.6")
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
            fxpAmountTakerWants = utils.fix(7)
            assert(contracts.cash.approve(contracts.takeAskOrder.address, utils.fix(10), sender=t.k2) == 1), "Approve takeAskOrder contract to spend cash from account 2"
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

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_TakeAskOrder(contracts)
