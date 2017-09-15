from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises
from datetime import timedelta
from reporting_utils import proceedToAutomatedReporting, proceedToLimitedReporting, proceedToAllReporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

def test_automatedReportingNoReport(registrationTokenRedemptionFixture):
    market = registrationTokenRedemptionFixture.market1
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the AUTOMATED REPORTING phase
    proceedToAutomatedReporting(registrationTokenRedemptionFixture, market, [0,10**18])

    # To progress into the AUTOMATED DISPUTE phase we do an automated report
    assert market.automatedReport([0,10**18], sender=tester.k0)

    # We're now in the AUTOMATED DISPUTE PHASE
    assert market.getReportingState() == registrationTokenRedemptionFixture.constants.AUTOMATED_DISPUTE()

    # Time passes until the end of the reporting window
    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # The reporter may not redeem their registration token as they did not report on the market that becomes reportable when there are no normally occuring reportable markets
    with raises(TransactionFailed, message="Reporters should not be able to redeem their bond if they do not report"):
        registrationToken.redeem(sender=tester.k1)

def test_checkInReporting(registrationTokenRedemptionFixture):
    market = registrationTokenRedemptionFixture.market1
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the AUTOMATED REPORTING phase
    proceedToAutomatedReporting(registrationTokenRedemptionFixture, market, [0,10**18])

    # To progress into the AUTOMATED DISPUTE phase we do an automated report
    assert market.automatedReport([0,10**18], sender=tester.k0)

    # We're now in the AUTOMATED DISPUTE PHASE
    assert market.getReportingState() == registrationTokenRedemptionFixture.constants.AUTOMATED_DISPUTE()

    # We can't yet check in since the reporting window hasn't started
    with raises(TransactionFailed, message="The checkIn method should only be callable once the reporting window starts and has no markets that can be reported on"):
        reportingWindow.checkIn(sender=tester.k1)

    # Time passes until the beginning of the reporting window
    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1

    # Since there are no normal markets on which we can report the checkIn function can be called
    assert reportingWindow.checkIn(sender=tester.k1)

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
def test_limitedReportingRedemptionSingleMarketHappyPath(registrationTokenRedemptionFixture, makeReport):
    market = registrationTokenRedemptionFixture.market1
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,10**18])

    # We only need to report on 1 market to satisfy reporting requirements
    assert reportingWindow.getRequiredReportsPerReporterForlimitedReporterMarkets() == 1

    # Have a tester report on the markets
    reportingTokenNo = registrationTokenRedemptionFixture.getReportingToken(market, [10**18,0])
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
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,10**18])

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
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,10**18])

    # We only need to report on 1 market to satisfy reporting requirements
    assert reportingWindow.getRequiredReportsPerReporterForlimitedReporterMarkets() == 1

    # Have a tester report on the markets
    reportingTokenNo = registrationTokenRedemptionFixture.getReportingToken(market, [10**18,0])
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
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,10**18])
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market2, makeReport, tester.k1, [0,10**18])

    # We need to report on 2 markets to satisfy reporting requirements
    assert reportingWindow.getRequiredReportsPerReporterForlimitedReporterMarkets() == 2

    # Have a tester report on both the markets
    reportingTokenNo = registrationTokenRedemptionFixture.getReportingToken(market, [10**18,0])
    reportingTokenNo.buy(1, sender=tester.k1)
    reportingTokenNo2 = registrationTokenRedemptionFixture.getReportingToken(market2, [10**18,0])
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
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market, makeReport, tester.k1, [0,10**18])
    
    # We need to report on 2 markets to satisfy reporting requirements
    assert reportingWindow.getRequiredReportsPerReporterForlimitedReporterMarkets() == 2

    # Have a tester report on one market
    reportingTokenNo = registrationTokenRedemptionFixture.getReportingToken(market, [10**18,0])
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
