from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises
from datetime import timedelta
from reporting_utils import proceedToAutomatedReporting, proceedToLimitedReporting, proceedToAllReporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

''' TODO: it should actually be impossible to have a reporting window with 0 markets to report on. The current thinking is to have reporting windows create a special IMarket on creation that will be reported on IFF no markets in the window enter limited reporting
def test_automatedReportingRedemption(registrationTokenRedemptionFixture):
    market = registrationTokenRedemptionFixture.market1
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the AUTOMATED REPORTING phase
    proceedToAutomatedReporting(registrationTokenRedemptionFixture, market)

    # To progress into the AUTOMATED DISPUTE phase we do an automated report
    assert market.automatedReport([0,2], sender=tester.k0)

    # We're now in the AUTOMATED DISPUTE PHASE
    assert market.getReportingState() == registrationTokenRedemptionFixture.constants.AUTOMATED_DISPUTE()

    # Time passes until the end of the reporting window
    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # Before redeeming a registration token the reporter does not have their registration bond in their rep balance
    previousBalance = reputationToken.balanceOf(tester.a1)

    # The reporter may redeem their registration token as there were no markets needing reporting
    assert registrationToken.redeem(sender=tester.k1)

    # The reporter now has their bond back
    assert reputationToken.balanceOf(tester.a1) == previousBalance + registrationTokenRedemptionFixture.constants.REGISTRATION_TOKEN_BOND_AMOUNT()
'''

@mark.parametrize('makeReport', [
    True,
    False
])
def test_limitedReportingRedemptionSingleMarketHappyPath(registrationTokenRedemptionFixture, makeReport):
    market = registrationTokenRedemptionFixture.market1
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,2])

    # We only need to report on 1 market to satisfy reporting requirements
    assert reportingWindow.getRequiredReportsPerReporterForlimitedReporterMarkets() == 1

    # Have a tester report on the markets
    reportingTokenNo = registrationTokenRedemptionFixture.getReportingToken(market, [2,0])
    reportingTokenNo.buy(1, sender=tester.k1)

    # Time passes until the end of the reporting window
    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # Before redeeming a registration token the reporter does not have their registration bond in their rep balance
    previousBalance = reputationToken.balanceOf(tester.a1)

    # The reporter may redeem their registration token as they reported on the only market needing it
    assert registrationToken.redeem(sender=tester.k1)

    # The reporter now has their bond back
    assert reputationToken.balanceOf(tester.a1) == previousBalance + registrationTokenRedemptionFixture.constants.REGISTRATION_TOKEN_BOND_AMOUNT()

@mark.parametrize('makeReport', [
    True,
    False
])
def test_limitedReportingRedemptionSingleMarketNoReports(registrationTokenRedemptionFixture, makeReport):
    market = registrationTokenRedemptionFixture.market1
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,2])

    # Time passes until the end of the reporting window
    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # The reporter may not redeem their registration token as they did not report on the market
    with raises(TransactionFailed, message="Reporters should not be able to redeem their bond if no one reported"):
        registrationToken.redeem(sender=tester.k1)

@mark.parametrize('makeReport', [
    True,
    False
])
def test_limitedReportingRedemptionSingleMarketRedeemerDidntReport(registrationTokenRedemptionFixture, makeReport):
    market = registrationTokenRedemptionFixture.market1
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,2])

    # We only need to report on 1 market to satisfy reporting requirements
    assert reportingWindow.getRequiredReportsPerReporterForlimitedReporterMarkets() == 1

    # Have a tester report on the markets
    reportingTokenNo = registrationTokenRedemptionFixture.getReportingToken(market, [2,0])
    reportingTokenNo.buy(1, sender=tester.k1)

    # Time passes until the end of the reporting window
    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # Try to redeem a different tester's registration token and fail as they did not report
    with raises(TransactionFailed, message="Reporters should not be able to redeem their bond if they dont report"):
        registrationToken.redeem(sender=tester.k2)

@mark.parametrize('makeReport', [
    True,
    False
])
def test_limitedReportingRedemptionMultipleMarketHappyPath(registrationTokenRedemptionFixture, makeReport):
    market = registrationTokenRedemptionFixture.market1
    market2 = registrationTokenRedemptionFixture.createReasonableBinaryMarket(registrationTokenRedemptionFixture.branch, registrationTokenRedemptionFixture.cash)
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the LIMITED REPORTING phase for both markets
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,2])
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market2, makeReport, tester.k1, [0,2])

    # We need to report on 2 markets to satisfy reporting requirements
    assert reportingWindow.getRequiredReportsPerReporterForlimitedReporterMarkets() == 2

    # Have a tester report on both the markets
    reportingTokenNo = registrationTokenRedemptionFixture.getReportingToken(market, [2,0])
    reportingTokenNo.buy(1, sender=tester.k1)
    reportingTokenNo2 = registrationTokenRedemptionFixture.getReportingToken(market2, [2,0])
    reportingTokenNo2.buy(1, sender=tester.k1)

    # Time passes until the end of the reporting window
    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # Before redeeming a registration token the reporter does not have their registration bond in their rep balance
    previousBalance = reputationToken.balanceOf(tester.a1)

    # The reporter may redeem their registration token as they reported on the required 2 markets
    assert registrationToken.redeem(sender=tester.k1)

    # The reporter now has their bond back
    assert reputationToken.balanceOf(tester.a1) == previousBalance + registrationTokenRedemptionFixture.constants.REGISTRATION_TOKEN_BOND_AMOUNT()

@mark.parametrize('makeReport', [
    True,
    False
])
def test_limitedReportingRedemptionMultipleMarketInsufficientReport(registrationTokenRedemptionFixture, makeReport):
    market = registrationTokenRedemptionFixture.market1
    market2 = registrationTokenRedemptionFixture.createReasonableBinaryMarket(registrationTokenRedemptionFixture.branch, registrationTokenRedemptionFixture.cash)
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,2])
    
    # We need to report on 2 markets to satisfy reporting requirements
    assert reportingWindow.getRequiredReportsPerReporterForlimitedReporterMarkets() == 2

    # Have a tester report on one market
    reportingTokenNo = registrationTokenRedemptionFixture.getReportingToken(market, [2,0])
    reportingTokenNo.buy(1, sender=tester.k1)

    # Time passes until the end of the reporting window
    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # The reporter may not redeem their registration token as they did not report on enough markets
    with raises(TransactionFailed, message="Reporters should not be able to redeem their bond if they performed insufficient reporting"):
        registrationToken.redeem(sender=tester.k1)

@fixture(scope="session")
def registrationTokenRedemptionSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    # Move to the next reporting window for these tests as we want to control market creation and reporting in isolation
    originalReportingWindow = sessionFixture.applySignature('ReportingWindow', sessionFixture.binaryMarket.getReportingWindow())
    sessionFixture.chain.head_state.timestamp = originalReportingWindow.getEndTime() + 1
    market = sessionFixture.market1 = sessionFixture.createReasonableBinaryMarket(sessionFixture.branch, sessionFixture.cash)
    return initializeReportingFixture(sessionFixture, market)

@fixture
def registrationTokenRedemptionFixture(sessionFixture, registrationTokenRedemptionSnapshot):
    sessionFixture.chain.revert(registrationTokenRedemptionSnapshot)
    return sessionFixture
