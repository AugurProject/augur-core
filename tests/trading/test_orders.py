#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
import numpy as np
from pytest import fixture, mark, lazy_fixture, raises
from utils import fix, bytesToLong, bytesToHexString, stringToBytes

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

ZEROED_ORDER_ID = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

def test_walkOrderList_bids(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    outcomeID = 1
    order = {
        "orderID": 5,
        "type": BID,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": ZEROED_ORDER_ID,
        "worseOrderID": ZEROED_ORDER_ID,
        "tradeGroupID": 0
    }
    hashedOrderID5 = orders.saveOrder(ZEROED_ORDER_ID, order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderID5, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == hashedOrderID5)
    assert(worstOrderID == hashedOrderID5)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderID5, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderID5, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.61'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderID5])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.58'), bestOrderID) == [hashedOrderID5, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderID5, ZEROED_ORDER_ID])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderID5, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderID5, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.61'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderID5])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.58'), worstOrderID) == [hashedOrderID5, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderID5, ZEROED_ORDER_ID])
    order = {
        "orderID": 6,
        "type": BID,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": ZEROED_ORDER_ID,
        "worseOrderID": ZEROED_ORDER_ID,
        "tradeGroupID": 0
    }
    hashedOrderID6 = orders.saveOrder(ZEROED_ORDER_ID, order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderID6, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == hashedOrderID5)
    assert(worstOrderID == hashedOrderID6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderID5, hashedOrderID6])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderID6, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.61'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderID5])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.58'), bestOrderID) == [hashedOrderID6, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderID5, hashedOrderID6])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderID5, hashedOrderID6])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderID6, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.61'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderID5])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.58'), worstOrderID) == [hashedOrderID6, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderID5, hashedOrderID6])
    order = {
        "orderID": 7,
        "type": BID,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": ZEROED_ORDER_ID,
        "worseOrderID": ZEROED_ORDER_ID,
        "tradeGroupID": 0
    }
    hashedOrderID7 = orders.saveOrder(ZEROED_ORDER_ID, order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderID7, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == hashedOrderID5)
    assert(worstOrderID == hashedOrderID6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderID5, hashedOrderID7])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderID6, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.61'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderID5])
    assert(ordersFetcher.descendOrderList(BID, market.address, outcomeID, fix('0.58'), bestOrderID) == [hashedOrderID6, ZEROED_ORDER_ID])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderID5, hashedOrderID7])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderID6, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.61'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderID5])
    assert(ordersFetcher.ascendOrderList(BID, market.address, outcomeID, fix('0.58'), worstOrderID) == [hashedOrderID6, ZEROED_ORDER_ID])
    assert(orders.removeOrder(hashedOrderID5, BID, market.address, outcomeID) == 1), "Remove order 5"
    assert(orders.removeOrder(hashedOrderID6, BID, market.address, outcomeID) == 1), "Remove order 6"
    assert(orders.removeOrder(hashedOrderID7, BID, market.address, outcomeID) == 1), "Remove order 7"

def test_walkOrderList_asks(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    outcomeID = 1
    order = {
        "orderID": 8,
        "type": ASK,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": ZEROED_ORDER_ID,
        "worseOrderID": ZEROED_ORDER_ID,
        "tradeGroupID": 0
    }
    hashedOrderID8 = orders.saveOrder(ZEROED_ORDER_ID, order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderID8, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == hashedOrderID8)
    assert(worstOrderID == hashedOrderID8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.59'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderID8])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.61'), bestOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.58'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderID8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.59'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderID8])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.61'), worstOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.58'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderID8])
    order = {
        "orderID": 9,
        "type": ASK,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": ZEROED_ORDER_ID,
        "worseOrderID": ZEROED_ORDER_ID,
        "tradeGroupID": 0
    }
    hashedOrderID9 = orders.saveOrder(ZEROED_ORDER_ID, order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderID9, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == hashedOrderID9)
    assert(worstOrderID == hashedOrderID8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderID9, hashedOrderID8])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.61'), bestOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.58'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderID9])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderID9, hashedOrderID8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderID9, hashedOrderID8])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.61'), worstOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.58'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderID9])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.595'), bestOrderID) == [hashedOrderID9, hashedOrderID8])
    order = {
        "orderID": 10,
        "type": ASK,
        "fxpAmount": fix('1'),
        "fxpPrice": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": ZEROED_ORDER_ID,
        "worseOrderID": ZEROED_ORDER_ID,
        "tradeGroupID": 0
    }
    hashedOrderID10 = orders.saveOrder(ZEROED_ORDER_ID, order["type"], market.address, order["fxpAmount"], order["fxpPrice"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(isinstance(hashedOrderID9, bytes)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == hashedOrderID9)
    assert(worstOrderID == hashedOrderID8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.6'), bestOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.59'), bestOrderID) == [hashedOrderID9, hashedOrderID10])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.61'), bestOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.descendOrderList(ASK, market.address, outcomeID, fix('0.58'), bestOrderID) == [ZEROED_ORDER_ID, hashedOrderID9])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.6'), worstOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.59'), worstOrderID) == [hashedOrderID9, hashedOrderID10])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.61'), worstOrderID) == [hashedOrderID8, ZEROED_ORDER_ID])
    assert(ordersFetcher.ascendOrderList(ASK, market.address, outcomeID, fix('0.58'), worstOrderID) == [ZEROED_ORDER_ID, hashedOrderID9])
    assert(orders.removeOrder(hashedOrderID8, ASK, market.address, outcomeID) == 1), "Remove order 8"
    assert(orders.removeOrder(hashedOrderID9, ASK, market.address, outcomeID) == 1), "Remove order 9"
    assert(orders.removeOrder(hashedOrderID10, ASK, market.address, outcomeID) == 1), "Remove order 10"

def test_orderSorting(contractsFixture):
    def runtest(testCase):
        market = contractsFixture.binaryMarket
        orders = contractsFixture.contracts['Orders']
        ordersFetcher = contractsFixture.contracts['OrdersFetcher']
        ordersCollection = []
        for order in testCase["orders"]:
            output = orders.saveOrder(
                order["hashedOrderID"],
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
    orders = contractsFixture.contracts['Orders']
    blockNumber = contractsFixture.chain.head_state.block_number
    hashedOrderID1 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderID2 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderID3 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderID4 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderID5 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderID6 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderID7 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderID8 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderID9 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderID10 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderID11 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderID12 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderID13 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderID14 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderID15 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderID16 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
    hashedOrderID17 = orders.getOrderIdHash(BID, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderID18 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.6'), tester.a0, blockNumber, 1, fix('0.6'), 0)
    hashedOrderID19 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.61'), tester.a0, blockNumber, 1, fix('0.61'), 0)
    hashedOrderID20 = orders.getOrderIdHash(ASK, market.address, fix('1'), fix('0.59'), tester.a0, blockNumber, 1, fix('0.59'), 0)
  
    # Bids
    runtest({
        "orders": [{
            "orderID": 1,
            "hashedOrderID": hashedOrderID1,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 2,
            "hashedOrderID": hashedOrderID2,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": hashedOrderID1,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderID2,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderID1,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": hashedOrderID2,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID1
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 3,
            "hashedOrderID": hashedOrderID3,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 4,
            "hashedOrderID": hashedOrderID4,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderID3,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderID3,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderID4,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID4
            }, {
                "betterOrderID": hashedOrderID3,
                "worseOrderID": ZEROED_ORDER_ID
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 5,
            "hashedOrderID": hashedOrderID5,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 6,
            "hashedOrderID": hashedOrderID6,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderID5,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 7,
            "hashedOrderID": hashedOrderID7,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": hashedOrderID5,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderID7,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderID6,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": hashedOrderID7,
                "worseOrderID": hashedOrderID6
            }, {
                "betterOrderID": hashedOrderID5,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID5
            }]
        }
    })
    # Without betterOrderID and/or worseOrderID parameters
    runtest({
        "orders": [{
            "orderID": 1,
            "hashedOrderID": hashedOrderID1,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 2,
            "hashedOrderID": hashedOrderID2,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderID2,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderID1,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": hashedOrderID2,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID1
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 3,
           "hashedOrderID": hashedOrderID3,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 4,
            "hashedOrderID": hashedOrderID4,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderID3,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderID4,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID4
            }, {
                "betterOrderID": hashedOrderID3,
                "worseOrderID": ZEROED_ORDER_ID
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 5,
            "hashedOrderID": hashedOrderID5,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 6,
            "hashedOrderID": hashedOrderID6,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 7,
            "hashedOrderID": hashedOrderID7,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderID7,
                "ask": ZEROED_ORDER_ID
            },
            "worstOrder": {
                "bid": hashedOrderID6,
                "ask": ZEROED_ORDER_ID
            },
            "orders": [{
                "betterOrderID": hashedOrderID7,
                "worseOrderID": hashedOrderID6
            }, {
                "betterOrderID": hashedOrderID5,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID5
            }]
        }
    })

    # Asks
    runtest({
        "orders": [{
            "orderID": 8,
            "hashedOrderID": hashedOrderID8,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 9,
            "hashedOrderID": hashedOrderID9,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": hashedOrderID8,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID9
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID8
            },
            "orders": [{
                "betterOrderID": hashedOrderID9,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID8
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 10,
            "hashedOrderID": hashedOrderID10,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 11,
            "hashedOrderID": hashedOrderID11,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderID10,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID10
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID11
            },
            "orders": [{
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID11
            }, {
                "betterOrderID": hashedOrderID10,
                "worseOrderID": ZEROED_ORDER_ID
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 12,
            "hashedOrderID": hashedOrderID12,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 13,
            "hashedOrderID": hashedOrderID13,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderID12,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 14,
            "hashedOrderID": hashedOrderID14,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": hashedOrderID12,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID14
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID13
            },
            "orders": [{
                "betterOrderID": hashedOrderID14,
                "worseOrderID": hashedOrderID13
            }, {
                "betterOrderID": hashedOrderID12,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID12
            }]
        }
    })
    # Without betterOrderID and/or worseOrderID
    runtest({
        "orders": [{
            "orderID": 8,
            "hashedOrderID": hashedOrderID8,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 9,
            "hashedOrderID": hashedOrderID9,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID9
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID8
            },
            "orders": [{
                "betterOrderID": hashedOrderID9,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID8
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 10,
            "hashedOrderID": hashedOrderID10,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 11,
            "hashedOrderID": hashedOrderID11,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID10
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID11
            },
            "orders": [{
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID11
            }, {
                "betterOrderID": hashedOrderID10,
                "worseOrderID": ZEROED_ORDER_ID
            }]
        }
    })
    runtest({
        "orders": [{
            "orderID": 12,
            "hashedOrderID": hashedOrderID12,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 13,
            "hashedOrderID": hashedOrderID13,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderID12,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 14,
            "hashedOrderID": hashedOrderID14,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID14
            },
            "worstOrder": {
                "bid": ZEROED_ORDER_ID,
                "ask": hashedOrderID13
            },
            "orders": [{
                "betterOrderID": hashedOrderID14,
                "worseOrderID": hashedOrderID13
            }, {
                "betterOrderID": hashedOrderID12,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID12
            }]
        }
    }) 

    # Bids and asks
    runtest({
        "orders": [{
            "orderID": 15,
            "hashedOrderID": hashedOrderID15,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 16,
            "hashedOrderID": hashedOrderID16,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderID15,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 17,
            "hashedOrderID": hashedOrderID17,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": hashedOrderID15,
            "tradeGroupID": 0
        }, {
            "orderID": 18,
            "hashedOrderID": hashedOrderID18,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 19,
            "hashedOrderID": hashedOrderID19,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": hashedOrderID18,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 20,
            "hashedOrderID": hashedOrderID20,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": hashedOrderID18,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderID17,
                "ask": hashedOrderID20
            },
            "worstOrder": {
                "bid": hashedOrderID16,
                "ask": hashedOrderID19
            },
            "orders": [{
                "betterOrderID": hashedOrderID17,
                "worseOrderID": hashedOrderID16
            }, {
                "betterOrderID": hashedOrderID15,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID15
            }, {
                "betterOrderID": hashedOrderID20,
                "worseOrderID": hashedOrderID19
            }, {
                "betterOrderID": hashedOrderID18,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID18
            }]
        }
    })
    # Without betterOrderID and/or worseOrderID
    runtest({
        "orders": [{
            "orderID": 15,
            "hashedOrderID": hashedOrderID15,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 16,
            "hashedOrderID": hashedOrderID16,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 17,
            "hashedOrderID": hashedOrderID17,
            "type": BID,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 18,
            "hashedOrderID": hashedOrderID18,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.6'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.6'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 19,
            "hashedOrderID": hashedOrderID19,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.61'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.61'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }, {
            "orderID": 20,
            "hashedOrderID": hashedOrderID20,
            "type": ASK,
            "fxpAmount": fix('1'),
            "fxpPrice": fix('0.59'),
            "sender": tester.a0,
            "outcome": 1,
            "fxpMoneyEscrowed": fix('0.59'),
            "fxpSharesEscrowed": 0,
            "betterOrderID": ZEROED_ORDER_ID,
            "worseOrderID": ZEROED_ORDER_ID,
            "tradeGroupID": 0
        }],
        "expected": {
            "bestOrder": {
                "bid": hashedOrderID17,
                "ask": hashedOrderID20
            },
            "worstOrder": {
                "bid": hashedOrderID16,
                "ask": hashedOrderID19
            },
            "orders": [{
                "betterOrderID": hashedOrderID17,
                "worseOrderID": hashedOrderID16
            }, {
                "betterOrderID": hashedOrderID15,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID15
            }, {
                "betterOrderID": hashedOrderID20,
                "worseOrderID": hashedOrderID19
            }, {
                "betterOrderID": hashedOrderID18,
                "worseOrderID": ZEROED_ORDER_ID
            }, {
                "betterOrderID": ZEROED_ORDER_ID,
                "worseOrderID": hashedOrderID18
            }]
        }
    })

def test_saveOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    hashedOrderID1 = orders.saveOrder(ZEROED_ORDER_ID, BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), ZEROED_ORDER_ID, ZEROED_ORDER_ID, 1)
    assert(isinstance(hashedOrderID1, bytes)), "saveOrder wasn't executed successfully"
    hashedOrderID2 = orders.saveOrder(ZEROED_ORDER_ID, ASK, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 1)
    assert(isinstance(hashedOrderID2, bytes)), "saveOrder wasn't executed successfully"

    assert(ordersFetcher.getOrder(hashedOrderID1, BID, market.address, NO) == [fix('10'), fix('0.5'), bytesToHexString(tester.a1), 0, fix('10'), ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order1 didn't return the expected array of data"
    assert(ordersFetcher.getOrder(hashedOrderID2, ASK, market.address, NO) == [fix('10'), fix('0.5'), bytesToHexString(tester.a2), fix('5'), 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order2 didn't return the expected array of data"

    assert(orders.getAmount(hashedOrderID1, BID, market.address, NO) == fix('10')), "amount for order1 should be set to 10 ETH"
    assert(orders.getAmount(hashedOrderID2, ASK, market.address, NO) == fix('10')), "amount for order2 should be set to 10 ETH"

    assert(orders.getPrice(hashedOrderID1, BID, market.address, NO) == fix('0.5')), "price for order1 should be set to 0.5 ETH"
    assert(orders.getPrice(hashedOrderID2, ASK, market.address, NO) == fix('0.5')), "price for order2 should be set to 0.5 ETH"

    assert(orders.getOrderOwner(hashedOrderID1, BID, market.address, NO) == bytesToHexString(tester.a1)), "orderOwner for order1 should be tester.a1"
    assert(orders.getOrderOwner(hashedOrderID2, ASK, market.address, NO) == bytesToHexString(tester.a2)), "orderOwner for order2 should be tester.a2"

    assert(orders.removeOrder(hashedOrderID1, BID, market.address, NO) == 1), "Remove order 1"
    assert(orders.removeOrder(hashedOrderID2, ASK, market.address, NO) == 1), "Remove order 2"

def test_fillOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    hashedOrderID1 = orders.saveOrder(ZEROED_ORDER_ID, BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), ZEROED_ORDER_ID, ZEROED_ORDER_ID, 1)
    assert(isinstance(hashedOrderID1, bytes)), "saveOrder wasn't executed successfully"
    hashedOrderID2 = orders.saveOrder(ZEROED_ORDER_ID, BID, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 1)
    assert(isinstance(hashedOrderID2, bytes)), "saveOrder wasn't executed successfully"

    # orderID, fill, money, shares
    with raises(TransactionFailed):
        orders.fillOrder(hashedOrderID1, BID, market.address, NO, fix('11'), 0)
    with raises(TransactionFailed):
        orders.fillOrder(hashedOrderID1, BID, market.address, NO, 0, fix('1'))
    with raises(TransactionFailed):
        orders.fillOrder(hashedOrderID1, BID, market.address, NO, fix('10'), fix('1'))
    # fully fill
    assert(orders.fillOrder(hashedOrderID1, BID, market.address, NO, fix('10'), 0) == 1), "fillOrder wasn't executed successfully"
    # prove all
    assert(ordersFetcher.getOrder(hashedOrderID1, BID, market.address, NO) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order1 didn't return the expected data array"
    # test partial fill
    assert(orders.fillOrder(hashedOrderID2, BID, market.address, NO, 0, fix('3')) == 1), "fillOrder wasn't executed successfully"
    # confirm partial fill
    assert(ordersFetcher.getOrder(hashedOrderID2, BID, market.address, NO) == [fix('4'), fix('0.5'), bytesToHexString(tester.a2), fix('2'), 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order2 didn't return the expected data array"
    # fill rest of order2
    assert(orders.fillOrder(hashedOrderID2, BID, market.address, NO, 0, fix('2')) == 1), "fillOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(hashedOrderID2, BID, market.address, NO) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order2 didn't return the expected data array"

def test_removeOrder(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    hashedOrderID1 = orders.saveOrder(ZEROED_ORDER_ID, BID, market.address, fix('10'), fix('0.5'), tester.a1, NO, 0, fix('10'), ZEROED_ORDER_ID, ZEROED_ORDER_ID, 1)
    assert(isinstance(hashedOrderID1, bytes)), "saveOrder wasn't executed successfully"
    hashedOrderID2 = orders.saveOrder(ZEROED_ORDER_ID, BID, market.address, fix('10'), fix('0.5'), tester.a2, NO, fix('5'), 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 1)
    assert(isinstance(hashedOrderID2, bytes)), "saveOrder wasn't executed successfully"
    hashedOrderID3 = orders.saveOrder(ZEROED_ORDER_ID, BID, market.address, fix('10'), fix('0.5'), tester.a1, YES, 0, fix('10'), ZEROED_ORDER_ID, ZEROED_ORDER_ID, 1)
    assert(isinstance(hashedOrderID3, bytes)), "saveOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(hashedOrderID3, BID, market.address, YES) == [fix('10'), fix('0.5'), bytesToHexString(tester.a1), 0, fix('10'), ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order3 didn't return the expected data array"
    assert(orders.removeOrder(hashedOrderID3, BID, market.address, YES) == 1), "removeOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(hashedOrderID3, BID, market.address, YES) == [0, 0, '0x0000000000000000000000000000000000000000', 0, 0, ZEROED_ORDER_ID, ZEROED_ORDER_ID, 0]), "getOrder for order3 should return an 0'd out array as it has been removed"
    assert(orders.removeOrder(hashedOrderID1, BID, market.address, NO) == 1), "Remove order 1"
    assert(orders.removeOrder(hashedOrderID2, BID, market.address, NO) == 1), "Remove order 2"
