from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from reporting_utils import proceedToDesignatedReporting, proceedToFirstReporting, initializeReportingFixture

def test_one_market_one_correct_report(reportingTokenPayoutFixture):
    market = reportingTokenPayoutFixture.market1
    reportingWindow = reportingTokenPayoutFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = reportingTokenPayoutFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    marketFeeCalculator = reportingTokenPayoutFixture.contracts["MarketFeeCalculator"]

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(reportingTokenPayoutFixture, market, [0,10**18])

    # To progress into the DESIGNATED DISPUTE phase we do a designated report
    initialRepBalance = reputationToken.balanceOf(tester.a0)
    assert reportingTokenPayoutFixture.designatedReport(market, [0,10**18], tester.k0)
    # The market owner gets back the no-show REP bond, which cancels out the amount used to pay for the required dispute tokens
    assert reputationToken.balanceOf(tester.a0) == initialRepBalance + marketFeeCalculator.getDesignatedReportNoShowBond(market.getUniverse()) - marketFeeCalculator.getDesignatedReportStake(market.getUniverse())
    initialREPBalance = reputationToken.balanceOf(tester.a0)

    # We're now in the DESIGNATED DISPUTE PHASE
    assert market.getReportingState() == reportingTokenPayoutFixture.constants.DESIGNATED_DISPUTE()

    # Time passes until the end of the reporting window
    reportingTokenPayoutFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # Finalize the market
    market.tryFinalize()

    # The designated reporter may redeem their reporting tokens which were purchased to make the designated report
    reportingToken = reportingTokenPayoutFixture.getReportingToken(market, [0, 10**18])
    assert reportingToken.balanceOf(tester.a0) == marketFeeCalculator.getDesignatedReportStake(market.getUniverse())

    expectedREPBalance = initialREPBalance

    # We can see that the designated reporter's balance of REP has returned to the original value since as the market creator the had to pay these REP fees initially
    assert reputationToken.balanceOf(tester.a0) == expectedREPBalance

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
    reportingToken = fixture.getReportingToken(market, [0,10**18])

    for i in range(0, numCorrectReporters):
        testerAddress = fixture.testerAddress[i]
        initialREPBalance = reputationToken.balanceOf(testerAddress)
        assert reportingToken.redeemWinningTokens(sender=fixture.testerKey[i])
        expectedRep = initialREPBalance + 10
        if (i == 0):
            expectedRep += marketFeeCalculator.getDesignatedReportNoShowBond(market.getUniverse())
        assert reputationToken.balanceOf(testerAddress) == expectedRep

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
