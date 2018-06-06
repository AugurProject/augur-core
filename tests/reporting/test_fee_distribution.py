from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed, ABIContract
from pytest import fixture, mark, raises
from utils import longTo32Bytes, bytesToHexString, TokenDelta, EtherDelta, longToHexString, PrintGasUsed, AssertLog
from reporting_utils import generateFees, proceedToNextRound, finalizeFork, getExpectedFees

def test_initial_report_and_participation_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    constants = localFixture.contracts["Constants"]

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
    assert feeWindow.buy(feeWindowAmount, sender=tester.k1)
    assert feeWindow.buy(feeWindowAmount, sender=tester.k2)
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

    # Cashing out Participation tokens will awards fees proportional to the total winning stake in the window
    with TokenDelta(reputationToken, feeWindowAmount, tester.a0, "Redeeming participation tokens didn't refund REP"):
        with TokenDelta(feeWindow, -feeWindowAmount, tester.a0, "Redeeming participation tokens didn't decrease participation token balance correctly"):
            with EtherDelta(expectedParticipationFees, tester.a0, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
                assert feeWindow.redeem(tester.a0)

    with TokenDelta(reputationToken, feeWindowAmount, tester.a1, "Redeeming participation tokens didn't refund REP"):
        with TokenDelta(feeWindow, -feeWindowAmount, tester.a1, "Redeeming participation tokens didn't decrease participation token balance correctly"):
            with EtherDelta(expectedParticipationFees, tester.a1, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
                assert feeWindow.redeem(tester.a1)

    with TokenDelta(reputationToken, feeWindowAmount, tester.a2, "Redeeming participation tokens didn't refund REP"):
        with TokenDelta(feeWindow, -feeWindowAmount, tester.a2, "Redeeming participation tokens didn't decrease participation token balance correctly"):
            with EtherDelta(expectedParticipationFees, tester.a2, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
                assert feeWindow.redeem(tester.a2)

    marketStake = marketInitialReport.getStake()
    expectedFees = reporterFees * marketStake / totalStake
    initialReporterRedeemedLog = {
        "reporter": bytesToHexString(tester.a0),
        "amountRedeemed": marketStake,
        "repReceived": marketStake,
        "reportingFeesReceived": expectedFees,
        "payoutNumerators": [market.getNumTicks(), 0],
        "universe": universe.address,
        "market": market.address
    }
    with AssertLog(localFixture, "InitialReporterRedeemed", initialReporterRedeemedLog):
        with TokenDelta(reputationToken, marketStake, tester.a0, "Redeeming didn't refund REP"):
            with EtherDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming didn't increase ETH correctly"):
                assert marketInitialReport.redeem(tester.a0)

    categoricalMarketStake = categoricalInitialReport.getStake()
    expectedFees = reporterFees * categoricalMarketStake / totalStake
    with TokenDelta(reputationToken, categoricalMarketStake, tester.a0, "Redeeming didn't refund REP"):
        with EtherDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert categoricalInitialReport.redeem(tester.a0)

@mark.parametrize('finalize', [
    True,
    False,
])
def test_failed_crowdsourcer_fees(finalize, localFixture, universe, market, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # generate some fees
    generateFees(localFixture, universe, market)

    # We'll make the window active
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # generate some fees
    generateFees(localFixture, universe, market)

    # We'll have testers contribute to a dispute but not reach the target
    amount = market.getParticipantStake()

    # confirm we can contribute 0
    assert market.contribute([1, market.getNumTicks()-1], False, 0, sender=tester.k1)

    with TokenDelta(reputationToken, -amount + 1, tester.a1, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([1, market.getNumTicks()-1], False, amount - 1, sender=tester.k1)

    with TokenDelta(reputationToken, -amount + 1, tester.a2, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([1, market.getNumTicks()-1], False, amount - 1, sender=tester.k2)

    assert market.getFeeWindow() == feeWindow.address

    payoutDistributionHash = market.derivePayoutDistributionHash([1, market.getNumTicks()-1], False)
    failedCrowdsourcer = localFixture.applySignature("DisputeCrowdsourcer", market.getCrowdsourcer(payoutDistributionHash))

    # confirm we cannot contribute directly to a crowdsourcer without going through the market
    with raises(TransactionFailed):
        failedCrowdsourcer.contribute(tester.a0, 1)

    if finalize:
        # Fast forward time until the fee window is over and we can redeem to recieve the REP back and fees
        localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
        expectedTotalFees = getExpectedFees(localFixture, cash, failedCrowdsourcer, 1)
    else:
        # Continue to the next round which will disavow failed crowdsourcers and let us redeem once the window is over
        market.contribute([0, market.getNumTicks()], False, amount * 2)
        assert market.getFeeWindow() != feeWindow.address
        localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
        expectedTotalFees = getExpectedFees(localFixture, cash, failedCrowdsourcer, 1)

    with TokenDelta(reputationToken, amount - 1, tester.a1, "Redeeming did not refund REP"):
        with EtherDelta(expectedTotalFees / 2, tester.a1, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert failedCrowdsourcer.redeem(tester.a1)

    with TokenDelta(reputationToken, amount - 1, tester.a2, "Redeeming did not refund REP"):
        with EtherDelta(cash.balanceOf(failedCrowdsourcer.address), tester.a2, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert failedCrowdsourcer.redeem(tester.a2)

def test_one_round_crowdsourcer_fees(localFixture, universe, market, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    constants = localFixture.contracts["Constants"]

    # We'll make the window active
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # generate some fees
    generateFees(localFixture, universe, market)

    # We'll have testers push markets into the next round by funding dispute crowdsourcers
    amount = 2 * market.getParticipantStake()
    with TokenDelta(reputationToken, -amount, tester.a1, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([0, market.getNumTicks()], False, amount, sender=tester.k1)

    newFeeWindowAddress = market.getFeeWindow()
    assert newFeeWindowAddress != feeWindow.address

    # fast forward time to the fee new window and generate additional fees
    feeWindow = localFixture.applySignature('FeeWindow', newFeeWindowAddress)
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # Fast forward time until the new fee window is over and we can redeem our winning stake, and dispute bond tokens and receive fees
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    initialReporter = localFixture.applySignature('InitialReporter', market.getReportingParticipant(0))
    marketDisputeCrowdsourcer = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(1))

    # The dispute crowdsourcer contributor locked in REP for 2 rounds, as did the Initial Reporter
    expectedTotalFees = cash.balanceOf(feeWindow.address) + cash.balanceOf(universe.getOrCreateFeeWindowBefore(feeWindow.address))

    expectedFees = expectedTotalFees * 2 / 3
    expectedRep = market.getParticipantStake()
    assert expectedRep == long(marketDisputeCrowdsourcer.getStake() + marketDisputeCrowdsourcer.getStake() / 2)
    disputeCrowdsourcerRedeemedLog = {
        "reporter": bytesToHexString(tester.a1),
        "disputeCrowdsourcer": marketDisputeCrowdsourcer.address,
        "amountRedeemed": marketDisputeCrowdsourcer.getStake(),
        "repReceived": expectedRep,
        "reportingFeesReceived": expectedFees,
        "payoutNumerators": [0, market.getNumTicks()],
        "universe": universe.address,
        "market": market.address
    }
    with AssertLog(localFixture, "DisputeCrowdsourcerRedeemed", disputeCrowdsourcerRedeemedLog):
        with TokenDelta(reputationToken, expectedRep, tester.a1, "Redeeming didn't refund REP"):
            with EtherDelta(expectedFees, tester.a1, localFixture.chain, "Redeeming didn't increase ETH correctly"):
                assert marketDisputeCrowdsourcer.redeem(tester.a1, sender=tester.k1)

    # The initial reporter gets fees even though they were not correct. They do not get their REP back though
    expectedFees = cash.balanceOf(feeWindow.address) + cash.balanceOf(universe.getOrCreateFeeWindowBefore(feeWindow.address))
    with TokenDelta(reputationToken, 0, tester.a0, "Redeeming didn't refund REP"):
        with EtherDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert initialReporter.redeem(tester.a0)

def test_multiple_round_crowdsourcer_fees(localFixture, universe, market, cash, reputationToken):
    constants = localFixture.contracts["Constants"]

    # Initial Report disputed
    proceedToNextRound(localFixture, market, tester.k1, True)
    # Initial Report winning
    proceedToNextRound(localFixture, market, tester.k2, True)
    # Initial Report disputed
    proceedToNextRound(localFixture, market, tester.k1, True, randomPayoutNumerators=True)
    # Initial Report winning
    proceedToNextRound(localFixture, market, tester.k3, True)

    # Get all the winning Reporting Participants
    initialReporter = localFixture.applySignature('InitialReporter', market.getReportingParticipant(0))
    winningDisputeCrowdsourcer1 = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(2))
    winningDisputeCrowdsourcer2 = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(4))

    # Get losing Reporting Participants
    losingDisputeCrowdsourcer1 = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(1))
    losingDisputeCrowdsourcer2 = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(3))

    # We can't redeem yet as the market isn't finalized
    with raises(TransactionFailed):
        initialReporter.redeem(tester.a0)

    with raises(TransactionFailed):
        winningDisputeCrowdsourcer1.redeem(tester.a2)

    # Fast forward time until the new fee window is over and we can receive fees
    feeWindow = localFixture.applySignature("FeeWindow", market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # The initial reporter locked in REP for 5 rounds.
    expectedInitialReporterFees = getExpectedFees(localFixture, cash, initialReporter, 5)
    expectedRep = long(initialReporter.getStake() + initialReporter.getStake() / 2)
    with TokenDelta(reputationToken, expectedRep, tester.a0, "Redeeming didn't refund REP"):
        with EtherDelta(expectedInitialReporterFees, tester.a0, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert initialReporter.redeem(tester.a0)

    # The first winning dispute crowdsourcer will get fees for 4 rounds
    expectedWinningDisputeCrowdsourcer1Fees = getExpectedFees(localFixture, cash, winningDisputeCrowdsourcer1, 4)
    expectedRep = long(winningDisputeCrowdsourcer1.getStake() + winningDisputeCrowdsourcer1.getStake() / 2)
    with TokenDelta(reputationToken, expectedRep, tester.a2, "Redeeming didn't refund REP"):
        with EtherDelta(expectedWinningDisputeCrowdsourcer1Fees, tester.a2, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert winningDisputeCrowdsourcer1.redeem(tester.a2)

    # The final winning dispute crowdsourcer will get fees for 2 rounds
    expectedWinningDisputeCrowdsourcer2Fees = getExpectedFees(localFixture, cash, winningDisputeCrowdsourcer2, 2)
    expectedRep = long(winningDisputeCrowdsourcer2.getStake() + winningDisputeCrowdsourcer2.getStake() / 2)
    with TokenDelta(reputationToken, expectedRep, tester.a3, "Redeeming didn't refund REP"):
        with EtherDelta(expectedWinningDisputeCrowdsourcer2Fees, tester.a3, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert winningDisputeCrowdsourcer2.redeem(tester.a3)

    # The losing reports get fees as well but no REP
    # The first losing bond has fees from 5 rounds
    expectedLosingDisputeCrowdsourcer1Fees = getExpectedFees(localFixture, cash, losingDisputeCrowdsourcer1, 5)
    with TokenDelta(reputationToken, 0, tester.a1, "Redeeming refunded REP"):
        with EtherDelta(expectedLosingDisputeCrowdsourcer1Fees, tester.a1, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert losingDisputeCrowdsourcer1.redeem(tester.a1)

    # The second losing bond has fees from 3 rounds
    expectedLosingDisputeCrowdsourcer2Fees = getExpectedFees(localFixture, cash, losingDisputeCrowdsourcer2, 3)
    with TokenDelta(reputationToken, 0, tester.a1, "Redeeming refunded REP"):
        with EtherDelta(expectedLosingDisputeCrowdsourcer2Fees, tester.a1, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert losingDisputeCrowdsourcer2.redeem(tester.a1)

def test_multiple_contributors_crowdsourcer_fees(localFixture, universe, market, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # We'll make the window active
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # generate some fees
    generateFees(localFixture, universe, market)

    # We'll have testers push markets into the next round by funding dispute crowdsourcers
    amount = market.getParticipantStake()
    with TokenDelta(reputationToken, -amount, tester.a1, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([0, market.getNumTicks()], False, amount, sender=tester.k1)
    with TokenDelta(reputationToken, -amount, tester.a2, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([0, market.getNumTicks()], False, amount, sender=tester.k2)

    newFeeWindowAddress = market.getFeeWindow()
    assert newFeeWindowAddress != feeWindow.address

    # fast forward time to the fee new window and generate additional fees
    feeWindow = localFixture.applySignature('FeeWindow', newFeeWindowAddress)
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # Fast forward time until the new fee window is over and we can redeem our winning stake, and dispute bond tokens and receive fees
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    marketDisputeCrowdsourcer = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(1))

    # The dispute crowdsourcer contributors locked in REP for 2 rounds and staked twice the initial reporter so they split 2/3 of the total stake
    expectedFees = cash.balanceOf(feeWindow.address) + cash.balanceOf(universe.getOrCreateFeeWindowBefore(feeWindow.address))
    expectedFees = expectedFees / 3 * 2

    expectedRep = long(amount + amount / 2)
    with TokenDelta(reputationToken, expectedRep, tester.a1, "Redeeming didn't refund REP"):
        with EtherDelta(expectedFees / 2, tester.a1, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert marketDisputeCrowdsourcer.redeem(tester.a1)

    with TokenDelta(reputationToken, expectedRep + 1, tester.a2, "Redeeming didn't refund REP"):
        with EtherDelta(expectedFees - expectedFees / 2, tester.a2, localFixture.chain, "Redeeming didn't increase ETH correctly"):
            assert marketDisputeCrowdsourcer.redeem(tester.a2)

def test_forkAndRedeem(localFixture, universe, market, categoricalMarket, cash, reputationToken):
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
    for i in range(market.getNumParticipants()):
        reportingParticipant = localFixture.applySignature("DisputeCrowdsourcer", market.getReportingParticipant(i))

    # Finalize the fork
    finalizeFork(localFixture, market, universe)

    categoricalDisputeCrowdsourcer = localFixture.applySignature("DisputeCrowdsourcer", categoricalMarket.getReportingParticipant(1))

    # Migrate the categorical market into the winning universe. This will disavow the dispute crowdsourcer on it, letting us redeem for original universe rep and eth
    assert categoricalMarket.migrateThroughOneFork()

    expectedRep = categoricalDisputeCrowdsourcer.getStake()
    expectedEth = getExpectedFees(localFixture, cash, categoricalDisputeCrowdsourcer, 2)
    with EtherDelta(expectedEth, tester.a1, localFixture.chain, "Redeeming didn't increase ETH correctly"):
        with TokenDelta(reputationToken, expectedRep, tester.a1, "Redeeming didn't increase REP correctly"):
            categoricalDisputeCrowdsourcer.redeem(tester.a1)

    noPayoutNumerators = [0] * market.getNumberOfOutcomes()
    noPayoutNumerators[0] = market.getNumTicks()
    yesPayoutNumerators = noPayoutNumerators[::-1]
    noUniverse =  localFixture.applySignature('Universe', universe.createChildUniverse(noPayoutNumerators, False))
    yesUniverse =  localFixture.applySignature('Universe', universe.createChildUniverse(yesPayoutNumerators, False))
    noUniverseReputationToken = localFixture.applySignature('ReputationToken', noUniverse.getReputationToken())
    yesUniverseReputationToken = localFixture.applySignature('ReputationToken', yesUniverse.getReputationToken())

    # Now we'll fork and redeem the reporting participants
    for i in range(market.getNumParticipants()):
        account = localFixture.testerAddress[i % 4]
        key = localFixture.testerKey[i % 4]
        reportingParticipant = localFixture.applySignature("DisputeCrowdsourcer", market.getReportingParticipant(i))
        expectedRep = reportingParticipant.getStake()
        expectedRep += expectedRep / localFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
        expectedRep += reportingParticipant.getStake() / 2
        repToken = noUniverseReputationToken if i % 2 == 0 else yesUniverseReputationToken
        with TokenDelta(repToken, expectedRep, account, "Redeeming didn't increase REP correctly for " + str(i)):
            assert reportingParticipant.forkAndRedeem(sender=key)

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['yesNoMarket'].translator, kitchenSinkSnapshot['yesNoMarket'].address)
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
        categoricalMarket.doInitialReport([categoricalMarket.getNumTicks(), 0, 0], False)
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
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['yesNoMarket'].translator, kitchenSinkSnapshot['yesNoMarket'].address)

@fixture
def categoricalMarket(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)

@fixture
def scalarMarket(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['scalarMarket'].translator, kitchenSinkSnapshot['scalarMarket'].address)

@fixture
def cash(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
