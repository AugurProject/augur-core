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

BID = 0
ASK = 1

WEI_TO_ETH = 10**18

ATTOSHARES = 0
DISPLAY_PRICE = 1
OWNER = 2
TOKENS_ESCROWED = 3
SHARES_ESCROWED = 4
BETTER_ORDER_ID = 5
WORSE_ORDER_ID = 6
GAS_PRICE = 7

ZEROED_ORDER_ID = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

def test_walkOrderList_bids(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['NewOrders']
    ordersFetcher = contractsFixture.contracts['NewOrdersFetcher']
    outcomeID = 1
    hash = hashlib.new('ripemd160')
    hash.update('0')
    hashedOrderId0 = hash.digest()
    order = {
        "orderID": 5,
        "type": BID,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": hashedOrderId0,
        "worseOrderID": hashedOrderId0,
        "tradeGroupID": 0
    }
    hashedOrderId5 = orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderId5, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == hashedOrderId5)
    assert(worstOrderID == hashedOrderId5)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderId5, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderId5, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.61'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderId5])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.58'), bestOrderID) == [hashedOrderId5, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderId5, ZEROED_ORDER_ID])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderId5, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderId5, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.61'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderId5])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.58'), worstOrderID) == [hashedOrderId5, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderId5, ZEROED_ORDER_ID])
    order = {
        "orderID": 6,
        "type": BID,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": hashedOrderId0,
        "worseOrderID": hashedOrderId0,
        "tradeGroupID": 0
    }
    hashedOrderId6 = orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderId6, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == hashedOrderId5)
    assert(worstOrderID == hashedOrderId6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderId5, hashedOrderId6])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderId6, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.61'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderId5])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.58'), bestOrderID) == [hashedOrderId6, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderId5, hashedOrderId6])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderId5, hashedOrderId6])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderId6, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.61'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderId5])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.58'), worstOrderID) == [hashedOrderId6, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderId5, hashedOrderId6])
    order = {
        "orderID": 7,
        "type": BID,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": hashedOrderId0,
        "worseOrderID": hashedOrderId0,
        "tradeGroupID": 0
    }
    hashedOrderId7 = orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderId7, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == hashedOrderId5)
    assert(worstOrderID == hashedOrderId6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderId5, hashedOrderId7])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderId6, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.61'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderId5])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.58'), bestOrderID) == [hashedOrderId6, ZEROED_ORDER_ID])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderId5, hashedOrderId7])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderId6, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.61'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderId5])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.58'), worstOrderID) == [hashedOrderId6, ZEROED_ORDER_ID])
    assert(orders.removeOrder(hashedOrderId5, BID, market.address, outcomeID) == 1), "Remove order 5"
    assert(orders.removeOrder(hashedOrderId6, BID, market.address, outcomeID) == 1), "Remove order 6"
    assert(orders.removeOrder(hashedOrderId7, BID, market.address, outcomeID) == 1), "Remove order 7"

def test_walkOrderList_asks(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['NewOrders']
    ordersFetcher = contractsFixture.contracts['NewOrdersFetcher']
    outcomeID = 1
    hash = hashlib.new('ripemd160')
    hash.update('0')
    hashedOrderId0 = hash.digest()
    order = {
        "orderID": 8,
        "type": ASK,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": hashedOrderId0,
        "worseOrderID": hashedOrderId0,
        "tradeGroupID": 0
    }
    hashedOrderId8 = orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderId8, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == hashedOrderId8)
    assert(worstOrderID == hashedOrderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.59'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderId8])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.61'), bestOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.58'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderId8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.59'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderId8])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.61'), worstOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.58'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderId8])
    order = {
        "orderID": 9,
        "type": ASK,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": hashedOrderId0,
        "worseOrderID": hashedOrderId0,
        "tradeGroupID": 0
    }
    hashedOrderId9 = orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderId9, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == hashedOrderId9)
    assert(worstOrderID == hashedOrderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderId9, hashedOrderId8])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.61'), bestOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.58'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderId9])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderId9, hashedOrderId8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderId9, hashedOrderId8])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.61'), worstOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.58'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderId9])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderId9, hashedOrderId8])
    order = {
        "orderID": 10,
        "type": ASK,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": hashedOrderId0,
        "worseOrderID": hashedOrderId0,
        "tradeGroupID": 0
    }
    hashedOrderId10 = orders.saveOrder(order["orderID"], order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderId9, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == hashedOrderId9)
    assert(worstOrderID == hashedOrderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderId9, hashedOrderId10])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.61'), bestOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.58'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderId9])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderId9, hashedOrderId10])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.61'), worstOrderID) == [hashedOrderId8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.58'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderId9])
    assert(orders.removeOrder(hashedOrderId8, ASK, market.address, outcomeID) == 1), "Remove order 8"
    assert(orders.removeOrder(hashedOrderId9, ASK, market.address, outcomeID) == 1), "Remove order 9"
    assert(orders.removeOrder(hashedOrderId10, ASK, market.address, outcomeID) == 1), "Remove order 10"

def test_orderSorting(contractsFixture):
    def runtest(testCase):
        market = contractsFixture.binaryMarket
        orders = contractsFixture.contracts['NewOrders']
        ordersFetcher = contractsFixture.contracts['NewOrdersFetcher']
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
            assert(isinstance(output, bytes)), "saveOrder wasn't executed successfully"
        for order in testCase["orders"]:
            ordersCollection.append(ordersFetcher.getOrder(order["hashedOrderID"], order["type"], market.address, order["outcome"]))
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
            removed = orders.removeOrder(order["hashedOrderID"], order["type"], market.address, order["outcome"])
            assert(removed == 1), "Removed not equal to 1"

    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['NewOrders']
    hash = hashlib.new('ripemd160')
    hash.update('0')
    hashedOrderId0 = hash.digest()
    blockNumber = orders.getBlockNumber()
    hashedOrderId1 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderId2 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderId3 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderId4 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderId5 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderId6 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderId7 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderId8 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderId9 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderId10 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderId11 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderId12 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderId13 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderId14 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderId15 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderId16 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderId17 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderId18 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderId19 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderId20 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
  
    # Bids
    runtest({
        "orders": [{
            "orderID": 1,
            "hashedOrderID": hashedOrderId1,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 2,
            "hashedOrderID": hashedOrderId2,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId1,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderId2,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderId1,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": hashedOrderId2,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId1
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 3,
            "hashedOrderID": hashedOrderId3,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 4,
            "hashedOrderID": hashedOrderId4,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId3,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderId3,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderId4,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId4
            }, {
                "betterOrderID": hashedOrderId3,
                "worseOrderID": ZEROED_ORDER_ID
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 5,
            "hashedOrderID": hashedOrderId5,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 6,
            "hashedOrderID": hashedOrderId6,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId5,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 7,
            "hashedOrderID": hashedOrderId7,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId5,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderId7,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderId6,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": hashedOrderId7,
                "worseOrderID": hashedOrderId6
            }, {
                "betterOrderID": hashedOrderId5,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId5
            }]
        }
    })
    # Without betterOrderID and/or worseOrderID parameters
    runtest({
        "orders": [{
            "orderID": 1,
            "hashedOrderID": hashedOrderId1,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 2,
            "hashedOrderID": hashedOrderId2,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderId2,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderId1,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": hashedOrderId2,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId1
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 3,
           "hashedOrderID": hashedOrderId3,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 4,
            "hashedOrderID": hashedOrderId4,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderId3,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderId4,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId4
            }, {
                "betterOrderID": hashedOrderId3,
                "worseOrderID": ZEROED_ORDER_ID
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 5,
            "hashedOrderID": hashedOrderId5,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 6,
            "hashedOrderID": hashedOrderId6,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 7,
            "hashedOrderID": hashedOrderId7,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderId7,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderId6,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": hashedOrderId7,
                "worseOrderID": hashedOrderId6
            }, {
                "betterOrderID": hashedOrderId5,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId5
            }]
        }
    })

    # Asks
    runtest({
        "orders": [{
            "orderID": 8,
            "hashedOrderID": hashedOrderId8,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 9,
            "hashedOrderID": hashedOrderId9,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId8,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId9
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId8
            },
            "orders": [{
                "betterOrderID": hashedOrderId9,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId8
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 10,
            "hashedOrderID": hashedOrderId10,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 11,
            "hashedOrderID": hashedOrderId11,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId10,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId10
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId11
            },
            "orders": [{
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId11
            }, {
                "betterOrderID": hashedOrderId10,
                "worseOrderID": ZEROED_ORDER_ID
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 12,
            "hashedOrderID": hashedOrderId12,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 13,
            "hashedOrderID": hashedOrderId13,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId12,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 14,
            "hashedOrderID": hashedOrderId14,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId12,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId14
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId13
            },
            "orders": [{
                "betterOrderID": hashedOrderId14,
                "worseOrderID": hashedOrderId13
            }, {
                "betterOrderID": hashedOrderId12,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId12
            }]
        }
    })
    # Without betterOrderID and/or worseOrderID
    runtest({
        "orders": [{
            "orderID": 8,
            "hashedOrderID": hashedOrderId8,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 9,
            "hashedOrderID": hashedOrderId9,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId9
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId8
            },
            "orders": [{
                "betterOrderID": hashedOrderId9,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId8
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 10,
            "hashedOrderID": hashedOrderId10,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 11,
            "hashedOrderID": hashedOrderId11,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId10
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId11
            },
            "orders": [{
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId11
            }, {
                "betterOrderID": hashedOrderId10,
                "worseOrderID": ZEROED_ORDER_ID
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 12,
            "hashedOrderID": hashedOrderId12,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 13,
            "hashedOrderID": hashedOrderId13,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId12,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 14,
            "hashedOrderID": hashedOrderId14,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId14
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderId13
            },
            "orders": [{
                "betterOrderID": hashedOrderId14,
                "worseOrderID": hashedOrderId13
            }, {
                "betterOrderID": hashedOrderId12,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId12
            }]
        }
    }) 

    # Bids and asks
    runtest({
        "orders": [{
            "orderID": 15,
            "hashedOrderID": hashedOrderId15,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 16,
            "hashedOrderID": hashedOrderId16,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId15,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 17,
            "hashedOrderID": hashedOrderId17,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId15,
            "tradeGroupID": 0
        }, {
            "orderID": 18,
            "hashedOrderID": hashedOrderId18,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 19,
            "hashedOrderID": hashedOrderId19,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId18,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 20,
            "hashedOrderID": hashedOrderId20,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId18,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderId17,
                "ask": hashedOrderId20
            },
            "worstOrder": {
                "bid": hashedOrderId16,
                "ask": hashedOrderId19
            },
            "orders": [{
                "betterOrderID": hashedOrderId17,
                "worseOrderID": hashedOrderId16
            }, {
                "betterOrderID": hashedOrderId15,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId15
            }, {
                "betterOrderID": hashedOrderId20,
                "worseOrderID": hashedOrderId19
            }, {
                "betterOrderID": hashedOrderId18,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId18
            }]
        }
    })
    # Without betterOrderID and/or worseOrderID
    runtest({
        "orders": [{
            "orderID": 15,
            "hashedOrderID": hashedOrderId15,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 16,
            "hashedOrderID": hashedOrderId16,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 17,
            "hashedOrderID": hashedOrderId17,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 18,
            "hashedOrderID": hashedOrderId18,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 19,
            "hashedOrderID": hashedOrderId19,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }, {
            "orderID": 20,
            "hashedOrderID": hashedOrderId20,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderId0,
            "worseOrderID": hashedOrderId0,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderId17,
                "ask": hashedOrderId20
            },
            "worstOrder": {
                "bid": hashedOrderId16,
                "ask": hashedOrderId19
            },
            "orders": [{
                "betterOrderID": hashedOrderId17,
                "worseOrderID": hashedOrderId16
            }, {
                "betterOrderID": hashedOrderId15,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId15
            }, {
                "betterOrderID": hashedOrderId20,
                "worseOrderID": hashedOrderId19
            }, {
                "betterOrderID": hashedOrderId18,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderId18
            }]
        }
    })

def test_saveOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['NewOrders']
    ordersFetcher = contractsFixture.contracts['NewOrdersFetcher']
    hash = hashlib.new('ripemd160')
    hash.update('0')
    hashedOrderId0 = hash.digest()
    hashedOrderId1 = orders.saveOrder(0, BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), hashedOrderId0, hashedOrderId0, 1)
    assert(isinstance(hashedOrderId1, bytes)), "saveOrder wasn't executed successfully"
    hashedOrderId2 = orders.saveOrder(0, ASK, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, hashedOrderId0, hashedOrderId0, 1)
    assert(isinstance(hashedOrderId2, bytes)), "saveOrder wasn't executed successfully"

    assert(ordersFetcher.getOrder(hashedOrderId1, BID, market.address, NO) == [fix('10'), fix('0.5'), '0x'+binascii.hexlify(tester.a1), 0, fix('10'), ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order1 didn't return the expected array of data"
    assert(ordersFetcher.getOrder(hashedOrderId2, ASK, market.address, NO) == [fix('10'), fix('0.5'), '0x'+binascii.hexlify(tester.a2), fix('5'), 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order2 didn't return the expected array of data"

    assert(orders.getAmount(hashedOrderId1, BID, market.address, NO) == fix('10')), "amount for order1 should be set to 10 ETH"
    assert(orders.getAmount(hashedOrderId2, ASK, market.address, NO) == fix('10')), "amount for order2 should be set to 10 ETH"

    assert(orders.getPrice(hashedOrderId1, BID, market.address, NO) == fix('0.5')), "price for order1 should be set to 0.5 ETH"
    assert(orders.getPrice(hashedOrderId2, ASK, market.address, NO) == fix('0.5')), "price for order2 should be set to 0.5 ETH"

    assert(orders.getOrderOwner(hashedOrderId1, BID, market.address, NO) == '0x'+binascii.hexlify(tester.a1)), "orderOwner for order1 should be tester.a1"
    assert(orders.getOrderOwner(hashedOrderId2, ASK, market.address, NO) == '0x'+binascii.hexlify(tester.a2)), "orderOwner for order2 should be tester.a2"

    assert(orders.removeOrder(hashedOrderId1, BID, market.address, NO) == 1), "Remove order 1"
    assert(orders.removeOrder(hashedOrderId2, ASK, market.address, NO) == 1), "Remove order 2"

def test_fillOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['NewOrders']
    ordersFetcher = contractsFixture.contracts['NewOrdersFetcher']
    hash = hashlib.new('ripemd160')
    hash.update('0')
    hashedOrderId0 = hash.digest()
    hashedOrderId1 = orders.saveOrder(0, BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), hashedOrderId0, hashedOrderId0, 1)
    assert(isinstance(hashedOrderId1, bytes)), "saveOrder wasn't executed successfully"
    hashedOrderId2 = orders.saveOrder(0, BID, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, hashedOrderId0, hashedOrderId0, 1)
    assert(isinstance(hashedOrderId2, bytes)), "saveOrder wasn't executed successfully"

    # orderID, fill, money, shares
    with raises(TransactionFailed):
        orders.fillOrder(hashedOrderId1, BID, market.address, NO, fix('11'), 0)
    with raises(TransactionFailed):
        orders.fillOrder(hashedOrderId1, BID, market.address, NO, 0, fix('1'))
    with raises(TransactionFailed):
        orders.fillOrder(hashedOrderId1, BID, market.address, NO, fix('10'), fix('1'))
    # fully fill
    assert(orders.fillOrder(hashedOrderId1, BID, market.address, NO, fix('10'), 0) == 1), "fillOrder wasn't executed successfully"
    # prove all
    assert(ordersFetcher.getOrder(hashedOrderId1, BID, market.address, NO) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order1 didn't return the expected data array"
    # test partial fill
    assert(orders.fillOrder(hashedOrderId2, BID, market.address, NO, 0, fix('3')) == 1), "fillOrder wasn't executed successfully"
    # confirm partial fill
    assert(ordersFetcher.getOrder(hashedOrderId2, BID, market.address, NO) == [fix('4'), fix('0.5'), '0x'+binascii.hexlify(tester.a2), fix('2'), 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order2 didn't return the expected data array"
    # fill rest of order2
    assert(orders.fillOrder(hashedOrderId2, BID, market.address, NO, 0, fix('2')) == 1), "fillOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(hashedOrderId2, BID, market.address, NO) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order2 didn't return the expected data array"

def test_removeOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['NewOrders']
    ordersFetcher = contractsFixture.contracts['NewOrdersFetcher']
    hash = hashlib.new('ripemd160')
    hash.update('0')
    hashedOrderId0 = hash.digest()
    hashedOrderId1 = orders.saveOrder(0, BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), hashedOrderId0, hashedOrderId0, 1)
    assert(isinstance(hashedOrderId1, bytes)), "saveOrder wasn't executed successfully"
    hashedOrderId2 = orders.saveOrder(0, BID, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, hashedOrderId0, hashedOrderId0, 1)
    assert(isinstance(hashedOrderId2, bytes)), "saveOrder wasn't executed successfully"
    hashedOrderId3 = orders.saveOrder(0, BID, market.address, fix('10'), fix('0.5'), tester.a1, YES, 0, fix('10'), hashedOrderId0, hashedOrderId0, 1)
    assert(isinstance(hashedOrderId3, bytes)), "saveOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(hashedOrderId3, BID, market.address, YES) == [fix('10'), fix('0.5'), '0x'+binascii.hexlify(tester.a1), 0, fix('10'), ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order3 didn't return the expected data array"
    assert(orders.removeOrder(hashedOrderId3, BID, market.address, YES) == 1), "removeOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(hashedOrderId3, BID, market.address, YES) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order3 should return an 0'd out array as it has been removed"
    assert(orders.removeOrder(hashedOrderId1, BID, market.address, NO) == 1), "Remove order 1"
    assert(orders.removeOrder(hashedOrderId2, BID, market.address, NO) == 1), "Remove order 2"
