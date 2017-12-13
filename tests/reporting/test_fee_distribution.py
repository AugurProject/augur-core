from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed, ABIContract
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString, TokenDelta, EtherDelta

def test_token_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, feeWindow):
    # We'll progress past the designated dispute phase and finalize all the markets
    localFixture.contracts["Time"].setTimestamp(market.getEndTime() + localFixture.contracts["Constants"].DESIGNATED_REPORTING_DURATION_SECONDS() + 1)

    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    # We can't redeem the stake used to do the designated report for fees yet since the window is not yet over
    marketDesignatedStake = localFixture.getOrCreateStakeToken(market, [0, market.getNumTicks()])
    categoricalMarketDesignatedStake = localFixture.getOrCreateStakeToken(categoricalMarket, [0, 0, categoricalMarket.getNumTicks()])
    scalarMarketDesignatedStake = localFixture.getOrCreateStakeToken(scalarMarket, [0, scalarMarket.getNumTicks()])

    with raises(TransactionFailed):
        marketDesignatedStake.redeemWinningTokens(False)

    # If we forgo fees we can redeem however. We'll do this for the scalar market. Note that the market total stake isn't decreased. Market total stake only decreases once it is finalized at which point it can no longer migrate so the value doesn't matter
    scalarStake = scalarMarketDesignatedStake.balanceOf(tester.a0)
    with TokenDelta(reputationToken, scalarStake, tester.a0, "Forgoing fees resulting in an incorrect REP refund"):
        with EtherDelta(0, tester.a0, localFixture.chain, "Forgoing fees gave fees incorrectly"):
            with StakeDelta(0, -scalarStake, -scalarStake, scalarMarket, feeWindow, "Forgoing fees incorrectly updated stake accounting"):
                assert scalarMarketDesignatedStake.redeemWinningTokens(True)

    # We cannot purchase participation tokens yet since the window isn't active
    feeWindow = localFixture.applySignature("FeeWindow", feeWindow.getFeeWindow())
    with raises(TransactionFailed):
        feeWindow.buy(1)

    # We'll progress to the start of the window and purchase some participation tokens
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    feeWindowAmount = 100
    with TokenDelta(reputationToken, -feeWindowAmount, tester.a0, "Buying participation tokens didn't deduct REP correctly"):
        with TokenDelta(feeWindow, feeWindowAmount, tester.a0, "Buying participation tokens didn't increase participation token balance correctly"):
            with StakeDelta(0, feeWindowAmount, feeWindowAmount, market, feeWindow, "Buying participation tokens din't adjust stake accounting correctly"):
                assert feeWindow.buy(feeWindowAmount)

    # As other testers we'll buy some more
    with StakeDelta(0, feeWindowAmount*3, feeWindowAmount*3, market, feeWindow, "Buying participation tokens din't adjust stake accounting correctly"):
        with TokenDelta(feeWindow, feeWindowAmount, tester.a1, "Buying participation tokens didn't increase participation token balance correctly"):
            assert feeWindow.buy(feeWindowAmount, sender=tester.k1)
        with TokenDelta(feeWindow, feeWindowAmount, tester.a2, "Buying participation tokens didn't increase participation token balance correctly"):
            assert feeWindow.buy(feeWindowAmount, sender=tester.k2)
        with TokenDelta(feeWindow, feeWindowAmount, tester.a3, "Buying participation tokens didn't increase participation token balance correctly"):
            assert feeWindow.buy(feeWindowAmount, sender=tester.k3)

    # We can't redeem the participation tokens for fees yet since the window isn't over
    with raises(TransactionFailed):
        feeWindow.redeem(False)

    # We can redeem them to just get back REP. We'll have tester 3 do this
    participationValue = feeWindow.balanceOf(tester.a3)
    with TokenDelta(reputationToken, participationValue, tester.a3, "Forgoing fees resulting in an incorrect REP refund"):
        with TokenDelta(feeWindow, -feeWindowAmount, tester.a3, "Redeeming participation tokens didn't decrease participation token balance correctly"):
            with EtherDelta(0, tester.a0, localFixture.chain, "Forgoing fees gave fees incorrectly"):
                with StakeDelta(0, -participationValue, -participationValue, market, feeWindow, "Forgoing fees incorrectly updated stake accounting"):
                    assert feeWindow.redeem(True, sender=tester.k3)

    # Fast forward time until the window is over and we can redeem our winning stake and participation tokens and receive fees
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    reporterFees = 1000 * market.getNumTicks() / universe.getOrCacheReportingFeeDivisor()
    totalWinningStake = feeWindow.getTotalWinningStake()
    assert cash.balanceOf(feeWindow.address) == reporterFees

    expectedParticipationFees = reporterFees * feeWindowAmount / totalWinningStake

    # Cashing out Participation tokens or Stake tokens will awards fees proportional to the total winning stake in the window
    with TokenDelta(feeWindow, -feeWindowAmount, tester.a0, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with EtherDelta(expectedParticipationFees, tester.a0, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
            assert feeWindow.redeem(False)

    with TokenDelta(feeWindow, -feeWindowAmount, tester.a1, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with EtherDelta(expectedParticipationFees, tester.a1, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
            assert feeWindow.redeem(False, sender=tester.k1)

    with TokenDelta(feeWindow, -feeWindowAmount, tester.a2, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with EtherDelta(expectedParticipationFees, tester.a2, localFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
            assert feeWindow.redeem(False, sender=tester.k2)

    logs = []
    captureFilteredLogs(localFixture.chain.head_state, localFixture.contracts['Augur'], logs)

    marketStake = marketDesignatedStake.balanceOf(tester.a0)
    expectedFees = reporterFees * marketStake / totalWinningStake + 1 # Rounding error
    with EtherDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(marketDesignatedStake, -marketStake, tester.a0, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert marketDesignatedStake.redeemWinningTokens(False)

    # Confirm redeeming stake tokens logs appropriately
    assert len(logs) == 3
    assert logs[2]['_event_type'] == 'WinningTokensRedeemed'
    assert logs[2]['reporter'] == bytesToHexString(tester.a0)
    assert logs[2]['reportingFeesReceived'] == expectedFees
    assert logs[2]['stakeToken'] == marketDesignatedStake.address
    assert logs[2]['market'] == market.address
    assert logs[2]['amountRedeemed'] == marketStake
    assert logs[2]['payoutNumerators'] == [0,market.getNumTicks()]

    categoricalMarketStake = categoricalMarketDesignatedStake.balanceOf(tester.a0)
    expectedFees = reporterFees * categoricalMarketStake / totalWinningStake + 1 # Rounding error
    with EtherDelta(expectedFees, tester.a0, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(categoricalMarketDesignatedStake, -categoricalMarketStake, tester.a0, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert categoricalMarketDesignatedStake.redeemWinningTokens(False)

def test_dispute_bond_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, feeWindow):
    # We'll have testers put up dispute bonds against the designated reports and place stake in other outcomes
    disputeStake = localFixture.contracts["Constants"].DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
    otherOutcomeStake = 10 ** 18
    totalCost = disputeStake + otherOutcomeStake
    with TokenDelta(reputationToken, -totalCost, tester.a1, "Disputing did not reduce REP balance correctly"):
        with StakeDelta(totalCost, totalCost, 0, market, feeWindow, "Disputing is not adjust stake accounting correctly"):
            assert market.disputeDesignatedReport([market.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k1)

    with StakeDelta(totalCost, totalCost, 0, categoricalMarket, feeWindow, "Disputing is not adjust stake accounting correctly"):
        with TokenDelta(reputationToken, -totalCost, tester.a2, "Disputing did not reduce REP balance correctly"):
            assert categoricalMarket.disputeDesignatedReport([categoricalMarket.getNumTicks(),0,0], otherOutcomeStake, False, sender=tester.k2)

    with TokenDelta(reputationToken, -totalCost, tester.a3, "Disputing did not reduce REP balance correctly"):
        with StakeDelta(totalCost, totalCost, 0, scalarMarket, feeWindow, "Disputing is not adjust stake accounting correctly"):
            assert scalarMarket.disputeDesignatedReport([scalarMarket.getNumTicks(),0], otherOutcomeStake, False, sender=tester.k3)

    # Fast forward time until the window is over and we can redeem our winning stake, and dispute bond tokens and receive fees
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    marketDesignatedStake = localFixture.getOrCreateStakeToken(market, [market.getNumTicks(), 0])
    categoricalMarketDesignatedStake = localFixture.getOrCreateStakeToken(categoricalMarket, [categoricalMarket.getNumTicks(), 0, 0])
    scalarMarketDesignatedStake = localFixture.getOrCreateStakeToken(scalarMarket, [scalarMarket.getNumTicks(), 0])

    reporterFees = 1000 * market.getNumTicks() / universe.getOrCacheReportingFeeDivisor()
    totalWinningStake = feeWindow.getTotalWinningStake()
    assert cash.balanceOf(feeWindow.address) == reporterFees

    # Tester 0 placed losing designated reports so that stake is worthless. The other testers have both stake and bonds that can be redeemed for a share of fees
    marketStake = marketDesignatedStake.balanceOf(tester.a1)
    expectedFees = reporterFees * marketStake / totalWinningStake
    with EtherDelta(expectedFees, tester.a1, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(marketDesignatedStake, -marketStake, tester.a1, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert marketDesignatedStake.redeemWinningTokens(False, sender=tester.k1)

    categoricalMarketStake = categoricalMarketDesignatedStake.balanceOf(tester.a2)
    expectedFees = reporterFees * categoricalMarketStake / totalWinningStake
    with EtherDelta(expectedFees, tester.a2, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(categoricalMarketDesignatedStake, -categoricalMarketStake, tester.a2, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert categoricalMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k2)

    scalarMarketStake = scalarMarketDesignatedStake.balanceOf(tester.a3)
    expectedFees = reporterFees * scalarMarketStake / totalWinningStake
    with EtherDelta(expectedFees, tester.a3, localFixture.chain, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(scalarMarketDesignatedStake, -scalarMarketStake, tester.a3, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert scalarMarketDesignatedStake.redeemWinningTokens(False, sender=tester.k3)

    # Now we'll redeem the dispute bonds
    marketDisputeBond = localFixture.applySignature("DisputeBond", market.getDesignatedReporterDisputeBond())
    categoricalMarketDisputeBond = localFixture.applySignature("DisputeBond", categoricalMarket.getDesignatedReporterDisputeBond())
    scalarMarketDisputeBond = localFixture.applySignature("DisputeBond", scalarMarket.getDesignatedReporterDisputeBond())

    expectedDisputeFees = reporterFees * disputeStake / totalWinningStake

    with EtherDelta(expectedDisputeFees, tester.a1, localFixture.chain, "Redeeming Dispute Bond token didn't increase ETH correctly"):
        assert marketDisputeBond.withdraw(False, sender=tester.k1)
    with EtherDelta(expectedDisputeFees, tester.a2, localFixture.chain, "Redeeming Dispute Bond token didn't increase ETH correctly"):
        assert categoricalMarketDisputeBond.withdraw(False, sender=tester.k2)
    remainingFees = cash.balanceOf(feeWindow.address)
    with EtherDelta(remainingFees, tester.a3, localFixture.chain, "Redeeming Dispute Bond token didn't increase ETH correctly"):
        assert scalarMarketDisputeBond.withdraw(False, sender=tester.k3)


def test_fee_migration(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, feeWindow):
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
    nextFeeWindow = localFixture.applySignature("FeeWindow", universe.getOrCreateNextFeeWindow())
    scalarMarketStake = scalarMarket.getTotalStake()
    firstDisputeCost = localFixture.contracts["Constants"].FIRST_REPORTERS_DISPUTE_BOND_AMOUNT()
    scalarMarketStakeDelta = firstDisputeCost + otherOutcomeStake
    totalScalarMarketStakeMoved = scalarMarketStake + scalarMarketStakeDelta
    migratedFees = reporterFees * (scalarMarketStake + firstDisputeCost) / (feeWindow.getTotalStake() + firstDisputeCost)

    with TokenDelta(cash, -migratedFees, feeWindow.address, "Disputing in first didn't migrate ETH out correctly"):
        with TokenDelta(cash, migratedFees, nextFeeWindow.address, "Disputing in first didn't migrate ETH in correctly"):
            with StakeDelta(scalarMarketStakeDelta, -scalarMarketStake, 0, scalarMarket, feeWindow, "Disputing in first is not migrating stake out correctly"):
                with StakeDelta(scalarMarketStakeDelta, totalScalarMarketStakeMoved, 0, scalarMarket, nextFeeWindow, "Disputing in first is not migrating stake in correctly"):
                    assert scalarMarket.disputeFirstReporters([scalarMarket.getNumTicks() - 1, 1], otherOutcomeStake, False, sender=tester.k4)

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
    cash = ABIContract(fixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
    completeSets = fixture.contracts['CompleteSets']
    mailbox = fixture.applySignature('Mailbox', market.getMarketCreatorMailbox())

    # Generate the fees in our initial fee window
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
    feeWindow = fixture.applySignature('FeeWindow', market.getFeeWindow())

    # Skip to Designated Reporting
    fixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)

    # Designated Report on each market
    designatedReportCost = universe.getOrCacheDesignatedReportStake()
    totalDesignatedReportCostInWindow = designatedReportCost * 3
    with TokenDelta(reputationToken, 0, tester.a0, "Doing the designated report didn't deduct REP correctly or didn't award the no show bond"):
        with StakeDelta(designatedReportCost, totalDesignatedReportCostInWindow, 0, market, feeWindow, "Doing the designated report din't adjust stake accounting correctly"):
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
def feeWindow(localFixture, kitchenSinkSnapshot, market):
    return localFixture.applySignature('FeeWindow', market.getFeeWindow())

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
