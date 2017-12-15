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
    True
])
def test_forking(finalizeByMigration, localFixture, universe, market, categoricalMarket):
    # proceed to forking
    proceedToFork(localFixture, market, universe)

    # finalize the fork
    finalizeFork(localFixture, market, universe, finalizeByMigration)

def test_fee_window_record_keeping(localFixture, universe, cash, market):
    # do invalid, no show, and incorrect
    pass


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture
