from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, PrintGasUsed, fix
from constants import BID, ASK, YES, NO
from datetime import timedelta
from trading.test_claimTradingProceeds import acquireLongShares, finalizeMarket
from reporting_utils import proceedToNextRound, proceedToFork, finalizeFork, proceedToDesignatedReporting

# Market Methods
MARKET_CREATION =               3127331
MARKET_FINALIZATION =           228345
INITIAL_REPORT =                1498320
FIRST_CONTRIBUTE =              1037377
FIRST_COMPLETED_CONTRIBUTE =    369810
LAST_COMPLETED_CONTRIBUTE =     4398805
FORKING_CONTRIBUTE =            1212533

# Redemption
REPORTING_WINDOW_CREATE =           848027
INITIAL_REPORT_REDEMPTION =         517315
CROWDSOURCER_REDEMPTION =           432903
PARTICIPATION_TOKEN_REDEMPTION =    93737

# Trading
CREATE_ORDER =      551929
FILL_ORDER =        828536
CLAIM_PROCEEDS =    2171595

pytestmark = mark.skip(reason="Just for testing gas cost")

tester.STARTGAS = long(6.7 * 10**6)

def test_feeWindowCreation(localFixture, universe, cash):
    endTime = long(localFixture.chain.head_state.timestamp + timedelta(days=365).total_seconds())

    with PrintGasUsed(localFixture, "REPORTING_WINDOW_CREATE", REPORTING_WINDOW_CREATE):
        universe.getOrCreateFeeWindowByTimestamp(endTime)

def test_marketCreation(localFixture, universe, cash):
    marketCreationFee = universe.getOrCacheMarketCreationCost()

    endTime = long(localFixture.chain.head_state.timestamp + timedelta(days=1).total_seconds())
    feePerEthInWei = 10**16
    denominationToken = cash
    designatedReporterAddress = tester.a0
    numTicks = 10 ** 18
    numOutcomes = 2

    with PrintGasUsed(localFixture, "FeeWindow:createMarket", MARKET_CREATION):
        marketAddress = universe.createYesNoMarket(endTime, feePerEthInWei, denominationToken.address, designatedReporterAddress, "", "description", "", value = marketCreationFee)

def test_marketFinalization(localFixture, universe, market):
    proceedToNextRound(localFixture, market)

    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    with PrintGasUsed(localFixture, "Market:finalize", MARKET_FINALIZATION):
        assert market.finalize()

@mark.parametrize('hints', [
    True,
    False
])
def test_orderCreation(hints, localFixture, categoricalMarket):
    createOrder = localFixture.contracts['CreateOrder']

    for i in range(3900, 4003):
        createOrder.publicCreateOrder(BID, fix(1), i, categoricalMarket.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, i))

    worseOrderId = createOrder.publicCreateOrder(BID, fix(1), 4004, categoricalMarket.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 4004))
    betterOrderId = createOrder.publicCreateOrder(BID, fix(1), 4006, categoricalMarket.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 4006))

    for i in range(4007, 4107):
        createOrder.publicCreateOrder(BID, fix(1), i, categoricalMarket.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, i))

    if not hints:
        with PrintGasUsed(localFixture, "CreateOrder:publicCreateOrder NO Hints", CREATE_ORDER):
            orderID = createOrder.publicCreateOrder(BID, fix(1), 4005, categoricalMarket.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 4005))
    else:
        with PrintGasUsed(localFixture, "CreateOrder:publicCreateOrder HINTS", CREATE_ORDER):
            orderID = createOrder.publicCreateOrder(BID, fix(1), 4005, categoricalMarket.address, 1, betterOrderId, worseOrderId, "7", value = fix(1, 4005))

def test_orderFilling(localFixture, market):
    createOrder = localFixture.contracts['CreateOrder']
    fillOrder = localFixture.contracts['FillOrder']
    tradeGroupID = "42"

    creatorCost = fix('2', '4000')
    fillerCost = fix('2', '6000')

    # create order
    orderID = createOrder.publicCreateOrder(ASK, fix(2), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    with PrintGasUsed(localFixture, "FillOrder:publicFillOrder", FILL_ORDER):
        fillOrderID = fillOrder.publicFillOrder(orderID, fix(2), tradeGroupID, sender = tester.k2, value=fillerCost)

def test_winningShareRedmption(localFixture, cash, market):
    claimTradingProceeds = localFixture.contracts['ClaimTradingProceeds']

    acquireLongShares(localFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k1)
    finalizeMarket(localFixture, market, [0,market.getNumTicks()])

    with PrintGasUsed(localFixture, "ClaimTradingProceeds:claimTradingProceeds", CLAIM_PROCEEDS):
        claimTradingProceeds.claimTradingProceeds(market.address, tester.a1)

def test_initial_report(localFixture, universe, cash, market):
    proceedToDesignatedReporting(localFixture, market)

    with PrintGasUsed(localFixture, "Market:doInitialReport", INITIAL_REPORT):
        market.doInitialReport([0, market.getNumTicks()], False)

def test_contribute(localFixture, universe, cash, market):
    proceedToNextRound(localFixture, market)

    with PrintGasUsed(localFixture, "Market.contribute", FIRST_CONTRIBUTE):
        market.contribute([0, market.getNumTicks()], False, 1)

    with PrintGasUsed(localFixture, "Market.contribute", FIRST_COMPLETED_CONTRIBUTE):
        market.contribute([0, market.getNumTicks()], False, market.getParticipantStake())

    for i in range(9):
        proceedToNextRound(localFixture, market, randomPayoutNumerators = True)

    with PrintGasUsed(localFixture, "Market.contribute", LAST_COMPLETED_CONTRIBUTE):
        proceedToNextRound(localFixture, market, randomPayoutNumerators = True)

    with PrintGasUsed(localFixture, "Market.contribute", FORKING_CONTRIBUTE):
        market.contribute([market.getNumTicks() / 2, market.getNumTicks() / 2], False, market.getParticipantStake())

def test_redeem(localFixture, universe, cash, market):
    # Initial report
    proceedToNextRound(localFixture, market)
    # Initial losing
    proceedToNextRound(localFixture, market)
    # Initial Winning
    proceedToNextRound(localFixture, market, doGenerateFees = True)

    initialReporter = localFixture.applySignature('InitialReporter', market.getReportingParticipant(0))
    winningDisputeCrowdsourcer1 = localFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(2))
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())

    assert feeWindow.buy(100)

    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    with PrintGasUsed(localFixture, "InitialReporter:redeem", INITIAL_REPORT_REDEMPTION):
        initialReporter.redeem(tester.a0)

    with PrintGasUsed(localFixture, "DisputeCrowdsourcer:redeem", CROWDSOURCER_REDEMPTION):
        winningDisputeCrowdsourcer1.redeem(tester.a0)

    with PrintGasUsed(localFixture, "FeeWindow:redeem", PARTICIPATION_TOKEN_REDEMPTION):
        feeWindow.redeem(tester.a0)


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['yesNoMarket'].translator, kitchenSinkSnapshot['yesNoMarket'].address)
    # Give some REP to testers to make things interesting
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

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
