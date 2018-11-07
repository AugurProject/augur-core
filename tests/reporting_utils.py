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

def proceedToNextRound(fixture, market, contributor = tester.k0, doGenerateFees = False, moveTimeForward = True, randomPayoutNumerators = False, description = ""):
    if fixture.contracts["Controller"].getTimestamp() < market.getEndTime():
        fixture.contracts["Time"].setTimestamp(market.getDesignatedReportingEndTime() + 1)

    disputeWindow = market.getDisputeWindow()

    payoutNumerators = [0] * market.getNumberOfOutcomes()
    payoutNumerators[1] = market.getNumTicks()

    if (disputeWindow == longToHexString(0)):
        market.doInitialReport(payoutNumerators, "")
        assert market.getDisputeWindow()
    else:
        disputeWindow = fixture.applySignature('DisputeWindow', market.getDisputeWindow())
        if market.getDisputePacingOn():
            fixture.contracts["Time"].setTimestamp(disputeWindow.getStartTime() + 1)
        # This will also use the InitialReporter which is not a DisputeCrowdsourcer, but has the called function from abstract inheritance
        winningReport = fixture.applySignature('DisputeCrowdsourcer', market.getWinningReportingParticipant())
        winningPayoutHash = winningReport.getPayoutDistributionHash()

        chosenPayoutNumerators = [0] * market.getNumberOfOutcomes()
        chosenPayoutNumerators[1] = market.getNumTicks()

        if (randomPayoutNumerators):
            chosenPayoutNumerators[1] = randint(0, market.getNumTicks())
            chosenPayoutNumerators[2] = market.getNumTicks() - chosenPayoutNumerators[1]
        else:
            firstReportWinning = market.derivePayoutDistributionHash(payoutNumerators) == winningPayoutHash
            if firstReportWinning:
                chosenPayoutNumerators[1] = 0
                chosenPayoutNumerators[2] = market.getNumTicks()

        chosenPayoutHash = market.derivePayoutDistributionHash(chosenPayoutNumerators)
        amount = 2 * market.getParticipantStake() - 3 * market.getStakeInOutcome(chosenPayoutHash)
        with PrintGasUsed(fixture, "Contribute:", 0):
            market.contribute(chosenPayoutNumerators, amount, description, sender=contributor)
        assert market.getForkingMarket() or market.getDisputeWindow() != disputeWindow

    if (doGenerateFees):
        universe = fixture.applySignature("Universe", market.getUniverse())
        generateFees(fixture, universe, market)

    if (moveTimeForward):
        disputeWindow = fixture.applySignature('DisputeWindow', market.getDisputeWindow())
        fixture.contracts["Time"].setTimestamp(disputeWindow.getStartTime() + 1)

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
    noPayoutNumerators[1] = market.getNumTicks()
    yesPayoutNumerators = [0] * market.getNumberOfOutcomes()
    yesPayoutNumerators[2] = market.getNumTicks()
    noUniverse =  fixture.applySignature('Universe', universe.createChildUniverse(noPayoutNumerators))
    yesUniverse =  fixture.applySignature('Universe', universe.createChildUniverse(yesPayoutNumerators))
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

    with raises(TransactionFailed):
        reputationToken.migrateOut(yesUniverseReputationToken.address, 0)

    with TokenDelta(yesUniverseReputationToken, amount, tester.a0, "Yes REP token balance was no correct"):
        reputationToken.migrateOut(yesUniverseReputationToken.address, amount)

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    with raises(TransactionFailed):
        market.finalizeFork()

    if (finalizeByMigration):
        # Tester 0 moves more than 50% of REP
        amount = reputationToken.balanceOf(tester.a0) - 20
        with TokenDelta(noUniverseReputationToken, amount, tester.a0, "No REP token balance was no correct"):
            reputationToken.migrateOut(noUniverseReputationToken.address, amount)
        assert reputationToken.balanceOf(tester.a0) == 20
        assert market.getWinningPayoutDistributionHash() == noUniverse.getParentPayoutDistributionHash()
    else:
        # Time marches on past the fork end time
        fixture.contracts["Time"].setTimestamp(universe.getForkEndTime() + 1)
        assert market.finalize()
        assert market.getWinningPayoutDistributionHash() == yesUniverse.getParentPayoutDistributionHash()
        # If the fork is past the fork period we can not migrate
        with raises(TransactionFailed):
            reputationToken.migrateOut(yesUniverseReputationToken.address, 1)

    # Finalize fork cannot be called again
    with raises(TransactionFailed):
        market.finalizeFork()

def generateFees(fixture, universe, market):
    completeSets = fixture.contracts['CompleteSets']
    cash = fixture.contracts['Cash']
    mailbox = fixture.applySignature('Mailbox', market.getMarketCreatorMailbox())
    assert mailbox.withdrawEther()
    oldFeesBalance = cash.balanceOf(universe.getAuction())

    cost = 1000 * market.getNumTicks()
    marketCreatorFees = cost / market.getMarketCreatorSettlementFeeDivisor()
    completeSets.publicBuyCompleteSets(market.address, 1000, sender = tester.k1, value = cost)
    with TokenDelta(cash, marketCreatorFees, mailbox.address, "The market creator mailbox didn't get their share of fees from complete set sale"):
        completeSets.publicSellCompleteSets(market.address, 1000, sender=tester.k1)
    with EtherDelta(marketCreatorFees, market.getOwner(), fixture.chain, "The market creator did not get their fees when withdrawing ETH from the mailbox"):
        assert mailbox.withdrawEther()
    newFeesBalance = cash.balanceOf(universe.getAuction())
    reporterFees = cost / universe.getOrCacheReportingFeeDivisor()
    feesGenerated = newFeesBalance - oldFeesBalance
    assert feesGenerated == reporterFees, "Cash balance of auction higher by: " + str(fees - reporterFees)
