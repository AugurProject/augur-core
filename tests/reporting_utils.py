#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from datetime import timedelta
from utils import captureFilteredLogs, bytesToHexString

def proceedToDesignatedReporting(fixture, market):
    fixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)

def proceedToInitialReporting(fixture, market):
    fixture.contracts["Time"].setTimestamp(market.getDesignatedReportingEndTime() + 1)

def proceedToNextRound(fixture, market):
    if fixture.contracts["Controller"].getTimestamp() < market.getEndTime():
        fixture.contracts["Time"].setTimestamp(market.getDesignatedReportingEndTime() + 1)

    feeWindow = market.getFeeWindow()

    if (not feeWindow):
        payoutNumerators = [0] * market.getNumOutcomes()
        payoutNumerators[0] = market.getNumTicks()
        market.doInitialReport(payoutNumerators, False)
        assert market.getFeeWindow()
    else:
        winningReport = fixture.applySignature('BaseReportingParticipant', market.getWinningReportingParticipant())
        winningPayoutNumerators = winningReport.getPayoutNumerators()
        amount = 2 * market.getStakeInOutcome(market.getWinningPayoutDistributionHash())
        market.contribute(winningPayoutNumerators[::-1], false, amount)
        assert market.getFeeWindow() != feeWindow

    feeWindow = fixture.applySignature('FeeWindow', market.getFeeWindow())
    fixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

def proceedToForking(fixture, market, universe):
    logs = []
    captureFilteredLogs(fixture.chain.head_state, fixture.contracts['Augur'], logs)

    while (not market.getForkingMarket()):
        proceedToNextRound(fixture, market)

    assert len(logs) >= 3
    log1 = logs[1]
    log2 = logs[2] if len(logs) == 3 else logs[3]
    assert log1['_event_type'] == 'UniverseForked'
    assert log1['universe'] == universe.address

def finalizeFork(fixture, market, universe, finalizeByMigration = True):
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())

    # The universe forks and there is now a universe where NO and YES are the respective outcomes of each
    payoutNumerators = [0] * market.getNumOutcomes()
    payoutNumerators[0] = market.getNumTicks()
    noUniverse =  fixture.applySignature('Universe', universe.getChildUniverse(payoutNumerators))
    yesUniverse =  fixture.applySignature('Universe', universe.getChildUniverse(payoutNumerators[::-1]))
    noUniverseReputationToken = reportingFixture.applySignature('ReputationToken', noUniverse.getReputationToken())
    yesUniverseReputationToken = reportingFixture.applySignature('ReputationToken', yesUniverse.getReputationToken())
    assert noUniverse.address != universe.address
    assert yesUniverse.address != universe.address
    assert yesUniverse.address != noUniverse.address
    assert noUniverseReputationToken.address != yesUniverseReputationToken.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated and not enough time has passed
    with raises(TransactionFailed):
        market.finalizeFork()

    # A Tester moves their REP to the YES universe
    balance = reputationToken.balanceOf(tester.a1)
    bonus = balance / reportingFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
    reputationToken.migrateOut(yesUniverseReputationToken.address, tester.a1, reputationToken.balanceOf(tester.a1), sender = tester.k1)
    assert not reputationToken.balanceOf(tester.a1)
    assert yesUniverseReputationToken.balanceOf(tester.a1) == balance + bonus

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    with raises(TransactionFailed):
        market.finalizeFork()

    if (finalizeByMigration):
        # 2 Testers move their combined REP to the NO universe
        tester1Balance = reputationToken.balanceOf(tester.a0)
        bonus = tester1Balance / reportingFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
        reputationToken.migrateOut(noUniverseReputationToken.address, tester.a1, reputationToken.balanceOf(tester.a0), sender = tester.k0)
        assert not reputationToken.balanceOf(tester.a0)
        assert noUniverseReputationToken.balanceOf(tester.a0) == tester1Balance + bonus
        tester2Balance = reputationToken.balanceOf(tester.a2)
        bonus = tester2Balance / reportingFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
        reputationToken.migrateOut(noUniverseReputationToken.address, tester.a2, reputationToken.balanceOf(tester.a2), sender = tester.k2)
        assert not reputationToken.balanceOf(tester.a2)
        assert noUniverseReputationToken.balanceOf(tester.a2) == tester2Balance + bonus
    else:
        # Time marches on past the fork end time
        reportingFixture.contracts["Time"].setTimestamp(universe.getForkEndTime() + 1)

    # We can finalize the market now
    assert market.finalize()

    # The market is now finalized
    assert market.getWinningPayoutDistributionHash() == noUniverse.getParentPayoutDistributionHash()
