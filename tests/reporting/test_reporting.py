from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises
from datetime import timedelta

tester.STARTGAS = long(6.7 * 10**6)

def test_reportingFullHappyPath(reportingFixture):
    cash = reportingFixture.cash
    market = reportingFixture.binaryMarket
    branch = reportingFixture.branch
    reputationToken = reportingFixture.applySignature('ReputationToken', branch.getReputationToken())
    reportingTokenNo = reportingFixture.getReportingToken(market, [2,0])
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,2])

    # We can't yet report on the market as it's in the pre reporting phase
    assert market.getReportingState() == reportingFixture.constants.PRE_REPORTING()
    with raises(TransactionFailed, message="Reporting cannot be done in the PRE REPORTING state"):
        reportingTokenNo.buy(100, sender=tester.k0)

    # Fast forward to one second after the next reporting window
    reportingWindow = reportingFixture.applySignature('ReportingWindow', branch.getNextReportingWindow())
    reportingFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1

    # This will cause us to be in the limited reporting phase
    assert market.getReportingState() == reportingFixture.constants.LIMITED_REPORTING()

    # Both reporters report on the outcome. Tester 1 buys 1 more share causing the YES outcome to be the tentative winner
    reportingTokenNo.buy(100, sender=tester.k0)
    assert reportingTokenNo.balanceOf(tester.a0) == 100
    assert reputationToken.balanceOf(tester.a0) == 8 * 10**6 * 10 **18 - 10**18 - 100
    reportingTokenYes.buy(101, sender=tester.k1)
    assert reportingTokenYes.balanceOf(tester.a1) == 101
    assert reputationToken.balanceOf(tester.a1) == 1 * 10**6 * 10 **18 - 10**18 - 101
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenYes.getPayoutDistributionHash()

    # Move time forward into the LIMITED DISPUTE phase
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.LIMITED_DISPUTE()

    # Contest the results with Tester 0
    market.disputeLimitedReporters(sender=tester.k0)
    assert not reportingWindow.isContainerForMarket(market.address)
    assert branch.isContainerForMarket(market.address)
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)

    # We're now in the ALL REPORTING phase
    assert market.getReportingState() == reportingFixture.constants.ALL_REPORTING()

    # Tester 0 has a REP balance less the limited bond amount
    assert reputationToken.balanceOf(tester.a0) == 8 * 10**6 * 10 **18 - 10**18 - 100 - 11 * 10**21

    # Tester 2 now registers as a new reporter for the new reporting window
    secondRegistrationToken = reportingFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())
    secondRegistrationToken.register(sender=tester.k2)
    assert secondRegistrationToken.balanceOf(tester.a2) == 1
    assert reputationToken.balanceOf(tester.a2) == 1 * 10**6 * 10**18 - 2 * 10**18 

    # Tester 2 reports for the NO outcome
    reportingFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1
    reportingTokenNo.buy(2, sender=tester.k2)
    assert reportingTokenNo.balanceOf(tester.a2) == 2
    assert reputationToken.balanceOf(tester.a2) == 1 * 10**6 * 10 **18 - 2 * 10**18 - 2
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenNo.getPayoutDistributionHash()

    # Move forward in time to put us in the ALL DISPUTE PHASE
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.ALL_DISPUTE()

    # Tester 1 contests the outcome of the ALL report which will cause a fork
    market.disputeAllReporters(sender=tester.k1)
    assert branch.getForkingMarket() == market.address
    assert not reportingWindow.isContainerForMarket(market.address)
    assert branch.isContainerForMarket(market.address)
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)
    assert market.getReportingState() == reportingFixture.constants.FORKING()

    # The universe forks and there is now a branch where NO and YES are the respective outcomes of each
    noBranch = reportingFixture.getChildBranch(branch, market, [2,0])
    noBranchReputationToken = reportingFixture.applySignature('ReputationToken', noBranch.getReputationToken())
    assert noBranch.address != branch.address
    yesBranch = reportingFixture.getChildBranch(branch, market, [0,2])
    yesBranchReputationToken = reportingFixture.applySignature('ReputationToken', yesBranch.getReputationToken())
    assert yesBranch.address != branch.address
    assert yesBranch.address != noBranch.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated
    assert market.tryFinalize() == 0

    # Tester 1 moves their ~1 Million REP to the YES branch
    reputationToken.migrateOut(yesBranchReputationToken.address, tester.a1, reputationToken.balanceOf(tester.a1), sender = tester.k1)
    assert not reputationToken.balanceOf(tester.a1)
    assert yesBranchReputationToken.balanceOf(tester.a1) == 1 * 10**6 * 10**18 - 10**18 - 101 - 110000 * 10**18

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    assert market.tryFinalize() == 0

    # Testers 0 and 2 move their combined ~9 million REP to the NO branch
    reputationToken.migrateOut(noBranchReputationToken.address, tester.a0, reputationToken.balanceOf(tester.a0), sender = tester.k0)
    assert not reputationToken.balanceOf(tester.a0)
    assert noBranchReputationToken.balanceOf(tester.a0) == 8 * 10 ** 6 * 10 ** 18 - 10 ** 18 - 100 - 11000 * 10 ** 18
    reputationToken.migrateOut(noBranchReputationToken.address, tester.a2, reputationToken.balanceOf(tester.a2), sender = tester.k2)
    assert not reputationToken.balanceOf(tester.a2)
    assert noBranchReputationToken.balanceOf(tester.a2) == 1 * 10 ** 6 * 10 ** 18 - 2 * 10 ** 18 - 2

    # We can finalize the market now since a mjaority of REP has moved. Alternatively we could "reportingFixture.chain.head_state.timestamp = branch.getForkEndTime() + 1" to move
    assert market.tryFinalize()

    # The market is now finalized and the NO outcome is the winner
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()
    assert market.getFinalWinningReportingToken() == reportingTokenNo.address

    # We can redeem forked REP on any branch we didn't dispute
    assert reportingTokenNo.redeemForkedTokens(sender = tester.k0)
    assert noBranchReputationToken.balanceOf(tester.a0) == 8 * 10 ** 6 * 10 ** 18 -10 ** 18 - 11000 * 10 ** 18


def test_automatedReportingHappyPath(reportingFixture):
    market = reportingFixture.binaryMarket

    # Proceed to the AUTOMATED REPORTING phase
    proceedToAutomatedReporting(reportingFixture)

    # To progress into the AUTOMATED DISPUTE phase we do an automated report
    assert market.automatedReport([0,2], sender=tester.k0)

    # We're now in the AUTOMATED DISPUTE PHASE
    assert market.getReportingState() == reportingFixture.constants.AUTOMATED_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    reportingFixture.chain.head_state.timestamp = market.getEndTime() + reportingFixture.constants.AUTOMATED_REPORTING_DURATION_SECONDS() + reportingFixture.constants.AUTOMATED_REPORTING_DISPUTE_DURATION_SECONDS() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == reportingFixture.constants.AWAITING_FINALIZATION()

    # We can finalize it
    assert market.tryFinalize()
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()

@mark.parametrize('makeReport', [
    True,
    False
])
def test_limitedReportingHappyPath(makeReport, reportingFixture):
    market = reportingFixture.binaryMarket
    branch = reportingFixture.branch
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = reportingFixture.applySignature('ReputationToken', branch.getReputationToken())

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(reportingFixture, makeReport)

    # We make one report by Tester 2
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,2])
    reportingTokenYes.buy(1, sender=tester.k2)
    assert reportingTokenYes.balanceOf(tester.a2) == 1
    assert reputationToken.balanceOf(tester.a2) == 1 * 10 ** 6 * 10 ** 18 - 10 ** 18 - 1
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenYes.getPayoutDistributionHash()

    # To progress into the LIMITED DISPUTE phase we move time forward
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.LIMITED_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == reportingFixture.constants.AWAITING_FINALIZATION()

    # We can finalize it
    assert market.tryFinalize()
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()


@mark.parametrize('makeReport', [
    True,
    False
])
def test_allReportingHappyPath(reportingFixture, makeReport):
    market = reportingFixture.binaryMarket
    branch = reportingFixture.branch
    reputationToken = reportingFixture.applySignature('ReputationToken', branch.getReputationToken())

    # Proceed to the ALL REPORTING phase
    proceedToAllReporting(reportingFixture, makeReport)

    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    # We make one report by Tester 3
    reportingTokenNo = reportingFixture.getReportingToken(market, [2,0])
    registrationToken = reportingFixture.applySignature('RegistrationToken', reportingTokenNo.getRegistrationToken())
    registrationToken.register(sender=tester.k3)
    reportingTokenNo.buy(1, sender=tester.k3)
    assert reportingTokenNo.balanceOf(tester.a3) == 1
    assert reputationToken.balanceOf(tester.a3) == 1 * 10 ** 6 * 10 ** 18 - 2 * 10 ** 18 - 11 * 10 ** 21 - 1
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenNo.getPayoutDistributionHash()

    # To progress into the ALL DISPUTE phase we move time forward
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.ALL_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == reportingFixture.constants.AWAITING_FINALIZATION()

    # We can finalize it
    assert market.tryFinalize()
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()


@mark.parametrize('makeReport, finalizeByMigration', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_forking(reportingFixture, makeReport, finalizeByMigration):
    # Proceed to the FORKING phase
    proceedToForking(reportingFixture, makeReport)

    # Finalize the market
    finalizeForkingMarket(reportingFixture, finalizeByMigration)


@mark.parametrize('makeReport, finalizeByMigration', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_forkMigration(reportingFixture, makeReport, finalizeByMigration):
    newMarket = reportingFixture.createReasonableBinaryMarket(reportingFixture.branch, reportingFixture.cash)

    # We proceed the standard market to the FORKING state
    proceedToForking(reportingFixture, makeReport)

    # The market we created is now awaiting migration
    assert newMarket.getReportingState() == reportingFixture.constants.AWAITING_MIGRATION()

    # If we attempt to migrate now it will not work since the forking market is not finalized
    with raises(TransactionFailed, message="Migration cannot occur until the forking market is finalized"):
        newMarket.migrateThroughOneFork()

    # We'll finalize the forking market
    finalizeForkingMarket(reportingFixture, finalizeByMigration)

    # Now we can migrate the market to the winning branch
    assert newMarket.migrateThroughOneFork()

    # Now that we're on the correct branch we are back to the LIMITED REPORTING phase
    assert newMarket.getReportingState() == reportingFixture.constants.LIMITED_REPORTING()


# FIXME Test the case where no reports are recieved within a window and it passes into awaiting finalization. It should move the market to the next reporting window.


def proceedToAutomatedReporting(reportingFixture):
    cash = reportingFixture.cash
    market = reportingFixture.binaryMarket
    branch = reportingFixture.branch
    reputationToken = reportingFixture.applySignature('ReputationToken', branch.getReputationToken())
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    # We can't yet do an automated report on the market as it's in the pre reporting phase
    assert market.getReportingState() == reportingFixture.constants.PRE_REPORTING()
    with raises(TransactionFailed, message="Reporting cannot be done in the PRE REPORTING state"):
        market.automatedReport([0,2], sender=tester.k0)

    # Fast forward to the reporting phase time
    reportingWindow = reportingFixture.applySignature('ReportingWindow', branch.getNextReportingWindow())
    reportingFixture.chain.head_state.timestamp = market.getEndTime() + 1

    # This will cause us to be in the AUTOMATED REPORTING phase
    assert market.getReportingState() == reportingFixture.constants.AUTOMATED_REPORTING()

def proceedToLimitedReporting(reportingFixture, makeReport):
    market = reportingFixture.binaryMarket

    proceedToAutomatedReporting(reportingFixture)

    # To proceed to limited reporting we will either dispute an automated report or not make an automated report within the alotted time window for doing so
    if (makeReport):
        assert market.automatedReport([0,2], sender=tester.k0)
        assert market.getReportingState() == reportingFixture.constants.AUTOMATED_DISPUTE()
        assert market.disputeAutomatedReport(sender=tester.k1)
    else:
        reportingFixture.chain.head_state.timestamp = market.getEndTime() + reportingFixture.constants.AUTOMATED_REPORTING_DURATION_SECONDS() + 1

    # We're in the LIMITED REPORTING phase now
    assert market.getReportingState() == reportingFixture.constants.LIMITED_REPORTING()

def proceedToAllReporting(reportingFixture, makeReport):
    cash = reportingFixture.cash
    market = reportingFixture.binaryMarket
    branch = reportingFixture.branch
    reputationToken = reportingFixture.applySignature('ReputationToken', branch.getReputationToken())
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    proceedToLimitedReporting(reportingFixture, makeReport)

    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.LIMITED_DISPUTE()

    assert market.disputeLimitedReporters(sender=tester.k3)

    # We're in the ALL REPORTING phase now
    assert market.getReportingState() == reportingFixture.constants.ALL_REPORTING()

def proceedToForking(reportingFixture, makeReport):
    market = reportingFixture.binaryMarket
    branch = reportingFixture.branch
    reputationToken = reportingFixture.applySignature('ReputationToken', branch.getReputationToken())

    # Proceed to the ALL REPORTING phase
    proceedToAllReporting(reportingFixture, makeReport)

    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    reportingTokenNo = reportingFixture.getReportingToken(market, [2,0])
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,2])

    # We make one report by Tester 3
    registrationToken = reportingFixture.applySignature('RegistrationToken', reportingTokenNo.getRegistrationToken())
    registrationToken.register(sender=tester.k3)
    reportingTokenNo.buy(1, sender=tester.k3)
    assert reportingTokenNo.balanceOf(tester.a3) == 1
    assert reputationToken.balanceOf(tester.a3) == 1 * 10 ** 6 * 10 ** 18 - 2 * 10 ** 18 - 11 * 10 ** 21 - 1
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenNo.getPayoutDistributionHash()

    # To progress into the ALL DISPUTE phase we move time forward
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.ALL_DISPUTE()

    # Making a dispute at this phase will progress the market into FORKING
    assert market.disputeAllReporters(sender=tester.k0)
    assert market.getReportingState() == reportingFixture.constants.FORKING()

def finalizeForkingMarket(reportingFixture, finalizeByMigration):
    market = reportingFixture.binaryMarket
    branch = reportingFixture.branch
    reputationToken = reportingFixture.applySignature('ReputationToken', branch.getReputationToken())

    # The universe forks and there is now a branch where NO and YES are the respective outcomes of each
    noBranch = reportingFixture.getChildBranch(branch, market, [2,0])
    noBranchReputationToken = reportingFixture.applySignature('ReputationToken', noBranch.getReputationToken())
    assert noBranch.address != branch.address
    yesBranch = reportingFixture.getChildBranch(branch, market, [0,2])
    yesBranchReputationToken = reportingFixture.applySignature('ReputationToken', yesBranch.getReputationToken())
    assert yesBranch.address != branch.address
    assert yesBranch.address != noBranch.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated and not enough time has passed
    assert market.tryFinalize() == 0

    # Tester 1 moves their ~1 Million REP to the YES branch
    balance = reputationToken.balanceOf(tester.a1)
    reputationToken.migrateOut(yesBranchReputationToken.address, tester.a1, reputationToken.balanceOf(tester.a1), sender = tester.k1)
    assert not reputationToken.balanceOf(tester.a1)
    assert yesBranchReputationToken.balanceOf(tester.a1) == balance

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    assert market.tryFinalize() == 0

    reportingTokenNo = reportingFixture.getReportingToken(market, [2,0])
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,2])

    winningTokenAddress = reportingTokenYes.address

    if (finalizeByMigration):
        # Testers 0 and 2 move their combined ~9 million REP to the NO branch
        tester0Balance = reputationToken.balanceOf(tester.a0)
        reputationToken.migrateOut(noBranchReputationToken.address, tester.a0, reputationToken.balanceOf(tester.a0), sender = tester.k0)
        assert not reputationToken.balanceOf(tester.a0)
        assert noBranchReputationToken.balanceOf(tester.a0) == tester0Balance
        tester2Balance = reputationToken.balanceOf(tester.a2)
        reputationToken.migrateOut(noBranchReputationToken.address, tester.a2, reputationToken.balanceOf(tester.a2), sender = tester.k2)
        assert not reputationToken.balanceOf(tester.a2)
        assert noBranchReputationToken.balanceOf(tester.a2) == tester2Balance
        winningTokenAddress = reportingTokenNo.address
    else:
        # Time marches on past the fork end time
        reportingFixture.chain.head_state.timestamp = branch.getForkEndTime() + 1

    # We can finalize the market now
    assert market.tryFinalize()

    # The market is now finalized
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()
    assert market.getFinalWinningReportingToken() == winningTokenAddress

@fixture(scope="session")
def reportingSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    # Seed legacy rep contract
    legacyRepContract = sessionFixture.contracts['LegacyRepContract']
    legacyRepContract.faucet(long(11 * 10**6 * 10**18))
    branch = sessionFixture.branch
    market = sessionFixture.binaryMarket

    # Get the reputation token for this branch and migrate legacy REP to it
    reputationToken = sessionFixture.applySignature('ReputationToken', branch.getReputationToken())
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract()

    # Give some REP to testers to make things interesting
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    reportingWindow = sessionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    firstRegistrationToken = sessionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())
    reportingTokenNo = sessionFixture.getReportingToken(market, [2,0])
    reportingTokenYes = sessionFixture.getReportingToken(market, [0,2])

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

@fixture
def reportingFixture(sessionFixture, reportingSnapshot):
    sessionFixture.chain.revert(reportingSnapshot)
    return sessionFixture
