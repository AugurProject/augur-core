from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed, ABIContract
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString, TokenDelta, ETHDelta

def test_token_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, reportingWindow):
    # We'll progress past the designated dispute phase and finalize all the markets
    localFixture.chain.head_state.timestamp = market.getEndTime() + localFixture.contracts["Constants"].DESIGNATED_REPORTING_DURATION_SECONDS() + 1

    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    # We can't redeem the stake used to do the designated report for fees yet since the window is not yet over
    marketDesignatedStake = localFixture.getStakeToken(market, [0, market.getNumTicks()])
    categoricalMarketDesignatedStake = localFixture.getStakeToken(categoricalMarket, [0, 0, categoricalMarket.getNumTicks()])
    scalarMarketDesignatedStake = localFixture.getStakeToken(scalarMarket, [0, scalarMarket.getNumTicks()])

    with raises(TransactionFailed):
        marketDesignatedStake.redeemWinningTokens(False)

    # If we forgo fees we can redeem however. We'll do this for the scalar market. Note that the market total stake isn't decreased. Market total stake only decreases once it is finalized at which point it can no longer migrate so the value doesn't matter
    scalarStake = scalarMarketDesignatedStake.balanceOf(tester.a0)
    with TokenDelta(reputationToken, scalarStake, tester.a0, "Forgoing fees resulting in an incorrect REP refund"):
        with ETHDelta(0, tester.a0, localFixture.chain, "Forgoing fees gave fees incorrectly"):
            with StakeDelta(0, -scalarStake, -scalarStake, scalarMarket, reportingWindow, "Forgoing fees incorrectly updated stake accounting"):
                assert scalarMarketDesignatedStake.redeemWinningTokens(True)

    # We cannot purchase participation tokens yet since the window isn't active
    participationToken = localFixture.applySignature("ParticipationToken", reportingWindow.getParticipationToken())
    with raises(TransactionFailed):
        participationToken.buy(1)

    # We'll progress to the start of the window and purchase some participation tokens
    localFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1
    participationTokenAmount = 100
    with TokenDelta(reputationToken, -participationTokenAmount, tester.a0, "Buying participation tokens didn't deduct REP correctly"):
        with TokenDelta(participationToken, participationTokenAmount, tester.a0, "Buying participation tokens didn't increase participation token balance correctly"):
            with StakeDelta(0, participationTokenAmount, participationTokenAmount, market, reportingWindow, "Buying participation tokens din't adjust stake accounting correctly"):
                assert participationToken.buy(participationTokenAmount)

    # As other testers we'll buy some more
    with StakeDelta(0, participationTokenAmount*3, participationTokenAmount*3, market, reportingWindow, "Buying participation tokens din't adjust stake accounting correctly"):
        with TokenDelta(participationToken, participationTokenAmount, tester.a1, "Buying participation tokens didn't increase participation token balance correctly"):
            assert participationToken.buy(participationTokenAmount, sender=tester.k1)
        with TokenDelta(participationToken, participationTokenAmount, tester.a2, "Buying participation tokens didn't increase participation token balance correctly"):
            assert participationToken.buy(participationTokenAmount, sender=tester.k2)
        with TokenDelta(participationToken, participationTokenAmount, tester.a3, "Buying participation tokens didn't increase participation token balance correctly"):
            assert participationToken.buy(participationTokenAmount, sender=tester.k3)

    # We can't redeem the participation tokens for fees yet since the window isn't over
    with raises(TransactionFailed):
        participationToken.redeem(False)

    # We can redeem them to just get back REP. We'll have tester 3 do this
    participationValue = participationToken.balanceOf(tester.a3)
    with TokenDelta(reputationToken, participationValue, tester.a3, "Forgoing fees resulting in an incorrect REP refund"):
        with TokenDelta(participationToken, -participationTokenAmount, tester.a3, "Redeeming participation tokens didn't decrease participation token balance correctly"):
            with ETHDelta(0, tester.a0, localFixture.chain, "Forgoing fees gave fees incorrectly"):
                with StakeDelta(0, -participationValue, -participationValue, market, reportingWindow, "Forgoing fees incorrectly updated stake accounting"):
                    assert participationToken.redeem(True, sender=tester.k3)

    # Fast forward time until the window is over and we can redeem our winning stake and participation tokens and receive fees
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    reporterFees = 1000 * market.getNumTicks() / universe.getReportingFeeDivisor()
    totalWinningStake = reportingWindow.getTotalWinningStake()
    assert cash.balanceOf(reportingWindow.address) == reporterFees

    expectedParticipationFees = reporterFees * participationTokenAmount / totalWinningStake

    # Cashing out Participation tokens or Stake tokens will awards fees proportional to the total winning stake in the window
    with TokenDelta(participationToken, -participationTokenAmount, tester.a0, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with ETHDelta(expectedParticipationFees, tester.a0, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
            assert participationToken.redeem(False)

    with TokenDelta(participationToken, -participationTokenAmount, tester.a1, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with ETHDelta(expectedParticipationFees, tester.a1, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
            assert participationToken.redeem(False, sender=tester.k1)

    with TokenDelta(participationToken, -participationTokenAmount, tester.a2, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with ETHDelta(expectedParticipationFees, tester.a2, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
            assert participationToken.redeem(False, sender=tester.k2)

    logs = []
    captureFilteredLogs(localFixture.chain.head_state, universe, logs)

    marketStake = marketDesignatedStake.balanceOf(tester.a0)
    expectedFees = reporterFees * marketStake / totalWinningStake + 1 # Rounding error
    with ETHDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(marketDesignatedStake, -marketStake, tester.a0, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert marketDesignatedStake.redeemWinningTokens(False)

    # Confirm redeeming stake tokens logs appropriately
    assert len(logs) == 1
    assert logs[0]['_event_type'] == 'WinningTokensRedeemed'
    assert logs[0]['reporter'] == bytesToHexString(tester.a0)
    assert logs[0]['reportingFeesReceived'] == expectedFees
    assert logs[0]['stakeToken'] == marketDesignatedStake.address
    assert logs[0]['market'] == market.address
    assert logs[0]['amountRedeemed'] == marketStake
    assert logs[0]['payoutNumerators'] == [0,market.getNumTicks()]

    categoricalMarketStake = categoricalMarketDesignatedStake.balanceOf(tester.a0)
    expectedFees = reporterFees * categoricalMarketStake / totalWinningStake + 1 # Rounding error
    with ETHDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(categoricalMarketDesignatedStake, -categoricalMarketStake, tester.a0, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert categoricalMarketDesignatedStake.redeemWinningTokens(False)

def test_dispute_bond_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, reportingWindow):    
    # We'll have testers put up dispute bonds against the designated reports and place stake in other outcomes
    disputeStake = localFixture.contracts["Constants"].DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
    otherOutcomeStake = 10 ** 18
    totalCost = disputeStake + otherOutcomeStake
    with TokenDelta(reputationToken, -totalCost, tester.a1, "Disputing did not reduce REP balance correctly"):
        with StakeDelta(totalCost, totalCost, 0, market, reportingWindow, "Disputing is not adjust stake accounting correctly"):
            assert market.disputeDesignatedReport([market.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k1)
    
    with StakeDelta(totalCost, totalCost, 0, categoricalMarket, reportingWindow, "Disputing is not adjust stake accounting correctly"):
        with TokenDelta(reputationToken, -totalCost, tester.a2, "Disputing did not reduce REP balance correctly"):
            assert categoricalMarket.disputeDesignatedReport([categoricalMarket.getNumTicks(),0,0], otherOutcomeStake, False, sender=tester.k2)

    with TokenDelta(reputationToken, -totalCost, tester.a3, "Disputing did not reduce REP balance correctly"):
        with StakeDelta(totalCost, totalCost, 0, scalarMarket, reportingWindow, "Disputing is not adjust stake accounting correctly"):
            assert scalarMarket.disputeDesignatedReport([scalarMarket.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k3)
    
    # Fast forward time until the window is over and we can redeem our winning stake, and dispute bond tokens and receive fees
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    marketDesignatedStake = localFixture.getStakeToken(market, [market.getNumTicks(), 0])
    categoricalMarketDesignatedStake = localFixture.getStakeToken(categoricalMarket, [categoricalMarket.getNumTicks(), 0, 0])
    scalarMarketDesignatedStake = localFixture.getStakeToken(scalarMarket, [scalarMarket.getNumTicks(), 0])

    reporterFees = 1000 * market.getNumTicks() / universe.getReportingFeeDivisor()
    totalWinningStake = reportingWindow.getTotalWinningStake()
    assert cash.balanceOf(reportingWindow.address) == reporterFees

    # Tester 0 placed losing designated reports so that stake is worthless. The other testers have both stake and bonds that can be redeemed for a share of fees
    marketStake = marketDesignatedStake.balanceOf(tester.a1)
    expectedFees = reporterFees * marketStake / totalWinningStake
    with ETHDelta(expectedFees, tester.a1, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(marketDesignatedStake, -marketStake, tester.a1, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert marketDesignatedStake.redeemWinningTokens(False, sender=tester.k1)

    categoricalMarketStake = categoricalMarketDesignatedStake.balanceOf(tester.a2)
    expectedFees = reporterFees * categoricalMarketStake / totalWinningStake
    with ETHDelta(expectedFees, tester.a2, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(categoricalMarketDesignatedStake, -categoricalMarketStake, tester.a2, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert categoricalMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k2)

    scalarMarketStake = scalarMarketDesignatedStake.balanceOf(tester.a3)
    expectedFees = reporterFees * scalarMarketStake / totalWinningStake
    with ETHDelta(expectedFees, tester.a3, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(scalarMarketDesignatedStake, -scalarMarketStake, tester.a3, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert scalarMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k3)

    # Now we'll redeem the dispute bonds
    marketDisputeBond = localFixture.applySignature("DisputeBondToken", market.getDesignatedReporterDisputeBondToken())
    categoricalMarketDisputeBond = localFixture.applySignature("DisputeBondToken", categoricalMarket.getDesignatedReporterDisputeBondToken())
    scalarMarketDisputeBond = localFixture.applySignature("DisputeBondToken", scalarMarket.getDesignatedReporterDisputeBondToken())

    expectedDisputeFees = reporterFees * disputeStake / totalWinningStake

    with ETHDelta(expectedDisputeFees, tester.a1, localFixture.chain, "Redeeming Dispute Bond token didn't increase ETH correctly"):
        assert marketDisputeBond.withdraw(False, sender=tester.k1)
    with ETHDelta(expectedDisputeFees, tester.a2, localFixture.chain, "Redeeming Dispute Bond token didn't increase ETH correctly"):
        assert categoricalMarketDisputeBond.withdraw(False, sender=tester.k2)
    remainingFees = cash.balanceOf(reportingWindow.address)
    with ETHDelta(remainingFees, tester.a3, localFixture.chain, "Redeeming Dispute Bond token didn't increase ETH correctly"):
        assert scalarMarketDisputeBond.withdraw(False, sender=tester.k3)


def test_fee_migration(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, reportingWindow):    
    # We'll have testers put up dispute bonds against the designated reports and place stake in other outcomes
    otherOutcomeStake = 10 ** 18
    assert market.disputeDesignatedReport([market.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k1)
    assert categoricalMarket.disputeDesignatedReport([categoricalMarket.getNumTicks(),0,0], otherOutcomeStake, False, sender=tester.k2)
    assert scalarMarket.disputeDesignatedReport([scalarMarket.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k3)

    reporterFees = 1000 * market.getNumTicks() / universe.getReportingFeeDivisor()
    totalWinningStake = reportingWindow.getTotalWinningStake()
    assert cash.balanceOf(reportingWindow.address) == reporterFees

    # Progress to the Limited dispute phase and dispute one of the markets. This should migrate fees to the reporting window the market migrates to proportional to its stake
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    nextReportingWindow = localFixture.applySignature("ReportingWindow", universe.getNextReportingWindow())
    scalarMarketStake = scalarMarket.getTotalStake()
    firstDisputeCost = localFixture.contracts["Constants"].FIRST_REPORTERS_DISPUTE_BOND_AMOUNT()
    scalarMarketStakeDelta = firstDisputeCost + otherOutcomeStake
    totalScalarMarketStakeMoved = scalarMarketStake + scalarMarketStakeDelta
    migratedFees = reporterFees * (scalarMarketStake + firstDisputeCost) / (reportingWindow.getTotalStake() + firstDisputeCost)

    with TokenDelta(cash, -migratedFees, reportingWindow.address, "Disputing in first didn't migrate ETH out correctly"):
        with TokenDelta(cash, migratedFees, nextReportingWindow.address, "Disputing in first didn't migrate ETH in correctly"):
            with StakeDelta(scalarMarketStakeDelta, -scalarMarketStake, 0, scalarMarket, reportingWindow, "Disputing in first is not migrating stake out correctly"):
                with StakeDelta(scalarMarketStakeDelta, totalScalarMarketStakeMoved, 0, scalarMarket, nextReportingWindow, "Disputing in first is not migrating stake in correctly"):
                    assert scalarMarket.disputeFirstReporters([scalarMarket.getNumTicks() - 1, 1], otherOutcomeStake, False, sender=tester.k4)

def test_forking(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, reportingWindow):    
    # We'll have testers put up dispute bonds against the designated reports and place stake in other outcomes
    otherOutcomeStake = 10 ** 18
    assert market.disputeDesignatedReport([market.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k1)
    assert categoricalMarket.disputeDesignatedReport([categoricalMarket.getNumTicks(),0,0], otherOutcomeStake, False, sender=tester.k2)
    assert scalarMarket.disputeDesignatedReport([scalarMarket.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k3)

    reporterFees = 1000 * market.getNumTicks() / universe.getReportingFeeDivisor()
    totalWinningStake = reportingWindow.getTotalWinningStake()
    assert cash.balanceOf(reportingWindow.address) == reporterFees

    # Progress to the Limited dispute phase and dispute one of the markets. This should migrate fees to the reporting window the market migrates to proportional to its stake
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    assert market.disputeFirstReporters([market.getNumTicks() - 1, 1], otherOutcomeStake, False, sender=tester.k4, startgas=long(6.7 * 10**6))
    assert categoricalMarket.disputeFirstReporters([categoricalMarket.getNumTicks() - 1, 1, 0], otherOutcomeStake, False, sender=tester.k4, startgas=long(6.7 * 10**6))
    assert scalarMarket.disputeFirstReporters([scalarMarket.getNumTicks() - 1, 1], otherOutcomeStake, False, sender=tester.k4, startgas=long(6.7 * 10**6))

    # Progress into last dispute and cause a fork
    reportingWindow = localFixture.applySignature("ReportingWindow", market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    forkDuration = lastDisputeCost = localFixture.contracts["Constants"].FORK_DURATION_SECONDS()
    nextReportingWindow = localFixture.applySignature("ReportingWindow", universe.getReportingWindowByTimestamp(localFixture.chain.head_state.timestamp + forkDuration))
    scalarMarketStake = scalarMarket.getTotalStake()
    lastDisputeCost = localFixture.contracts["Constants"].LAST_REPORTERS_DISPUTE_BOND_AMOUNT()
    totalScalarMarketStakeMoved = scalarMarketStake + lastDisputeCost
    migratedFees = reporterFees * (scalarMarketStake + lastDisputeCost) / (reportingWindow.getTotalStake() + lastDisputeCost)

    with TokenDelta(cash, -migratedFees, reportingWindow.address, "Disputing in last didn't migrate ETH out correctly"):
        with TokenDelta(cash, migratedFees, nextReportingWindow.address, "Disputing in last didn't migrate ETH in correctly"):
            with StakeDelta(lastDisputeCost, -scalarMarketStake, 0, scalarMarket, reportingWindow, "Disputing in last is not migrating stake out correctly"):
                with StakeDelta(lastDisputeCost, totalScalarMarketStakeMoved, 0, scalarMarket, nextReportingWindow, "Disputing in last is not migrating stake in correctly"):
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
    oldReportingWindowAddress = market.getReportingWindow()
    designatedReportingDuration = localFixture.contracts["Constants"].DESIGNATED_REPORTING_DURATION_SECONDS()
    newReportingWindowAddress = newUniverse.getReportingWindowByMarketEndTime(localFixture.chain.head_state.timestamp - designatedReportingDuration)
    migratedFees = cash.balanceOf(oldReportingWindowAddress)
    with TokenDelta(cash, -migratedFees, oldReportingWindowAddress, "Migrating to a new universe didn't migrate ETH out correctly"):
        with TokenDelta(cash, migratedFees, newReportingWindowAddress, "Migrating to a new universe didn't migrate ETH in correctly"):
            market.migrateThroughAllForks()

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    categoricalMarket = ABIContract(fixture.chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)
    scalarMarket = ABIContract(fixture.chain, kitchenSinkSnapshot['scalarMarket'].translator, kitchenSinkSnapshot['scalarMarket'].address)
    cash = ABIContract(fixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
    completeSets = fixture.contracts['CompleteSets']

    # Generate the fees in our initial reporting window
    cost = 1000 * market.getNumTicks()
    marketCreatorFees = cost / market.getMarketCreatorSettlementFeeDivisor()
    completeSets.publicBuyCompleteSets(market.address, 1000, sender = tester.k1, value = cost)
    with ETHDelta(marketCreatorFees, tester.a0, fixture.chain, "The market creator didn't get their share of fees from complete set sale"):
        completeSets.publicSellCompleteSets(market.address, 1000, sender=tester.k1)
    fees = cash.balanceOf(market.getReportingWindow())
    reporterFees = cost / universe.getReportingFeeDivisor()
    assert fees == reporterFees

    # Distribute REP
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    for testAccount in [tester.a1, tester.a2, tester.a3, tester.a4, tester.a5]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot, kitchenSinkSnapshot):
    fixture.resetToSnapshot(localSnapshot)

    market = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    categoricalMarket = ABIContract(fixture.chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)
    scalarMarket = ABIContract(fixture.chain, kitchenSinkSnapshot['scalarMarket'].translator, kitchenSinkSnapshot['scalarMarket'].address)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingWindow = fixture.applySignature('ReportingWindow', market.getReportingWindow())

    # Skip to Designated Reporting
    fixture.chain.head_state.timestamp = market.getEndTime() + 1

    # Designated Report on each market
    designatedReportCost = universe.getDesignatedReportStake()
    totalDesignatedReportCostInWindow = designatedReportCost * 3
    with TokenDelta(reputationToken, 0, tester.a0, "Doing the designated report didn't deduct REP correctly or didn't award the no show bond"):
        with StakeDelta(designatedReportCost, totalDesignatedReportCostInWindow, 0, market, reportingWindow, "Doing the designated report din't adjust stake accounting correctly"):
            fixture.designatedReport(market, [0,market.getNumTicks()], tester.k0)
            fixture.designatedReport(categoricalMarket, [0,0,categoricalMarket.getNumTicks()], tester.k0)
            fixture.designatedReport(scalarMarket, [0,scalarMarket.getNumTicks()], tester.k0)

    return fixture

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

@fixture
def reputationToken(localFixture, kitchenSinkSnapshot, universe):
    return localFixture.applySignature('ReputationToken', universe.getReputationToken())

@fixture
def reportingWindow(localFixture, kitchenSinkSnapshot, market):
    return localFixture.applySignature('ReportingWindow', market.getReportingWindow())

class StakeDelta():

    def __init__(self, marketTotalStakeDelta, windowTotalStakeDelta, windowTotalWinningStakeDelta, market, window, err=""):
        self.market = market
        self.window = window
        self.marketTotalStakeDelta = marketTotalStakeDelta
        self.windowTotalStakeDelta = windowTotalStakeDelta
        self.windowTotalWinningStakeDelta = windowTotalWinningStakeDelta
        self.err = err

    def __enter__(self):
        self.marketTotalStake = self.market.getTotalStake()
        self.windowTotalStake = self.window.getTotalStake()
        self.windowTotalWinningStake = self.window.getTotalWinningStake()
    
    def __exit__(self, *args):
        if args[1]:
            raise args[1]
        # We make sure to have locals for everything here so we can see the values in traceback output
        originalMarketTotalStake = self.marketTotalStake
        originalWindowTotalStake = self.windowTotalStake
        originalWindowTotalWinningStake = self.windowTotalWinningStake
        marketTotalStake = self.market.getTotalStake()
        windowTotalStake = self.window.getTotalStake()
        windowTotalWinningStake = self.window.getTotalWinningStake()
        marketTotalStakeDelta = self.marketTotalStakeDelta
        windowTotalStakeDelta = self.windowTotalStakeDelta
        windowTotalWinningStakeDelta = self.windowTotalWinningStakeDelta
        resultmarketTotalStakeDelta = marketTotalStake - originalMarketTotalStake
        resultWindowTotalStakeDelta = windowTotalStake - originalWindowTotalStake
        resultWindowTotalWinningStakeDelta = windowTotalWinningStake - originalWindowTotalWinningStake
        assert resultmarketTotalStakeDelta == marketTotalStakeDelta, self.err + ". Market stake delta EXPECTED: %i ACTUAL: %i" % (marketTotalStakeDelta, resultmarketTotalStakeDelta)
        assert resultWindowTotalStakeDelta == windowTotalStakeDelta, self.err + ". Window stake delta EXPECTED: %i ACTUAL: %i" % (windowTotalStakeDelta, resultWindowTotalStakeDelta)
        assert resultWindowTotalWinningStakeDelta == windowTotalWinningStakeDelta, self.err + ". Window winning stake delta EXPECTED: %i ACTUAL: %i" % (windowTotalWinningStakeDelta, resultWindowTotalWinningStakeDelta)
