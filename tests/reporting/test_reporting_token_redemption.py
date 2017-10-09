from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from reporting_utils import proceedToDesignatedReporting, proceedToFirstReporting, initializeReportingFixture

''' TODO: Once designated report is in reporting tokens
def test_one_market_one_correct_report(reportingTokenPayoutFixture):
    market = reportingTokenPayoutFixture.market1
    reportingWindow = reportingTokenPayoutFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = reportingTokenPayoutFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    marketFeeCalculator = reportingTokenPayoutFixture.contracts["MarketFeeCalculator"]
    initialETHBalance = reportingTokenPayoutFixture.utils.getETHBalance(tester.a0)

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(reportingTokenPayoutFixture, market, [0,10**18])

    # To progress into the DESIGNATED DISPUTE phase we do a designated report
    assert market.designatedReport([0,10**18], sender=tester.k0)
    # initialREPBalance = reputationToken.balanceOf(tester.a0)

    # We're now in the DESIGNATED DISPUTE PHASE
    assert market.getReportingState() == reportingTokenPayoutFixture.constants.DESIGNATED_DISPUTE()

    # Time passes until the end of the reporting window
    reportingTokenPayoutFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # The designated reporter may redeem their reporting tokens which were purchased to make the designated report
    reportingToken = reportingTokenPayoutFixture.getReportingToken(market, [0, 10**18])
    assert reportingToken.redeemWinningTokens()

    expectedETHBalance = initialETHBalance + marketFeeCalculator.getMarketCreationFee(reportingWindow.address)
    expectedREPBalance = initialREPBalance + marketFeeCalculator.getDesignatedReportStake(reportingWindow.address)

    # We can see that the designated reporter's balance of REP and ETH has increased as expected
    assert reportingTokenPayoutFixture.utils.getETHBalance(tester.a0) == expectedETHBalance
    assert reputationToken.balanceOf(tester.a0) == expectedREPBalance
'''

@mark.parametrize('numReports, numCorrect', [
    (1, 1),
    (2, 2),
    (3, 3),
    (2, 1),
    (3, 2),
    (3, 1),
])
def test_reporting_token_redemption(numReports, numCorrect, reportingTokenPayoutFixture):
    market = reportingTokenPayoutFixture.market1
    reportingWindow = reportingTokenPayoutFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = reportingTokenPayoutFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    marketFeeCalculator = reportingTokenPayoutFixture.contracts["MarketFeeCalculator"]

    # Proceed to FIRST REPORTING
    proceedToFirstReporting(reportingTokenPayoutFixture, market, False, tester.k1, [0,10**18], [10**18,0])

    doReports(reportingTokenPayoutFixture, market, numReports, numCorrect)

    confirmPayouts(reportingTokenPayoutFixture, market, numCorrect)

def doReports(fixture, market, numReporters, numCorrect):
    reportingWindow = fixture.applySignature('ReportingWindow', market.getReportingWindow())
    reportingTokenWinner = fixture.getReportingToken(market, [0,10**18])
    reportingTokenLoser = fixture.getReportingToken(market, [10**18,0])

    for i in range(0, numReporters):
        testerKey = fixture.testerKey[i]
        if numCorrect > 0:
            reportingTokenWinner.buy(10, sender=testerKey)
        else:
            reportingTokenLoser.buy(1, sender=testerKey)
        numCorrect -= 1

    fixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()

def confirmPayouts(fixture, market, numCorrectReporters):
    reportingWindow = fixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = fixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    marketFeeCalculator = fixture.contracts["MarketFeeCalculator"]
    targetReporterGasFeePayout = marketFeeCalculator.getTargetReporterGasCosts(reportingWindow.address) / numCorrectReporters
    reportingToken = fixture.getReportingToken(market, [0,10**18])

    for i in range(0, numCorrectReporters):
        testerAddress = fixture.testerAddress[i]
        initialETHBalance = fixture.utils.getETHBalance(testerAddress)
        initialREPBalance = reputationToken.balanceOf(testerAddress)
        assert reportingToken.redeemWinningTokens(sender=fixture.testerKey[i])
        assert fixture.utils.getETHBalance(testerAddress) == initialETHBalance + targetReporterGasFeePayout
        assert reputationToken.balanceOf(testerAddress) == initialREPBalance + 10

@fixture(scope="session")
def reportingFeePayoutSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    # Move to the next reporting window for these tests as we want to control market creation and reporting in isolation
    originalReportingWindow = sessionFixture.applySignature('ReportingWindow', sessionFixture.binaryMarket.getReportingWindow())
    sessionFixture.chain.head_state.timestamp = originalReportingWindow.getEndTime() + 1
    market = sessionFixture.market1 = sessionFixture.createReasonableBinaryMarket(sessionFixture.universe, sessionFixture.cash)
    return initializeReportingFixture(sessionFixture, market)

@fixture
def reportingTokenPayoutFixture(sessionFixture, reportingFeePayoutSnapshot):
    sessionFixture.resetToSnapshot(reportingFeePayoutSnapshot)
    return sessionFixture
