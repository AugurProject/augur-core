from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises
from datetime import timedelta

def initializeReportingFixture(sessionFixture, market):
    # Seed legacy rep contract
    legacyRepContract = sessionFixture.contracts['LegacyRepContract']
    legacyRepContract.faucet(long(11 * 10**6 * 10**18))
    branch = sessionFixture.branch

    # Get the reputation token for this branch and migrate legacy REP to it
    reputationToken = sessionFixture.applySignature('ReputationToken', branch.getReputationToken())
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract()

    # Give some REP to testers to make things interesting
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    reportingWindow = sessionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    firstRegistrationToken = sessionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())
    reportingTokenNo = sessionFixture.getReportingToken(market, [10**18,0])
    reportingTokenYes = sessionFixture.getReportingToken(market, [0,10**18])

    # Tester 0, 1, 2, and 3 will buy registration tokens so they can report on the market
    firstRegistrationToken.register(sender=tester.k0)
    assert firstRegistrationToken.balanceOf(tester.a0) == 1
    # Testers will have their previous REP balance less the registration token bond of 1 REP
    assert reputationToken.balanceOf(tester.a0) == 8 * 10**6 * 10**18 - 10**18

    for (key, address) in [(tester.k1, tester.a1), (tester.k2, tester.a2), (tester.k3, tester.a3)]:
        firstRegistrationToken.register(sender=key)
        assert firstRegistrationToken.balanceOf(address) == 1
        assert reputationToken.balanceOf(address) == 1 * 10**6 * 10**18 - 10**18

    return sessionFixture.chain.snapshot()

def proceedToAutomatedReporting(testFixture, market, reportOutcomes):
    cash = testFixture.cash
    branch = testFixture.branch
    reputationToken = testFixture.applySignature('ReputationToken', branch.getReputationToken())
    reportingWindow = testFixture.applySignature('ReportingWindow', market.getReportingWindow())

    # We can't yet do an automated report on the market as it's in the pre reporting phase
    if (market.getReportingState() == testFixture.constants.PRE_REPORTING()):
        with raises(TransactionFailed, message="Reporting cannot be done in the PRE REPORTING state"):
            market.automatedReport(reportOutcomes, sender=tester.k0)

    # Fast forward to the reporting phase time
    reportingWindow = testFixture.applySignature('ReportingWindow', branch.getNextReportingWindow())
    testFixture.chain.head_state.timestamp = market.getEndTime() + 1

    # This will cause us to be in the AUTOMATED REPORTING phase
    assert market.getReportingState() == testFixture.constants.AUTOMATED_REPORTING()

def proceedToLimitedReporting(testFixture, market, makeReport, disputer, reportOutcomes):
    if (market.getReportingState() != testFixture.constants.AUTOMATED_REPORTING()):
        proceedToAutomatedReporting(testFixture, market, reportOutcomes)

    # To proceed to limited reporting we will either dispute an automated report or not make an automated report within the alotted time window for doing so
    if (makeReport):
        assert market.automatedReport(reportOutcomes, sender=tester.k0)
        assert market.getReportingState() == testFixture.constants.AUTOMATED_DISPUTE()
        assert market.disputeAutomatedReport(sender=disputer)
    else:
        testFixture.chain.head_state.timestamp = market.getEndTime() + testFixture.constants.AUTOMATED_REPORTING_DURATION_SECONDS() + 1

    # We're in the LIMITED REPORTING phase now
    assert market.getReportingState() == testFixture.constants.LIMITED_REPORTING()

def proceedToAllReporting(testFixture, market, makeReport, automatedDisputer, limitedDisputer, reportOutcomes):
    cash = testFixture.cash
    branch = testFixture.branch
    reputationToken = testFixture.applySignature('ReputationToken', branch.getReputationToken())
    reportingWindow = testFixture.applySignature('ReportingWindow', market.getReportingWindow())

    if (market.getReportingState() != testFixture.constants.LIMITED_REPORTING()):
        proceedToLimitedReporting(testFixture, market, makeReport, automatedDisputer, reportOutcomes)

    testFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == testFixture.constants.LIMITED_DISPUTE()

    assert market.disputeLimitedReporters(sender=limitedDisputer)

    # We're in the ALL REPORTING phase now
    assert market.getReportingState() == testFixture.constants.ALL_REPORTING()

def proceedToForking(testFixture, market, makeReport, automatedDisputer, limitedDisputer, reporter, reportOutcomes, allReportOutcomes):
    market = testFixture.binaryMarket
    branch = testFixture.branch
    reputationToken = testFixture.applySignature('ReputationToken', branch.getReputationToken())

    # Proceed to the ALL REPORTING phase
    if (market.getReportingState() != testFixture.constants.ALL_REPORTING()):
        proceedToAllReporting(testFixture, market, makeReport, automatedDisputer, limitedDisputer, reportOutcomes)

    reportingWindow = testFixture.applySignature('ReportingWindow', market.getReportingWindow())

    reportingTokenNo = testFixture.getReportingToken(market, allReportOutcomes)

    # We make one report by the reporter
    registrationToken = testFixture.applySignature('RegistrationToken', reportingTokenNo.getRegistrationToken())
    registrationToken.register(sender=reporter)
    reportingTokenNo.buy(1, sender=reporter)
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenNo.getPayoutDistributionHash()

    # To progress into the ALL DISPUTE phase we move time forward
    testFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == testFixture.constants.ALL_DISPUTE()

    # Making a dispute at this phase will progress the market into FORKING
    assert market.disputeAllReporters(sender=tester.k0)
    assert market.getReportingState() == testFixture.constants.FORKING()

def finalizeForkingMarket(reportingFixture, market, finalizeByMigration, yesMigratorAddress, yesMigratorKey, noMigratorAddress1, noMigratorKey1, noMigratorAddress2, noMigratorKey2, firstReportOutcomes, secondReportOutcomes):
    branch = reportingFixture.branch
    reputationToken = reportingFixture.applySignature('ReputationToken', branch.getReputationToken())

    # The universe forks and there is now a branch where NO and YES are the respective outcomes of each
    noBranch = reportingFixture.getOrCreateChildBranch(branch, market, secondReportOutcomes)
    noBranchReputationToken = reportingFixture.applySignature('ReputationToken', noBranch.getReputationToken())
    assert noBranch.address != branch.address
    yesBranch = reportingFixture.getOrCreateChildBranch(branch, market, firstReportOutcomes)
    yesBranchReputationToken = reportingFixture.applySignature('ReputationToken', yesBranch.getReputationToken())
    assert yesBranch.address != branch.address
    assert yesBranch.address != noBranch.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated and not enough time has passed
    assert market.tryFinalize() == 0

    # A Tester moves their REP to the YES branch
    balance = reputationToken.balanceOf(yesMigratorAddress)
    reputationToken.migrateOut(yesBranchReputationToken.address, yesMigratorAddress, reputationToken.balanceOf(yesMigratorAddress), sender = yesMigratorKey)
    assert not reputationToken.balanceOf(yesMigratorAddress)
    assert yesBranchReputationToken.balanceOf(yesMigratorAddress) == balance

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    assert market.tryFinalize() == 0

    reportingTokenNo = reportingFixture.getReportingToken(market, secondReportOutcomes)
    reportingTokenYes = reportingFixture.getReportingToken(market, firstReportOutcomes)

    winningTokenAddress = reportingTokenYes.address

    if (finalizeByMigration):
        # 2 Testers move their combined REP to the NO branch
        tester1Balance = reputationToken.balanceOf(noMigratorAddress1)
        reputationToken.migrateOut(noBranchReputationToken.address, noMigratorAddress1, reputationToken.balanceOf(noMigratorAddress1), sender = noMigratorKey1)
        assert not reputationToken.balanceOf(noMigratorAddress1)
        assert noBranchReputationToken.balanceOf(noMigratorAddress1) == tester1Balance
        tester2Balance = reputationToken.balanceOf(noMigratorAddress2)
        reputationToken.migrateOut(noBranchReputationToken.address, noMigratorAddress2, reputationToken.balanceOf(noMigratorAddress2), sender = noMigratorKey2)
        assert not reputationToken.balanceOf(noMigratorAddress2)
        assert noBranchReputationToken.balanceOf(noMigratorAddress2) == tester2Balance
        winningTokenAddress = reportingTokenNo.address
    else:
        # Time marches on past the fork end time
        reportingFixture.chain.head_state.timestamp = branch.getForkEndTime() + 1

    # We can finalize the market now
    assert market.tryFinalize()

    # The market is now finalized
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()
    assert market.getFinalWinningReportingToken() == winningTokenAddress
