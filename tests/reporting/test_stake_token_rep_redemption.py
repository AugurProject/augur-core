from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture as pytest_fixture, mark, raises
from utils import captureFilteredLogs
from reporting_utils import proceedToDesignatedReporting, proceedToFirstReporting, initializeReportingFixture

def test_one_market_one_correct_report(localFixture, universe, market):
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = localFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    # To progress into the DESIGNATED DISPUTE phase we do a designated report
    initialRepBalance = reputationToken.balanceOf(tester.a0)
    assert localFixture.designatedReport(market, [0,10**18], tester.k0)
    # The market owner gets back the no-show REP bond, which cancels out the amount used to pay for the required dispute tokens
    assert reputationToken.balanceOf(tester.a0) == initialRepBalance + universe.getDesignatedReportNoShowBond() - universe.getDesignatedReportStake()
    initialREPBalance = reputationToken.balanceOf(tester.a0)

    # We're now in the DESIGNATED DISPUTE PHASE
    assert market.getReportingState() == localFixture.contracts['Constants'].DESIGNATED_DISPUTE()

    expectedStakeTokenBalance = universe.getDesignatedReportStake()

    # Time passes until the end of the reporting window
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # Finalize the market
    market.tryFinalize()

    # The designated reporter may redeem their stake tokens which were purchased to make the designated report
    stakeToken = localFixture.getOrCreateStakeToken(market, [0, 10**18])
    assert stakeToken.balanceOf(tester.a0) == expectedStakeTokenBalance

    expectedREPBalance = initialREPBalance

    # We can see that the designated reporter's balance of REP has returned to the original value since as the market creator the had to pay these REP fees initially
    assert reputationToken.balanceOf(tester.a0) == expectedREPBalance

    # We'll redeem the winning tokens we have on the market and confirm we get that amount returned in REP
    assert stakeToken.redeemWinningTokens()
    assert reputationToken.balanceOf(tester.a0) == expectedREPBalance + expectedStakeTokenBalance

def test_two_markets_two_correct_reports_one_with_no_fees(localFixture, universe, market):
    cash = localFixture.contracts["Cash"]
    market2 = localFixture.createReasonableBinaryMarket(universe, cash)
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = localFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    # To progress into the DESIGNATED DISPUTE phase we do a designated report
    initialRepBalance = reputationToken.balanceOf(tester.a0)
    assert localFixture.designatedReport(market, [0,10**18], tester.k0)
    # The market owner gets back the no-show REP bond, which cancels out the amount used to pay for the required dispute tokens
    assert reputationToken.balanceOf(tester.a0) == initialRepBalance + universe.getDesignatedReportNoShowBond() - universe.getDesignatedReportStake()
    initialREPBalance = reputationToken.balanceOf(tester.a0)

    # We're now in the DESIGNATED DISPUTE PHASE
    assert market.getReportingState() == localFixture.contracts['Constants'].DESIGNATED_DISPUTE()

    # We'll do the same with the second market
    proceedToDesignatedReporting(localFixture, universe, market2, [0,10**18])
    initialRepBalance = reputationToken.balanceOf(tester.a0)
    assert localFixture.designatedReport(market2, [0,10**18], tester.k0)
    # The market owner gets back the no-show REP bond, which cancels out the amount used to pay for the required dispute tokens
    assert reputationToken.balanceOf(tester.a0) == initialRepBalance + universe.getDesignatedReportNoShowBond() - universe.getDesignatedReportStake()
    initialREPBalance = reputationToken.balanceOf(tester.a0)
    assert market2.getReportingState() == localFixture.contracts['Constants'].DESIGNATED_DISPUTE()

    designatedReportStake = universe.getDesignatedReportStake()

    # Time passes until the end of the reporting window
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    # Finalize the first market
    market.tryFinalize()

    # The market1 designated reporter may redeem their stake tokens which were purchased to make the designated report
    stakeToken = localFixture.getOrCreateStakeToken(market, [0, 10**18])
    assert stakeToken.balanceOf(tester.a0) == designatedReportStake

    expectedREPBalance = initialREPBalance

    # We can see that the designated reporter's balance of REP has returned to the original value since as the market creator the had to pay these REP fees initially
    assert reputationToken.balanceOf(tester.a0) == expectedREPBalance

    # If we try to redeem tokens and recieve trading fees now we'll get a failure since not all markets are finalized
    with raises(TransactionFailed):
        stakeToken.redeemWinningTokens()

    # We'll redeem the winning tokens we have on the market and forgo fees and confirm we get that amount returned in REP
    initialETHBalance = localFixture.chain.head_state.get_balance(tester.a0)
    assert stakeToken.redeemWinningTokens(True)
    assert reputationToken.balanceOf(tester.a0) == expectedREPBalance + designatedReportStake
    assert localFixture.chain.head_state.get_balance(tester.a0) == initialETHBalance

    # If we redeem the second tester's tokens they'll get ALL of the fees on the reporting window now and their normal share of REP
    market2.tryFinalize()
    stakeToken = localFixture.getOrCreateStakeToken(market2, [0, 10**18])
    assert stakeToken.balanceOf(tester.a0) == designatedReportStake

    initialREPBalance = reputationToken.balanceOf(tester.a0)

    # We'll redeem the winning tokens we have on the market and confirm we get that amount returned in REP and all the fees in the reporting window
    expectedETHBalance = localFixture.chain.head_state.get_balance(tester.a0) + cash.balanceOf(reportingWindow.address)
    assert stakeToken.redeemWinningTokens()
    assert reputationToken.balanceOf(tester.a0) == initialREPBalance + designatedReportStake
    assert localFixture.chain.head_state.get_balance(tester.a0) == expectedETHBalance

@mark.parametrize('numReports, numCorrect', [
    (1, 1),
    (2, 2),
    (3, 3),
    (2, 1),
    (3, 2),
    (3, 1),
])
def test_stake_token_redemption(localFixture, universe, market, numReports, numCorrect):
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = localFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())

    # Proceed to FIRST REPORTING
    proceedToFirstReporting(localFixture, universe, market, False, 1, [0,10**18], [10**18,0])

    noShowBond = universe.getDesignatedReportNoShowBond()

    doReports(localFixture, market, numReports, numCorrect)

    confirmPayouts(localFixture, market, numCorrect, noShowBond)

def doReports(fixture, market, numReporters, numCorrect):
    reportingWindow = fixture.applySignature('ReportingWindow', market.getReportingWindow())
    stakeTokenWinner = fixture.getOrCreateStakeToken(market, [0,10**18])
    stakeTokenLoser = fixture.getOrCreateStakeToken(market, [10**18,0])

    for i in range(0, numReporters):
        testerKey = fixture.testerKey[i]
        if numCorrect > 0:
            stakeTokenWinner.buy(10, sender=testerKey)
        else:
            stakeTokenLoser.buy(1, sender=testerKey)
        numCorrect -= 1

    fixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()

def confirmPayouts(fixture, market, numCorrectReporters, noShowBond):
    reportingWindow = fixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = fixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    universe = fixture.applySignature('Universe', market.getUniverse())
    stakeToken = fixture.getOrCreateStakeToken(market, [0,10**18])

    for i in range(0, numCorrectReporters):
        testerAddress = fixture.testerAddress[i]
        initialREPBalance = reputationToken.balanceOf(testerAddress)
        assert stakeToken.redeemWinningTokens(sender=fixture.testerKey[i])
        expectedRep = initialREPBalance + 10
        if (i == 0):
            expectedRep += noShowBond
        assert reputationToken.balanceOf(testerAddress) == expectedRep

@pytest_fixture(scope="session")
def localSnapshot(fixture, augurInitializedSnapshot):
    fixture.resetToSnapshot(augurInitializedSnapshot)
    fixture.upload("solidity_test_helpers/Constants.sol")
    universe = fixture.createUniverse(0, "")
    fixture.distributeRep(universe)
    market = fixture.createReasonableBinaryMarket(universe, fixture.contracts['Cash'])
    snapshot = initializeReportingFixture(fixture, universe, market)
    snapshot['universe'] = universe
    snapshot['market'] = market
    return snapshot

@pytest_fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@pytest_fixture
def universe(localFixture, localSnapshot):
    return ABIContract(localFixture.chain, localSnapshot['universe'].translator, localSnapshot['universe'].address)

@pytest_fixture
def market(localFixture, localSnapshot):
    return ABIContract(localFixture.chain, localSnapshot['market'].translator, localSnapshot['market'].address)
