from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises, mark
from utils import longToHexString, EtherDelta, TokenDelta
from reporting_utils import proceedToFirstReporting, proceedToForking, finalizeForkingMarket

@mark.parametrize('collectFees', [
    True,
    False
])
def test_redeem_stake(collectFees, kitchenSinkFixture, universe, market, cash, categoricalMarket, scalarMarket):
    reportingWindow = kitchenSinkFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = kitchenSinkFixture.applySignature('ReputationToken', universe.getReputationToken())
    completeSets = kitchenSinkFixture.contracts['CompleteSets']

    reputationToken.transfer(tester.a1, 1 * 10**6 * 10**18)

    # Generate some fees to confirm fee distribution works
    cost = 10 * market.getNumTicks()
    assert completeSets.publicBuyCompleteSets(market.address, 10, sender=tester.k1, value=cost)
    assert completeSets.publicSellCompleteSets(market.address, 10, sender=tester.k1)
    fees = cash.balanceOf(market.getReportingWindow())
    assert fees > 0

    # Proceed to the FIRST REPORTING phase
    proceedToFirstReporting(kitchenSinkFixture, universe, market, True, 1, [0,market.getNumTicks()], [market.getNumTicks(),0])

    # Move to finalization so we can redeem stake
    kitchenSinkFixture.contracts["Time"].setTimestamp(reportingWindow.getDisputeEndTime() + 1)
    assert market.tryFinalize()
    assert market.getReportingState() == kitchenSinkFixture.contracts['Constants'].FINALIZED()

    expectedEther = fees
    if (collectFees):
        assert categoricalMarket.migrateDueToNoReports()
        assert scalarMarket.migrateDueToNoReports()
    else:
        expectedEther = 0

    # Redeem all of the disputer's stake tokens and dispute bonds
    stakeTokenAddress = kitchenSinkFixture.getOrCreateStakeToken(market, [market.getNumTicks(),0]).address
    disputeBondAddress = market.getDesignatedReporterDisputeBond()
    expectedREP = 1 + kitchenSinkFixture.contracts["Constants"].DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
    with EtherDelta(expectedEther, tester.a1, kitchenSinkFixture.chain, "Redeeming didn't give eth correctly"):
        with TokenDelta(reputationToken, expectedREP, tester.a1, "Redeeming didn't give REP correctly"):
            universe.redeemStake([stakeTokenAddress], [disputeBondAddress], [], not collectFees, sender=tester.k1)

@mark.parametrize('collectFees', [
    True,
    False
])
def test_redeem_participation_tokens(collectFees, kitchenSinkFixture, market, categoricalMarket, scalarMarket, universe, cash):
    reportingWindow = kitchenSinkFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = kitchenSinkFixture.applySignature('ReputationToken', universe.getReputationToken())
    participationToken = kitchenSinkFixture.applySignature("ParticipationToken", reportingWindow.getParticipationToken())
    completeSets = kitchenSinkFixture.contracts['CompleteSets']

    reputationToken.transfer(tester.a1, 1 * 10**6 * 10**18)

    # Generate some fees to confirm fee distribution works
    cost = 10 * market.getNumTicks()
    assert completeSets.publicBuyCompleteSets(market.address, 10, sender=tester.k1, value=cost)
    assert completeSets.publicSellCompleteSets(market.address, 10, sender=tester.k1)
    fees = cash.balanceOf(market.getReportingWindow())
    assert fees > 0

    kitchenSinkFixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)

    assert kitchenSinkFixture.designatedReport(market, [0, market.getNumTicks()], tester.k0)
    assert kitchenSinkFixture.designatedReport(categoricalMarket, [0, 0, categoricalMarket.getNumTicks()], tester.k0)
    assert kitchenSinkFixture.designatedReport(scalarMarket, [0, scalarMarket.getNumTicks()], tester.k0)

    kitchenSinkFixture.contracts["Time"].setTimestamp(reportingWindow.getStartTime() + 1)

    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    amountTokens = reportingWindow.getTotalWinningStake()
    assert participationToken.buy(amountTokens, sender=tester.k1)

    expectedEther = fees / 2
    if (collectFees):
        kitchenSinkFixture.contracts["Time"].setTimestamp(reportingWindow.getDisputeEndTime() + 1)
    else:
        expectedEther = 0

    with EtherDelta(expectedEther, tester.a1, kitchenSinkFixture.chain, "Redeeming didn't give eth correctly"):
        with TokenDelta(reputationToken, amountTokens, tester.a1, "Redeeming didn't give REP correctly"):
            universe.redeemStake([], [], [participationToken.address], not collectFees, sender=tester.k1)

def test_redeem_disavowed_and_forking_stake(kitchenSinkFixture, universe, cash, market):
    newMarket = kitchenSinkFixture.createReasonableBinaryMarket(universe, cash)
    reputationToken = kitchenSinkFixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingWindow = kitchenSinkFixture.applySignature('ReportingWindow', market.getReportingWindow())
    completeSets = kitchenSinkFixture.contracts['CompleteSets']

    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    # We'll do a designated report in the new market then dispute it to get stake and a dispute bond
    proceedToFirstReporting(kitchenSinkFixture, universe, newMarket, True, 1, [0,market.getNumTicks()], [market.getNumTicks(),0])

    # We proceed the standard market to the FORKING state
    proceedToForking(kitchenSinkFixture, universe, market, True, 1, 2, 3, [0,market.getNumTicks()], [market.getNumTicks(),0], 2, [market.getNumTicks(),0], [0,market.getNumTicks()], [market.getNumTicks(),0])
    forkingMarketStake = kitchenSinkFixture.getOrCreateStakeToken(market, [market.getNumTicks(),0])
    assert forkingMarketStake.balanceOf(tester.a1) > 0

    # The market we created is now awaiting migration
    assert newMarket.getReportingState() == kitchenSinkFixture.contracts['Constants'].AWAITING_FORK_MIGRATION()

    # We'll finalize the forking market
    finalizeForkingMarket(kitchenSinkFixture, universe, market, True, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,market.getNumTicks()], [market.getNumTicks(),0])

    stakeTokenAddress = kitchenSinkFixture.getOrCreateStakeToken(newMarket, [newMarket.getNumTicks(),0]).address
    disputeBondAddress = newMarket.getDesignatedReporterDisputeBond()

    # Now we can migrate the new market to the winning universe.
    assert newMarket.migrateThroughOneFork()

    # Redeem all of the disputer's disavowed stake tokens and dispute bonds in the new market
    childUniverseHash = market.derivePayoutDistributionHash([market.getNumTicks(),0], False)
    forkUniverse = kitchenSinkFixture.applySignature('Universe', universe.getOrCreateChildUniverse(childUniverseHash))
    forkReputationToken = kitchenSinkFixture.applySignature('ReputationToken', forkUniverse.getReputationToken())
    expectedForkREP = forkingMarketStake.balanceOf(tester.a1)
    expectedREP = 1 + kitchenSinkFixture.contracts["Constants"].DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()

    with TokenDelta(reputationToken, expectedREP, tester.a1, "Redeeming didn't give REP correctly"):
        with TokenDelta(forkReputationToken, expectedForkREP, tester.a1, "Redeeming forkingMarketStake didn't give REP correctly"):
            universe.redeemStake([stakeTokenAddress, forkingMarketStake.address], [disputeBondAddress], [], False, sender=tester.k1)
