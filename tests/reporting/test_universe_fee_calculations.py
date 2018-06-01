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

def test_default_target_reporter_gas_costs(contractsFixture, universe, market):
    # The target reporter gas cost is an attempt to charge the market creator for the estimated cost of reporting that may occur for their market. With no previous fee window to base costs off of it assumes basic default values

    targetReporterGasCosts = universe.getOrCacheTargetReporterGasCosts()
    expectedTargetReporterGasCost = contractsFixture.contracts['Constants'].GAS_TO_REPORT()
    expectedTargetReporterGasCost *= contractsFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()
    expectedTargetReporterGasCost *= 2
    assert targetReporterGasCosts == expectedTargetReporterGasCost

@mark.parametrize('numReports, gasPrice', [
    (1, 1),
    (2, 1),
    (3, 1),
    (3, 1),
    (2, 10),
    (2, 20),
    (2, 100),
])
def test_initial_reporter_gas_costs(numReports, gasPrice, reportingFixture, universe, market, categoricalMarket, scalarMarket):
    markets = [market, categoricalMarket, scalarMarket]

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(reportingFixture, market)

    for i in range(0, numReports):
        curMarket = markets[i]
        payoutNumerators = [0] * curMarket.getNumberOfOutcomes()
        payoutNumerators[0] = curMarket.getNumTicks()
        assert curMarket.doInitialReport(payoutNumerators, False, sender=tester.k1, gasprice=gasPrice)

    # The target reporter gas cost is an attempt to charge the market creator for the estimated cost of reporting that may occur for their market. It will use the previous fee window's data to estimate costs if it is available
    feeWindow = reportingFixture.applySignature('FeeWindow', market.getFeeWindow())

    # Now we'll skip ahead in time and finalize the market
    reportingFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    for i in range(0, numReports):
        assert markets[i].finalize()

    actualAvgGasPrice = feeWindow.getAvgReportingGasPrice()
    expectedAvgReportingGasCost = (reportingFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE() + gasPrice * numReports) / (numReports + 1)
    assert actualAvgGasPrice == expectedAvgReportingGasCost

    # Confirm our estimated gas cost is caluclated as expected
    expectedTargetReporterGasCost = reportingFixture.contracts['Constants'].GAS_TO_REPORT()
    expectedTargetReporterGasCost *= expectedAvgReportingGasCost
    expectedTargetReporterGasCost *= 2
    targetReporterGasCosts = universe.getOrCacheTargetReporterGasCosts()
    assert targetReporterGasCosts == expectedTargetReporterGasCost

def test_reporter_fees(contractsFixture, universe, market):
    defaultValue = 100
    completeSets = contractsFixture.contracts['CompleteSets']

    assert universe.getOrCacheReportingFeeDivisor() == defaultValue

    # Generate OI
    assert universe.getOpenInterestInAttoEth() == 0
    cost = 10 * market.getNumTicks()
    completeSets.publicBuyCompleteSets(market.address, 10, sender = tester.k1, value = cost)
    assert universe.getOpenInterestInAttoEth() > 0

    # Move fee window forward
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    assert universe.getOrCacheReportingFeeDivisor() != defaultValue

def test_validity_bond_up(contractsFixture, universe, market):
    initialValidityBond = universe.getOrCacheValidityBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will admit the market is invalid
    payoutNumerators = [5000, 5000]
    assert market.doInitialReport(payoutNumerators, True)

    # Move time forward to finalize the market
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the validity bond is now doubled in the next fee window
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    newValidityBond = universe.getOrCacheValidityBond()
    assert newValidityBond == initialValidityBond * 2

def test_validity_bond_min(contractsFixture, universe, market):
    initialValidityBond = universe.getOrCacheValidityBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will report the market had a normal resolution
    payoutNumerators = [0, 10000]
    assert market.doInitialReport(payoutNumerators, False)

    # Move time forward to finalize the market
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the validity bond stayed the same since it is at the minimum value
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    newValidityBond = universe.getOrCacheValidityBond()
    assert newValidityBond == initialValidityBond

def test_validity_bond_down(contractsFixture, universe, market, scalarMarket, cash):
    initialValidityBond = universe.getOrCacheValidityBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will admit the market is invalid
    payoutNumerators = [5000, 5000]
    assert market.doInitialReport(payoutNumerators, True)

    # Move time forward into the fee window and report on the other market
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    payoutNumerators = [200000, 200000]
    assert scalarMarket.doInitialReport(payoutNumerators, False)

    # And then move time forward further and finalize the first market
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the validity bond is now doubled
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    newValidityBond = universe.getOrCacheValidityBond()
    assert newValidityBond == initialValidityBond * 2

    # Move time forward to finalize the other market
    feeWindow = contractsFixture.applySignature('FeeWindow', scalarMarket.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert scalarMarket.finalize()

    # Confirm that the validity bond is now halved
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    finalValidityBond = universe.getOrCacheValidityBond()
    assert finalValidityBond == newValidityBond / 2

def test_dr_report_stake_up(contractsFixture, universe, market):
    designatedReportStake = universe.getOrCacheDesignatedReportStake()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will report
    numTicks = market.getNumTicks()
    payoutNumerators = [numTicks, 0]
    assert market.doInitialReport(payoutNumerators, False)

    # Proceed to the next round so we can dispute the DR
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    payoutNumerators = [0, numTicks]
    chosenPayoutHash = market.derivePayoutDistributionHash(payoutNumerators, False)
    amount = 2 * market.getParticipantStake() - 3 * market.getStakeInOutcome(chosenPayoutHash)
    assert market.contribute(payoutNumerators, False, amount)

    # Move time forward to finalize the market
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond is now doubled in the next fee window
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    newDesignatedReportStake = universe.getOrCacheDesignatedReportStake()
    assert newDesignatedReportStake == designatedReportStake * 2

def test_dr_report_stake_min(contractsFixture, universe, market):
    designatedReportStake = universe.getOrCacheDesignatedReportStake()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will report
    numTicks = market.getNumTicks()
    payoutNumerators = [numTicks, 0]
    assert market.doInitialReport(payoutNumerators, False)

    # Move time forward to finalize the market
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond doesn't change since it is at the minimum value
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    newDesignatedReportStake = universe.getOrCacheDesignatedReportStake()
    assert newDesignatedReportStake == designatedReportStake

def test_dr_report_stake_down(contractsFixture, universe, market, cash):
    designatedReportStake = universe.getOrCacheDesignatedReportStake()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will report
    numTicks = market.getNumTicks()
    payoutNumerators = [numTicks, 0]
    assert market.doInitialReport(payoutNumerators, False)

    # Proceed to the next round so we can dispute the DR
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    payoutNumerators = [0, numTicks]
    chosenPayoutHash = market.derivePayoutDistributionHash(payoutNumerators, False)
    amount = 2 * market.getParticipantStake() - 3 * market.getStakeInOutcome(chosenPayoutHash)
    assert market.contribute(payoutNumerators, False, amount)

    # Move time forward to finalize the market
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond is now doubled in the next fee window
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    newDesignatedReportStake = universe.getOrCacheDesignatedReportStake()
    assert newDesignatedReportStake == designatedReportStake * 2

    # Now we'll allow a window to pass with no markets and see the bond decrease
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert universe.getOrCacheDesignatedReportStake() == designatedReportStake

def test_no_show_bond_up(contractsFixture, universe, market):
    noShowBond = universe.getOrCacheDesignatedReportNoShowBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will be absent and we'll do an initial report as another user
    numTicks = market.getNumTicks()
    payoutNumerators = [numTicks, 0]
    assert market.doInitialReport(payoutNumerators, False, sender=tester.k1)

    # Move time forward to finalize the market
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond is now doubled in the next fee window
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    newNoShowBond = universe.getOrCacheDesignatedReportNoShowBond()
    assert newNoShowBond == noShowBond * 2

def test_no_show_bond_min(contractsFixture, universe, market):
    noShowBond = universe.getOrCacheDesignatedReportNoShowBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will show up
    numTicks = market.getNumTicks()
    payoutNumerators = [numTicks, 0]
    assert market.doInitialReport(payoutNumerators, False)

    # Move time forward to finalize the market
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond does not reduce below the original value
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    newNoShowBond = universe.getOrCacheDesignatedReportNoShowBond()
    assert newNoShowBond == noShowBond

def test_no_show_bond_down(contractsFixture, universe, market, cash):
    noShowBond = universe.getOrCacheDesignatedReportNoShowBond()

    # We'll have the markets go to initial reporting
    proceedToInitialReporting(contractsFixture, market)

    # The DR will be absent and we'll do an initial report as another user
    numTicks = market.getNumTicks()
    payoutNumerators = [numTicks, 0]
    assert market.doInitialReport(payoutNumerators, False, sender=tester.k1)

    # Move time forward to finalize the market
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Confirm that the report stake bond is now doubled in the next fee window
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    newNoShowBond = universe.getOrCacheDesignatedReportNoShowBond()
    assert newNoShowBond == noShowBond * 2

    # Wait for a fee window with no markets to se the bond decrease
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())
    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
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
