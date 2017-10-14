from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs
from reporting_utils import proceedToDesignatedReporting, proceedToRound1Reporting, proceedToRound2Reporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

@mark.parametrize('makeReport, finalizeByMigration', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_forkMigration(reportingFixture, makeReport, finalizeByMigration):
    market = reportingFixture.binaryMarket
    cash = reportingFixture.cash
    newMarket = reportingFixture.createReasonableBinaryMarket(reportingFixture.universe, cash)
    completeSets = reportingFixture.contracts['CompleteSets']

    # We'll do some transactions that cause fee collection here so we can test that fees are properly migrated automatically when a market migrates from a fork
    cost = 10 * newMarket.getNumTicks()
    completeSets.publicBuyCompleteSets(newMarket.address, 10, sender = tester.k1, value = cost)
    completeSets.publicSellCompleteSets(newMarket.address, 10, sender=tester.k1)
    oldReportingWindowAddress = newMarket.getReportingWindow()
    fees = cash.balanceOf(oldReportingWindowAddress)
    assert fees > 0
    assert cash.balanceOf(oldReportingWindowAddress) == fees

    # We proceed the standard market to the FORKING state
    proceedToForking(reportingFixture,  market, makeReport, tester.k1, tester.k2, tester.k3, [0,10**18], [10**18,0], tester.k2, [10**18,0], [0,10**18], [10**18,0])

    # The market we created is now awaiting migration
    assert newMarket.getReportingState() == reportingFixture.constants.AWAITING_FORK_MIGRATION()

    # If we attempt to migrate now it will not work since the forking market is not finalized
    with raises(TransactionFailed, message="Migration cannot occur until the forking market is finalized"):
        newMarket.migrateThroughOneFork()

    # We'll finalize the forking market
    finalizeForkingMarket(reportingFixture, market, finalizeByMigration, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,10**18], [10**18,0])

    # Now we can migrate the market to the winning universe
    assert newMarket.migrateThroughOneFork()

    # We observe that the reporting window no longer has the fees collected
    assert cash.balanceOf(oldReportingWindowAddress) == 0

    # Now that we're on the correct universe we are send back to the DESIGNATED REPORTING phase
    assert newMarket.getReportingState() == reportingFixture.constants.DESIGNATED_REPORTING()

    # We can confirm that migrating the market also triggered a migration of its reporting window's ETH fees to the new reporting window
    assert cash.balanceOf(newMarket.getReportingWindow()) == fees

@fixture(scope="session")
def reportingSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    return initializeReportingFixture(sessionFixture, sessionFixture.binaryMarket)

@fixture
def reportingFixture(sessionFixture, reportingSnapshot):
    sessionFixture.resetToSnapshot(reportingSnapshot)
    return sessionFixture
