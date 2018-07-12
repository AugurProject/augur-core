from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, PrintGasUsed, fix
from constants import BID, ASK, YES, NO
from datetime import timedelta
from trading.test_claimTradingProceeds import acquireLongShares, finalizeMarket
from reporting_utils import proceedToNextRound, proceedToFork, finalizeFork, proceedToDesignatedReporting

# Trading Max Costs

CREATE_ORDER_MAXES    =   [
    695034,
    794664,
    894294,
    993924,
    1093554,
    1193184,
    1292814,
]

CANCEL_ORDER_MAXES    =   [
    289826,
    379095,
    468364,
    557633,
    646902,
    736171,
    825440,
]

FILL_ORDER_MAXES    =   [
    933495,
    1172245,
    1410995,
    1649744,
    1888494,
    2127244,
    2365994,
]

#pytestmark = mark.skip(reason="Just for testing gas cost")

tester.STARTGAS = long(6.7 * 10**6)

@mark.parametrize('numOutcomes', range(2,9))
def test_orderCreationMax(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder']
    completeSets = localFixture.contracts['CompleteSets']
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    maxGas = 0
    cost = fix('1', '5000')

    assert completeSets.publicBuyCompleteSets(market.address, 100, value=1000000)
    outcome = 0
    shareToken = localFixture.applySignature('ShareToken', market.getShareToken(outcome))
    shareToken.transfer(tester.a7, 100)

    startGas = localFixture.chain.head_state.gas_used
    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == CREATE_ORDER_MAXES[marketIndex]

@mark.parametrize('numOutcomes', range(2,9))
def test_orderCancelationMax(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder']
    cancelOrder = localFixture.contracts['CancelOrder']
    completeSets = localFixture.contracts['CompleteSets']
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    assert completeSets.publicBuyCompleteSets(market.address, 100, value=1000000)
    outcome = 0
    shareToken = localFixture.applySignature('ShareToken', market.getShareToken(outcome))
    shareToken.transfer(tester.a7, 100)

    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))

    startGas = localFixture.chain.head_state.gas_used
    cancelOrder.cancelOrder(orderID)
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == CANCEL_ORDER_MAXES[marketIndex]

@mark.parametrize('numOutcomes', range(2,9))
def test_orderFilling(numOutcomes, localFixture, markets):
    createOrder = localFixture.contracts['CreateOrder']
    completeSets = localFixture.contracts['CompleteSets']
    fillOrder = localFixture.contracts['FillOrder']
    tradeGroupID = "42"
    marketIndex = numOutcomes - 2
    market = markets[marketIndex]

    cost = fix('1', '5000')

    assert completeSets.publicBuyCompleteSets(market.address, 100, value=1000000)
    outcome = 0
    shareToken = localFixture.applySignature('ShareToken', market.getShareToken(outcome))
    shareToken.transfer(tester.a7, 100)
    orderID = createOrder.publicCreateOrder(BID, fix(1), 5000, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), "7", value = fix(1, 5000))

    startGas = localFixture.chain.head_state.gas_used
    fillOrder.publicFillOrder(orderID, fix(1), tradeGroupID, sender = tester.k1, value=cost)
    maxGas = localFixture.chain.head_state.gas_used - startGas

    assert maxGas == FILL_ORDER_MAXES[marketIndex]


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    cash = ABIContract(fixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
    fixture.markets = [
        fixture.createReasonableCategoricalMarket(universe, 2, cash),
        fixture.createReasonableCategoricalMarket(universe, 3, cash),
        fixture.createReasonableCategoricalMarket(universe, 4, cash),
        fixture.createReasonableCategoricalMarket(universe, 5, cash),
        fixture.createReasonableCategoricalMarket(universe, 6, cash),
        fixture.createReasonableCategoricalMarket(universe, 7, cash),
        fixture.createReasonableCategoricalMarket(universe, 8, cash)
    ]

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def universe(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)

@fixture
def markets(localFixture, kitchenSinkSnapshot):
    return localFixture.markets
