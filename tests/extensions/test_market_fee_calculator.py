from ethereum.tools import tester
from pytest import fixture, mark
from reporting_utils import proceedToLimitedReporting, initializeReportingFixture

ONE = 10 ** 18

@mark.parametrize('numInvalid, targetInvalidPerHundred, previousBond, expectedValue', [
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
])
def test_validity_bond_calculation(numInvalid, targetInvalidPerHundred, previousBond, expectedValue, contractsFixture):
    feeCalculator = contractsFixture.contracts["MarketFeeCalculator"]
    targetInvalidDivisor = 100 / targetInvalidPerHundred
    newBond = feeCalculator.calculateValidityBond(numInvalid, 100, targetInvalidDivisor, previousBond)
    assert newBond == expectedValue

def test_default_target_reporter_gas_costs(contractsFixture):
    # The target reporter gas cost is an attempt to charge the market creator for the estimated cost of reporting that may occur for their market. With no previous reporting window to base costs off of it assumes basic default values
    feeCalculator = contractsFixture.contracts["MarketFeeCalculator"]
    market = contractsFixture.binaryMarket

    targetReporterGasCosts = feeCalculator.getTargetReporterGasCosts(market.getReportingWindow())
    expectedTargetReporterGasCost = contractsFixture.constants.GAS_TO_REPORT()
    expectedTargetReporterGasCost *= contractsFixture.constants.DEFAULT_REPORTING_GAS_PRICE()
    expectedTargetReporterGasCost *= contractsFixture.constants.DEFAULT_REPORTS_PER_MARKET()
    expectedTargetReporterGasCost *= 2
    assert targetReporterGasCosts == expectedTargetReporterGasCost

@mark.parametrize('numReports, gasPrice', [
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 1),
    (2, 10),
    (2, 20),
    (2, 100),
])
def test_target_reporter_gas_costs(numReports, gasPrice, reportingFixture):
    # The target reporter gas cost is an attempt to charge the market creator for the estimated cost of reporting that may occur for their market. It will use the previous reporting window's data to estimate costs if it is available
    feeCalculator = reportingFixture.contracts["MarketFeeCalculator"]
    market = reportingFixture.binaryMarket
    universe = reportingFixture.universe
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    # We'll have a market go through basic reporting and then make its reporting window over.
    proceedToLimitedReporting(reportingFixture, market, False, tester.k1, [0,10**18])

    reportingTokenYes = reportingFixture.getReportingToken(market, [0,10**18])
    for i in range(0,numReports):
        assert reportingTokenYes.buy(1, sender=getattr(tester, 'k%i' % i), gasprice=gasPrice)

    # Now we'll skip ahead in time and finalzie the market
    reportingFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()

    actualAvgReportsPerMarket = reportingWindow.getAvgReportsPerMarket()
    expectedAvgReportsPerMarket = (reportingFixture.constants.DEFAULT_REPORTS_PER_MARKET() + numReports) / 2
    assert actualAvgReportsPerMarket == expectedAvgReportsPerMarket

    actualAvgGasPrice = reportingWindow.getAvgReportingGasCost()
    expectedAvgReportingGasCost = (reportingFixture.constants.DEFAULT_REPORTING_GAS_PRICE() + gasPrice * numReports) / (numReports + 1)
    assert actualAvgGasPrice == expectedAvgReportingGasCost

    # Confirm our estimated gas cost is caluclated as expected
    expectedTargetReporterGasCost = reportingFixture.constants.GAS_TO_REPORT()
    expectedTargetReporterGasCost *= expectedAvgReportingGasCost
    expectedTargetReporterGasCost *= expectedAvgReportsPerMarket
    expectedTargetReporterGasCost *= 2
    targetReporterGasCosts = feeCalculator.getTargetReporterGasCosts(universe.getCurrentReportingWindow())
    assert targetReporterGasCosts == expectedTargetReporterGasCost 

@fixture(scope="session")
def reportingSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    return initializeReportingFixture(sessionFixture, sessionFixture.binaryMarket)

@fixture
def reportingFixture(sessionFixture, reportingSnapshot):
    sessionFixture.chain.revert(reportingSnapshot)
    return sessionFixture
