from ethereum.tools import tester
from ethereum.tools.tester import ABIContract
from pytest import fixture, mark
from reporting_utils import proceedToInitialReporting, proceedToNextRound

ONE = 10 ** 18

@mark.parametrize('numWithCondition, targetWithConditionPerHundred, previousAmount, expectedValue', [
    # No change
    (1, 1, ONE, ONE),
    (5, 5, ONE, ONE),
    (1, 1, 5 * ONE, 5 * ONE),

    # Maximum Decrease
    (0, 1, 2 * ONE, ONE),
    (0, 50, 2 * ONE, ONE),
    (0, 1, 10 * ONE, 5 * ONE),

    # Maximum Increase
    (100, 1, ONE, 2 * ONE),
    (100, 50, ONE, 2 * ONE),
    (100, 1, 10 * ONE, 20 * ONE),

    # Decrease
    (1, 10, 10 * ONE, 5.5 * ONE),
    (2, 10, 10 * ONE, 6 * ONE),
    (4, 10, 10 * ONE, 7 * ONE),
    (8, 10, 10 * ONE, 9 * ONE),
    (9, 10, 10 * ONE, 9.5 * ONE),

    # Increase
    (51, 50, 10 * ONE, 10.2 * ONE),
    (55, 50, 10 * ONE, 11 * ONE),
    (60, 50, 10 * ONE, 12 * ONE),
    (80, 50, 10 * ONE, 16 * ONE),
    (90, 50, 10 * ONE, 18 * ONE),

    #Floor test
    (0, 1, ONE / 100, ONE / 100),
])
def test_floating_amount_calculation(numWithCondition, targetWithConditionPerHundred, previousAmount, expectedValue, contractsFixture, universe):
    targetDivisor = 100 / targetWithConditionPerHundred
    newAmount = universe.calculateFloatingValue(numWithCondition, 100, targetDivisor, previousAmount, contractsFixture.contracts['Constants'].DEFAULT_VALIDITY_BOND(), ONE / 100)
    assert newAmount == expectedValue

def test_reporter_fees(contractsFixture, universe, market):
    defaultValue = 100
    completeSets = contractsFixture.contracts['CompleteSets']

    assert universe.getOrCacheReportingFeeDivisor() == defaultValue

    # Generate OI
    assert universe.getOpenInterestInAttoEth() == 0
    cost = 10 * market.getNumTicks()
    completeSets.publicBuyCompleteSets(market.address, 10, sender = tester.k1, value = cost)
    assert universe.getOpenInterestInAttoEth() > 0

    # Move dispute window forward
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)

    assert universe.getOrCacheReportingFeeDivisor() != defaultValue

def test_validity_bond_up(contractsFixture, universe, market):
    initialValidityBond = universe.getOrCacheValidityBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will admit the market is invalid
    payoutNumerators = [10000, 0, 0]
    assert market.doInitialReport(payoutNumerators, "")

    # Move time forward to finalize the market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the validity bond is now doubled in the next dispute window
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    newValidityBond = universe.getOrCacheValidityBond()
    assert newValidityBond == initialValidityBond * 2

def test_validity_bond_min(contractsFixture, universe, market):
    initialValidityBond = universe.getOrCacheValidityBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will report the market had a normal resolution
    payoutNumerators = [0, 0, 10000]
    assert market.doInitialReport(payoutNumerators, "")

    # Move time forward to finalize the market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the validity bond stayed the same since it is at the minimum value
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    newValidityBond = universe.getOrCacheValidityBond()
    assert newValidityBond == initialValidityBond

def test_validity_bond_down(contractsFixture, universe, market, scalarMarket, cash):
    initialValidityBond = universe.getOrCacheValidityBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will admit the market is invalid
    payoutNumerators = [10000, 0, 0]
    assert market.doInitialReport(payoutNumerators, "")

    # Move time forward into the dispute window and report on the other market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getStartTime() + 1)
    payoutNumerators = [0, 200000, 200000]
    assert scalarMarket.doInitialReport(payoutNumerators, "")

    # And then move time forward further and finalize the first market
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the validity bond is now doubled
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    newValidityBond = universe.getOrCacheValidityBond()
    assert newValidityBond == initialValidityBond * 2

    # Move time forward to finalize the other market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', scalarMarket.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert scalarMarket.finalize()

    # Confirm that the validity bond is now halved
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    finalValidityBond = universe.getOrCacheValidityBond()
    assert finalValidityBond == newValidityBond / 2

def test_dr_report_stake_up(contractsFixture, universe, market):
    designatedReportStake = universe.getOrCacheDesignatedReportStake()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will report
    numTicks = market.getNumTicks()
    payoutNumerators = [0, numTicks, 0]
    assert market.doInitialReport(payoutNumerators, "")

    # Proceed to the next round so we can dispute the DR
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getStartTime() + 1)
    payoutNumerators = [0, 0, numTicks]
    chosenPayoutHash = market.derivePayoutDistributionHash(payoutNumerators)
    amount = 2 * market.getParticipantStake() - 3 * market.getStakeInOutcome(chosenPayoutHash)
    assert market.contribute(payoutNumerators, amount, "")

    # Move time forward to finalize the market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond is now doubled in the next dispute window
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    newDesignatedReportStake = universe.getOrCacheDesignatedReportStake()
    assert newDesignatedReportStake == designatedReportStake * 2

def test_dr_report_stake_min(contractsFixture, universe, market):
    designatedReportStake = universe.getOrCacheDesignatedReportStake()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will report
    numTicks = market.getNumTicks()
    payoutNumerators = [0, numTicks, 0]
    assert market.doInitialReport(payoutNumerators, "")

    # Move time forward to finalize the market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond doesn't change since it is at the minimum value
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    newDesignatedReportStake = universe.getOrCacheDesignatedReportStake()
    assert newDesignatedReportStake == designatedReportStake

def test_dr_report_stake_down(contractsFixture, universe, market, cash):
    designatedReportStake = universe.getOrCacheDesignatedReportStake()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will report
    numTicks = market.getNumTicks()
    payoutNumerators = [0, numTicks, 0]
    assert market.doInitialReport(payoutNumerators, "")

    # Proceed to the next round so we can dispute the DR
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getStartTime() + 1)
    payoutNumerators = [0, 0, numTicks]
    chosenPayoutHash = market.derivePayoutDistributionHash(payoutNumerators)
    amount = 2 * market.getParticipantStake() - 3 * market.getStakeInOutcome(chosenPayoutHash)
    assert market.contribute(payoutNumerators, amount, "")

    # Move time forward to finalize the market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond is now doubled in the next dispute window
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    newDesignatedReportStake = universe.getOrCacheDesignatedReportStake()
    assert newDesignatedReportStake == designatedReportStake * 2

    # Now we'll allow a window to pass with no markets and see the bond decrease
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert universe.getOrCacheDesignatedReportStake() == designatedReportStake

def test_no_show_bond_up(contractsFixture, universe, market):
    noShowBond = universe.getOrCacheDesignatedReportNoShowBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will be absent and we'll do an initial report as another user
    numTicks = market.getNumTicks()
    payoutNumerators = [0, numTicks, 0]
    assert market.doInitialReport(payoutNumerators, "", sender=tester.k1)

    # Move time forward to finalize the market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond is now doubled in the next dispute window
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    newNoShowBond = universe.getOrCacheDesignatedReportNoShowBond()
    assert newNoShowBond == noShowBond * 2

def test_no_show_bond_min(contractsFixture, universe, market):
    noShowBond = universe.getOrCacheDesignatedReportNoShowBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will show up
    numTicks = market.getNumTicks()
    payoutNumerators = [0, numTicks, 0]
    assert market.doInitialReport(payoutNumerators, "")

    # Move time forward to finalize the market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond does not reduce below the original value
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    newNoShowBond = universe.getOrCacheDesignatedReportNoShowBond()
    assert newNoShowBond == noShowBond

def test_no_show_bond_down(contractsFixture, universe, market, cash):
    noShowBond = universe.getOrCacheDesignatedReportNoShowBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will be absent and we'll do an initial report as another user
    numTicks = market.getNumTicks()
    payoutNumerators = [0, numTicks, 0]
    assert market.doInitialReport(payoutNumerators, "", sender=tester.k1)

    # Move time forward to finalize the market
    disputeWindow = contractsFixture.applySignature('DisputeWindow', market.getDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond is now doubled in the next dispute window
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    newNoShowBond = universe.getOrCacheDesignatedReportNoShowBond()
    assert newNoShowBond == noShowBond * 2

    # Wait for a dispute window with no markets to se the bond decrease
    disputeWindow = contractsFixture.applySignature('DisputeWindow', universe.getOrCreateCurrentDisputeWindow())
    contractsFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert universe.getOrCacheDesignatedReportNoShowBond() == noShowBond

@fixture(scope="session")
def reportingSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    # Give some REP to testers to make things interesting
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    return fixture.createSnapshot()

@fixture
def reportingFixture(fixture, reportingSnapshot):
    fixture.resetToSnapshot(reportingSnapshot)
    return fixture
