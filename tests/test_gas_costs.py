from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, PrintGasUsed, fix
from constants import BID, ASK, YES, NO
from trading.test_claimProceeds import acquireLongShares, finalizeMarket
from reporting_utils import proceedToDesignatedReporting, proceedToRound1Reporting, proceedToRound2Reporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

tester.STARTGAS = long(6.7 * 10**6)

#pytestmark = mark.skip(reason="Just for testing gas cost")

def test_orderCreation(localFixture, market):
    createOrder = localFixture.contracts['CreateOrder']

    with PrintGasUsed(localFixture, "CreateOrder:publicCreateOrder", 439478):
        orderID = createOrder.publicCreateOrder(BID, 1, 10**17, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), 7, value = 10**17)

def test_orderFilling(localFixture, market):
    createOrder = localFixture.contracts['CreateOrder']
    fillOrder = localFixture.contracts['FillOrder']
    tradeGroupID = 42

    creatorCost = fix('2', '0.6')
    fillerCost = fix('2', '0.4')

    orderID = createOrder.publicCreateOrder(BID, 2, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender = tester.k1, value=creatorCost)

    with PrintGasUsed(localFixture, "FillOrder:publicFillOrder", 553789):
        fillOrderID = fillOrder.publicFillOrder(orderID, 2, tradeGroupID, sender = tester.k2, value=fillerCost)

def test_winningShareRedmption(localFixture, cash, market):
    claimProceeds = localFixture.contracts['ClaimProceeds']

    acquireLongShares(localFixture, cash, market, YES, 1, claimProceeds.address, sender = tester.k1)
    finalizeMarket(localFixture, market, [0,10**18])

    with PrintGasUsed(localFixture, "ClaimProceeds:claimProceeds", 405416):
        claimProceeds.claimProceeds(market.address, sender = tester.k1)

def test_designatedReport(localFixture, universe, cash, market):
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    with PrintGasUsed(localFixture, "Market:designatedReport", 913077):
        assert localFixture.designatedReport(market, [0,10**18], tester.k0)

def test_report(localFixture, universe, cash, market):
    proceedToRound1Reporting(localFixture, universe, market, False, tester.k1, [0,10**18], [10**18,0])

    stakeTokenYes = localFixture.getStakeToken(market, [0,10**18])
    with PrintGasUsed(localFixture, "StakeToken:buy", 646809):
        stakeTokenYes.buy(0, sender=tester.k2)

def test_disputeDesignated(localFixture, universe, cash, market):
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    assert localFixture.designatedReport(market, [0,10**18], tester.k0)

    with PrintGasUsed(localFixture, "Market:disputeDesignatedReport", 1945547):
        assert market.disputeDesignatedReport([1, market.getNumTicks()-1], 1, False, sender=tester.k1)

def test_disputeRound1(localFixture, universe, cash, market):
    proceedToRound1Reporting(localFixture, universe, market, True, tester.k1, [0,10**18], [10**18,0])

    reportingWindow = localFixture.applySignature("ReportingWindow", market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    with PrintGasUsed(localFixture, "Market:disputeRound1Reporters", 2557652):
        assert market.disputeRound1Reporters([1, market.getNumTicks()-1], 1, False, sender=tester.k2)

def test_disputeRound2(localFixture, universe, cash, market):
    proceedToRound2Reporting(localFixture, universe, market, True, tester.k1, tester.k3, [0,10**18], [10**18,0], tester.k2, [10**18,0], [0,10**18])

    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    with PrintGasUsed(localFixture, "Market:disputeRound2Reporters", 1541875):
        assert market.disputeRound2Reporters()

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

    with PrintGasUsed(localFixture, "StakeToken:redeemWinningTokens", 199893):
        stakeToken.redeemWinningTokens(False)

def test_redeemDispute(localFixture, universe, cash, market, categoricalMarket, scalarMarket):
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    assert localFixture.designatedReport(market, [0,10**18], tester.k0)
    assert localFixture.designatedReport(categoricalMarket, [0,0,categoricalMarket.getNumTicks()], tester.k0)
    assert localFixture.designatedReport(scalarMarket, [0,scalarMarket.getNumTicks()], tester.k0)

    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    disputeBond = localFixture.applySignature("DisputeBondToken", market.getDesignatedReporterDisputeBondToken())

    with PrintGasUsed(localFixture, "DisputeBondToken:withdraw", 21272):
        disputeBond.withdraw()

# TODO when this gets merged
def test_redeemAttendance(localFixture, universe, cash, market):
    pass


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
