#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from datetime import timedelta
from utils import captureFilteredLogs, bytesToHexString


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

def proceedToFirstReporting(testFixture, universe, market, makeReport, disputer, reportOutcomes, designatedDisputeOutcomes):
    if (market.getReportingState() != testFixture.contracts['Constants'].DESIGNATED_REPORTING()):
        proceedToDesignatedReporting(testFixture, universe, market, reportOutcomes)

    # To proceed to first reporting we will either dispute a designated report or not make a designated report within the alotted time window for doing so
    if (makeReport):
        assert testFixture.designatedReport(market, reportOutcomes, tester.k0)
        assert market.getReportingState() == testFixture.contracts['Constants'].DESIGNATED_DISPUTE()
        
        logs = []
        captureFilteredLogs(testFixture.chain.head_state, testFixture.contracts['Augur'], logs)
        
        assert market.disputeDesignatedReport(designatedDisputeOutcomes, 1, False, sender=testFixture.testerKey[disputer])

        # Confirm the designated dispute logging works
        assert len(logs) == 3
        assert logs[2]['_event_type'] == 'ReportsDisputed'
        assert logs[2]['reportingPhase'] == testFixture.contracts['Constants'].DESIGNATED_DISPUTE()
        assert logs[2]['disputer'] == bytesToHexString(testFixture.testerAddress[disputer])
        assert logs[2]['disputeBondAmount'] == testFixture.contracts['Constants'].DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
        assert logs[2]['market'] == market.address

    else:
        testFixture.chain.head_state.timestamp = market.getEndTime() + testFixture.contracts['Constants'].DESIGNATED_REPORTING_DURATION_SECONDS() + 1

    # We're in the FIRST REPORTING phase now
    assert market.getReportingState() == testFixture.contracts['Constants'].FIRST_REPORTING()

def proceedToLastReporting(testFixture, universe, market, makeReport, designatedDisputer, firstDisputer, reportOutcomes, designatedDisputeOutcomes, firstReporter, firstReportOutcomes, firstReportDisputeOutcomes):
    cash = testFixture.contracts['Cash']
    reputationToken = testFixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingWindow = testFixture.applySignature('ReportingWindow', market.getReportingWindow())

    if (market.getReportingState() != testFixture.contracts['Constants'].FIRST_REPORTING()):
        proceedToFirstReporting(testFixture, universe, market, makeReport, designatedDisputer, reportOutcomes, designatedDisputeOutcomes)

    stakeToken = testFixture.getStakeToken(market, firstReportOutcomes)

    # We make one report by the firstReporter
    assert stakeToken.buy(1, sender=testFixture.testerKey[firstReporter])
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == stakeToken.getPayoutDistributionHash()

    testFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    assert market.getReportingState() == testFixture.contracts['Constants'].FIRST_DISPUTE()

    logs = []
    captureFilteredLogs(testFixture.chain.head_state, testFixture.contracts['Augur'], logs)

    disputeFirstReportOutcomeStake = testFixture.contracts['Constants'].DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
    assert market.disputeFirstReporters(firstReportDisputeOutcomes, disputeFirstReportOutcomeStake, False, sender=testFixture.testerKey[firstDisputer])

    # Confirm the first dispute logging works
    assert len(logs) == 3
    assert logs[2]['_event_type'] == 'ReportsDisputed'
    assert logs[2]['reportingPhase'] == testFixture.contracts['Constants'].FIRST_DISPUTE()
    assert logs[2]['disputer'] == bytesToHexString(testFixture.testerAddress[firstDisputer])
    assert logs[2]['disputeBondAmount'] == testFixture.contracts['Constants'].FIRST_REPORTERS_DISPUTE_BOND_AMOUNT()
    assert logs[2]['market'] == market.address

    # We're in the LAST REPORTING phase now
    assert market.getReportingState() == testFixture.contracts['Constants'].LAST_REPORTING()

def proceedToForking(testFixture, universe, market, makeReport, designatedDisputer, firstDisputer, reporter, reportOutcomes, designatedDisputeOutcomes, firstReporter, firstReportOutcomes, firstReportDisputeOutcomes, lastReportOutcomes):
    reputationToken = testFixture.applySignature('ReputationToken', universe.getReputationToken())

    # Proceed to the LAST REPORTING phase
    if (market.getReportingState() != testFixture.contracts['Constants'].LAST_REPORTING()):
        proceedToLastReporting(testFixture, universe, market, makeReport, designatedDisputer, firstDisputer, reportOutcomes, designatedDisputeOutcomes, firstReporter, firstReportOutcomes, firstReportDisputeOutcomes)

    reportingWindow = testFixture.applySignature('ReportingWindow', market.getReportingWindow())

    stakeTokenNo = testFixture.getStakeToken(market, lastReportOutcomes)
    stakeTokenYes = testFixture.getStakeToken(market, firstReportDisputeOutcomes)

    # If we buy the delta between outcome stakes that will be sufficient to make the outcome win
    noStake = market.getPayoutDistributionHashStake(stakeTokenNo.getPayoutDistributionHash())
    yesStake = market.getPayoutDistributionHashStake(stakeTokenYes.getPayoutDistributionHash())
    stakeDelta = yesStake - noStake
    stakeTokenNo.buy(stakeDelta + 1, sender=testFixture.testerKey[reporter])
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == stakeTokenNo.getPayoutDistributionHash()

    # To progress into the LAST DISPUTE phase we move time forward
    testFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == testFixture.contracts['Constants'].LAST_DISPUTE()

    logs = []
    captureFilteredLogs(testFixture.chain.head_state, testFixture.contracts['Augur'], logs)

    # Making a dispute at this phase will progress the market into FORKING
    assert market.disputeLastReporters(sender=tester.k0)
    assert market.getReportingState() == testFixture.contracts['Constants'].FORKING()

    # Confirm the last dispute logging and universe fork logging works
    assert len(logs) == 3
    assert logs[1]['_event_type'] == 'UniverseForked'
    assert logs[1]['universe'] == universe.address

    assert logs[2]['_event_type'] == 'ReportsDisputed'
    assert logs[2]['reportingPhase'] == testFixture.contracts['Constants'].LAST_DISPUTE()
    assert logs[2]['disputer'] == bytesToHexString(tester.a0)
    assert logs[2]['disputeBondAmount'] == testFixture.contracts['Constants'].LAST_REPORTERS_DISPUTE_BOND_AMOUNT()
    assert logs[2]['market'] == market.address

def finalizeForkingMarket(reportingFixture, universe, market, finalizeByMigration, yesMigratorAddress, yesMigratorKey, noMigratorAddress1, noMigratorKey1, noMigratorAddress2, noMigratorKey2, firstReportOutcomes, secondReportOutcomes):
    reputationToken = reportingFixture.applySignature('ReputationToken', universe.getReputationToken())

    # The universe forks and there is now a universe where NO and YES are the respective outcomes of each
    noUniverse = reportingFixture.getOrCreateChildUniverse(universe, market, secondReportOutcomes)
    noUniverseReputationToken = reportingFixture.applySignature('ReputationToken', noUniverse.getReputationToken())
    assert noUniverse.address != universe.address
    yesUniverse = reportingFixture.getOrCreateChildUniverse(universe, market, firstReportOutcomes)
    yesUniverseReputationToken = reportingFixture.applySignature('ReputationToken', yesUniverse.getReputationToken())
    assert yesUniverse.address != universe.address
    assert yesUniverse.address != noUniverse.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated and not enough time has passed
    assert market.tryFinalize() == 0

    # A Tester moves their REP to the YES universe
    balance = reputationToken.balanceOf(yesMigratorAddress)
    bonus = balance / reportingFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
    reputationToken.migrateOut(yesUniverseReputationToken.address, yesMigratorAddress, reputationToken.balanceOf(yesMigratorAddress), sender = yesMigratorKey)
    assert not reputationToken.balanceOf(yesMigratorAddress)
    assert yesUniverseReputationToken.balanceOf(yesMigratorAddress) == balance + bonus

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    assert market.tryFinalize() == 0

    stakeTokenNo = reportingFixture.getStakeToken(market, secondReportOutcomes)
    stakeTokenYes = reportingFixture.getStakeToken(market, firstReportOutcomes)

    winningTokenAddress = stakeTokenYes.address

    if (finalizeByMigration):
        # 2 Testers move their combined REP to the NO universe
        tester1Balance = reputationToken.balanceOf(noMigratorAddress1)
        bonus = tester1Balance / reportingFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
        reputationToken.migrateOut(noUniverseReputationToken.address, noMigratorAddress1, reputationToken.balanceOf(noMigratorAddress1), sender = noMigratorKey1)
        assert not reputationToken.balanceOf(noMigratorAddress1)
        assert noUniverseReputationToken.balanceOf(noMigratorAddress1) == tester1Balance + bonus
        tester2Balance = reputationToken.balanceOf(noMigratorAddress2)
        bonus = tester2Balance / reportingFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
        reputationToken.migrateOut(noUniverseReputationToken.address, noMigratorAddress2, reputationToken.balanceOf(noMigratorAddress2), sender = noMigratorKey2)
        assert not reputationToken.balanceOf(noMigratorAddress2)
        assert noUniverseReputationToken.balanceOf(noMigratorAddress2) == tester2Balance + bonus
        winningTokenAddress = stakeTokenNo.address
    else:
        # Time marches on past the fork end time
        reportingFixture.chain.head_state.timestamp = universe.getForkEndTime() + 1

    # We can finalize the market now
    assert market.tryFinalize()

    # The market is now finalized
    assert market.getReportingState() == reportingFixture.contracts['Constants'].FINALIZED()
    assert market.getFinalWinningStakeToken() == winningTokenAddress
