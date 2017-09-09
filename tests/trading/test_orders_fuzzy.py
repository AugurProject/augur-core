from ethereum.tools import tester
import numpy as np
from os import getenv
from pytest import fixture, mark, lazy_fixture
from utils import fix

pytestmark = mark.skipif(not getenv('INCLUDE_FUZZY_TESTS'), reason="take forever to run")

BID = 1
ASK = 2

ATTOSHARES = 0
DISPLAY_PRICE = 1
OWNER = 2
TOKENS_ESCROWED = 3
SHARES_ESCROWED = 4
BETTER_ORDER_ID = 5
WORSE_ORDER_ID = 6
GAS_PRICE = 7

@mark.parametrize('orderType,numOrders,withBoundingOrders,deadOrderProbability', [
    (BID,  10, False,  0.0),
    (ASK,  10, False,  0.0),
    (BID,  50, False,  0.0),
    (ASK,  50, False,  0.0),
    (BID, 100, False,  0.0),
    (ASK, 100, False,  0.0),

    (BID,  10, True,   0.0),
    (ASK,  10, True,   0.0),
    (BID,  50, True,   0.0),
    (ASK,  50, True,   0.0),
    (BID, 100, True,   0.0),
    (ASK, 100, True,   0.0),

    (BID,  10, True,  0.25),
    (ASK,  10, True,  0.25),
    (BID,  50, True,  0.25),
    (ASK,  50, True,  0.25),
    (BID, 100, True,  0.25),
    (ASK, 100, True,  0.25),

    (BID,  10, True,   0.5),
    (ASK,  10, True,   0.5),
    (BID,  50, True,   0.5),
    (ASK,  50, True,   0.5),
    (BID, 100, True,   0.5),
    (ASK, 100, True,   0.5),

    (BID,  10, True,  0.75),
    (ASK,  10, True,  0.75),
    (BID,  50, True,  0.75),
    (ASK,  50, True,  0.75),
    (BID, 100, True,  0.75),
    (ASK, 100, True,  0.75),

    (BID,  10, True,   1.0),
    (ASK,  10, True,   1.0),
    (BID,  50, True,   1.0),
    (ASK,  50, True,   1.0),
    (BID, 100, True,   1.0),
    (ASK, 100, True,   1.0),
])
def test_randomSorting(orderType, numOrders, withBoundingOrders, deadOrderProbability, contractsFixture):
    print("Order sorting tests (orderType=" + str(orderType) + ", numOrders=" + str(numOrders) + ", withBoundingOrders=" + str(withBoundingOrders) + ", deadOrderProbability=" + str(deadOrderProbability) + ")")
    contractsFixture.resetSnapshot()
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    outcomeID = 1
    orderIDs = np.arange(1, numOrders + 1)
    # Generate random prices on [0, 1) and rank them (smallest price @ rank 0)
    fxpPrices = np.vectorize(fix)(np.random.rand(numOrders))
    priceRanks = np.argsort(np.argsort(fxpPrices))
    logs = []
    assert orderType == BID or orderType == ASK
    if orderType == BID:
        bestOrderID = orderIDs[np.argmax(priceRanks)]
        worstOrderID = orderIDs[np.argmin(priceRanks)]
    if orderType == ASK:
        bestOrderID = orderIDs[np.argmin(priceRanks)]
        worstOrderID = orderIDs[np.argmax(priceRanks)]
    betterOrderIDs = np.zeros(numOrders, dtype=np.int)
    worseOrderIDs = np.zeros(numOrders, dtype=np.int)
    deadOrders = np.random.rand(numOrders, 2) < deadOrderProbability
    for i, priceRank in enumerate(priceRanks):
        if withBoundingOrders:
            if orderType == BID:
                betterOrders = np.flatnonzero(priceRank < priceRanks)
                worseOrders = np.flatnonzero(priceRank > priceRanks)
            else:
                betterOrders = np.flatnonzero(priceRank > priceRanks)
                worseOrders = np.flatnonzero(priceRank < priceRanks)
            if len(betterOrders): betterOrderIDs[i] = orderIDs[np.random.choice(betterOrders)]
            if len(worseOrders): worseOrderIDs[i] = orderIDs[np.random.choice(worseOrders)]
    print(np.c_[orderIDs, fxpPrices, priceRanks, betterOrderIDs, worseOrderIDs, deadOrders])
    for i, orderID in enumerate(orderIDs):
        betterOrderID = betterOrderIDs[i]
        worseOrderID = worseOrderIDs[i]
        if withBoundingOrders:
            if orderType == BID:
                assert((orderID == bestOrderID and betterOrderID == 0) or fxpPrices[i] < fxpPrices[betterOrderID - 1]), "Input price is < better order price, or this is the best order so better order ID is zero"
                assert((orderID == worstOrderID and worseOrderID == 0) or fxpPrices[i] > fxpPrices[worseOrderID - 1]), "Input price is > worse order price, or this is the worst order so worse order ID is zero"
            else:
                assert((orderID == bestOrderID and betterOrderID == 0) or fxpPrices[i] > fxpPrices[betterOrderID - 1]), "Input price is > better order price, or this is the best order so better order ID is zero"
                assert((orderID == worstOrderID and worseOrderID == 0) or fxpPrices[i] < fxpPrices[worseOrderID - 1]), "Input price is < worse order price, or this is the worst order so worse order ID is zero"
            if deadOrders[i, 0]: betterOrderID = numOrders + 1
            if deadOrders[i, 1]: worseOrderID = numOrders + 1
        output = orders.saveOrder(orderType, market.address, 1, fxpPrices[i], tester.a1, outcomeID, 0, 0, betterOrderID, worseOrderID, 0)
        assert(output == 1), "Insert order into list"
    assert(bestOrderID == int(orders.getBestOrderID(orderType, market.address, outcomeID), 16)), "Verify best order ID"
    assert(worstOrderID == int(orders.getWorstOrderId(orderType, market.address, outcomeID), 16)), "Verify worst order ID"
    for orderID in orderIDs:
        order = ordersFetcher.getOrder(orderID)
        orderPrice = order[DISPLAY_PRICE]
        betterOrderID = order[BETTER_ORDER_ID]
        worseOrderID = order[WORSE_ORDER_ID]
        betterOrderPrice = orders.getPrice(betterOrderID, orderType, market.address, outcomeID)
        worseOrderPrice = orders.getPrice(worseOrderID, orderType, market.address, outcomeID)
        if orderType == BID:
            if betterOrderPrice: assert(orderPrice <= betterOrderPrice), "Order price <= better order price"
            if worseOrderPrice: assert(orderPrice >= worseOrderPrice), "Order price >= worse order price"
        else:
            if betterOrderPrice: assert(orderPrice >= betterOrderPrice), "Order price >= better order price"
            if worseOrderPrice: assert(orderPrice <= worseOrderPrice), "Order price <= worse order price"
        if betterOrderID:
            assert(ordersFetcher.getOrder(betterOrderID)[WORSE_ORDER_ID] == orderID), "Better order's worseOrderID should equal orderID"
        else:
            assert(orderID == bestOrderID), "Should be the best order ID"
        if worseOrderID:
            assert(ordersFetcher.getOrder(worseOrderID)[BETTER_ORDER_ID] == orderID), "Worse order's betterOrderID should equal orderID"
        else:
            assert(orderID == worstOrderID), "Should be the worst order ID"
    for orderID in orderIDs:
        assert(orders.removeOrder(orderID, orderType, market.address, outcomeID) == 1), "Remove order from list"
