from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, PrintGasUsed, fix
from constants import BID, ASK, YES, NO
from trading.test_claimProceeds import acquireLongShares, finalizeMarket
from reporting_utils import proceedToDesignatedReporting, proceedToFirstReporting, proceedToLastReporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

tester.STARTGAS = long(6.7 * 10**6)

pytestmark = mark.skip(reason="Just for testing gas cost")

def test_orderCreation(localFixture, market):
    createOrder = localFixture.contracts['CreateOrder']

    with PrintGasUsed(localFixture, "CreateOrder:publicCreateOrder", 432784):
        orderID = createOrder.publicCreateOrder(BID, 1, 10**17, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), 7, value = 10**17)

def test_orderFilling(localFixture, market):
    createOrder = localFixture.contracts['CreateOrder']
    fillOrder = localFixture.contracts['FillOrder']
    tradeGroupID = 42

    creatorCost = fix('2', '0.6')
    fillerCost = fix('2', '0.4')

    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    with PrintGasUsed(localFixture, "FillOrder:publicFillOrder", 547527):
        fillOrderID = fillOrder.publicFillOrder(orderID, 2, tradeGroupID, sender = tester.k2, value=fillerCost)

def test_winningShareRedmption(localFixture, cash, market):
    claimProceeds = localFixture.contracts['ClaimProceeds']

    acquireLongShares(localFixture, cash, market, YES, 1, claimProceeds.address, sender = tester.k1)
    finalizeMarket(localFixture, market, [0,10**18])

    with PrintGasUsed(localFixture, "ClaimProceeds:claimProceeds", 408079):
        claimProceeds.claimProceeds(market.address, sender = tester.k1)

def test_designatedReport(localFixture, universe, cash, market):
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    with PrintGasUsed(localFixture, "Market:designatedReport", 743518):
        assert localFixture.designatedReport(market, [0,10**18], tester.k0)

def test_report(localFixture, universe, cash, market):
    proceedToFirstReporting(localFixture, universe, market, False, tester.k1, [0,10**18], [10**18,0])

    stakeTokenYes = localFixture.getStakeToken(market, [0,10**18])
    with PrintGasUsed(localFixture, "StakeToken:buy", 531560):
        stakeTokenYes.buy(0, sender=tester.k2)

def test_disputeDesignated(localFixture, universe, cash, market):
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    assert localFixture.designatedReport(market, [0,10**18], tester.k0)

    with PrintGasUsed(localFixture, "Market:disputeDesignatedReport", 1680957):
        assert market.disputeDesignatedReport([1, market.getNumTicks()-1], 1, False, sender=tester.k1)

def test_disputeFirst(localFixture, universe, cash, market):
    proceedToFirstReporting(localFixture, universe, market, True, tester.k1, [0,10**18], [10**18,0])

    reportingWindow = localFixture.applySignature("ReportingWindow", market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    with PrintGasUsed(localFixture, "Market:disputeFirstReporters", 2735270):
        assert market.disputeFirstReporters([1, market.getNumTicks()-1], 1, False, sender=tester.k2)

def test_disputeLast(localFixture, universe, cash, market):
    proceedToLastReporting(localFixture, universe, market, True, tester.k1, tester.k3, [0,10**18], [10**18,0], tester.k2, [10**18,0], [0,10**18])

    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    with PrintGasUsed(localFixture, "Market:disputeLastReporters", 1818038):
        assert market.disputeLastReporters()

def test_redeemStake(localFixture, universe, cash, market, categoricalMarket, scalarMarket):
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    assert localFixture.designatedReport(market, [0,10**18], tester.k0)
    assert localFixture.designatedReport(categoricalMarket, [0,0,categoricalMarket.getNumTicks()], tester.k0)
    assert localFixture.designatedReport(scalarMarket, [0,scalarMarket.getNumTicks()], tester.k0)

    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    stakeToken = localFixture.getStakeToken(market, [0,10**18])

    with PrintGasUsed(localFixture, "StakeToken:redeemWinningTokens", 189534):
        stakeToken.redeemWinningTokens(False)

def test_redeemDispute(localFixture, universe, cash, market, categoricalMarket, scalarMarket):
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    assert localFixture.designatedReport(market, [0,10**18], tester.k0)
    assert localFixture.designatedReport(categoricalMarket, [0,0,categoricalMarket.getNumTicks()], tester.k0)
    assert localFixture.designatedReport(scalarMarket, [0,scalarMarket.getNumTicks()], tester.k0)

    assert market.disputeDesignatedReport([10**18,0], 1, False)

    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    disputeBond = localFixture.applySignature("DisputeBondToken", market.getDesignatedReporterDisputeBondToken())

    with PrintGasUsed(localFixture, "DisputeBondToken:withdraw", 160161):
        assert disputeBond.withdraw()

def test_redeemParticipation(localFixture, universe, cash, market, categoricalMarket, scalarMarket):
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    assert localFixture.designatedReport(market, [0,10**18], tester.k0)
    assert localFixture.designatedReport(categoricalMarket, [0,0,categoricalMarket.getNumTicks()], tester.k0)
    assert localFixture.designatedReport(scalarMarket, [0,scalarMarket.getNumTicks()], tester.k0)

    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    # We cannot purchase participation tokens yet since the window isn't active
    participationToken = localFixture.applySignature("ParticipationToken", reportingWindow.getParticipationToken())

    # We'll progress to the start of the window and purchase some participation tokens
    localFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1
    assert participationToken.buy(1)

    # Fast forward time until the window is over and we can redeem our winning stake and participation tokens and receive fees
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

    with PrintGasUsed(localFixture, "DisputeBondToken:withdraw", 55303):
        assert participationToken.redeem(False)

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    return initializeReportingFixture(fixture, universe, market)

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
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
