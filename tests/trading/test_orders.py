#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
import numpy as np
from pytest import fixture, mark, lazy_fixture, raises
from utils import fix, bytesToLong, bytesToHexString, longTo32Bytes, longToHexString, stringToBytes
from constants import BID, ASK, YES, NO

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
        "price": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId5 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId5 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == orderId5)
    assert(worstOrderID == orderId5)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, fix('0.6'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, fix('0.59'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, fix('0.61'), bestOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.descendOrderList(BID, fix('0.58'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, fix('0.595'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, fix('0.6'), worstOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.59'), worstOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.61'), worstOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.58'), worstOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.595'), bestOrderID) == [orderId5, longTo32Bytes(0)])
    order = {
        "orderID": longTo32Bytes(6),
        "type": BID,
        "fxpAmount": fix('1'),
        "price": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId6 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId6 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == orderId5)
    assert(worstOrderID == orderId6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, fix('0.6'), bestOrderID) == [orderId5, orderId6])
    assert(ordersFetcher.descendOrderList(BID, fix('0.59'), bestOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, fix('0.61'), bestOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.descendOrderList(BID, fix('0.58'), bestOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, fix('0.595'), bestOrderID) == [orderId5, orderId6])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, fix('0.6'), worstOrderID) == [orderId5, orderId6])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.59'), worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.61'), worstOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.58'), worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.595'), bestOrderID) == [orderId5, orderId6])
    order = {
        "orderID": longTo32Bytes(7),
        "type": BID,
        "fxpAmount": fix('1'),
        "price": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId7 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId7 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == orderId5)
    assert(worstOrderID == orderId6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, fix('0.6'), bestOrderID) == [orderId5, orderId7])
    assert(ordersFetcher.descendOrderList(BID, fix('0.59'), bestOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, fix('0.61'), bestOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.descendOrderList(BID, fix('0.58'), bestOrderID) == [orderId6, longTo32Bytes(0)])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, fix('0.6'), worstOrderID) == [orderId5, orderId7])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.59'), worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.61'), worstOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.ascendOrderList(BID, fix('0.58'), worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(orders.removeOrder(orderId5) == 1), "Remove order 5"
    assert(orders.removeOrder(orderId6) == 1), "Remove order 6"
    assert(orders.removeOrder(orderId7) == 1), "Remove order 7"

def test_walkOrderList_asks(contractsFixture):
    market = contractsFixture.binaryMarket
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    outcomeID = 1
    order = {
        "orderID": longTo32Bytes(8),
        "type": ASK,
        "fxpAmount": fix('1'),
        "price": fix('0.6'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.6'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId8 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId8 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == orderId8)
    assert(worstOrderID == orderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, fix('0.6'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.59'), bestOrderID) == [longTo32Bytes(0), orderId8])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.61'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.58'), bestOrderID) == [longTo32Bytes(0), orderId8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.6'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.59'), worstOrderID) == [longTo32Bytes(0), orderId8])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.61'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.58'), worstOrderID) == [longTo32Bytes(0), orderId8])
    order = {
        "orderID": longTo32Bytes(9),
        "type": ASK,
        "fxpAmount": fix('1'),
        "price": fix('0.59'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.59'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId9 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId9 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == orderId9)
    assert(worstOrderID == orderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, fix('0.6'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.59'), bestOrderID) == [orderId9, orderId8])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.61'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.58'), bestOrderID) == [longTo32Bytes(0), orderId9])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.595'), bestOrderID) == [orderId9, orderId8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.6'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.59'), worstOrderID) == [orderId9, orderId8])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.61'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.58'), worstOrderID) == [longTo32Bytes(0), orderId9])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.595'), bestOrderID) == [orderId9, orderId8])
    order = {
        "orderID": longTo32Bytes(10),
        "type": ASK,
        "fxpAmount": fix('1'),
        "price": fix('0.595'),
        "sender": tester.a0,
        "outcome": outcomeID,
        "fxpMoneyEscrowed": fix('0.595'),
        "fxpSharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": 0
    }
    orderId10 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["fxpMoneyEscrowed"], order["fxpSharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId10 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == orderId9)
    assert(worstOrderID == orderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, fix('0.6'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.59'), bestOrderID) == [orderId9, orderId10])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.61'), bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, fix('0.58'), bestOrderID) == [longTo32Bytes(0), orderId9])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.6'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.59'), worstOrderID) == [orderId9, orderId10])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.61'), worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, fix('0.58'), worstOrderID) == [longTo32Bytes(0), orderId9])
    assert(orders.removeOrder(orderId8) == 1), "Remove order 8"
    assert(orders.removeOrder(orderId9) == 1), "Remove order 9"
    assert(orders.removeOrder(orderId10) == 1), "Remove order 10"

@mark.parametrize('where, orderType, hints, fixture', [
    ('best', BID, True, lazy_fixture('contractsFixture')),
    ('middle', BID, True, lazy_fixture('contractsFixture')),
    ('worst', BID, True, lazy_fixture('contractsFixture')),
    ('best', BID, False, lazy_fixture('contractsFixture')),
    ('middle', BID, False, lazy_fixture('contractsFixture')),
    ('worst', BID, False, lazy_fixture('contractsFixture')),
    ('best', ASK, True, lazy_fixture('contractsFixture')),
    ('middle', ASK, True, lazy_fixture('contractsFixture')),
    ('worst', ASK, True, lazy_fixture('contractsFixture')),
    ('best', ASK, False, lazy_fixture('contractsFixture')),
    ('middle', ASK, False, lazy_fixture('contractsFixture')),
    ('worst', ASK, False, lazy_fixture('contractsFixture')),
])
def test_orderBidSorting(where, orderType, hints, fixture):
    print dir(fixture)
    market = fixture.binaryMarket
    orders = fixture.contracts['Orders']
    ordersFetcher = fixture.contracts['OrdersFetcher']

    # setup pre-existing orders
    worstPrice = fix('0.60') if orderType == BID else fix('0.66')
    bestPrice = fix('0.66') if orderType == BID else fix('0.60')
    worstOrderId = orders.saveOrder(orderType, market.address, fix('1'), worstPrice, tester.a0, YES, worstPrice, 0, longTo32Bytes(0), longTo32Bytes(0), 0)
    bestOrderId = orders.saveOrder(orderType, market.address, fix('1'), bestPrice, tester.a0, YES, bestPrice, 0, longTo32Bytes(0), longTo32Bytes(0), 0)

    # validate that our setup went smoothly
    assert orders.getBestOrderId(orderType, market.address, YES) == bestOrderId
    assert orders.getWorstOrderId(orderType, market.address, YES) == worstOrderId
    assert orders.getWorseOrderId(bestOrderId) == worstOrderId
    assert orders.getWorseOrderId(worstOrderId) == longTo32Bytes(0)
    assert orders.getBetterOrderId(worstOrderId) == bestOrderId
    assert orders.getBetterOrderId(bestOrderId) == longTo32Bytes(0)

    # insert our new order
    if where == 'best':
        orderPrice = fix('0.67') if orderType == BID else fix('0.59')
        betterOrderId = longTo32Bytes(0)
        worseOrderId = bestOrderId if hints else longTo32Bytes(0)
    if where == 'middle':
        orderPrice = fix('0.63')
        betterOrderId = bestOrderId if hints else longTo32Bytes(0)
        worseOrderId = worstOrderId if hints else longTo32Bytes(0)
    if where == 'worst':
        orderPrice = fix('0.59') if orderType == BID else fix('0.67')
        betterOrderId = worstOrderId if hints else longTo32Bytes(0)
        worseOrderId = longTo32Bytes(0)
    insertedOrder = orders.saveOrder(orderType, market.address, fix('1'), orderPrice, tester.a0, YES, orderPrice, 0, betterOrderId, worseOrderId, 0)

    # validate the new order was inserted correctly
    assert orders.getBetterOrderId(insertedOrder) == longTo32Bytes(0) if where == 'best' else bestOrderId
    assert orders.getWorseOrderId(insertedOrder) == longTo32Bytes(0) if where == 'worst' else worstOrderId
    assert orders.getBestOrderId(orderType, market.address, YES) == insertedOrder if where == 'best' else bestOrderId
    assert orders.getWorstOrderId(orderType, market.address, YES) == insertedOrder if where == 'worst' else worstOrderId

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

    assert(orders.getAmount(orderId1) == fix('10')), "amount for order1 should be set to 10 ETH"
    assert(orders.getAmount(orderId2) == fix('10')), "amount for order2 should be set to 10 ETH"

    assert(orders.getPrice(orderId1) == fix('0.5')), "price for order1 should be set to 0.5 ETH"
    assert(orders.getPrice(orderId2) == fix('0.5')), "price for order2 should be set to 0.5 ETH"

    assert(orders.getOrderMaker(orderId1) == bytesToHexString(tester.a1)), "orderOwner for order1 should be tester.a1"
    assert(orders.getOrderMaker(orderId2) == bytesToHexString(tester.a2)), "orderOwner for order2 should be tester.a2"

    assert(orders.removeOrder(orderId1) == 1), "Remove order 1"
    assert(orders.removeOrder(orderId2) == 1), "Remove order 2"

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
        orders.fillOrder(orderId1, fix('11'), 0)
    with raises(TransactionFailed):
        orders.fillOrder(orderId1, 0, fix('1'))
    with raises(TransactionFailed):
        orders.fillOrder(orderId1, fix('10'), fix('1'))
    # fully fill
    assert(orders.fillOrder(orderId1, fix('10'), 0) == 1), "fillOrder wasn't executed successfully"
    # prove all
    assert(ordersFetcher.getOrder(orderId1) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order1 didn't return the expected data array"
    # test partial fill
    assert(orders.fillOrder(orderId2, 0, fix('3')) == 1), "fillOrder wasn't executed successfully"
    # confirm partial fill
    assert(ordersFetcher.getOrder(orderId2) == [fix('4'), fix('0.5'), bytesToHexString(tester.a2), fix('2'), 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order2 didn't return the expected data array"
    # fill rest of order2
    assert(orders.fillOrder(orderId2, 0, fix('2')) == 1), "fillOrder wasn't executed successfully"
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
    assert(orders.removeOrder(orderId3) == 1), "removeOrder wasn't executed successfully"
    assert(ordersFetcher.getOrder(orderId3) == [0, 0, longToHexString(0), 0, 0, longTo32Bytes(0), longTo32Bytes(0), 0]), "getOrder for order3 should return an 0'd out array as it has been removed"
    assert(orders.removeOrder(orderId1) == 1), "Remove order 1"
    assert(orders.removeOrder(orderId2) == 1), "Remove order 2"
