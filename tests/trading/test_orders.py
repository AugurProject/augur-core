#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
import numpy as np
from pytest import fixture, mark, lazy_fixture, raises
from utils import fix, bytesToLong, bytesToHexString
import binascii
import hashlib

NO = 0
YES = 1

BID = 1
ASK = 2

WEI_TO_ETH = 10**18

ATTOSHARES = 0
DISPLAY_PRICE = 1
OWNER = 2
TOKENS_ESCROWED = 3
SHARES_ESCROWED = 4
BETTER_ORDER_ID = 5
WORSE_ORDER_ID = 6
GAS_PRICE = 7

def test_walkOrderList_bids(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    outcomeID = 1
    order = {
        "orderID": 5,
        "type": 1,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": 0,
        "worseOrderID": 0,
        "tradeGroupID": 0
    }
    assert(orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], 1) == 1), "Save order"
    bestOrderID = orders.getBestOrderId(1, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(1, market.address, outcomeID)
    assert(bestOrderID == 5)
    assert(worstOrderID == 5)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.6'), bestOrderID) == [5, 0])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.59'), bestOrderID) == [5, 0])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.61'), bestOrderID) == [0, 5])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.58'), bestOrderID) == [5, 0])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.595'), bestOrderID) == [5, 0])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.6'), worstOrderID) == [5, 0])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.59'), worstOrderID) == [5, 0])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.61'), worstOrderID) == [0, 5])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.58'), worstOrderID) == [5, 0])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.595'), bestOrderID) == [5, 0])
    order = {
        "orderID": 6,
        "type": 1,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": 0,
        "worseOrderID": 0,
        "tradeGroupID": 0
    }
    assert(orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], 1) == 1), "Save order"
    bestOrderID = orders.getBestOrderId(1, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(1, market.address, outcomeID)
    assert(bestOrderID == 5)
    assert(worstOrderID == 6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.6'), bestOrderID) == [5, 6])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.59'), bestOrderID) == [6, 0])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.61'), bestOrderID) == [0, 5])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.58'), bestOrderID) == [6, 0])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.595'), bestOrderID) == [5, 6])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.6'), worstOrderID) == [5, 6])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.59'), worstOrderID) == [6, 0])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.61'), worstOrderID) == [0, 5])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.58'), worstOrderID) == [6, 0])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.595'), bestOrderID) == [5, 6])
    order = {
        "orderID": 7,
        "type": 1,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": 0,
        "worseOrderID": 0,
        "tradeGroupID": 0
    }
    assert(orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], 1) == 1), "Save order"
    bestOrderID = orders.getBestOrderId(1, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(1, market.address, outcomeID)
    assert(bestOrderID == 5)
    assert(worstOrderID == 6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.6'), bestOrderID) == [5, 7])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.59'), bestOrderID) == [6, 0])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.61'), bestOrderID) == [0, 5])
    assert(ordersFetcher.descendOrderList(1, market.address, outcomeID, fix('0.58'), bestOrderID) == [6, 0])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.6'), worstOrderID) == [5, 7])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.59'), worstOrderID) == [6, 0])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.61'), worstOrderID) == [0, 5])
    assert(ordersFetcher.ascendOrderList(1, market.address, outcomeID, fix('0.58'), worstOrderID) == [6, 0])
    assert(orders.removeOrder(5, BID, market.address, outcomeID) == 1), "Remove order 5"
    assert(orders.removeOrder(6, BID, market.address, outcomeID) == 1), "Remove order 6"
    assert(orders.removeOrder(7, BID, market.address, outcomeID) == 1), "Remove order 7"

def test_walkOrderList_asks(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    outcomeID = 1
    order = {
        "orderID": 8,
        "type": 2,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": 0,
        "worseOrderID": 0,
        "tradeGroupID": 0
    }
    assert(orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], 1) == 1), "Save order"
    bestOrderID = orders.getBestOrderId(2, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(2, market.address, outcomeID)
    assert(bestOrderID == 8)
    assert(worstOrderID == 8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.6'), bestOrderID) == [8, 0])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.59'), bestOrderID) == [0, 8])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.61'), bestOrderID) == [8, 0])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.58'), bestOrderID) == [0, 8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.6'), worstOrderID) == [8, 0])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.59'), worstOrderID) == [0, 8])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.61'), worstOrderID) == [8, 0])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.58'), worstOrderID) == [0, 8])
    order = {
        "orderID": 9,
        "type": 2,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": 0,
        "worseOrderID": 0,
        "tradeGroupID": 0
    }
    assert(orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], 1) == 1), "Save order"
    bestOrderID = orders.getBestOrderId(2, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(2, market.address, outcomeID)
    assert(bestOrderID == 9)
    assert(worstOrderID == 8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.6'), bestOrderID) == [8, 0])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.59'), bestOrderID) == [9, 8])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.61'), bestOrderID) == [8, 0])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.58'), bestOrderID) == [0, 9])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.595'), bestOrderID) == [9, 8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.6'), worstOrderID) == [8, 0])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.59'), worstOrderID) == [9, 8])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.61'), worstOrderID) == [8, 0])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.58'), worstOrderID) == [0, 9])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.595'), bestOrderID) == [9, 8])
    order = {
        "orderID": 10,
        "type": 2,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": 0,
        "worseOrderID": 0,
        "tradeGroupID": 0
    }
    assert(orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], 1) == 1), "Save order"
    bestOrderID = orders.getBestOrderId(2, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(2, market.address, outcomeID)
    assert(bestOrderID == 9)
    assert(worstOrderID == 8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.6'), bestOrderID) == [8, 0])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.59'), bestOrderID) == [9, 10])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.61'), bestOrderID) == [8, 0])
    assert(ordersFetcher.descendOrderList(2, market.address, outcomeID, fix('0.58'), bestOrderID) == [0, 9])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.6'), worstOrderID) == [8, 0])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.59'), worstOrderID) == [9, 10])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.61'), worstOrderID) == [8, 0])
    assert(ordersFetcher.ascendOrderList(2, market.address, outcomeID, fix('0.58'), worstOrderID) == [0, 9])
    assert(orders.removeOrder(8, ASK, market.address, outcomeID) == 1), "Remove order 8"
    assert(orders.removeOrder(9, ASK, market.address, outcomeID) == 1), "Remove order 9"
    assert(orders.removeOrder(10, ASK, market.address, outcomeID) == 1), "Remove order 10"

def test_orderSorting(contractsFixture):
    def runtest(testCase):
        market = contractsFixture.binaryMarket
        orders = contractsFixture.contracts['Orders']
        ordersFetcher = contractsFixture.contracts['OrdersFetcher']
        ordersCollection = []
        for order in testCase["orders"]:
            output = orders.saveOrder(
                order["orderID"],
                order["type"],
                market.address,
                order["fxpAmount"],
                order["fxpPrice"],
                order["sender"],
                order["outcome"],
                order["fxpMoneyEscrowed"],
                order["fxpSharesEscrowed"],
                order["betterOrderID"],
                order["worseOrderID"], 1)
            assert(output == 1), "saveOrder wasn't executed successfully"
        for order in testCase["orders"]:
            ordersCollection.append(ordersFetcher.getOrder(order["orderID"], order["type"], market.address, order["outcome"]))
        assert(len(ordersCollection) == len(testCase["expected"]["orders"])), "Number of orders not as expected"
        for i, order in enumerate(ordersCollection):
            outcomeID = testCase["orders"][i]["outcome"]
            assert(orders.getBestOrderId(1, market.address, outcomeID) == testCase["expected"]["bestOrder"]["bid"]), "Best bid order ID incorrect"
            assert(orders.getBestOrderId(2, market.address, outcomeID) == testCase["expected"]["bestOrder"]["ask"]), "Best ask order ID incorrect"
            assert(orders.getWorstOrderId(1,market.address, outcomeID) == testCase["expected"]["worstOrder"]["bid"]), "Worst bid order ID incorrect"
            assert(orders.getWorstOrderId(2, market.address, outcomeID) == testCase["expected"]["worstOrder"]["ask"]), "Worst ask order ID incorrect"
            assert(order[BETTER_ORDER_ID] == testCase["expected"]["orders"][i]["betterOrderID"]), "Better order ID incorrect"
            assert(order[WORSE_ORDER_ID] == testCase["expected"]["orders"][i]["worseOrderID"]), "Worse order ID incorrect"
        for order in testCase["orders"]:
            removed = orders.removeOrder(order["orderID"], order["type"], market.address, order["outcome"])
            assert(removed == 1), "Removed not equal to 1"

    # Bids
    runtest({
        "orders": [{
            "orderID": 1,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 2,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 4,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 6,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 5,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 7,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 2,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 4,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 6,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 7,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 9,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 11,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 13,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 12,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 14,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 9,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 11,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 13,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 12,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 14,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 16,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 15,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 17,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 15,
            "tradeGroupID": 0
        }, {
            "orderID": 18,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 19,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 18,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 20,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
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
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 16,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 17,
            "type": 1,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 18,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 19,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": 0,
            "worseOrderID": 0,
            "tradeGroupID": 0
        }, {
            "orderID": 20,
            "type": 2,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
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

def test_saveOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    order1 = 12345
    order2 = 98765

    assert(orders.saveOrder(order1, BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), 0, 0, 1) == 1), "saveOrder wasn't executed successfully"
    assert(orders.saveOrder(order2, ASK, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, 0, 0, 1) == 1), "saveOrder wasn't executed successfully"

    assert(ordersFetcher.getOrder(order1, BID, market.address, NO) == [fix('10'), fix('0.5'), '0x'+binascii.hexlify(tester.a1), 0, fix('10'), 0, 0, 1]), "getOrder for order1 didn't return the expected array of data"
    assert(ordersFetcher.getOrder(order2, ASK, market.address, NO) == [fix('10'), fix('0.5'), '0x'+binascii.hexlify(tester.a2), fix('5'), 0, 0, 0, 1]), "getOrder for order2 didn't return the expected array of data"

    assert(orders.getAmount(order1, BID, market.address, NO) == fix('10')), "amount for order1 should be set to 10 ETH"
    assert(orders.getAmount(order2, ASK, market.address, NO) == fix('10')), "amount for order2 should be set to 10 ETH"

    assert(orders.getPrice(order1, BID, market.address, NO) == fix('0.5')), "price for order1 should be set to 0.5 ETH"
    assert(orders.getPrice(order2, ASK, market.address, NO) == fix('0.5')), "price for order2 should be set to 0.5 ETH"

    assert(orders.getOrderOwner(order1, BID, market.address, NO) == '0x'+binascii.hexlify(tester.a1)), "orderOwner for order1 should be tester.a1"
    assert(orders.getOrderOwner(order2, ASK, market.address, NO) == '0x'+binascii.hexlify(tester.a2)), "orderOwner for order2 should be tester.a2"

    assert(orders.removeOrder(order1, BID, market.address, NO) == 1), "Remove order 1"
    assert(orders.removeOrder(order2, ASK, market.address, NO) == 1), "Remove order 2"

def test_fillOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    order1 = 12345
    order2 = 98765

    assert(orders.saveOrder(order1, BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), 0, 0, 1) == 1), "saveOrder wasn't executed successfully"
    assert(orders.saveOrder(order2, BID, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, 0, 0, 1) == 1), "saveOrder wasn't executed successfully"

    # orderID, fill, money, shares
    with raises(TransactionFailed):
        orders.fillOrder(order1, BID, market.address, NO, fix('11'), 0)
    with raises(TransactionFailed):
        orders.fillOrder(order1, BID, market.address, NO, 0, fix('1'))
    with raises(TransactionFailed):
        orders.fillOrder(order1, BID, market.address, NO, fix('10'), fix('1'))
    # fully fill
    assert(orders.fillOrder(order1, BID, market.address, NO, fix('10'), 0) == 1), "fillOrder wasn't executed successfully"
    # prove all
    assert(ordersFetcher.getOrder(order1, BID, market.address, NO) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, 0, 0, 0]), "getOrder for order1 didn't return the expected data array"
    # test partial fill
    assert(orders.fillOrder(order2, BID, market.address, NO, 0, fix('3')) == 1), "fillOrder wasn't executed successfully"
    # confirm partial fill
    assert(ordersFetcher.getOrder(order2, BID, market.address, NO) == [fix('4'), fix('0.5'), '0x'+binascii.hexlify(tester.a2), fix('2'), 0, 0, 0, 1]), "getOrder for order2 didn't return the expected data array"
    # fill rest of order2
    assert(orders.fillOrder(order2, BID, market.address, NO, 0, fix('2')) == 1), "fillOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(order2, BID, market.address, NO) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, 0, 0, 0]), "getOrder for order2 didn't return the expected data array"

def test_removeOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    order1 = 12345
    order2 = 98765
    order3 = 321321321
    h = hashlib.new('ripemd160')
    h.update('0')
    print h.hexdigest()
    assert(orders.saveOrder(order1, BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), h.hexdigest(), h.hexdigest(), 1) == 1), "saveOrder wasn't executed successfully"
    assert(orders.saveOrder(order2, BID, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, 0, 0, 1) == 1), "saveOrder wasn't executed successfully"
    assert(orders.saveOrder(order3, BID, market.address, fix('10'), fix('0.5'), tester.a1, YES, 0, fix('10'), 0, 0, 1) == 1), "saveOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(order3, BID, market.address, YES) == [fix('10'), fix('0.5'), '0x'+binascii.hexlify(tester.a1), 0, fix('10'), 0, 0, 1]), "getOrder for order3 didn't return the expected data array"
    assert(orders.removeOrder(order3, BID, market.address, YES) == 1), "removeOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(order3, BID, market.address, YES) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, 0, 0, 0]), "getOrder for order3 should return an 0'd out array as it has been removed"
    assert(orders.removeOrder(order1, BID, market.address, NO) == 1), "Remove order 1"
    assert(orders.removeOrder(order2, BID, market.address, NO) == 1), "Remove order 2"
