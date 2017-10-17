from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed, ABIContract
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString, TokenDelta, ETHDelta

def test_token_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, reportingWindow):
    # We'll progress past the designated dispute phase and finalize all the markets
    localFixture.chain.head_state.timestamp = market.getEndTime() + localFixture.contracts["Constants"].DESIGNATED_REPORTING_DURATION_SECONDS() + 1
    utils = localFixture.contracts["Utils"]

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
        with ETHDelta(0, tester.a0, utils, "Forgoing fees gave fees incorrectly"):
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
            with ETHDelta(0, tester.a0, utils, "Forgoing fees gave fees incorrectly"):
                with StakeDelta(0, -participationValue, -participationValue, market, reportingWindow, "Forgoing fees incorrectly updated stake accounting"):
                    assert participationToken.redeem(True, sender=tester.k3)

    # Fast forward time until the window is over and we can redeem our winning stake and participation tokens and receive fees
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    reporterFees = 1000 * market.getNumTicks() / universe.getReportingFeeDivisor()
    totalWinningStake = reportingWindow.getTotalWinningStake()
    assert cash.balanceOf(reportingWindow.address) == reporterFees

    # Cashing out Participation tokens or Stake tokens will awards fees proportional to the total winning stake in the window
    expectedFees = reporterFees * participationTokenAmount / totalWinningStake
    with TokenDelta(participationToken, -participationTokenAmount, tester.a0, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with ETHDelta(expectedFees, tester.a0, utils, "Redeeming participation tokens didn't increase ETH correctly"):
            assert participationToken.redeem(False)

    expectedFees = reporterFees * participationTokenAmount / totalWinningStake
    with TokenDelta(participationToken, -participationTokenAmount, tester.a1, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with ETHDelta(expectedFees, tester.a1, utils, "Redeeming participation tokens didn't increase ETH correctly"):
            assert participationToken.redeem(False, sender=tester.k1)

    expectedFees = reporterFees * participationTokenAmount / totalWinningStake
    with TokenDelta(participationToken, -participationTokenAmount, tester.a2, "Redeeming participation tokens didn't decrease participation token balance correctly"):
        with ETHDelta(expectedFees, tester.a2, utils, "Redeeming participation tokens didn't increase ETH correctly"):
            assert participationToken.redeem(False, sender=tester.k2)

    marketStake = marketDesignatedStake.balanceOf(tester.a0)
    expectedFees = reporterFees * marketStake / totalWinningStake + 1 # Rounding error
    with ETHDelta(expectedFees, tester.a0, utils, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(marketDesignatedStake, -marketStake, tester.a0, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert marketDesignatedStake.redeemWinningTokens(False)

    categoricalMarketStake = categoricalMarketDesignatedStake.balanceOf(tester.a0)
    expectedFees = reporterFees * categoricalMarketStake / totalWinningStake + 1 # Rounding error
    with ETHDelta(expectedFees, tester.a0, utils, "Redeeming Stake tokens didn't increase ETH correctly"):
        with TokenDelta(categoricalMarketDesignatedStake, -categoricalMarketStake, tester.a0, "Redeeming Stake tokens didn't decrease Stake token balance correctly"):
            assert categoricalMarketDesignatedStake.redeemWinningTokens(False)

def test_dispute_bond_fee_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, reportingWindow):
    pass
    # And we'll put up a dispute bond for each of the markets and progress into the Limited Reporting phase

    # We can't redeem the stake used to do the designated report yet since the window is not yet over

    # We'll purchase some participation tokens

    # Fast forward time until the window is over and we can redeem our winning stake, participation, and dispute bond tokens and receive fees

def test_fee_migration_collection(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, reportingWindow):
    pass
    # And we'll put up a dispute bond for each of the markets and progress into the Limited Reporting phase

    # Progress to the Limited dispute phase and dispute one of the markets

    # Fast forward time until the window is over and we can redeem our winning stake, participation, and dispute bond tokens and receive fees

    # Confirm fees in the migrated to window and then fast forward time and collect in that window

def test_forking(localFixture, universe, market, categoricalMarket, scalarMarket, cash, reputationToken, reportingWindow):
    pass
    # And we'll put up a dispute bond for each of the markets and progress into the Round 1 & 2 Reporting phase

    # Progress into round 2 dispute and cause a fork

    # migrate REP to the universes and finalize the forking market

    # migrate one of the markets to the winning universe and confirm fees went with it

    # migrate the other markets

    # Fast forward time until the new window is over and we can redeem our winning stake, participation, and dispute bond tokens and receive fees

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
    with ETHDelta(marketCreatorFees, tester.a0, utils, "The market creator didn't get their share of fees from complete set sale"):
        completeSets.publicSellCompleteSets(market.address, 1000, sender=tester.k1)
    fees = cash.balanceOf(market.getReportingWindow())
    reporterFees = cost / universe.getReportingFeeDivisor()
    assert fees == reporterFees

    # Distribute REP
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    for testAccount in [tester.a1, tester.a2, tester.a3]:
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
        assert resultmarketTotalStakeDelta == marketTotalStakeDelta, self.err
        assert resultWindowTotalStakeDelta == windowTotalStakeDelta, self.err
        assert resultWindowTotalWinningStakeDelta == windowTotalWinningStakeDelta, self.err
