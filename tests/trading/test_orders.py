#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
import numpy as np
from pytest import fixture, mark, lazy_fixture, raises
from utils import fix, bytesToLong, bytesToHexString, longTo32Bytes, longToHexString, stringToBytes

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
        "orderID": longTo32Bytes(5),
        "type": BID,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId5 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId5 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == orderId5)
    assert(worstOrderID == orderId5)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.6'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.59'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.61'), bestOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.58'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.6'), worstOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.59'), worstOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.61'), worstOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.58'), worstOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    order = {
        "orderID": longTo32Bytes(6),
        "type": BID,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId6 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId6 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == orderId5)
    assert(worstOrderID == orderId6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.6'), bestOrderID) == [orderId5, orderId6])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.59'), bestOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.61'), bestOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.58'), bestOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [orderId5, orderId6])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.6'), worstOrderID) == [orderId5, orderId6])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.59'), worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.61'), worstOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.58'), worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [orderId5, orderId6])
    order = {
        "orderID": longTo32Bytes(7),
        "type": BID,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId7 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId7 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == orderId5)
    assert(worstOrderID == orderId6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.6'), bestOrderID) == [orderId5, orderId7])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.59'), bestOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.61'), bestOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.58'), bestOrderID) == [orderId6, longTo32Bytes(0)])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.6'), worstOrderID) == [orderId5, orderId7])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.59'), worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.61'), worstOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.58'), worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(orders.removeOrder(orderId5, BID, market.address, outcomeID) == 1), "Remove order 5"
    assert(orders.removeOrder(orderId6, BID, market.address, outcomeID) == 1), "Remove order 6"
    assert(orders.removeOrder(orderId7, BID, market.address, outcomeID) == 1), "Remove order 7"

def test_walkOrderList_asks(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    outcomeID = 1
    order = {
        "orderID": longTo32Bytes(8),
        "type": ASK,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId8 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId8 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == orderId8)
    assert(worstOrderID == orderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.6'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.59'), bestOrderID) == [longTo32Bytes(0), orderId8])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.61'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.58'), bestOrderID) == [longTo32Bytes(0), orderId8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.6'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.59'), worstOrderID) == [longTo32Bytes(0), orderId8])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.61'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.58'), worstOrderID) == [longTo32Bytes(0), orderId8])
    order = {
        "orderID": longTo32Bytes(9),
        "type": ASK,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId9 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId9 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == orderId9)
    assert(worstOrderID == orderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.6'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.59'), bestOrderID) == [orderId9, orderId8])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.61'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.58'), bestOrderID) == [longTo32Bytes(0), orderId9])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.595'), bestOrderID) == [orderId9, orderId8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.6'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.59'), worstOrderID) == [orderId9, orderId8])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.61'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.58'), worstOrderID) == [longTo32Bytes(0), orderId9])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.595'), bestOrderID) == [orderId9, orderId8])
    order = {
        "orderID": longTo32Bytes(10),
        "type": ASK,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId10 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId10 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == orderId9)
    assert(worstOrderID == orderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.6'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.59'), bestOrderID) == [orderId9, orderId10])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.61'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.58'), bestOrderID) == [longTo32Bytes(0), orderId9])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.6'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.59'), worstOrderID) == [orderId9, orderId10])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.61'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.58'), worstOrderID) == [longTo32Bytes(0), orderId9])
    assert(orders.removeOrder(orderId8, ASK, market.address, outcomeID) == 1), "Remove order 8"
    assert(orders.removeOrder(orderId9, ASK, market.address, outcomeID) == 1), "Remove order 9"
    assert(orders.removeOrder(orderId10, ASK, market.address, outcomeID) == 1), "Remove order 10"

def test_orderSorting(contractsFixture):
    def runtest(testCase):
        market = contractsFixture.binaryMarket
        orders = contractsFixture.contracts['Orders']
        ordersFetcher = contractsFixture.contracts['OrdersFetcher']
        ordersCollection = []
        for order in testCase["orders"]:
            output = orders.saveOrder(
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
            assert(output != bytearray(32)), "saveOrder wasn't executed successfully"
        for order in testCase["orders"]:
            ordersCollection.append(ordersFetcher.getOrder(order["orderID"]))
        assert(len(ordersCollection) == len(testCase["expected"]["orders"])), "Number of orders not as expected"
        for i, order in enumerate(ordersCollection):
            outcomeID = testCase["orders"][i]["outcome"]
            assert(orders.getBestOrderId(BID, market.address, outcomeID) == testCase["expected"]["bestOrder"]["bid"]), "Best bid order ID incorrect"
            assert(orders.getBestOrderId(ASK, market.address, outcomeID) == testCase["expected"]["bestOrder"]["ask"]), "Best ask order ID incorrect"
            assert(orders.getWorstOrderId(BID,market.address, outcomeID) == testCase["expected"]["worstOrder"]["bid"]), "Worst bid order ID incorrect"
            assert(orders.getWorstOrderId(ASK, market.address, outcomeID) == testCase["expected"]["worstOrder"]["ask"]), "Worst ask order ID incorrect"
            assert(order[BETTER_ORDER_ID] == testCase["expected"]["orders"][i]["betterOrderID"]), "Better order ID incorrect"
            assert(order[WORSE_ORDER_ID] == testCase["expected"]["orders"][i]["worseOrderID"]), "Worse order ID incorrect"
        for order in testCase["orders"]:
            removed = orders.removeOrder(order["orderID"], order["type"], market.address, order["outcome"])
            assert(removed == 1), "Removed not equal to 1"

    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    blockNumber = contractsFixture.chain.head_state.block_number
    orderId1 = orders.getOrderId(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    orderId2 = orders.getOrderId(BID, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    orderId3 = orders.getOrderId(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    orderId4 = orders.getOrderId(BID, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    orderId5 = orders.getOrderId(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    orderId6 = orders.getOrderId(BID, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    orderId7 = orders.getOrderId(BID, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    orderId8 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    orderId9 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    orderId10 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    orderId11 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    orderId12 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    orderId13 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    orderId14 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    orderId15 = orders.getOrderId(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    orderId16 = orders.getOrderId(BID, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    orderId17 = orders.getOrderId(BID, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    orderId18 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    orderId19 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    orderId20 = orders.getOrderId(ASK, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)

    # Bids
    runtest({
        "orders": [{
            "orderID": orderId1,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId2,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": orderId1,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": orderId2,
                "ask": longTo32Bytes(0)
            },
            "worstOrder": {
                "bid": orderId1,
                "ask": longTo32Bytes(0)
            },
            "orders": [{
                "betterOrderID": orderId2,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId1
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": orderId3,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId4,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": orderId3,
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": orderId3,
                "ask": longTo32Bytes(0)
            },
            "worstOrder": {
                "bid": orderId4,
                "ask": longTo32Bytes(0)
            },
            "orders": [{
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId4
            }, {
                "betterOrderID": orderId3,
                "worseOrderID": longTo32Bytes(0)
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": orderId5,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId6,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": orderId5,
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId7,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": orderId5,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": orderId7,
                "ask": longTo32Bytes(0)
            },
            "worstOrder": {
                "bid": orderId6,
                "ask": longTo32Bytes(0)
            },
            "orders": [{
                "betterOrderID": orderId7,
                "worseOrderID": orderId6
            }, {
                "betterOrderID": orderId5,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId5
            }]
        }
    })
    # Without betterOrderID and/or worseOrderID parameters
    runtest({
        "orders": [{
            "orderID": orderId1,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId2,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": orderId2,
                "ask": longTo32Bytes(0)
            },
            "worstOrder": {
                "bid": orderId1,
                "ask": longTo32Bytes(0)
            },
            "orders": [{
                "betterOrderID": orderId2,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId1
            }]
        }
    })
    runtest({
        "orders": [{
           "orderID": orderId3,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId4,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": orderId3,
                "ask": longTo32Bytes(0)
            },
            "worstOrder": {
                "bid": orderId4,
                "ask": longTo32Bytes(0)
            },
            "orders": [{
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId4
            }, {
                "betterOrderID": orderId3,
                "worseOrderID": longTo32Bytes(0)
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": orderId5,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId6,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId7,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": orderId7,
                "ask": longTo32Bytes(0)
            },
            "worstOrder": {
                "bid": orderId6,
                "ask": longTo32Bytes(0)
            },
            "orders": [{
                "betterOrderID": orderId7,
                "worseOrderID": orderId6
            }, {
                "betterOrderID": orderId5,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId5
            }]
        }
    })

    # Asks
    runtest({
        "orders": [{
            "orderID": orderId8,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId9,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": orderId8,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId9
            },
            "worstOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId8
            },
            "orders": [{
                "betterOrderID": orderId9,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId8
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": orderId10,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId11,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": orderId10,
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId10
            },
            "worstOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId11
            },
            "orders": [{
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId11
            }, {
                "betterOrderID": orderId10,
                "worseOrderID": longTo32Bytes(0)
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": orderId12,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId13,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": orderId12,
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId14,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": orderId12,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId14
            },
            "worstOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId13
            },
            "orders": [{
                "betterOrderID": orderId14,
                "worseOrderID": orderId13
            }, {
                "betterOrderID": orderId12,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId12
            }]
        }
    })
    # Without betterOrderID and/or worseOrderID
    runtest({
        "orders": [{
            "orderID": orderId8,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId9,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId9
            },
            "worstOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId8
            },
            "orders": [{
                "betterOrderID": orderId9,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId8
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": orderId10,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId11,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId10
            },
            "worstOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId11
            },
            "orders": [{
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId11
            }, {
                "betterOrderID": orderId10,
                "worseOrderID": longTo32Bytes(0)
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": orderId12,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId13,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": orderId12,
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId14,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId14
            },
            "worstOrder": {
                "bid": longTo32Bytes(0),
                "ask": orderId13
            },
            "orders": [{
                "betterOrderID": orderId14,
                "worseOrderID": orderId13
            }, {
                "betterOrderID": orderId12,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId12
            }]
        }
    })

    # Bids and asks
    runtest({
        "orders": [{
            "orderID": orderId15,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId16,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": orderId15,
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId17,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": orderId15,
            "tradeGroupID": 0
        }, {
            "orderID": orderId18,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId19,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": orderId18,
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId20,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": orderId18,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": orderId17,
                "ask": orderId20
            },
            "worstOrder": {
                "bid": orderId16,
                "ask": orderId19
            },
            "orders": [{
                "betterOrderID": orderId17,
                "worseOrderID": orderId16
            }, {
                "betterOrderID": orderId15,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId15
            }, {
                "betterOrderID": orderId20,
                "worseOrderID": orderId19
            }, {
                "betterOrderID": orderId18,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId18
            }]
        }
    })
    # Without betterOrderID and/or worseOrderID
    runtest({
        "orders": [{
            "orderID": orderId15,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId16,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId17,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId18,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId19,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }, {
            "orderID": orderId20,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": longTo32Bytes(0),
            "worseOrderID": longTo32Bytes(0),
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": orderId17,
                "ask": orderId20
            },
            "worstOrder": {
                "bid": orderId16,
                "ask": orderId19
            },
            "orders": [{
                "betterOrderID": orderId17,
                "worseOrderID": orderId16
            }, {
                "betterOrderID": orderId15,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId15
            }, {
                "betterOrderID": orderId20,
                "worseOrderID": orderId19
            }, {
                "betterOrderID": orderId18,
                "worseOrderID": longTo32Bytes(0)
            }, {
                "betterOrderID": longTo32Bytes(0),
                "worseOrderID": orderId18
            }]
        }
    })

def test_saveOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']

    orderId1 = orders.saveOrder(BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), longTo32Bytes(0), longTo32Bytes(0), 1)
    assert(orderId1 != bytearray(32)), "saveOrder wasn't executed successfully"
    orderId2 = orders.saveOrder(ASK, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, longTo32Bytes(0), longTo32Bytes(0), 1)
    assert(orderId2 != bytearray(32)), "saveOrder wasn't executed successfully"

    assert(ordersFetcher.getOrder(orderId1) == [fix('10'), fix('0.5'), bytesToHexString(tester.a1), 0, fix('10'), longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order1 didn't return the expected array of data"
    assert(ordersFetcher.getOrder(orderId2) == [fix('10'), fix('0.5'), bytesToHexString(tester.a2), fix('5'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order2 didn't return the expected array of data"

    assert(orders.getAmount(orderId1, BID, market.address, NO) == fix('10')), "amount for order1 should be set to 10 ETH"
    assert(orders.getAmount(orderId2, ASK, market.address, NO) == fix('10')), "amount for order2 should be set to 10 ETH"

    assert(orders.getPrice(orderId1, BID, market.address, NO) == fix('0.5')), "price for order1 should be set to 0.5 ETH"
    assert(orders.getPrice(orderId2, ASK, market.address, NO) == fix('0.5')), "price for order2 should be set to 0.5 ETH"

    assert(orders.getOrderOwner(orderId1, BID, market.address, NO) == bytesToHexString(tester.a1)), "orderOwner for order1 should be tester.a1"
    assert(orders.getOrderOwner(orderId2, ASK, market.address, NO) == bytesToHexString(tester.a2)), "orderOwner for order2 should be tester.a2"

    assert(orders.removeOrder(orderId1, BID, market.address, NO) == 1), "Remove order 1"
    assert(orders.removeOrder(orderId2, ASK, market.address, NO) == 1), "Remove order 2"

def test_fillOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']

    orderId1 = orders.saveOrder(BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), longTo32Bytes(0), longTo32Bytes(0), 1)
    assert(orderId1 != bytearray(32)), "saveOrder wasn't executed successfully"
    orderId2 = orders.saveOrder(BID, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, longTo32Bytes(0), longTo32Bytes(0), 1)
    assert(orderId2 != bytearray(32)), "saveOrder wasn't executed successfully"

    # orderID, fill, money, shares
    with raises(TransactionFailed):
        orders.fillOrder(orderId1, BID, market.address, NO, fix('11'), 0)
    with raises(TransactionFailed):
        orders.fillOrder(orderId1, BID, market.address, NO, 0, fix('1'))
    with raises(TransactionFailed):
        orders.fillOrder(orderId1, BID, market.address, NO, fix('10'), fix('1'))
    # fully fill
    assert(orders.fillOrder(orderId1, BID, market.address, NO, fix('10'), 0) == 1), "fillOrder wasn't executed successfully"
    # prove all
    assert(ordersFetcher.getOrder(orderId1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order1 didn't return the expected data array"
    # test partial fill
    assert(orders.fillOrder(orderId2, BID, market.address, NO, 0, fix('3')) == 1), "fillOrder wasn't executed successfully"
    # confirm partial fill
    assert(ordersFetcher.getOrder(orderId2) == [fix('4'), fix('0.5'), bytesToHexString(tester.a2), fix('2'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order2 didn't return the expected data array"
    # fill rest of order2
    assert(orders.fillOrder(orderId2, BID, market.address, NO, 0, fix('2')) == 1), "fillOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(orderId2) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order2 didn't return the expected data array"

def test_removeOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']

    orderId1 = orders.saveOrder(BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), longTo32Bytes(0), longTo32Bytes(0), 1)
    assert(orderId1 != bytearray(32)), "saveOrder wasn't executed successfully"
    orderId2 = orders.saveOrder(BID, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, longTo32Bytes(0), longTo32Bytes(0), 1)
    assert(orderId2 != bytearray(32)), "saveOrder wasn't executed successfully"
    orderId3 = orders.saveOrder(BID, market.address, fix('10'), fix('0.5'), tester.a1, YES, 0, fix('10'), longTo32Bytes(0), longTo32Bytes(0), 1)
    assert(orderId3 != bytearray(32)), "saveOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(orderId3) == [fix('10'), fix('0.5'), bytesToHexString(tester.a1), 0, fix('10'), longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order3 didn't return the expected data array"
    assert(orders.removeOrder(orderId3, BID, market.address, YES) == 1), "removeOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(orderId3) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order3 should return an 0'd out array as it has been removed"
    assert(orders.removeOrder(orderId1, BID, market.address, NO) == 1), "Remove order 1"
    assert(orders.removeOrder(orderId2, BID, market.address, NO) == 1), "Remove order 2"
