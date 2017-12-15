from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString, TokenDelta
from reporting_utils import proceedToDesignatedReporting, proceedToInitialReporting, proceedToNextRound, proceedToFork, finalizeFork

tester.STARTGAS = long(6.7 * 10**6)

def test_designatedReportHappyPath(localFixture, universe, market):
    # proceed to the designated reporting period
    proceedToDesignatedReporting(localFixture, market)

    # an address that is not the designated reporter cannot report
    with raises(TransactionFailed):
        market.doInitialReport([0, market.getNumTicks()], False, sender=tester.k1)

    # do an initial report as the designated reporter
    assert market.doInitialReport([0, market.getNumTicks()], False)

    # the market is now assigned a fee window
    assert market.getFeeWindow()
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # time marches on and the market can be finalized
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

def test_initialReportHappyPath(localFixture, universe, market):
    # proceed to the initial reporting period
    proceedToInitialReporting(localFixture, market)

    # do an initial report as someone other than the designated reporter
    assert market.doInitialReport([0, market.getNumTicks()], False, sender=tester.k1)

    # the market is now assigned a fee window
    assert market.getFeeWindow()
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # time marches on and the market can be finalized
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

@mark.parametrize('rounds', [
    1,
    2,
    6,
    16
])
def test_roundsOfReporting(rounds, localFixture, market, universe):
    feeWindow = universe.getOrCreateCurrentFeeWindow()

    # proceed through several rounds of disputing
    for i in range(rounds):
        proceedToNextRound(localFixture, market)
        assert feeWindow != market.getFeeWindow()
        feeWindow = market.getFeeWindow()
        assert feeWindow == universe.getCurrentFeeWindow()

@mark.parametrize('finalizeByMigration', [
    True,
    False
])
def test_forking(finalizeByMigration, localFixture, universe, market, categoricalMarket):
    # proceed to forking
    proceedToFork(localFixture, market, universe)

    # finalize the fork
    finalizeFork(localFixture, market, universe, finalizeByMigration)

def test_fee_window_record_keeping(localFixture, universe, cash, market, categoricalMarket, scalarMarket):
    feeWindow = localFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    
    # First we'll confirm we get the expected default values for the window record keeping
    assert feeWindow.getNumMarkets() == 0
    assert feeWindow.getNumInvalidMarkets() == 0
    assert feeWindow.getNumIncorrectDesignatedReportMarkets() == 0
    assert feeWindow.getNumDesignatedReportNoShows() == 0

    # Go to designated reporting
    proceedToDesignatedReporting(localFixture, market)

    # Do a report that we'll make incorrect
    assert market.doInitialReport([0, market.getNumTicks()], False)

    # Do a report for a market we'll say is invalid
    assert categoricalMarket.doInitialReport([0, 0, categoricalMarket.getNumTicks()], False)

    # Designated reporter doesn't show up for the third market. Go into initial reporting and do a report by someone else
    reputationToken = localFixture.applySignature('ReputationToken', universe.getReputationToken())
    reputationToken.transfer(tester.a1, 10**6 * 10**18)
    proceedToInitialReporting(localFixture, scalarMarket)
    assert scalarMarket.doInitialReport([0, scalarMarket.getNumTicks()], False, sender=tester.k1)

    # proceed to the window start time
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # dispute the first market
    chosenPayoutNumerators = [market.getNumTicks(), 0]
    chosenPayoutHash = market.derivePayoutDistributionHash(chosenPayoutNumerators, False)
    amount = 2 * market.getTotalStake() - 3 * market.getStakeInOutcome(chosenPayoutHash)
    assert market.contribute(chosenPayoutNumerators, False, amount)
    assert market.getFeeWindow() != feeWindow

    # dispute the second market with an invalid outcome
    chosenPayoutNumerators = [categoricalMarket.getNumTicks() / 2, categoricalMarket.getNumTicks() / 2]
    chosenPayoutHash = categoricalMarket.derivePayoutDistributionHash(chosenPayoutNumerators, True)
    amount = 2 * categoricalMarket.getTotalStake() - 3 * categoricalMarket.getStakeInOutcome(chosenPayoutHash)
    assert categoricalMarket.contribute(chosenPayoutNumerators, True, amount)
    assert categoricalMarket.getFeeWindow() != feeWindow

    # progress time forward
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    # finalize the markets
    assert market.finalize()
    assert categoricalMarket.finalize()
    assert scalarMarket.finalize()

    # Now we'll confirm the record keeping was updated
    assert feeWindow.getNumMarkets() == 2
    assert feeWindow.getNumInvalidMarkets() == 1
    assert feeWindow.getNumIncorrectDesignatedReportMarkets() == 2

    feeWindow = localFixture.applySignature('FeeWindow', scalarMarket.getFeeWindow())
    assert feeWindow.getNumMarkets() == 1
    assert feeWindow.getNumDesignatedReportNoShows() == 1


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture
