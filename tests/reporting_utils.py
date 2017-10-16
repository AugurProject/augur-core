#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from datetime import timedelta

def initializeReportingFixture(sessionFixture, universe, market):
    # Give some REP to testers to make things interesting
    reputationToken = sessionFixture.applySignature('ReputationToken', universe.getReputationToken())
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    return sessionFixture.createSnapshot()

def proceedToDesignatedReporting(testFixture, universe, market, reportOutcomes, designatedReporter=tester.k0):
    cash = testFixture.contracts['Cash']
    reputationToken = testFixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingWindow = testFixture.applySignature('ReportingWindow', market.getReportingWindow())

    # We can't yet do a designated report on the market as it's in the pre reporting phase
    if (market.getReportingState() == testFixture.contracts['Constants'].PRE_REPORTING()):
        with raises(TransactionFailed, message="Reporting cannot be done in the PRE REPORTING state"):
            testFixture.designatedReport(market, reportOutcomes, designatedReporter)

    # Fast forward to the reporting phase time
    reportingWindow = testFixture.applySignature('ReportingWindow', universe.getNextReportingWindow())
    testFixture.chain.head_state.timestamp = market.getEndTime() + 1

    # This will cause us to be in the DESIGNATED REPORTING phase
    assert market.getReportingState() == testFixture.contracts['Constants'].DESIGNATED_REPORTING()

def proceedToRound1Reporting(testFixture, universe, market, makeReport, disputer, reportOutcomes, designatedDisputeOutcomes):
    if (market.getReportingState() != testFixture.contracts['Constants'].DESIGNATED_REPORTING()):
        proceedToDesignatedReporting(testFixture, universe, market, reportOutcomes)

    # To proceed to first reporting we will either dispute a designated report or not make a designated report within the alotted time window for doing so
    if (makeReport):
        assert testFixture.designatedReport(market, reportOutcomes, tester.k0)
        assert market.getReportingState() == testFixture.contracts['Constants'].DESIGNATED_DISPUTE()
        assert market.disputeDesignatedReport(designatedDisputeOutcomes, 1, False, sender=disputer)
    else:
        testFixture.chain.head_state.timestamp = market.getEndTime() + testFixture.contracts['Constants'].DESIGNATED_REPORTING_DURATION_SECONDS() + 1

    # We're in the ROUND1 REPORTING phase now
    assert market.getReportingState() == testFixture.contracts['Constants'].ROUND1_REPORTING()

def proceedToRound2Reporting(testFixture, universe, market, makeReport, designatedDisputer, round1Disputer, reportOutcomes, designatedDisputeOutcomes, round1Reporter, round1ReportOutcomes, round1ReportDisputeOutcomes):
    cash = testFixture.contracts['Cash']
    reputationToken = testFixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingWindow = testFixture.applySignature('ReportingWindow', market.getReportingWindow())

    if (market.getReportingState() != testFixture.contracts['Constants'].ROUND1_REPORTING()):
        proceedToRound1Reporting(testFixture, universe, market, makeReport, designatedDisputer, reportOutcomes, designatedDisputeOutcomes)

    stakeToken = testFixture.getStakeToken(market, round1ReportOutcomes)

    # We make one report by the round1Reporter
    assert stakeToken.buy(1, sender=round1Reporter)
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == stakeToken.getPayoutDistributionHash()

    testFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    assert market.getReportingState() == testFixture.contracts['Constants'].FIRST_DISPUTE()

    disputeRound1ReportOutcomeStake = testFixture.contracts['Constants'].DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
    assert market.disputeRound1Reporters(round1ReportDisputeOutcomes, disputeRound1ReportOutcomeStake, False, sender=round1Disputer)

    # We're in the ROUND2 REPORTING phase now
    assert market.getReportingState() == testFixture.contracts['Constants'].ROUND2_REPORTING()

def proceedToForking(testFixture, universe, market, makeReport, designatedDisputer, round1Disputer, reporter, reportOutcomes, designatedDisputeOutcomes, round1Reporter, round1ReportOutcomes, round1ReportDisputeOutcomes, round2ReportOutcomes):
    reputationToken = testFixture.applySignature('ReputationToken', universe.getReputationToken())

    # Proceed to the ROUND2 REPORTING phase
    if (market.getReportingState() != testFixture.contracts['Constants'].ROUND2_REPORTING()):
        proceedToRound2Reporting(testFixture, universe, market, makeReport, designatedDisputer, round1Disputer, reportOutcomes, designatedDisputeOutcomes, round1Reporter, round1ReportOutcomes, round1ReportDisputeOutcomes)

    reportingWindow = testFixture.applySignature('ReportingWindow', market.getReportingWindow())

    stakeTokenNo = testFixture.getStakeToken(market, round2ReportOutcomes)
    stakeTokenYes = testFixture.getStakeToken(market, round1ReportDisputeOutcomes)

    # If we buy the delta between outcome stakes that will be sufficient to make the outcome win
    marketExtensions = testFixture.contracts["MarketExtensions"]
    noStake = marketExtensions.getPayoutDistributionHashStake(market.address, stakeTokenNo.getPayoutDistributionHash())
    yesStake = marketExtensions.getPayoutDistributionHashStake(market.address, stakeTokenYes.getPayoutDistributionHash())
    stakeDelta = yesStake - noStake
    stakeTokenNo.buy(stakeDelta + 1, sender=reporter)
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == stakeTokenNo.getPayoutDistributionHash()

    # To progress into the LAST DISPUTE phase we move time forward
    testFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == testFixture.contracts['Constants'].LAST_DISPUTE()

    # Making a dispute at this phase will progress the market into FORKING
    assert market.disputeRound2Reporters(sender=tester.k0)
    assert market.getReportingState() == testFixture.contracts['Constants'].FORKING()

def finalizeForkingMarket(reportingFixture, universe, market, finalizeByMigration, yesMigratorAddress, yesMigratorKey, noMigratorAddress1, noMigratorKey1, noMigratorAddress2, noMigratorKey2, round1ReportOutcomes, secondReportOutcomes):
    reputationToken = reportingFixture.applySignature('ReputationToken', universe.getReputationToken())

    # The universe forks and there is now a universe where NO and YES are the respective outcomes of each
    noUniverse = reportingFixture.getOrCreateChildUniverse(universe, market, secondReportOutcomes)
    noUniverseReputationToken = reportingFixture.applySignature('ReputationToken', noUniverse.getReputationToken())
    assert noUniverse.address != universe.address
    yesUniverse = reportingFixture.getOrCreateChildUniverse(universe, market, round1ReportOutcomes)
    yesUniverseReputationToken = reportingFixture.applySignature('ReputationToken', yesUniverse.getReputationToken())
    assert yesUniverse.address != universe.address
    assert yesUniverse.address != noUniverse.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated and not enough time has passed
    assert market.tryFinalize() == 0

    # A Tester moves their REP to the YES universe
    balance = reputationToken.balanceOf(yesMigratorAddress)
    reputationToken.migrateOut(yesUniverseReputationToken.address, yesMigratorAddress, reputationToken.balanceOf(yesMigratorAddress), sender = yesMigratorKey)
    assert not reputationToken.balanceOf(yesMigratorAddress)
    assert yesUniverseReputationToken.balanceOf(yesMigratorAddress) == balance

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    assert market.tryFinalize() == 0

    stakeTokenNo = reportingFixture.getStakeToken(market, secondReportOutcomes)
    stakeTokenYes = reportingFixture.getStakeToken(market, round1ReportOutcomes)

    winningTokenAddress = stakeTokenYes.address

    if (finalizeByMigration):
        # 2 Testers move their combined REP to the NO universe
        tester1Balance = reputationToken.balanceOf(noMigratorAddress1)
        reputationToken.migrateOut(noUniverseReputationToken.address, noMigratorAddress1, reputationToken.balanceOf(noMigratorAddress1), sender = noMigratorKey1)
        assert not reputationToken.balanceOf(noMigratorAddress1)
        assert noUniverseReputationToken.balanceOf(noMigratorAddress1) == tester1Balance
        tester2Balance = reputationToken.balanceOf(noMigratorAddress2)
        reputationToken.migrateOut(noUniverseReputationToken.address, noMigratorAddress2, reputationToken.balanceOf(noMigratorAddress2), sender = noMigratorKey2)
        assert not reputationToken.balanceOf(noMigratorAddress2)
        assert noUniverseReputationToken.balanceOf(noMigratorAddress2) == tester2Balance
        winningTokenAddress = stakeTokenNo.address
    else:
        # Time marches on past the fork end time
        reportingFixture.chain.head_state.timestamp = universe.getForkEndTime() + 1

    # We can finalize the market now
    assert market.tryFinalize()

    # The market is now finalized
    assert market.getReportingState() == reportingFixture.contracts['Constants'].FINALIZED()
    assert market.getFinalWinningStakeToken() == winningTokenAddress
