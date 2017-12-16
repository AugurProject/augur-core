from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed, ABIContract
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString, TokenDelta, EtherDelta, longToHexString

def test_initial_report_and_participation_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # We cannot purchase participation tokens yet since the window isn't active
    with raises(TransactionFailed):
        feeWindow.buy(1)

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
    with EtherDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        assert marketInitialReport.redeem(tester.a0)

    categoricalMarketStake = categoricalInitialReport.getStake()
    expectedFees = reporterFees * categoricalMarketStake / totalStake
    with EtherDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        assert categoricalInitialReport.redeem(tester.a0)

def test_one_round_crowdsourcer_fees(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # We'll make the window active
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # generate some fees in this window as well
    generateFees(localFixture, universe, market)
    
    # We'll have testers push markets into the next round by funding dispute crowdsourcers
    amount = 2 * market.getTotalStake()
    with TokenDelta(reputationToken, -amount, tester.a1, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([market.getNumTicks(), 0], False, amount, sender=tester.k1, startgas=long(6.7 * 10**6))

    assert market.getFeeWindow() != feeWindow.address

    # fast forward time to the fee new window and generate additional fees
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    generateFees(localFixture, universe, market)

    # Fast forward time until the new fee window is over and we can redeem our winning stake, and dispute bond tokens and receive fees
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    marketDisputeCrowdsourcer = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(1))

    # The dispute crowdsourcer contributor locked in REP for 2 rounds and is the only winner in those rounds
    expectedFees = cash.balanceOf(feeWindow.address) + cash.balanceOf(universe.getOrCreateFeeWindowBefore(feeWindow.address))

    with EtherDelta(expectedFees, tester.a1, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        assert marketDisputeCrowdsourcer.redeem(tester.a1, sender=tester.k1)

def test_two_round_crowdsourcer_fees(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # We'll make the window active
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    
    # We'll push the market into the next round by funding dispute crowdsourcers
    amount = 2 * market.getTotalStake()
    with TokenDelta(reputationToken, -amount, tester.a1, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([market.getNumTicks(), 0], False, amount, sender=tester.k1, startgas=long(6.7 * 10**6))

    assert market.getFeeWindow() != feeWindow.address

    # Move time forward into the new fee window and push the market over once more
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    amount = 2 * market.getTotalStake() - 3 * amount
    with TokenDelta(reputationToken, -amount, tester.a2, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([0, market.getNumTicks()], False, amount, sender=tester.k2, startgas=long(6.7 * 10**6))

    assert market.getFeeWindow() != feeWindow.address

    # Fast forward time until the new fee window is over and we can redeem our winning stake, and dispute bond tokens and receive fees
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()
    assert categoricalMarket.finalize()
    assert scalarMarket.finalize()

    marketDisputeCrowdsourcer = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(1))

    reporterFees = 1000 * market.getNumTicks() / universe.getOrCacheReportingFeeDivisor()
    totalStake = feeWindow.getTotalFeeStake()
    assert cash.balanceOf(feeWindow.address) == reporterFees

    marketStake = marketDisputeCrowdsourcer.getStake()
    expectedFees = reporterFees * marketStake / totalStake
    with EtherDelta(expectedFees, tester.a1, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(marketDisputeCrowdsourcer, -marketStake, tester.a1, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert marketDisputeCrowdsourcer.redeem(False, sender=tester.k1)

    categoricalMarketStake = categoricalMarketDesignatedStake.getStake()
    expectedFees = reporterFees * categoricalMarketStake / totalStake
    with EtherDelta(expectedFees, tester.a2, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(categoricalMarketDesignatedStake, -categoricalMarketStake, tester.a2, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert categoricalMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k2)

    scalarMarketStake = scalarMarketDesignatedStake.getStake() / 2
    expectedFees = reporterFees * scalarMarketStake / totalStake
    with EtherDelta(expectedFees, tester.a2, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(scalarMarketDesignatedStake, -scalarMarketStake, tester.a2, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert scalarMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k2)
    with EtherDelta(expectedFees, tester.a3, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(scalarMarketDesignatedStake, -scalarMarketStake, tester.a3, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert scalarMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k3)

def test_multiple_contributors_crowdsourcer_fees(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken):
    pass


def test_crowdsourcer_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken):
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    # We'll make the window active
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    
    # We'll have testers push markets into the next round by funding dispute crowdsourcers
    amount = 2 * market.getTotalStake()
    with TokenDelta(reputationToken, -amount, tester.a1, "Disputing did not reduce REP balance correctly"):
        assert market.contribute([market.getNumTicks(), 0], False, amount, sender=tester.k1, startgas=long(6.7 * 10**6))

    assert market.getFeeWindow() != feeWindow.address

    with TokenDelta(reputationToken, -amount, tester.a2, "Disputing did not reduce REP balance correctly"):
        assert categoricalMarket.contribute([categoricalMarket.getNumTicks(), 0, 0], False, amount, sender=tester.k2, startgas=long(6.7 * 10**6))

    assert categoricalMarket.getFeeWindow() != feeWindow.address

    # The scalar crowdsourcer will be completed by two contributors
    with TokenDelta(reputationToken, -amount / 2, tester.a2, "Disputing did not reduce REP balance correctly"):
        assert scalarMarket.contribute([scalarMarket.getNumTicks(), 0], False, amount / 2, sender=tester.k2, startgas=long(6.7 * 10**6))
    with TokenDelta(reputationToken, -amount / 2, tester.a3, "Disputing did not reduce REP balance correctly"):
        assert scalarMarket.contribute([scalarMarket.getNumTicks(), 0], False, amount / 2, sender=tester.k3, startgas=long(6.7 * 10**6))

    assert scalarMarket.getFeeWindow() != feeWindow.address

    # Move time forward into the new fee window and push the categorical market over once more

    # Fast forward time until the new fee window is over and we can redeem our winning stake, and dispute bond tokens and receive fees
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()
    assert categoricalMarket.finalize()
    assert scalarMarket.finalize()

    marketDisputeCrowdsourcer = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(1))
    categoricalMarketDesignatedStake = localFixture.applySignature('DisputeCrowdsourcer', categoricalMarket.getReportingParticipant(1))
    scalarMarketDesignatedStake = localFixture.applySignature('DisputeCrowdsourcer', scalarMarket.getReportingParticipant(1))

    reporterFees = 1000 * market.getNumTicks() / universe.getOrCacheReportingFeeDivisor()
    totalStake = feeWindow.getTotalFeeStake()
    assert cash.balanceOf(feeWindow.address) == reporterFees

    marketStake = marketDisputeCrowdsourcer.getStake()
    expectedFees = reporterFees * marketStake / totalStake
    with EtherDelta(expectedFees, tester.a1, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(marketDisputeCrowdsourcer, -marketStake, tester.a1, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert marketDisputeCrowdsourcer.redeem(False, sender=tester.k1)

    categoricalMarketStake = categoricalMarketDesignatedStake.getStake()
    expectedFees = reporterFees * categoricalMarketStake / totalStake
    with EtherDelta(expectedFees, tester.a2, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(categoricalMarketDesignatedStake, -categoricalMarketStake, tester.a2, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert categoricalMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k2)

    scalarMarketStake = scalarMarketDesignatedStake.getStake() / 2
    expectedFees = reporterFees * scalarMarketStake / totalStake
    with EtherDelta(expectedFees, tester.a2, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(scalarMarketDesignatedStake, -scalarMarketStake, tester.a2, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert scalarMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k2)
    with EtherDelta(expectedFees, tester.a3, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(scalarMarketDesignatedStake, -scalarMarketStake, tester.a3, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert scalarMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k3)

def test_forking(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, feeWindow):
    # We'll have testers put up dispute bonds against the designated reports and place stake in other outcomes
    otherOutcomeStake = 10 ** 18
    assert market.disputeDesignatedReport([market.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k1)
    assert categoricalMarket.disputeDesignatedReport([categoricalMarket.getNumTicks(),0,0], otherOutcomeStake, False, sender=tester.k2)
    assert scalarMarket.disputeDesignatedReport([scalarMarket.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k3)

    reporterFees = 1000 * market.getNumTicks() / universe.getOrCacheReportingFeeDivisor()
    totalWinningStake = feeWindow.getTotalWinningStake()
    assert cash.balanceOf(feeWindow.address) == reporterFees

    # Progress to the Limited dispute phase and dispute one of the markets. This should migrate fees to the fee window the market migrates to proportional to its stake
    localFixture.contracts["Time"].setTimestamp(feeWindow.getDisputeStartTime() + 1)

    assert market.disputeFirstReporters([market.getNumTicks() - 1, 1], otherOutcomeStake, False, sender=tester.k4, startgas=long(6.7 * 10**6))
    assert categoricalMarket.disputeFirstReporters([categoricalMarket.getNumTicks() - 1, 1, 0], otherOutcomeStake, False, sender=tester.k4, startgas=long(6.7 * 10**6))
    assert scalarMarket.disputeFirstReporters([scalarMarket.getNumTicks() - 1, 1], otherOutcomeStake, False, sender=tester.k4, startgas=long(6.7 * 10**6))

    # Progress into last dispute and cause a fork
    feeWindow = localFixture.applySignature("FeeWindow", market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getDisputeStartTime() + 1)

    forkDuration = lastDisputeCost = localFixture.contracts["Constants"].FORK_DURATION_SECONDS()
    nextWindowTimestamp = localFixture.contracts["Time"].getTimestamp() + forkDuration
    nextFeeWindow = localFixture.applySignature("FeeWindow", universe.getOrCreateFeeWindowByTimestamp(nextWindowTimestamp))
    scalarMarketStake = scalarMarket.getTotalStake()
    lastDisputeCost = localFixture.contracts["Constants"].LAST_REPORTERS_DISPUTE_BOND_AMOUNT()
    totalScalarMarketStakeMoved = scalarMarketStake + lastDisputeCost
    migratedFees = reporterFees * (scalarMarketStake + lastDisputeCost) / (feeWindow.getTotalStake() + lastDisputeCost)

    with TokenDelta(cash, -migratedFees, feeWindow.address, "Disputing in last didn't migrate ETH out correctly"):
        with TokenDelta(cash, migratedFees, nextFeeWindow.address, "Disputing in last didn't migrate ETH in correctly"):
            with StakeDelta(lastDisputeCost, -scalarMarketStake, 0, scalarMarket, feeWindow, "Disputing in last is not migrating stake out correctly"):
                with StakeDelta(lastDisputeCost, totalScalarMarketStakeMoved, 0, scalarMarket, nextFeeWindow, "Disputing in last is not migrating stake in correctly"):
                    assert scalarMarket.disputeLastReporters(sender=tester.k5)

    # We migrate REP to a new universe and finalize the forking market
    newUniverse = localFixture.getOrCreateChildUniverse(universe, scalarMarket, [0, scalarMarket.getNumTicks()])
    newUniverseReputationToken = localFixture.applySignature('ReputationToken', newUniverse.getReputationToken())

    # Testers all move their REP to the new universe
    for i in range(0,5):
        reputationToken.migrateOut(newUniverseReputationToken.address, localFixture.testerAddress[i], reputationToken.balanceOf(localFixture.testerAddress[i]), sender=localFixture.testerKey[i])

    # Finalize the forking market
    assert scalarMarket.tryFinalize()

    # migrate one of the markets to the winning universe and confirm fees went with it
    oldFeeWindowAddress = market.getFeeWindow()
    designatedReportingDuration = localFixture.contracts["Constants"].DESIGNATED_REPORTING_DURATION_SECONDS()
    newFeeWindowAddress = newUniverse.getOrCreateFeeWindowByMarketEndTime(localFixture.contracts["Time"].getTimestamp() - designatedReportingDuration)
    migratedFees = cash.balanceOf(oldFeeWindowAddress)
    with TokenDelta(cash, -migratedFees, oldFeeWindowAddress, "Migrating to a new universe didn't migrate ETH out correctly"):
        with TokenDelta(cash, migratedFees, newFeeWindowAddress, "Migrating to a new universe didn't migrate ETH in correctly"):
            market.migrateThroughAllForks()

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
        market.doInitialReport([0, market.getNumTicks()], False)
        categoricalMarket.doInitialReport([0, 0, categoricalMarket.getNumTicks()], False)
        scalarMarket.doInitialReport([0, scalarMarket.getNumTicks()], False)

    # generate fees in the existing window
    generateFees(fixture, universe, market)

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


def generateFees(fixture, universe, market):
    completeSets = fixture.contracts['CompleteSets']
    cash = fixture.contracts['Cash']
    mailbox = fixture.applySignature('Mailbox', market.getMarketCreatorMailbox())
    
    cost = 1000 * market.getNumTicks()
    marketCreatorFees = cost / market.getMarketCreatorSettlementFeeDivisor()
    completeSets.publicBuyCompleteSets(market.address, 1000, sender = tester.k1, value = cost)
    with TokenDelta(cash, marketCreatorFees, mailbox.address, "The market creator mailbox didn't get their share of fees from complete set sale"):
        completeSets.publicSellCompleteSets(market.address, 1000, sender=tester.k1)
    with EtherDelta(marketCreatorFees, market.getOwner(), fixture.chain, "The market creator did not get their fees when withdrawing ETH from the mailbox"):
        assert mailbox.withdrawEther()
    fees = cash.balanceOf(market.getFeeWindow())
    reporterFees = cost / universe.getOrCacheReportingFeeDivisor()
    assert fees == reporterFees