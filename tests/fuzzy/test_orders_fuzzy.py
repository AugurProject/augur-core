from ethereum.tools import tester
import numpy as np
from os import getenv
from pytest import fixture, mark
from utils import fix, longTo32Bytes
from constants import BID, ASK

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
    (BID,  20, False,  0.0),
    (ASK,  20, False,  0.0),
    (BID,  40, False,  0.0),
    (ASK,  40, False,  0.0),

    (BID,  10, True,   0.0),
    (ASK,  10, True,   0.0),
    (BID,  20, True,   0.0),
    (ASK,  20, True,   0.0),
    (BID,  40, True,   0.0),
    (ASK,  40, True,   0.0),

    (BID,  10, True,  0.25),
    (ASK,  10, True,  0.25),
    (BID,  20, True,  0.25),
    (ASK,  20, True,  0.25),
    (BID,  40, True,  0.25),
    (ASK,  40, True,  0.25),

    (BID,  10, True,   0.5),
    (ASK,  10, True,   0.5),
    (BID,  20, True,   0.5),
    (ASK,  20, True,   0.5),
    (BID,  40, True,   0.5),
    (ASK,  40, True,   0.5),

    (BID,  10, True,  0.75),
    (ASK,  10, True,  0.75),
    (BID,  20, True,  0.75),
    (ASK,  20, True,  0.75),
    (BID,  40, True,  0.75),
    (ASK,  40, True,  0.75),

    (BID,  10, True,   1.0),
    (ASK,  10, True,   1.0),
    (BID,  20, True,   1.0),
    (ASK,  20, True,   1.0),
    (BID,  40, True,   1.0),
    (ASK,  40, True,   1.0),
])
def test_randomSorting(market, orderType, numOrders, withBoundingOrders, deadOrderProbability, fixture, kitchenSinkSnapshot):
    print("Order sorting tests (orderType=" + str(orderType) + ", numOrders=" + str(numOrders) + ", withBoundingOrders=" + str(withBoundingOrders) + ", deadOrderProbability=" + str(deadOrderProbability) + ")")
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    orders = fixture.contracts['Orders']
    outcomeId = 1
    orderIds = np.arange(1, numOrders + 1)
    # Generate random prices on [0, 1) and rank them (smallest price @ rank 0)
    fxpPrices = np.vectorize(fix)(np.random.rand(numOrders))
    orderIdsToPriceMapping = {}
    priceRanks = np.argsort(np.argsort(fxpPrices))
    logs = []
    assert orderType == BID or orderType == ASK
    if orderType == BID:
        bestOrderId = orderIds[np.argmax(priceRanks)]
        worstOrderId = orderIds[np.argmin(priceRanks)]
    if orderType == ASK:
        bestOrderId = orderIds[np.argmin(priceRanks)]
        worstOrderId = orderIds[np.argmax(priceRanks)]
    betterOrderIds = np.zeros(numOrders, dtype=np.int)
    worseOrderIds = np.zeros(numOrders, dtype=np.int)
    deadOrders = np.random.rand(numOrders, 2) < deadOrderProbability
    for i, priceRank in enumerate(priceRanks):
        if withBoundingOrders:
            if orderType == BID:
                betterOrders = np.flatnonzero(priceRank < priceRanks)
                worseOrders = np.flatnonzero(priceRank > priceRanks)
            else:
                betterOrders = np.flatnonzero(priceRank > priceRanks)
                worseOrders = np.flatnonzero(priceRank < priceRanks)
            if len(betterOrders): betterOrderIds[i] = orderIds[np.random.choice(betterOrders)]
            if len(worseOrders): worseOrderIds[i] = orderIds[np.random.choice(worseOrders)]
    print(np.c_[orderIds, fxpPrices, priceRanks, betterOrderIds, worseOrderIds, deadOrders])
    orderIdsToBytesMapping = {}
    bytesToOrderIdsMapping = {}
    for i, orderId in enumerate(orderIds):
        betterOrderId = betterOrderIds[i]
        worseOrderId = worseOrderIds[i]
        if withBoundingOrders:
            if orderType == BID:
                assert((orderId == bestOrderId and betterOrderId == 0) or fxpPrices[i] < fxpPrices[betterOrderId - 1]), "Input price is < better order price, or this is the best order so better order Id is zero"
                assert((orderId == worstOrderId and worseOrderId == 0) or fxpPrices[i] > fxpPrices[worseOrderId - 1]), "Input price is > worse order price, or this is the worst order so worse order Id is zero"
            else:
                assert((orderId == bestOrderId and betterOrderId == 0) or fxpPrices[i] > fxpPrices[betterOrderId - 1]), "Input price is > better order price, or this is the best order so better order Id is zero"
                assert((orderId == worstOrderId and worseOrderId == 0) or fxpPrices[i] < fxpPrices[worseOrderId - 1]), "Input price is < worse order price, or this is the worst order so worse order Id is zero"
            if deadOrders[i, 0]: betterOrderId = numOrders + 1
            if deadOrders[i, 1]: worseOrderId = numOrders + 1
        actualOrderId = orders.saveOrder(orderType, market.address, 1, fxpPrices[i], tester.a1, outcomeId, 0, 0, longTo32Bytes(betterOrderId), longTo32Bytes(worseOrderId), "0")
        assert(actualOrderId != bytearray(32)), "Insert order into list"
        orderIdsToPriceMapping[orderId] = fxpPrices[i]
        orderIdsToBytesMapping[orderId] = actualOrderId
        bytesToOrderIdsMapping[actualOrderId] =  orderId
    assert(orderIdsToBytesMapping[bestOrderId] == orders.getBestOrderId(orderType, market.address, outcomeId)), "Verify best order Id"
    assert(orderIdsToBytesMapping[worstOrderId] == orders.getWorstOrderId(orderType, market.address, outcomeId)), "Verify worst order Id"
    for orderId in orderIds:
        orderPrice = orderIdsToPriceMapping[orderId]
        betterOrderIdAsBytes = orders.getBetterOrderId(orderIdsToBytesMapping[orderId])
        worseOrderIdAsBytes = orders.getWorseOrderId(orderIdsToBytesMapping[orderId])
        betterOrderId = 0 if betterOrderIdAsBytes == longTo32Bytes(0) else bytesToOrderIdsMapping[betterOrderIdAsBytes]
        worseOrderId = 0 if worseOrderIdAsBytes == longTo32Bytes(0) else bytesToOrderIdsMapping[worseOrderIdAsBytes]
        betterOrderPrice = 0 if betterOrderId == 0 else orderIdsToPriceMapping[betterOrderId]
        worseOrderPrice = 0 if worseOrderId == 0 else orderIdsToPriceMapping[worseOrderId]
        if orderType == BID:
            if betterOrderPrice: assert(orderPrice <= betterOrderPrice), "Order price <= better order price"
            if worseOrderPrice: assert(orderPrice >= worseOrderPrice), "Order price >= worse order price"
        else:
            if betterOrderPrice: assert(orderPrice >= betterOrderPrice), "Order price >= better order price"
            if worseOrderPrice: assert(orderPrice <= worseOrderPrice), "Order price <= worse order price"
        if betterOrderId:
            assert(orders.getWorseOrderId(betterOrderIdAsBytes) == orderIdsToBytesMapping[orderId]), "Better order's worseOrderId should equal orderId"
        else:
            assert(orderId == bestOrderId), "Should be the best order Id"
        if worseOrderId:
            assert(orders.getBetterOrderId(worseOrderIdAsBytes) == orderIdsToBytesMapping[orderId]), "Worse order's betterOrderId should equal orderId"
        else:
            assert(orderId == worstOrderId), "Should be the worst order Id"
    for orderId in orderIds:
        assert(orders.removeOrder(orderIdsToBytesMapping[orderId]) == 1), "Remove order from list"
