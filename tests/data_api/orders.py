#!/usr/bin/env python

from __future__ import division
import os
import sys
import json
import iocapture
import ethereum.tester
import utils
import numpy as np

np.set_printoptions(linewidth=225)

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir)
src = os.path.join(ROOT, "src")

BID = 1
ASK = 2

WEI_TO_ETH = 10**18
TWO = 2*WEI_TO_ETH
HALF = WEI_TO_ETH/2

def test_orders(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
    c = contracts.orders
    market1 = 1111111111
    address0 = long(t.a0.encode("hex"), 16)
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    order1 = 123456789
    order2 = 987654321
    WEI_TO_ETH = 10**18
    pointFive = 10**17*5

    def test_randomOrderSorting():
        def test_randomSorting(orderType, numOrders, withBoundingOrders=False, deadOrderProbability=0.0):
            print("Order sorting tests (orderType=" + str(orderType) + ", numOrders=" + str(numOrders) + ", withBoundingOrders=" + str(withBoundingOrders) + ", deadOrderProbability=" + str(deadOrderProbability) + ")")
            marketID = utils.createMarket(contracts, utils.createBinaryEvent(contracts))
            contracts._ContractLoader__state.mine(1)
            outcomeID = 1
            orderIDs = np.arange(1, numOrders + 1)
            # Generate random prices on [0, 1) and rank them (smallest price @ rank 0)
            fxpPrices = np.vectorize(utils.fix)(np.random.rand(numOrders))
            priceRanks = np.argsort(np.argsort(fxpPrices))
            if orderType == BID:
                bestOrderID = orderIDs[np.argmax(priceRanks)]
                worstOrderID = orderIDs[np.argmin(priceRanks)]
            else:
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
                with iocapture.capture() as captured:
                    output = contracts.orders.saveOrder(orderID, orderType, marketID, 1, fxpPrices[i], t.a1, outcomeID, 0, 0, betterOrderID, worseOrderID, 0, 20000000)
                assert(output == 1), "Insert order into list"
                contracts._ContractLoader__state.mine(1)
            assert(bestOrderID == int(contracts.orders.getBestOrderID(orderType, marketID, outcomeID), 16)), "Verify best order ID"
            assert(worstOrderID == int(contracts.orders.getWorstOrderID(orderType, marketID, outcomeID), 16)), "Verify worst order ID"
            for orderID in orderIDs:
                order = contracts.orders.getOrder(orderID, orderType, marketID, outcomeID)
                orderPrice = order[4]
                betterOrderID = order[10]
                worseOrderID = order[11]
                betterOrderPrice = contracts.orders.getPrice(betterOrderID, orderType, marketID, outcomeID)
                worseOrderPrice = contracts.orders.getPrice(worseOrderID, orderType, marketID, outcomeID)
                if orderType == BID:
                    if betterOrderPrice: assert(orderPrice <= betterOrderPrice), "Order price <= better order price"
                    if worseOrderPrice: assert(orderPrice >= worseOrderPrice), "Order price >= worse order price"
                else:
                    if betterOrderPrice: assert(orderPrice >= betterOrderPrice), "Order price >= better order price"
                    if worseOrderPrice: assert(orderPrice <= worseOrderPrice), "Order price <= worse order price"
                if betterOrderID:
                    assert(contracts.orders.getOrder(betterOrderID, orderType, marketID, outcomeID)[11] == orderID), "Better order's worseOrderID should equal orderID"
                else:
                    assert(orderID == bestOrderID), "Should be the best order ID"
                if worseOrderID:
                    assert(contracts.orders.getOrder(worseOrderID, orderType, marketID, outcomeID)[10] == orderID), "Worse order's betterOrderID should equal orderID"
                else:
                    assert(orderID == worstOrderID), "Should be the worst order ID"
            for orderID in orderIDs:
                assert(contracts.orders.removeOrder(orderID, orderType, marketID, outcomeID) == 1), "Remove order from list"
                contracts._ContractLoader__state.mine(1)

        def run_randomSorting_tests(withBoundingOrders, deadOrderProbability=0.0):
            test_randomSorting(BID, 10, withBoundingOrders=withBoundingOrders, deadOrderProbability=deadOrderProbability)
            test_randomSorting(ASK, 10, withBoundingOrders=withBoundingOrders, deadOrderProbability=deadOrderProbability)
            test_randomSorting(BID, 50, withBoundingOrders=withBoundingOrders, deadOrderProbability=deadOrderProbability)
            test_randomSorting(ASK, 50, withBoundingOrders=withBoundingOrders, deadOrderProbability=deadOrderProbability)
            test_randomSorting(BID, 100, withBoundingOrders=withBoundingOrders, deadOrderProbability=deadOrderProbability)
            test_randomSorting(ASK, 100, withBoundingOrders=withBoundingOrders, deadOrderProbability=deadOrderProbability)

        run_randomSorting_tests(False)
        run_randomSorting_tests(True, deadOrderProbability=0.0)
        run_randomSorting_tests(True, deadOrderProbability=0.25)
        run_randomSorting_tests(True, deadOrderProbability=0.5)
        run_randomSorting_tests(True, deadOrderProbability=0.75)
        run_randomSorting_tests(True, deadOrderProbability=1.0)

    def test_walkOrderList():
        def test_walkOrderList_bids():
            marketID = utils.createMarket(contracts, utils.createBinaryEvent(contracts))
            contracts._ContractLoader__state.mine(1)
            outcomeID = 1
            order = {
                "orderID": 5,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": outcomeID,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }
            assert(contracts.orders.saveOrder(order["orderID"], order["type"], marketID, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"], 1) == 1), "Save order"
            contracts._ContractLoader__state.mine(1)
            bestOrderID = int(contracts.orders.getBestOrderID(1, marketID, outcomeID), 16)
            worstOrderID = int(contracts.orders.getWorstOrderID(1, marketID, outcomeID), 16)
            assert(bestOrderID == 5)
            assert(worstOrderID == 5)
            # walk down order list starting from bestOrderID
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.6"), bestOrderID) == [5, 0])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.59"), bestOrderID) == [5, 0])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.61"), bestOrderID) == [0, 5])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.58"), bestOrderID) == [5, 0])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.595"), bestOrderID) == [5, 0])
            # walk up order list starting from worstOrderID
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.6"), worstOrderID) == [5, 0])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.59"), worstOrderID) == [5, 0])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.61"), worstOrderID) == [0, 5])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.58"), worstOrderID) == [5, 0])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.595"), bestOrderID) == [5, 0])
            order = {
                "orderID": 6,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": outcomeID,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }
            assert(contracts.orders.saveOrder(order["orderID"], order["type"], marketID, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"], 1) == 1), "Save order"
            contracts._ContractLoader__state.mine(1)
            bestOrderID = int(contracts.orders.getBestOrderID(1, marketID, outcomeID), 16)
            worstOrderID = int(contracts.orders.getWorstOrderID(1, marketID, outcomeID), 16)
            assert(bestOrderID == 5)
            assert(worstOrderID == 6)
            # walk down order list starting from bestOrderID
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.6"), bestOrderID) == [5, 6])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.59"), bestOrderID) == [6, 0])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.61"), bestOrderID) == [0, 5])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.58"), bestOrderID) == [6, 0])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.595"), bestOrderID) == [5, 6])
            # walk up order list starting from worstOrderID
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.6"), worstOrderID) == [5, 6])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.59"), worstOrderID) == [6, 0])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.61"), worstOrderID) == [0, 5])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.58"), worstOrderID) == [6, 0])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.595"), bestOrderID) == [5, 6])
            order = {
                "orderID": 7,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.595"),
                "sender": t.a0,
                "outcome": outcomeID,
                "fxpMoneyEscrowed": utils.fix("0.595"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }
            assert(contracts.orders.saveOrder(order["orderID"], order["type"], marketID, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"], 1) == 1), "Save order"
            contracts._ContractLoader__state.mine(1)
            bestOrderID = int(contracts.orders.getBestOrderID(1, marketID, outcomeID), 16)
            worstOrderID = int(contracts.orders.getWorstOrderID(1, marketID, outcomeID), 16)
            assert(bestOrderID == 5)
            assert(worstOrderID == 6)
            # walk down order list starting from bestOrderID
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.6"), bestOrderID) == [5, 7])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.59"), bestOrderID) == [6, 0])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.61"), bestOrderID) == [0, 5])
            assert(contracts.orders.descendOrderList(1, marketID, outcomeID, utils.fix("0.58"), bestOrderID) == [6, 0])
            # walk up order list starting from worstOrderID
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.6"), worstOrderID) == [5, 7])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.59"), worstOrderID) == [6, 0])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.61"), worstOrderID) == [0, 5])
            assert(contracts.orders.ascendOrderList(1, marketID, outcomeID, utils.fix("0.58"), worstOrderID) == [6, 0])
            assert(contracts.orders.removeOrder(5, 1, marketID, outcomeID) == 1), "Remove order 5"
            assert(contracts.orders.removeOrder(6, 1, marketID, outcomeID) == 1), "Remove order 6"
            assert(contracts.orders.removeOrder(7, 1, marketID, outcomeID) == 1), "Remove order 7"
        def test_walkOrderList_asks():
            marketID = utils.createMarket(contracts, utils.createBinaryEvent(contracts))
            contracts._ContractLoader__state.mine(1)
            outcomeID = 1
            order = {
                "orderID": 8,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": outcomeID,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }
            assert(contracts.orders.saveOrder(order["orderID"], order["type"], marketID, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"], 1) == 1), "Save order"
            contracts._ContractLoader__state.mine(1)
            bestOrderID = int(contracts.orders.getBestOrderID(2, marketID, outcomeID), 16)
            worstOrderID = int(contracts.orders.getWorstOrderID(2, marketID, outcomeID), 16)
            assert(bestOrderID == 8)
            assert(worstOrderID == 8)
            # walk down order list starting from bestOrderID
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.6"), bestOrderID) == [8, 0])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.59"), bestOrderID) == [0, 8])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.61"), bestOrderID) == [8, 0])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.58"), bestOrderID) == [0, 8])
            # walk up order list starting from worstOrderID
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.6"), worstOrderID) == [8, 0])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.59"), worstOrderID) == [0, 8])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.61"), worstOrderID) == [8, 0])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.58"), worstOrderID) == [0, 8])
            order = {
                "orderID": 9,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": outcomeID,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }
            assert(contracts.orders.saveOrder(order["orderID"], order["type"], marketID, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"], 1) == 1), "Save order"
            contracts._ContractLoader__state.mine(1)
            bestOrderID = int(contracts.orders.getBestOrderID(2, marketID, outcomeID), 16)
            worstOrderID = int(contracts.orders.getWorstOrderID(2, marketID, outcomeID), 16)
            assert(bestOrderID == 9)
            assert(worstOrderID == 8)
            # walk down order list starting from bestOrderID
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.6"), bestOrderID) == [8, 0])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.59"), bestOrderID) == [9, 8])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.61"), bestOrderID) == [8, 0])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.58"), bestOrderID) == [0, 9])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.595"), bestOrderID) == [9, 8])
            # walk up order list starting from worstOrderID
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.6"), worstOrderID) == [8, 0])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.59"), worstOrderID) == [9, 8])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.61"), worstOrderID) == [8, 0])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.58"), worstOrderID) == [0, 9])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.595"), bestOrderID) == [9, 8])
            order = {
                "orderID": 10,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.595"),
                "sender": t.a0,
                "outcome": outcomeID,
                "fxpMoneyEscrowed": utils.fix("0.595"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }
            assert(contracts.orders.saveOrder(order["orderID"], order["type"], marketID, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"], 1) == 1), "Save order"
            contracts._ContractLoader__state.mine(1)
            bestOrderID = int(contracts.orders.getBestOrderID(2, marketID, outcomeID), 16)
            worstOrderID = int(contracts.orders.getWorstOrderID(2, marketID, outcomeID), 16)
            assert(bestOrderID == 9)
            assert(worstOrderID == 8)
            # walk down order list starting from bestOrderID
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.6"), bestOrderID) == [8, 0])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.59"), bestOrderID) == [9, 10])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.61"), bestOrderID) == [8, 0])
            assert(contracts.orders.descendOrderList(2, marketID, outcomeID, utils.fix("0.58"), bestOrderID) == [0, 9])
            # walk up order list starting from worstOrderID
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.6"), worstOrderID) == [8, 0])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.59"), worstOrderID) == [9, 10])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.61"), worstOrderID) == [8, 0])
            assert(contracts.orders.ascendOrderList(2, marketID, outcomeID, utils.fix("0.58"), worstOrderID) == [0, 9])
            assert(contracts.orders.removeOrder(8, 2, marketID, outcomeID) == 1), "Remove order 8"
            assert(contracts.orders.removeOrder(9, 2, marketID, outcomeID) == 1), "Remove order 9"
            assert(contracts.orders.removeOrder(10, 2, marketID, outcomeID) == 1), "Remove order 10"
        test_walkOrderList_bids()
        test_walkOrderList_asks()

    def test_orderSorting():
        def runtest(testCase):
            marketID = utils.createMarket(contracts, utils.createBinaryEvent(contracts))
            contracts._ContractLoader__state.mine(1)
            orders = []
            for order in testCase["orders"]:
                with iocapture.capture() as captured:
                    output = contracts.orders.saveOrder(order["orderID"],
                                                        order["type"],
                                                        marketID,
                                                        order["fxpAmount"],
                                                        order["fxpPrice"],
                                                        order["sender"],
                                                        order["outcome"],
                                                        order["fxpMoneyEscrowed"],
                                                        order["fxpSharesEscrowed"],
                                                        order["betterOrderID"],
                                                        order["worseOrderID"],
                                                        order["tradeGroupID"], 1)
                assert(output == 1), "saveOrder wasn't executed successfully"
                contracts._ContractLoader__state.mine(1)
            for order in testCase["orders"]:
                orders.append(contracts.orders.getOrder(order["orderID"], order["type"], marketID, order["outcome"]))
            assert(len(orders) == len(testCase["expected"]["orders"])), "Number of orders not as expected"
            for i, order in enumerate(orders):
                outcomeID = testCase["orders"][i]["outcome"]
                assert(int(contracts.orders.getBestOrderID(1, marketID, outcomeID), 16) == testCase["expected"]["bestOrder"]["bid"]), "Best bid order ID incorrect"
                assert(int(contracts.orders.getBestOrderID(2, marketID, outcomeID), 16) == testCase["expected"]["bestOrder"]["ask"]), "Best ask order ID incorrect"
                assert(int(contracts.orders.getWorstOrderID(1,marketID, outcomeID), 16) == testCase["expected"]["worstOrder"]["bid"]), "Worst bid order ID incorrect"
                assert(int(contracts.orders.getWorstOrderID(2, marketID, outcomeID), 16) == testCase["expected"]["worstOrder"]["ask"]), "Worst ask order ID incorrect"
                assert(order[10] == testCase["expected"]["orders"][i]["betterOrderID"]), "Better order ID incorrect"
                assert(order[11] == testCase["expected"]["orders"][i]["worseOrderID"]), "Worse order ID incorrect"
            for order in testCase["orders"]:
                print contracts.orders.getGasPrice(order["orderID"], order["type"], marketID, order["outcome"])
                removed = contracts.orders.removeOrder(order["orderID"])
                assert(removed == 1), "Removed not equal to 1"

        # Bids
        runtest({
            "orders": [{
                "orderID": 1,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 2,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 1,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 2,
                    "ask": 0
                },
                "worstOrder": {
                    "bid": 1,
                    "ask": 0
                },
                "orders": [{
                    "betterOrderID": 2,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 1
                }]
            }
        })
        runtest({
            "orders": [{
                "orderID": 3,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 4,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 3,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 3,
                    "ask": 0
                },
                "worstOrder": {
                    "bid": 4,
                    "ask": 0
                },
                "orders": [{
                    "betterOrderID": 0,
                    "worseOrderID": 4
                }, {
                    "betterOrderID": 3,
                    "worseOrderID": 0
                }]
            }
        })
        runtest({
            "orders": [{
                "orderID": 5,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 6,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 5,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 7,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 5,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 7,
                    "ask": 0
                },
                "worstOrder": {
                    "bid": 6,
                    "ask": 0
                },
                "orders": [{
                    "betterOrderID": 7,
                    "worseOrderID": 6
                }, {
                    "betterOrderID": 5,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 5
                }]
            }
        })
        # Without betterOrderID and/or worseOrderID parameters
        runtest({
            "orders": [{
                "orderID": 1,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 2,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 2,
                    "ask": 0
                },
                "worstOrder": {
                    "bid": 1,
                    "ask": 0
                },
                "orders": [{
                    "betterOrderID": 2,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 1
                }]
            }
        })
        runtest({
            "orders": [{
                "orderID": 3,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 4,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 3,
                    "ask": 0
                },
                "worstOrder": {
                    "bid": 4,
                    "ask": 0
                },
                "orders": [{
                    "betterOrderID": 0,
                    "worseOrderID": 4
                }, {
                    "betterOrderID": 3,
                    "worseOrderID": 0
                }]
            }
        })
        runtest({
            "orders": [{
                "orderID": 5,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 6,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 7,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 7,
                    "ask": 0
                },
                "worstOrder": {
                    "bid": 6,
                    "ask": 0
                },
                "orders": [{
                    "betterOrderID": 7,
                    "worseOrderID": 6
                }, {
                    "betterOrderID": 5,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 5
                }]
            }
        })

        # Asks
        runtest({
            "orders": [{
                "orderID": 8,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 9,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 8,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 0,
                    "ask": 9
                },
                "worstOrder": {
                    "bid": 0,
                    "ask": 8
                },
                "orders": [{
                    "betterOrderID": 9,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 8
                }]
            }
        })
        runtest({
            "orders": [{
                "orderID": 10,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 11,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 10,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 0,
                    "ask": 10
                },
                "worstOrder": {
                    "bid": 0,
                    "ask": 11
                },
                "orders": [{
                    "betterOrderID": 0,
                    "worseOrderID": 11
                }, {
                    "betterOrderID": 10,
                    "worseOrderID": 0
                }]
            }
        })
        runtest({
            "orders": [{
                "orderID": 12,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 13,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 12,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 14,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 12,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 0,
                    "ask": 14
                },
                "worstOrder": {
                    "bid": 0,
                    "ask": 13
                },
                "orders": [{
                    "betterOrderID": 14,
                    "worseOrderID": 13
                }, {
                    "betterOrderID": 12,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 12
                }]
            }
        })
        # Without betterOrderID and/or worseOrderID
        runtest({
            "orders": [{
                "orderID": 8,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 9,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 0,
                    "ask": 9
                },
                "worstOrder": {
                    "bid": 0,
                    "ask": 8
                },
                "orders": [{
                    "betterOrderID": 9,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 8
                }]
            }
        })
        runtest({
            "orders": [{
                "orderID": 10,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 11,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 0,
                    "ask": 10
                },
                "worstOrder": {
                    "bid": 0,
                    "ask": 11
                },
                "orders": [{
                    "betterOrderID": 0,
                    "worseOrderID": 11
                }, {
                    "betterOrderID": 10,
                    "worseOrderID": 0
                }]
            }
        })
        runtest({
            "orders": [{
                "orderID": 12,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 13,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 12,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 14,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 0,
                    "ask": 14
                },
                "worstOrder": {
                    "bid": 0,
                    "ask": 13
                },
                "orders": [{
                    "betterOrderID": 14,
                    "worseOrderID": 13
                }, {
                    "betterOrderID": 12,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 12
                }]
            }
        })

        # Bids and asks
        runtest({
            "orders": [{
                "orderID": 15,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 16,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 15,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 17,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 15,
                "tradeGroupID": 0
            }, {
                "orderID": 18,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 19,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 18,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 20,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 18,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 17,
                    "ask": 20
                },
                "worstOrder": {
                    "bid": 16,
                    "ask": 19
                },
                "orders": [{
                    "betterOrderID": 17,
                    "worseOrderID": 16
                }, {
                    "betterOrderID": 15,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 15
                }, {
                    "betterOrderID": 20,
                    "worseOrderID": 19
                }, {
                    "betterOrderID": 18,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 18
                }]
            }
        })
        # Without betterOrderID and/or worseOrderID
        runtest({
            "orders": [{
                "orderID": 15,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 16,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 17,
                "type": 1,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 18,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.6"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.6"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 19,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.61"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.61"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }, {
                "orderID": 20,
                "type": 2,
                "fxpAmount": utils.fix(1),
                "fxpPrice": utils.fix("0.59"),
                "sender": t.a0,
                "outcome": 1,
                "fxpMoneyEscrowed": utils.fix("0.59"),
                "fxpSharesEscrowed": 0,
                "betterOrderID": 0,
                "worseOrderID": 0,
                "tradeGroupID": 0
            }],
            "expected": {
                "bestOrder": {
                    "bid": 17,
                    "ask": 20
                },
                "worstOrder": {
                    "bid": 16,
                    "ask": 19
                },
                "orders": [{
                    "betterOrderID": 17,
                    "worseOrderID": 16
                }, {
                    "betterOrderID": 15,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 15
                }, {
                    "betterOrderID": 20,
                    "worseOrderID": 19
                }, {
                    "betterOrderID": 18,
                    "worseOrderID": 0
                }, {
                    "betterOrderID": 0,
                    "worseOrderID": 18
                }]
            }
        })

    def test_saveOrder():
        assert(contracts.orders.saveOrder(order1, 1, market1, WEI_TO_ETH*10, pointFive, address0, 1, 0, WEI_TO_ETH*10, 0, 0, 2, 1) == 1), "saveOrder wasn't executed successfully"
        assert(contracts.orders.saveOrder(order2, 2, market1, WEI_TO_ETH*10, pointFive, address1, 1, WEI_TO_ETH*5, 0, 0, 0, 1, 1) == 1), "saveOrder wasn't executed successfully"

        assert(contracts.orders.getOrder(order1, 1, market1, 1) == [order1, 1, market1, WEI_TO_ETH*10, pointFive, address0, 0, 1, 0, WEI_TO_ETH*10, 0, 0, 1]), "getOrder for order1 didn't return the expected array of data"
        assert(contracts.orders.getOrder(order2, 2, market1, 1) == [order2, 2, market1, WEI_TO_ETH*10, pointFive, address1, 0, 1, WEI_TO_ETH*5, 0, 0, 0, 1]), "getOrder for order2 didn't return the expected array of data"

        assert(contracts.orders.getAmount(order1, 1, market1, 1) == WEI_TO_ETH*10), "amount for order1 should be set to WEI_TO_ETH*10 (WEI_TO_ETH = 10**18)"
        assert(contracts.orders.getAmount(order2, 2, market1, 1) == WEI_TO_ETH*10), "amount for order2 should be set to WEI_TO_ETH*10 (WEI_TO_ETH = 10**18)"

        assert(contracts.orders.getPrice(order1, 1, market1, 1) == pointFive), "price for order1 should be set to pointFive (.5*WEI_TO_ETH)"
        assert(contracts.orders.getPrice(order2, 2, market1, 1) == pointFive), "price for order2 should be set to pointFive (.5*WEI_TO_ETH)"

        assert(contracts.orders.getOrderOwner(order1, 1, market1, 1) == t.a0.encode("hex")), "orderOwner for order1 should be address0"
        assert(contracts.orders.getOrderOwner(order2, 2, market1, 1) == t.a1.encode("hex")), "orderOwner for order2 should be address1"

        assert(contracts.orders.removeOrder(order1, 1, market1, 1) == 1), "Remove order 1"
        assert(contracts.orders.removeOrder(order2, 2, market1, 1) == 1), "Remove order 2"

    def test_fillOrder():
        assert(contracts.orders.saveOrder(order1, 1, market1, WEI_TO_ETH*10, pointFive, address0, 1, 0, WEI_TO_ETH*10, 0, 0, 2, 1) == 1), "saveOrder wasn't executed successfully"
        assert(contracts.orders.saveOrder(order2, 2, market1, WEI_TO_ETH*10, pointFive, address1, 1, WEI_TO_ETH*5, 0, 0, 0, 1, 1) == 1), "saveOrder wasn't executed successfully"

        # orderID, fill, money, shares
        try:
            raise Exception(contracts.orders.fillOrder(order1, WEI_TO_ETH*20, 0, 0))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "fillOrder should fail if fill is greater then the amount of the order"
        try:
            raise Exception(contracts.orders.fillOrder(order1, WEI_TO_ETH*10, 0, WEI_TO_ETH*20))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "fillOrder should fail if shares is greater than the sharesEscrowed in the order"
        try:
            raise Exception(contracts.orders.fillOrder(order1, WEI_TO_ETH*10, WEI_TO_ETH*20, 0))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "fillOrder should fail if money is greater than the moneyEscrowed in the order"
        # fully fill
        assert(contracts.orders.fillOrder(order1, 1, market1, 1, WEI_TO_ETH*10, 0, WEI_TO_ETH*10) == 1), "fillOrder wasn't executed successfully"
        # prove all
        assert(contracts.orders.getOrder(order1, 1, market1, 1) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "getOrder for order1 didn't return the expected data array"
        # test partial fill
        assert(contracts.orders.fillOrder(order2, 2, market1, 1, WEI_TO_ETH*6, WEI_TO_ETH*3, 0) == 1), "fillOrder wasn't executed successfully"
        # confirm partial fill
        assert(contracts.orders.getOrder(order2, 2, market1, 1) == [order2, 2, market1, WEI_TO_ETH*4, pointFive, address1, 0, 1, WEI_TO_ETH*2, 0, 0, 0, 1]), "getOrder for order2 didn't return the expected data array"
        # fill rest of order2
        assert(contracts.orders.fillOrder(order2, 2, market1, 1, WEI_TO_ETH*4, WEI_TO_ETH*2, 0) == 1), "fillOrder wasn't executed successfully"
        assert(contracts.orders.getOrder(order2, 2, market1, 1) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "getOrder for order2 didn't return the expected data array"

        assert(contracts.orders.removeOrder(order1, 1, market1, 1) == 1), "Remove order 1"
        assert(contracts.orders.removeOrder(order2, 2, market1, 1) == 1), "Remove order 2"

    def test_removeOrder():
        order3 = 321321321
        assert(contracts.orders.saveOrder(order1, 1, market1, WEI_TO_ETH*10, pointFive, address0, 1, 0, WEI_TO_ETH*10, 0, 0, 2, 1) == 1), "saveOrder wasn't executed successfully"
        assert(contracts.orders.saveOrder(order2, 2, market1, WEI_TO_ETH*10, pointFive, address1, 1, WEI_TO_ETH*5, 0, 0, 0, 1, 1) == 1), "saveOrder wasn't executed successfully"
        assert(contracts.orders.saveOrder(order3, 1, market1, WEI_TO_ETH*10, pointFive, address0, 2, 0, WEI_TO_ETH*10, 0, 0, 0, 1) == 1), "saveOrder wasn't executed successfully"
        assert(contracts.orders.getOrder(order3, 1, market1, 2) == [order3, 1, market1, WEI_TO_ETH*10, pointFive, address0, 0, 2, 0, WEI_TO_ETH*10, 0, 0, 1]), "getOrder for order3 didn't return the expected data array"
        assert(contracts.orders.removeOrder(order3, 1, market1, 2) == 1), "removeOrder wasn't executed successfully"
        assert(contracts.orders.getOrder(order3, 1, market1, 2) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "getOrder for order3 should return an 0'd out array as it has been removed"
        assert(contracts.orders.removeOrder(order1, 1, market1, 1) == 1), "Remove order 1"
        assert(contracts.orders.removeOrder(order2, 2, market1, 1) == 1), "Remove order 2"
        assert(contracts.orders.removeOrder(order3, 1, market1, 2) == 1), "Remove order 3"

    test_randomOrderSorting()
    test_walkOrderList()
    test_orderSorting()
    test_saveOrder()
    test_fillOrder()
    test_removeOrder()

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_orders(contracts)
