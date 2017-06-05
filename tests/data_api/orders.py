#!/usr/bin/env python

from __future__ import division
import os
import sys
import json
import iocapture
import ethereum.tester
import utils

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir)
src = os.path.join(ROOT, "src")

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

    def test_hashcommit():
        order = contracts.orders.makeOrderHash(market1, 1, 1)
        assert(order != 0), "makeOrderHash for market1 shouldn't be 0"

        assert(contracts.orders.commitOrder(order) == 1), "commitOrder wasn't executed successfully"
        try:
            raise Exception(contracts.orders.checkHash(order, address0))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "checkHash for order should throw because that order was placed in the same block we are checking"
        # move the block.number up 1
        contracts._ContractLoader__state.mine(1)
        assert(contracts.orders.checkHash(order, address0) == 1), "checkHash for order should now be 1"

    def test_saveOrder():
        assert(contracts.orders.saveOrder(order1, 1, market1, WEI_TO_ETH*10, pointFive, address0, 1, 0, WEI_TO_ETH*10, 0, 0, 2) == 1), "saveOrder wasn't executed successfully"
        assert(contracts.orders.saveOrder(order2, 2, market1, WEI_TO_ETH*10, pointFive, address1, 1, WEI_TO_ETH*5, 0, 0, 0, 1) == 1), "saveOrder wasn't executed successfully"

        assert(contracts.orders.getOrder(order1) == [order1, 1, market1, WEI_TO_ETH*10, pointFive, address0, contracts._ContractLoader__state.block.number, 1, 0, WEI_TO_ETH*10, 0, 0]), "getOrder for order1 didn't return the expected array of data"
        assert(contracts.orders.getOrder(order2) == [order2, 2, market1, WEI_TO_ETH*10, pointFive, address1, contracts._ContractLoader__state.block.number, 1, WEI_TO_ETH*5, 0, 0, 0]), "getOrder for order2 didn't return the expected array of data"

        assert(contracts.orders.getAmount(order1) == WEI_TO_ETH*10), "amount for order1 should be set to WEI_TO_ETH*10 (WEI_TO_ETH = 10**18)"
        assert(contracts.orders.getAmount(order2) == WEI_TO_ETH*10), "amount for order2 should be set to WEI_TO_ETH*10 (WEI_TO_ETH = 10**18)"

        assert(int(contracts.orders.getID(order1), 16) == order1), "getID didn't return the expected order"
        assert(int(contracts.orders.getID(order2), 16) == order2), "getID didn't return the expected order"

        assert(contracts.orders.getPrice(order1) == pointFive), "price for order1 should be set to pointFive (.5*WEI_TO_ETH)"
        assert(contracts.orders.getPrice(order2) == pointFive), "price for order2 should be set to pointFive (.5*WEI_TO_ETH)"

        assert(contracts.orders.getOrderOwner(order1) == t.a0.encode("hex")), "orderOwner for order1 should be address0"
        assert(contracts.orders.getOrderOwner(order2) == t.a1.encode("hex")), "orderOwner for order2 should be address1"

        assert(contracts.orders.getType(order1) == 1), "type for order1 should be set to 1"
        assert(contracts.orders.getType(order2) == 2), "type for order2 should be set to 2"

    def test_orderSorting():
        def runtest(testCase):
            marketID = utils.createMarket(contracts, utils.createBinaryEvent(contracts))
            contracts._ContractLoader__state.mine(1)
            orders = []
            for order in testCase["orders"]:
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
                                                    order["tradeGroupID"])
                assert(output == 1), "saveOrder wasn't executed successfully"
                contracts._ContractLoader__state.mine(1)
            for order in testCase["orders"]:
                orders.append(contracts.orders.getOrder(order["orderID"]))
            assert(len(orders) == len(testCase["expected"]["orders"]))
            for i, order in enumerate(orders):
                outcomeID = testCase["orders"][i]["outcome"]
                assert(int(contracts.orders.getBestBidOrderID(marketID, outcomeID), 16) == testCase["expected"]["bestOrder"]["bid"])
                assert(int(contracts.orders.getBestAskOrderID(marketID, outcomeID), 16) == testCase["expected"]["bestOrder"]["ask"])
                assert(int(contracts.orders.getWorstBidOrderID(marketID, outcomeID), 16) == testCase["expected"]["worstOrder"]["bid"])
                assert(int(contracts.orders.getWorstAskOrderID(marketID, outcomeID), 16) == testCase["expected"]["worstOrder"]["ask"])
                assert(order[10] == testCase["expected"]["orders"][i]["betterOrderID"])
                assert(order[11] == testCase["expected"]["orders"][i]["worseOrderID"])

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

    def test_fillOrder():
        # orderID, fill, money, shares
        try:
            raise Exception(contracts.orders.fillOrder(order1, WEI_TO_ETH*20, 0, 0))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "fillOrder should fail if fill is greated then the amount of the order"
        try:
            raise Exception(contracts.orders.fillOrder(order1, WEI_TO_ETH*10, 0, WEI_TO_ETH*20))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "fillOrder should fail if shares is greater than the sharesEscrowed in the order"
        try:
            raise Exception(contracts.orders.fillOrder(order1, WEI_TO_ETH*10, WEI_TO_ETH*20, 0))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "fillOrder should fail if money is greater than the moneyEscrowed in the order"
        # fully fill
        assert(contracts.orders.fillOrder(order1, WEI_TO_ETH*10, 0, WEI_TO_ETH*10) == 1), "fillOrder wasn't executed successfully"
        # prove all
        order1BlockNumber = contracts.orders.getOrder(order1)[6]
        assert(contracts.orders.getOrder(order1) == [order1, 1, market1, 0, pointFive, address0, order1BlockNumber, 1, 0, 0, 0, 0]), "getOrder for order1 didn't return the expected data array"
        # test partial fill
        assert(contracts.orders.fillOrder(order2, WEI_TO_ETH*6, WEI_TO_ETH*3, 0) == 1), "fillOrder wasn't executed successfully"
        # confirm partial fill
        order2BlockNumber = contracts.orders.getOrder(order2)[6]
        assert(contracts.orders.getOrder(order2) == [order2, 2, market1, WEI_TO_ETH*4, pointFive, address1, order2BlockNumber, 1, WEI_TO_ETH*2, 0, 0, 0]), "getOrder for order2 didn't return the expected data array"
        # fill rest of order2
        assert(contracts.orders.fillOrder(order2, WEI_TO_ETH*4, WEI_TO_ETH*2, 0) == 1), "fillOrder wasn't executed successfully"
        assert(contracts.orders.getOrder(order2) == [order2, 2, market1, 0, pointFive, address1, order2BlockNumber, 1, 0, 0, 0, 0]), "getOrder for order2 didn't return the expected data array"

    def test_removeOrder():
        order3 = 321321321
        assert(contracts.orders.saveOrder(order3, 1, market1, WEI_TO_ETH*10, pointFive, address0, 2, 0, WEI_TO_ETH*10, 123456789, 0, 0) == 1), "saveOrder wasn't executed successfully"
        order3BlockNumber = contracts.orders.getOrder(order3)[6]
        assert(contracts.orders.getOrder(order3) == [order3, 1, market1, WEI_TO_ETH*10, pointFive, address0, order3BlockNumber, 2, 0, WEI_TO_ETH*10, 123456789, 0]), "getOrder for order3 didn't return the expected data array"
        assert(contracts.orders.removeOrder(order3) == 1), "removeOrder wasn't executed successfully"
        assert(contracts.orders.getOrder(order3) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "getOrder for order3 should return an 0'd out array as it has been removed"

    test_hashcommit()
    test_saveOrder()
    test_orderSorting()
    test_fillOrder()
    test_removeOrder()

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_orders(contracts)
