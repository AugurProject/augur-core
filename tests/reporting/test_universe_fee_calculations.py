from ethereum.tools import tester
from ethereum.tools.tester import ABIContract
from pytest import fixture, mark
from reporting_utils import proceedToRound1Reporting, initializeReportingFixture

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
    # The target reporter gas cost is an attempt to charge the market creator for the estimated cost of reporting that may occur for their market. With no previous reporting window to base costs off of it assumes basic default values

    targetReporterGasCosts = universe.getTargetReporterGasCosts()
    expectedTargetReporterGasCost = contractsFixture.contracts['Constants'].GAS_TO_REPORT()
    expectedTargetReporterGasCost *= contractsFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()
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
def test_target_reporter_gas_costs(numReports, gasPrice, reportingFixture, universe, market):
    # The target reporter gas cost is an attempt to charge the market creator for the estimated cost of reporting that may occur for their market. It will use the previous reporting window's data to estimate costs if it is available
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    # We'll have a market go through basic reporting and then make its reporting window over.
    proceedToRound1Reporting(reportingFixture, universe, market, False, tester.k1, [0,10**18], [10**18,0])

    reportingTokenYes = reportingFixture.getReportingToken(market, [0,10**18])
    for i in range(0,numReports):
        assert reportingTokenYes.buy(1, sender=getattr(tester, 'k%i' % i), gasprice=gasPrice)

    # Now we'll skip ahead in time and finalzie the market
    reportingFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()

    actualAvgGasPrice = reportingWindow.getAvgReportingGasPrice()
    expectedAvgReportingGasCost = (reportingFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE() + gasPrice * numReports) / (numReports + 1)
    assert actualAvgGasPrice == expectedAvgReportingGasCost

    # Confirm our estimated gas cost is caluclated as expected
    expectedTargetReporterGasCost = reportingFixture.contracts['Constants'].GAS_TO_REPORT()
    expectedTargetReporterGasCost *= expectedAvgReportingGasCost
    expectedTargetReporterGasCost *= 2
    targetReporterGasCosts = universe.getTargetReporterGasCosts()
    assert targetReporterGasCosts == expectedTargetReporterGasCost

@fixture(scope="session")
def reportingSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    return initializeReportingFixture(fixture, kitchenSinkSnapshot['universe'], kitchenSinkSnapshot['binaryMarket'])

@fixture
def reportingFixture(fixture, reportingSnapshot):
    fixture.resetToSnapshot(reportingSnapshot)
    return fixture

@fixture
def universe(reportingFixture, kitchenSinkSnapshot):
    return ABIContract(reportingFixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)


@fixture
def market(reportingFixture, kitchenSinkSnapshot):
    return ABIContract(reportingFixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
