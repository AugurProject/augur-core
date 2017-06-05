#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

shareTokenContractTranslator = ethereum.abi.ContractTranslator('[{"constant": false, "type": "function", "name": "allowance(address,address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "address", "name": "spender"}]}, {"constant": false, "type": "function", "name": "approve(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "spender"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "balanceOf(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "address"}]}, {"constant": false, "type": "function", "name": "changeTokens(int256,int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "trader"}, {"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "createShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "destroyShares(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "owner"}, {"type": "uint256", "name": "fxpValue"}]}, {"constant": false, "type": "function", "name": "getDecimals()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getName()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "getSymbol()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "modifySupply(int256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "int256", "name": "amount"}]}, {"constant": false, "type": "function", "name": "setController(address)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "newController"}]}, {"constant": false, "type": "function", "name": "suicideFunds(address)", "outputs": [], "inputs": [{"type": "address", "name": "to"}]}, {"constant": false, "type": "function", "name": "totalSupply()", "outputs": [{"type": "int256", "name": "out"}], "inputs": []}, {"constant": false, "type": "function", "name": "transfer(address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"constant": false, "type": "function", "name": "transferFrom(address,address,uint256)", "outputs": [{"type": "int256", "name": "out"}], "inputs": [{"type": "address", "name": "from"}, {"type": "address", "name": "to"}, {"type": "uint256", "name": "value"}]}, {"inputs": [{"indexed": true, "type": "address", "name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Approval(address,address,uint256)"}, {"inputs": [{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address", "name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event", "name": "Transfer(address,address,uint256)"}, {"inputs": [{"indexed": false, "type": "int256", "name": "from"}, {"indexed": false, "type": "int256", "name": "to"}, {"indexed": false, "type": "int256", "name": "value"}, {"indexed": false, "type": "int256", "name": "senderBalance"}, {"indexed": false, "type": "int256", "name": "sender"}, {"indexed": false, "type": "int256", "name": "spenderMaxValue"}], "type": "event", "name": "echo(int256,int256,int256,int256,int256,int256)"}]')

def test_ClaimProceeds(contracts):
    t = contracts._ContractLoader__tester
    def test_BinaryOrCategoricalPayouts():
        def test_payoutBinaryOrCategoricalMarket():
            def test_binary():
                def test_userWithoutShares():
                    contracts._ContractLoader__state.mine(1)
                    eventID = utils.createBinaryEvent(contracts)
                    marketID = utils.createMarket(contracts, eventID)
                    outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                    outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                    outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                    outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                    contracts._ContractLoader__state.mine(1)
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                    outcomeID = 2
                    assert(contracts.events.setOutcome(eventID, utils.fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
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
                    outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                    contracts._ContractLoader__state.mine(1)
                    fxpEtherDepositValue = utils.fix(100)
                    assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                    contracts._ContractLoader__state.mine(1)
                    eventID = utils.createBinaryEvent(contracts)
                    marketID = utils.createMarket(contracts, eventID)
                    outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                    outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                    outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                    outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                    contracts._ContractLoader__state.mine(1)
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                    fxpNumCompleteSets = utils.fix(3)
                    utils.buyCompleteSets(contracts, marketID, fxpNumCompleteSets)
                    contracts._ContractLoader__state.mine(1)
                    transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                    assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                    outcomeID = 2
                    assert(contracts.events.setOutcome(eventID, utils.fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
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
                    eventID = utils.createCategoricalEvent(contracts, numOutcomes)
                    marketID = utils.createMarket(contracts, eventID)
                    outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                    outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                    outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                    outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                    contracts._ContractLoader__state.mine(1)
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                    outcomeID = 2
                    assert(contracts.events.setOutcome(eventID, utils.fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
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
                    outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                    contracts._ContractLoader__state.mine(1)
                    fxpEtherDepositValue = utils.fix(100)
                    assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                    contracts._ContractLoader__state.mine(1)
                    numOutcomes = 3
                    eventID = utils.createCategoricalEvent(contracts, numOutcomes)
                    marketID = utils.createMarket(contracts, eventID)
                    outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                    outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                    outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                    outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                    contracts._ContractLoader__state.mine(1)
                    contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                    fxpNumCompleteSets = utils.fix(3)
                    utils.buyCompleteSets(contracts, marketID, fxpNumCompleteSets)
                    contracts._ContractLoader__state.mine(1)
                    transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                    assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                    outcomeID = 2
                    assert(contracts.events.setOutcome(eventID, utils.fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
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
                outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                contracts._ContractLoader__state.mine(1)
                fxpEtherDepositValue = utils.fix(100)
                assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                contracts._ContractLoader__state.mine(1)
                eventID = utils.createBinaryEvent(contracts)
                marketID = utils.createMarket(contracts, eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                fxpNumCompleteSets = utils.fix(3)
                utils.buyCompleteSets(contracts, marketID, fxpNumCompleteSets)
                contracts._ContractLoader__state.mine(1)
                transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                assert(contracts.events.setOutcome(eventID, utils.fix("0.5"), sender=t.k0) == 1), "Should manually set event outcome"
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
                outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                contracts._ContractLoader__state.mine(1)
                fxpEtherDepositValue = utils.fix(100)
                assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                contracts._ContractLoader__state.mine(1)
                numOutcomes = 3
                eventID = utils.createCategoricalEvent(contracts, numOutcomes)
                marketID = utils.createMarket(contracts, eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeThreeShareContract = contracts.markets.getOutcomeShareContract(marketID, 3)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                outcomeThreeShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 3)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                fxpNumCompleteSets = utils.fix(3)
                utils.buyCompleteSets(contracts, marketID, fxpNumCompleteSets)
                contracts._ContractLoader__state.mine(1)
                transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                assert(contracts.events.setOutcome(eventID, utils.fix("0.5"), sender=t.k0) == 1), "Should manually set event outcome"
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
        def test_payoutScalarMarket():
            def test_userWithoutShares():
                contracts._ContractLoader__state.mine(1)
                fxpMinValue = utils.fix(5)
                fxpMaxValue = utils.fix(15)
                eventID = utils.createScalarEvent(contracts, fxpMinValue, fxpMaxValue)
                marketID = utils.createMarket(contracts, eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                outcomeID = "12.5"
                assert(contracts.events.setOutcome(eventID, utils.fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
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
                outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                contracts._ContractLoader__state.mine(1)
                fxpEtherDepositValue = utils.fix(100)
                assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                contracts._ContractLoader__state.mine(1)
                fxpMinValue = utils.fix(5)
                fxpMaxValue = utils.fix(15)
                eventID = utils.createScalarEvent(contracts, fxpMinValue, fxpMaxValue)
                marketID = utils.createMarket(contracts, eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                fxpNumCompleteSets = utils.fix(3)
                utils.buyCompleteSets(contracts, marketID, fxpNumCompleteSets)
                contracts._ContractLoader__state.mine(1)
                transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeOneShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 1 to address 0"
                outcomeID = "12.5"
                assert(contracts.events.setOutcome(eventID, utils.fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
                assert(contracts.events.getOutcome(eventID) == utils.fix(outcomeID)), "Event outcome should be equal to value set"
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
                userFinalCash = contracts.cash.balanceOf(t.a1)
                marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                fxpShare1Value = fxpMaxValue - utils.fix(outcomeID)
                fxpShare2Value = utils.fix(outcomeID) - fxpMinValue
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
                outcomeShareContractWrapper = utils.makeOutcomeShareContractWrapper(contracts)
                contracts._ContractLoader__state.mine(1)
                fxpEtherDepositValue = utils.fix(100)
                assert(contracts.cash.publicDepositEther(value=fxpEtherDepositValue, sender=t.k1) == 1), "publicDepositEther to user account should succeed"
                contracts._ContractLoader__state.mine(1)
                fxpMinValue = utils.fix(5)
                fxpMaxValue = utils.fix(15)
                eventID = utils.createScalarEvent(contracts, fxpMinValue, fxpMaxValue)
                marketID = utils.createMarket(contracts, eventID)
                outcomeOneShareContract = contracts.markets.getOutcomeShareContract(marketID, 1)
                outcomeTwoShareContract = contracts.markets.getOutcomeShareContract(marketID, 2)
                outcomeOneShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 1)
                outcomeTwoShareWallet = contracts.markets.getOutcomeShareWallet(marketID, 2)
                contracts._ContractLoader__state.mine(1)
                contracts._ContractLoader__state.block.timestamp = contracts.events.getExpiration(eventID) + 259201
                fxpNumCompleteSets = utils.fix(3)
                utils.buyCompleteSets(contracts, marketID, fxpNumCompleteSets)
                contracts._ContractLoader__state.mine(1)
                transferAbiEncodedData = shareTokenContractTranslator.encode("transfer", [t.a0, fxpNumCompleteSets])
                assert(int(contracts._ContractLoader__state.send(t.k1, outcomeTwoShareContract, 0, transferAbiEncodedData).encode("hex"), 16) == 1), "Transfer shares of outcome 2 to address 0"
                outcomeID = "12.5"
                assert(contracts.events.setOutcome(eventID, utils.fix(outcomeID), sender=t.k0) == 1), "Should manually set event outcome"
                assert(contracts.events.getOutcome(eventID) == utils.fix(outcomeID)), "Event outcome should be equal to value set"
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
                userFinalCash = contracts.cash.balanceOf(t.a1)
                marketFinalCash = contracts.cash.balanceOf(contracts.info.getWallet(marketID))
                fxpShare1Value = fxpMaxValue - utils.fix(outcomeID)
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

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_ClaimProceeds(contracts)
