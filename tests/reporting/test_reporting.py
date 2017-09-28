from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from reporting_utils import proceedToDesignatedReporting, proceedToLimitedReporting, proceedToAllReporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

tester.STARTGAS = long(6.7 * 10**6)

def test_reportingFullHappyPath(reportingFixture):
    cash = reportingFixture.cash
    market = reportingFixture.binaryMarket
    universe = reportingFixture.universe
    reputationToken = reportingFixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingTokenNo = reportingFixture.getReportingToken(market, [10**18,0])
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,10**18])

    # We can't yet report on the market as it's in the pre reporting phase
    assert market.getReportingState() == reportingFixture.constants.PRE_REPORTING()
    with raises(TransactionFailed, message="Reporting cannot be done in the PRE REPORTING state"):
        reportingTokenNo.buy(100, sender=tester.k0)

    # Fast forward to one second after the next reporting window
    reportingWindow = reportingFixture.applySignature('ReportingWindow', universe.getNextReportingWindow())
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
    assert universe.isContainerForMarket(market.address)
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
    assert universe.getForkingMarket() == market.address
    assert not reportingWindow.isContainerForMarket(market.address)
    assert universe.isContainerForMarket(market.address)
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)
    assert market.getReportingState() == reportingFixture.constants.FORKING()

    # The universe forks and there is now a universe where NO and YES are the respective outcomes of each
    noUniverse = reportingFixture.getOrCreateChildUniverse(universe, market, [10**18,0])
    noUniverseReputationToken = reportingFixture.applySignature('ReputationToken', noUniverse.getReputationToken())
    assert noUniverse.address != universe.address
    yesUniverse = reportingFixture.getOrCreateChildUniverse(universe, market, [0,10**18])
    yesUniverseReputationToken = reportingFixture.applySignature('ReputationToken', yesUniverse.getReputationToken())
    assert yesUniverse.address != universe.address
    assert yesUniverse.address != noUniverse.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated
    assert market.tryFinalize() == 0

    # Tester 1 moves their ~1 Million REP to the YES universe
    reputationToken.migrateOut(yesUniverseReputationToken.address, tester.a1, reputationToken.balanceOf(tester.a1), sender = tester.k1)
    assert not reputationToken.balanceOf(tester.a1)
    assert yesUniverseReputationToken.balanceOf(tester.a1) == 1 * 10**6 * 10**18 - 10**18 - 101 - 110000 * 10**18

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    assert market.tryFinalize() == 0

    # Testers 0 and 2 move their combined ~9 million REP to the NO universe
    reputationToken.migrateOut(noUniverseReputationToken.address, tester.a0, reputationToken.balanceOf(tester.a0), sender = tester.k0)
    assert not reputationToken.balanceOf(tester.a0)
    assert noUniverseReputationToken.balanceOf(tester.a0) == 8 * 10 ** 6 * 10 ** 18 - 10 ** 18 - 100 - 11000 * 10 ** 18
    reputationToken.migrateOut(noUniverseReputationToken.address, tester.a2, reputationToken.balanceOf(tester.a2), sender = tester.k2)
    assert not reputationToken.balanceOf(tester.a2)
    assert noUniverseReputationToken.balanceOf(tester.a2) == 1 * 10 ** 6 * 10 ** 18 - 2 * 10 ** 18 - 2

    # We can finalize the market now since a mjaority of REP has moved. Alternatively we could "reportingFixture.chain.head_state.timestamp = universe.getForkEndTime() + 1" to move
    assert market.tryFinalize()

    # The market is now finalized and the NO outcome is the winner
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()
    assert market.getFinalWinningReportingToken() == reportingTokenNo.address

    # We can redeem forked REP on any universe we didn't dispute
    assert reportingTokenNo.redeemForkedTokens(sender = tester.k0)
    assert noUniverseReputationToken.balanceOf(tester.a0) == 8 * 10 ** 6 * 10 ** 18 -10 ** 18 - 11000 * 10 ** 18


def test_designatedReportingHappyPath(reportingFixture):
    market = reportingFixture.binaryMarket

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(reportingFixture, market, [0,10**18])

    # To progress into the DESIGNATED DISPUTE phase we do a designated report
    assert market.designatedReport([0,10**18], sender=tester.k0)

    # We're now in the DESIGNATED DISPUTE PHASE
    assert market.getReportingState() == reportingFixture.constants.DESIGNATED_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    reportingFixture.chain.head_state.timestamp = market.getEndTime() + reportingFixture.constants.DESIGNATED_REPORTING_DURATION_SECONDS() + reportingFixture.constants.DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS() + 1

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
    universe = reportingFixture.universe
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = reportingFixture.applySignature('ReputationToken', universe.getReputationToken())

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(reportingFixture, market, makeReport, tester.k1, [0,10**18])

    # We make one report by Tester 2
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,10**18])
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
    universe = reportingFixture.universe
    reputationToken = reportingFixture.applySignature('ReputationToken', universe.getReputationToken())

    # Proceed to the ALL REPORTING phase
    proceedToAllReporting(reportingFixture, market, makeReport, tester.k1, tester.k3, [0,10**18], tester.k2, [10**18,0])

    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    # We make one report by Tester 3 for the NO outcome
    reportingTokenNo = reportingFixture.getReportingToken(market, [10**18,0])
    registrationToken = reportingFixture.applySignature('RegistrationToken', reportingTokenNo.getRegistrationToken())
    registrationToken.register(sender=tester.k3)
    reportingTokenNo.buy(1, sender=tester.k3)
    assert reportingTokenNo.balanceOf(tester.a3) == 1
    assert reputationToken.balanceOf(tester.a3) == 1 * 10 ** 6 * 10 ** 18 - 2 * 10 ** 18 - 11 * 10 ** 21 - 1
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()

    # If a dispute bond was placed for this outcome it is actually not the tentative winning outcome since the bond amount counts negatively toward its stake
    if (makeReport):
        assert tentativeWinner != reportingTokenNo.getPayoutDistributionHash()
        # If we buy (LIMITED_BOND_AMOUNT - DESIGNATED_BOND_AMOUNT) that will be sufficient to make the outcome win
        negativeBondBalance = reportingFixture.constants.LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT() - reportingFixture.constants.DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
        reportingTokenNo.buy(negativeBondBalance, sender=tester.k3)
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
    market = reportingFixture.binaryMarket
    # Proceed to the FORKING phase
    proceedToForking(reportingFixture, market, makeReport, tester.k1, tester.k3, tester.k3, [0,10**18], tester.k2, [10**18,0], [10**18,0])

    # Finalize the market
    finalizeForkingMarket(reportingFixture, market, finalizeByMigration, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,10**18], [10**18,0])


@mark.parametrize('makeReport, finalizeByMigration', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_forkMigration(reportingFixture, makeReport, finalizeByMigration):
    market = reportingFixture.binaryMarket
    newMarket = reportingFixture.createReasonableBinaryMarket(reportingFixture.universe, reportingFixture.cash)

    # We proceed the standard market to the FORKING state
    proceedToForking(reportingFixture,  market, makeReport, tester.k1, tester.k2, tester.k3, [0,10**18], tester.k2, [10**18,0], [10**18,0])

    # The market we created is now awaiting migration
    assert newMarket.getReportingState() == reportingFixture.constants.AWAITING_FORK_MIGRATION()

    # If we attempt to migrate now it will not work since the forking market is not finalized
    with raises(TransactionFailed, message="Migration cannot occur until the forking market is finalized"):
        newMarket.migrateThroughOneFork()

    # We'll finalize the forking market
    finalizeForkingMarket(reportingFixture, market, finalizeByMigration, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,10**18], [10**18,0])

    # Now we can migrate the market to the winning universe
    assert newMarket.migrateThroughOneFork()

    # Now that we're on the correct universe we are send back to the DESIGNATED REPORTING phase
    assert newMarket.getReportingState() == reportingFixture.constants.DESIGNATED_REPORTING()

@mark.parametrize('pastDisputePhase', [
    True,
    False
])
def test_noReports(reportingFixture, pastDisputePhase):
    market = reportingFixture.binaryMarket

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(reportingFixture, market, False, tester.k1, [0,10**18])

    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    if (pastDisputePhase):
        reportingFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    else:
        reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    
    # If we receive no reports by the time Limited Reporting is finished we will be in the AWAITING NO REPORT MIGRATION phase
    assert market.getReportingState() == reportingFixture.constants.AWAITING_NO_REPORT_MIGRATION()

    # We can try to report on the market, which will move it to the next reporting window where it will be back in LIMITED REPORTING
    reportingToken = reportingFixture.getReportingToken(market, [0,10**18])
    registrationToken = reportingFixture.applySignature('RegistrationToken', reportingToken.getRegistrationToken())

    # We get false back from the attempt to report since we aren't registered for the reporting window it migrates to, but the migration still occurs
    assert reportingToken.buy(1, sender=tester.k2) == False

    assert market.getReportingState() == reportingFixture.constants.LIMITED_REPORTING()
    assert market.getReportingWindow() != reportingWindow.address

@fixture(scope="session")
def reportingSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    return initializeReportingFixture(sessionFixture, sessionFixture.binaryMarket)

@fixture
def reportingFixture(sessionFixture, reportingSnapshot):
    sessionFixture.chain.revert(reportingSnapshot)
    return sessionFixture
