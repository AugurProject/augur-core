from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises
from datetime import timedelta

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

def test_limitedReportingRedemptionSingleMarketHappyPath(registrationTokenRedemptionFixture):
    market = registrationTokenRedemptionFixture.market1
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market)

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

def test_limitedReportingRedemptionSingleMarketSadPath(registrationTokenRedemptionFixture):
    market = registrationTokenRedemptionFixture.market1
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    registrationToken = registrationTokenRedemptionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Proceed to the LIMITED REPORTING phase
    proceedToLimitedReporting(registrationTokenRedemptionFixture, market)

    # Time passes until the end of the reporting window
    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # Before redeeming a registration token the reporter does not have their registration bond in their rep balance
    previousBalance = reputationToken.balanceOf(tester.a1)

    # The reporter may not redeem their registration token as they did not report on the market
    with raises(TransactionFailed, message="Reporters should not be able to redeem their bond if they dont report"):
        registrationToken.redeem(sender=tester.k1)


def proceedToAutomatedReporting(registrationTokenRedemptionFixture, market):
    branch = registrationTokenRedemptionFixture.branch
    reputationToken = registrationTokenRedemptionFixture.applySignature('ReputationToken', branch.getReputationToken())
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())

    registrationTokenRedemptionFixture.chain.head_state.timestamp = market.getEndTime() + 1

    # This will cause us to be in the AUTOMATED REPORTING phase
    assert market.getReportingState() == registrationTokenRedemptionFixture.constants.AUTOMATED_REPORTING()

def proceedToLimitedReporting(registrationTokenRedemptionFixture, market):
    # Proceed to automated reporting first if needed
    if (market.getReportingState() < registrationTokenRedemptionFixture.constants.AUTOMATED_REPORTING()):
        proceedToAutomatedReporting(registrationTokenRedemptionFixture, market)

    registrationTokenRedemptionFixture.chain.head_state.timestamp = market.getEndTime() + registrationTokenRedemptionFixture.constants.AUTOMATED_REPORTING_DURATION_SECONDS() + 1

    # We're in the LIMITED REPORTING phase now
    assert market.getReportingState() == registrationTokenRedemptionFixture.constants.LIMITED_REPORTING()

def proceedToAllReporting(registrationTokenRedemptionFixture, market, disptuter):
    reportingWindow = registrationTokenRedemptionFixture.applySignature('ReportingWindow', market.getReportingWindow())

    # Proceed to limited reporting first if needed
    if (market.getReportingState() < registrationTokenRedemptionFixture.constants.LIMITED_REPORTING()):
        proceedToLimitedReporting(registrationTokenRedemptionFixture, market)

    registrationTokenRedemptionFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == registrationTokenRedemptionFixture.constants.LIMITED_DISPUTE()

    assert market.disputeLimitedReporters(sender=disptuter)

    # We're in the ALL REPORTING phase now
    assert market.getReportingState() == registrationTokenRedemptionFixture.constants.ALL_REPORTING()

def proceedToForking(registrationTokenRedemptionFixture, market, reporterAddress, reporterKey, disputer):
    branch = reportingFixture.branch
    reputationToken = reportingFixture.applySignature('ReputationToken', branch.getReputationToken())
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reportingTokenNo = reportingFixture.getReportingToken(market, [2,0])
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,2])

    # proceed to all reporting first if needed
    if (market.getReportingState() < registrationTokenRedemptionFixture.constants.ALL_REPORTING()):
        proceedToAllReporting(registrationTokenRedemptionFixture, market)

    # We make one report by the reporter
    registrationToken = reportingFixture.applySignature('RegistrationToken', reportingTokenNo.getRegistrationToken())
    registrationToken.register(sender=reporterKey)
    reportingTokenNo.buy(1, sender=reporterKey)

    # To progress into the ALL DISPUTE phase we move time forward
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.ALL_DISPUTE()

    # Making a dispute at this phase will progress the market into FORKING
    assert market.disputeAllReporters(sender=disputer)
    assert market.getReportingState() == reportingFixture.constants.FORKING()


@fixture(scope="session")
def registrationTokenRedemptionSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    # Move to the next reporting window for these tests as we want to control market creation and reporting in isolation
    originalReportingWindow = sessionFixture.applySignature('ReportingWindow', sessionFixture.binaryMarket.getReportingWindow())
    sessionFixture.chain.head_state.timestamp = originalReportingWindow.getEndTime() + 1
    # Seed legacy rep contract
    legacyRepContract = sessionFixture.contracts['LegacyRepContract']
    legacyRepContract.faucet(long(11 * 10**6 * 10**18))
    
    market = sessionFixture.market1 = sessionFixture.createReasonableBinaryMarket(sessionFixture.branch, sessionFixture.cash)
    branch = sessionFixture.branch

    # Get the reputation token for this branch and migrate legacy REP to it
    reputationToken = sessionFixture.applySignature('ReputationToken', branch.getReputationToken())
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract()

    # Give some REP to testers to make things interesting
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    reportingWindow = sessionFixture.applySignature('ReportingWindow', market.getReportingWindow())
    firstRegistrationToken = sessionFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())

    # Tester 0, 1, 2, and 3 will buy registration tokens so they can report on the market
    firstRegistrationToken.register(sender=tester.k0)
    assert firstRegistrationToken.balanceOf(tester.a0) == 1
    # Testers will have their previous REP balance less the registration token bond of 1 REP
    assert reputationToken.balanceOf(tester.a0) == 8 * 10**6 * 10**18 - 10**18

    for (key, address) in [(tester.k1, tester.a1), (tester.k2, tester.a2), (tester.k3, tester.a3)]:
        firstRegistrationToken.register(sender=key)
        assert firstRegistrationToken.balanceOf(address) == 1
        assert reputationToken.balanceOf(address) == 1 * 10**6 * 10**18 - 10**18

    return sessionFixture.chain.snapshot()

@fixture
def registrationTokenRedemptionFixture(sessionFixture, registrationTokenRedemptionSnapshot):
    sessionFixture.chain.revert(registrationTokenRedemptionSnapshot)
    return sessionFixture
