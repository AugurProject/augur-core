#!/usr/bin/env python

from random import randint
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from datetime import timedelta
from utils import bytesToHexString, longToHexString, PrintGasUsed, TokenDelta, EtherDelta

def proceedToDesignatedReporting(fixture, market):
    fixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)

def proceedToInitialReporting(fixture, market):
    fixture.contracts["Time"].setTimestamp(market.getDesignatedReportingEndTime() + 1)

def proceedToNextRound(fixture, market, contributor = tester.k0, doGenerateFees = False, moveTimeForward = True, randomPayoutNumerators = False):
    if fixture.contracts["Controller"].getTimestamp() < market.getEndTime():
        fixture.contracts["Time"].setTimestamp(market.getDesignatedReportingEndTime() + 1)

    feeWindow = market.getFeeWindow()

    payoutNumerators = [0] * market.getNumberOfOutcomes()
    payoutNumerators[0] = market.getNumTicks()

    if (feeWindow == longToHexString(0)):
        market.doInitialReport(payoutNumerators, False)
        assert market.getFeeWindow()
    else:
        feeWindow = fixture.applySignature('FeeWindow', market.getFeeWindow())
        fixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
        # This will also use the InitialReporter which is not a DisputeCrowdsourcer, but has the called function from abstract inheritance
        winningReport = fixture.applySignature('DisputeCrowdsourcer', market.getWinningReportingParticipant())
        winningPayoutHash = winningReport.getPayoutDistributionHash()

        if (randomPayoutNumerators):
            chosenPayoutNumerators = [0] * market.getNumberOfOutcomes()
            chosenPayoutNumerators[0] = randint(0, market.getNumTicks())
            chosenPayoutNumerators[1] = market.getNumTicks() - chosenPayoutNumerators[0]
        else:
            firstReportWinning = market.derivePayoutDistributionHash(payoutNumerators, False) == winningPayoutHash
            chosenPayoutNumerators = payoutNumerators if not firstReportWinning else payoutNumerators[::-1]

        chosenPayoutHash = market.derivePayoutDistributionHash(chosenPayoutNumerators, False)
        amount = 2 * market.getParticipantStake() - 3 * market.getStakeInOutcome(chosenPayoutHash)
        with PrintGasUsed(fixture, "Contribute:", 0):
            market.contribute(chosenPayoutNumerators, False, amount, sender=contributor)
        assert market.getForkingMarket() or market.getFeeWindow() != feeWindow

    if (doGenerateFees):
        universe = fixture.applySignature("Universe", market.getUniverse())
        generateFees(fixture, universe, market)

    if (moveTimeForward):
        feeWindow = fixture.applySignature('FeeWindow', market.getFeeWindow())
        fixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

def proceedToFork(fixture, market, universe):
    while (market.getForkingMarket() == longToHexString(0)):
        proceedToNextRound(fixture, market)

    for i in range(market.getNumParticipants()):
        reportingParticipant = fixture.applySignature("DisputeCrowdsourcer", market.getReportingParticipant(i))
        reportingParticipant.forkAndRedeem()

def finalizeFork(fixture, market, universe, finalizeByMigration = True):
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())

    # The universe forks and there is now a universe where NO and YES are the respective outcomes of each
    noPayoutNumerators = [0] * market.getNumberOfOutcomes()
    noPayoutNumerators[0] = market.getNumTicks()
    yesPayoutNumerators = noPayoutNumerators[::-1]
    noUniverse =  fixture.applySignature('Universe', universe.createChildUniverse(noPayoutNumerators, False))
    yesUniverse =  fixture.applySignature('Universe', universe.createChildUniverse(yesPayoutNumerators, False))
    noUniverseReputationToken = fixture.applySignature('ReputationToken', noUniverse.getReputationToken())
    yesUniverseReputationToken = fixture.applySignature('ReputationToken', yesUniverse.getReputationToken())
    assert noUniverse.address != universe.address
    assert yesUniverse.address != universe.address
    assert yesUniverse.address != noUniverse.address
    assert noUniverseReputationToken.address != yesUniverseReputationToken.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated and not enough time has passed
    with raises(TransactionFailed):
        market.finalizeFork()

    # A Tester moves some of their REP to the YES universe
    amount = 10 ** 6 * 10 ** 18
    bonus = amount / fixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()

    with raises(TransactionFailed):
        reputationToken.migrateOut(yesUniverseReputationToken.address, 0)

    with TokenDelta(yesUniverseReputationToken, amount + bonus, tester.a0, "Yes REP token balance was no correct"):
        reputationToken.migrateOut(yesUniverseReputationToken.address, amount)

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    with raises(TransactionFailed):
        market.finalizeFork()

    if (finalizeByMigration):
        # Tester 0 moves more than 50% of REP
        amount = reputationToken.balanceOf(tester.a0) - 20
        bonus = amount / fixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
        with TokenDelta(noUniverseReputationToken, amount + bonus, tester.a0, "No REP token balance was no correct"):
            reputationToken.migrateOut(noUniverseReputationToken.address, amount)
        assert reputationToken.balanceOf(tester.a0) == 20
        assert market.getWinningPayoutDistributionHash() == noUniverse.getParentPayoutDistributionHash()
    else:
        # Time marches on past the fork end time
        fixture.contracts["Time"].setTimestamp(universe.getForkEndTime() + 1)
        assert market.finalize()
        assert market.getWinningPayoutDistributionHash() == yesUniverse.getParentPayoutDistributionHash()

    # if the fork finalized by migration we're still in the 60 day fork window and can still get a bonus for migrating. If the fork is past the fork period we can no longer get the 5% bonus
    amount = 20
    amountAdded = amount
    if finalizeByMigration:
        bonus = amount / fixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
        amountAdded += bonus

    with TokenDelta(yesUniverseReputationToken, amountAdded, tester.a0, "reputation migration bonus did not work correctly"):
        reputationToken.migrateOut(yesUniverseReputationToken.address, amount)

    # Finalize fork cannot be called again
    with raises(TransactionFailed):
        market.finalizeFork()

def generateFees(fixture, universe, market):
    completeSets = fixture.contracts['CompleteSets']
    cash = fixture.contracts['Cash']
    mailbox = fixture.applySignature('Mailbox', market.getMarketCreatorMailbox())
    assert mailbox.withdrawEther()

    cost = 1000 * market.getNumTicks()
    marketCreatorFees = cost / market.getMarketCreatorSettlementFeeDivisor()
    completeSets.publicBuyCompleteSets(market.address, 1000, sender = tester.k1, value = cost)
    with TokenDelta(cash, marketCreatorFees, mailbox.address, "The market creator mailbox didn't get their share of fees from complete set sale"):
        completeSets.publicSellCompleteSets(market.address, 1000, sender=tester.k1)
    with EtherDelta(marketCreatorFees, market.getOwner(), fixture.chain, "The market creator did not get their fees when withdrawing ETH from the mailbox"):
        assert mailbox.withdrawEther()
    fees = cash.balanceOf(universe.getNextFeeWindow())
    reporterFees = cost / universe.getOrCacheReportingFeeDivisor()
    assert fees == reporterFees, "Cash balance of window higher by: " + str(fees - reporterFees)

def getExpectedFees(fixture, cash, reportingParticipant, expectedRounds):
    stake = reportingParticipant.getStake()
    feeWindow = fixture.applySignature("FeeWindow", reportingParticipant.getFeeWindow())
    universe = fixture.applySignature("Universe", feeWindow.getUniverse())
    feeToken = fixture.applySignature("FeeToken", feeWindow.getFeeToken())
    expectedFees = 0
    rounds = 0
    while feeToken.balanceOf(reportingParticipant.address) > 0:
        rounds += 1
        expectedFees += cash.balanceOf(feeWindow.address) * stake / feeToken.totalSupply()
        feeWindow = fixture.applySignature("FeeWindow", universe.getOrCreateFeeWindowBefore(feeWindow.address))
        feeToken = fixture.applySignature("FeeToken", feeWindow.getFeeToken())
    assert expectedRounds == rounds, "Had fees from " + str(rounds) + " rounds instead of " + str(expectedRounds)
    assert expectedFees > 0, "No fees. Tests should just use 0 if this is the expected case"
    return expectedFees