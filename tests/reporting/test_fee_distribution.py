from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed, ABIContract
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString, TokenDelta, EtherDelta, longToHexString, PrintGasUsed
from reporting_utils import generateFees, proceedToNextRound, finalizeFork

def test_initial_report_and_participation_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # We cannot purchase participation tokens yet since the window isn't active
    with raises(TransactionFailed):
        feeWindow.buy(1)

    # generate some fees
    generateFees(localFixture, universe, market)

    # We'll make the window active then purchase some participation tokens
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    feeWindowAmount = 100
    with TokenDelta(reputationToken, -feeWindowAmount, tester.a0, "Buying participation tokens didn't deduct REP correctly"):
        with TokenDelta(feeWindow, feeWindowAmount, tester.a0, "Buying participation tokens didn't increase participation token balance correctly"):
            assert feeWindow.buy(feeWindowAmount)

    # As other testers we'll buy some more
    with TokenDelta(feeWindow, feeWindowAmount, tester.a1, "Buying participation tokens didn't increase participation token balance correctly"):
        assert feeWindow.buy(feeWindowAmount, sender=tester.k1)
    with TokenDelta(feeWindow, feeWindowAmount, tester.a2, "Buying participation tokens didn't increase participation token balance correctly"):
        assert feeWindow.buy(feeWindowAmount, sender=tester.k2)
    with TokenDelta(feeWindow, feeWindowAmount, tester.a3, "Buying participation tokens didn't increase participation token balance correctly"):
        assert feeWindow.buy(feeWindowAmount, sender=tester.k3)

    # We can't redeem the participation tokens yet since the window isn't over
    with raises(TransactionFailed):
        feeWindow.redeem(False)

    # Now end the window and finalize
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    assert market.finalize()
    assert categoricalMarket.finalize()
    assert scalarMarket.finalize()

    marketInitialReport = localFixture.applySignature('InitialReporter', market.getInitialReporter())
    categoricalInitialReport = localFixture.applySignature('InitialReporter', categoricalMarket.getInitialReporter())
    scalarInitialReport = localFixture.applySignature('InitialReporter', scalarMarket.getInitialReporter())

    reporterFees = 1000 * market.getNumTicks() / universe.getOrCacheReportingFeeDivisor()
    totalStake = feeWindow.getTotalFeeStake()
    assert cash.balanceOf(feeWindow.address) == reporterFees

    expectedParticipationFees = reporterFees * feeWindowAmount / totalStake

    # Cashing out Participation tokens or Stake tokens will awards fees proportional to the total winning stake in the window
    with TokenDelta(feeWindow, -feeWindowAmount, tester.a0, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with EtherDelta(expectedParticipationFees, tester.a0, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
            assert feeWindow.redeem(tester.a0)

    with TokenDelta(feeWindow, -feeWindowAmount, tester.a1, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with EtherDelta(expectedParticipationFees, tester.a1, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
            assert feeWindow.redeem(tester.a1)

    with TokenDelta(feeWindow, -feeWindowAmount, tester.a2, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with EtherDelta(expectedParticipationFees, tester.a2, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
            assert feeWindow.redeem(tester.a2)

    logs = []
    captureFilteredLogs(localFixture.chain.head_state, localFixture.contracts['Augur'], logs)

    marketStake = marketInitialReport.getStake()
    expectedFees = reporterFees * marketStake / totalStake
    with EtherDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        assert marketInitialReport.redeem(tester.a0)

    categoricalMarketStake = categoricalInitialReport.getStake()
    expectedFees = reporterFees * categoricalMarketStake / totalStake
    with EtherDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        assert categoricalInitialReport.redeem(tester.a0)

def test_one_round_crowdsourcer_fees(localFixture, universe, market, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # We'll make the window active
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # generate some fees
    generateFees(localFixture, universe, market)
    
    # We'll have testers push markets into the next round by funding dispute crowdsourcers
    amount = 2 * market.getTotalStake()
    with TokenDelta(reputationToken, -amount, tester.a1, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([0, market.getNumTicks()], False, amount, sender=tester.k1, startgas=long(6.7 * 10**6))

    assert market.getFeeWindow() != feeWindow.address

    # fast forward time to the fee new window and generate additional fees
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # Fast forward time until the new fee window is over and we can redeem our winning stake, and dispute bond tokens and receive fees
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    marketDisputeCrowdsourcer = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(1))

    # The dispute crowdsourcer contributor locked in REP for 2 rounds and is the only winner in those rounds
    expectedFees = cash.balanceOf(feeWindow.address) + cash.balanceOf(universe.getOrCreateFeeWindowBefore(feeWindow.address))

    with EtherDelta(expectedFees, tester.a1, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        assert marketDisputeCrowdsourcer.redeem(tester.a1, sender=tester.k1)

def test_multiple_round_crowdsourcer_fees(localFixture, universe, market, cash, reputationToken):
    # Initial Report disputed
    proceedToNextRound(localFixture, market, tester.k1, True)
    # Initial Report winning
    proceedToNextRound(localFixture, market, tester.k2, True)
    # Initial Report disputed
    proceedToNextRound(localFixture, market, tester.k1, True)
    # Initial Report winning
    proceedToNextRound(localFixture, market, tester.k3, True)

    # Fast forward time until the new fee window is over and we can receive fees
    feeWindow = localFixture.applySignature("FeeWindow", market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # Get all the winning Reporting Participants
    initialReporter = localFixture.applySignature('InitialReporter', market.getReportingParticipant(0))
    winningDisputeCrowdsourcer1 = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(2))
    winningDisputeCrowdsourcer2 = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(4))

    # The initial reporter locked in REP for 5 rounds.
    expectedInitialReporterFees = getExpectedFees(localFixture, cash, initialReporter, 5)
    with EtherDelta(expectedInitialReporterFees, tester.a0, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        assert initialReporter.redeem(tester.a0)

    # The first winning dispute crowdsourcer will get fees for 4 rounds
    expectedWinningDisputeCrowdsourcer1Fees = getExpectedFees(localFixture, cash, winningDisputeCrowdsourcer1, 4)
    with EtherDelta(expectedWinningDisputeCrowdsourcer1Fees, tester.a2, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        assert winningDisputeCrowdsourcer1.redeem(tester.a2)

    # The final winning dispute crowdsourcer will get fees for 2 rounds
    expectedWinningDisputeCrowdsourcer2Fees = getExpectedFees(localFixture, cash, winningDisputeCrowdsourcer2, 2)
    with EtherDelta(expectedWinningDisputeCrowdsourcer2Fees, tester.a3, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        assert winningDisputeCrowdsourcer2.redeem(tester.a3) 

def test_multiple_contributors_crowdsourcer_fees(localFixture, universe, market, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # We'll make the window active
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # generate some fees
    generateFees(localFixture, universe, market)
    
    # We'll have testers push markets into the next round by funding dispute crowdsourcers
    amount = market.getTotalStake()
    with TokenDelta(reputationToken, -amount, tester.a1, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([0, market.getNumTicks()], False, amount, sender=tester.k1, startgas=long(6.7 * 10**6))
    with TokenDelta(reputationToken, -amount, tester.a2, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([0, market.getNumTicks()], False, amount, sender=tester.k2, startgas=long(6.7 * 10**6))

    assert market.getFeeWindow() != feeWindow.address

    # fast forward time to the fee new window and generate additional fees
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # Fast forward time until the new fee window is over and we can redeem our winning stake, and dispute bond tokens and receive fees
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    marketDisputeCrowdsourcer = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(1))

    # The dispute crowdsourcer contributors locked in REP for 2 rounds and are the only winners in those rounds, so they split it
    expectedFees = cash.balanceOf(feeWindow.address) + cash.balanceOf(universe.getOrCreateFeeWindowBefore(feeWindow.address))
    
    with EtherDelta(expectedFees / 2, tester.a1, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        assert marketDisputeCrowdsourcer.redeem(tester.a1)

    with EtherDelta(expectedFees - expectedFees / 2, tester.a2, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        assert marketDisputeCrowdsourcer.redeem(tester.a2)

def test_forking(localFixture, universe, market, categoricalMarket, cash, reputationToken):
    # Let's do some initial disputes for the categorical market
    proceedToNextRound(localFixture, categoricalMarket, tester.k1, moveTimeForward = False)

    # Get to a fork
    testers = [tester.k0, tester.k1, tester.k2, tester.k3]
    testerIndex = 1
    while (market.getForkingMarket() == longToHexString(0)):
        proceedToNextRound(localFixture, market, testers[testerIndex], True)
        testerIndex += 1
        testerIndex = testerIndex % len(testers)

    # Have the participants fork and create new child universes
    for i in range(17):
        reportingParticipant = localFixture.applySignature("DisputeCrowdsourcer", market.getReportingParticipant(i))
        with PrintGasUsed(localFixture, "Fork:", 0):
            reportingParticipant.fork(startgas=long(6.7 * 10**6))

    # Finalize the fork
    finalizeFork(localFixture, market, universe)

    categoricalDisputeCrowdsourcer = localFixture.applySignature("DisputeCrowdsourcer", categoricalMarket.getReportingParticipant(1))

    # Migrate the categorical market into the winning universe. This will disavow the dispute crowdsourcer on it, letting us redeem for original universe rep and eth
    assert categoricalMarket.migrateThroughOneFork()

    expectedRep = categoricalDisputeCrowdsourcer.getStake()
    expectedEth = getExpectedFees(localFixture, cash, categoricalDisputeCrowdsourcer, 2)
    with EtherDelta(expectedEth, tester.a1, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        with TokenDelta(reputationToken, expectedRep, tester.a1, "Redeeming didn't increase REP correctly"):
            categoricalDisputeCrowdsourcer.redeem(tester.a1, startgas=long(6.7 * 10**6))

    # TODO confirm the forking market reporting participants can be redeemed for eth and their destination universe's REP

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    categoricalMarket = ABIContract(fixture.chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)
    scalarMarket = ABIContract(fixture.chain, kitchenSinkSnapshot['scalarMarket'].translator, kitchenSinkSnapshot['scalarMarket'].address)

    # Skip to Designated Reporting
    fixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)

    # Distribute REP
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    # Designated Report on the markets
    designatedReportCost = universe.getOrCacheDesignatedReportStake()
    with TokenDelta(reputationToken, 0, tester.a0, "Doing the designated report didn't deduct REP correctly or didn't award the no show bond"):
        market.doInitialReport([market.getNumTicks(), 0], False)
        categoricalMarket.doInitialReport([categoricalMarket.getNumTicks(), 0], False)
        scalarMarket.doInitialReport([scalarMarket.getNumTicks(), 0], False)

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def reputationToken(localFixture, kitchenSinkSnapshot, universe):
    return localFixture.applySignature('ReputationToken', universe.getReputationToken())

@fixture
def universe(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)

@fixture
def market(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)

@fixture
def categoricalMarket(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)

@fixture
def scalarMarket(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['scalarMarket'].translator, kitchenSinkSnapshot['scalarMarket'].address)

@fixture
def cash(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)

def getExpectedFees(fixture, cash, reportingParticipant, expectedRounds):
    stake = reportingParticipant.getStake()
    feeWindow = fixture.applySignature("FeeWindow", reportingParticipant.getFeeWindow())
    universe = fixture.applySignature("Universe", feeWindow.getUniverse())
    feeToken = fixture.applySignature("FeeToken", feeWindow.getFeeToken())
    expectedFees = 0
    rounds = 0
    while feeToken.balanceOf(reportingParticipant.address) > 0:
        rounds += 1
        expectedFees += cash.balanceOf(feeWindow.address) * stake / feeToken.totalSupply()
        feeWindow = fixture.applySignature("FeeWindow", universe.getOrCreateFeeWindowBefore(feeWindow.address))
        feeToken = fixture.applySignature("FeeToken", feeWindow.getFeeToken())
    assert expectedRounds == rounds, "Only had fees from " + str(rounds) + " rounds"
    return expectedFees