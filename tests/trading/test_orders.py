#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import mark, raises
from utils import fix, bytesToHexString, longTo32Bytes, longToHexString
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

def test_walkOrderList_bids(contractsFixture, market):
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    outcomeID = 1
    order = {
        "orderID": longTo32Bytes(5),
        "type": BID,
        "fxpAmount": fix('1'),
        "price": 6000,
        "sender": tester.a0,
        "outcome": outcomeID,
        "moneyEscrowed": fix('6000'),
        "sharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": "0"
    }
    orderId5 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["moneyEscrowed"], order["sharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId5 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == orderId5)
    assert(worstOrderID == orderId5)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, 6000, bestOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, 5900, bestOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, 6100, bestOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.descendOrderList(BID, 5800, bestOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, 5950, bestOrderID) == [orderId5, longTo32Bytes(0)])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, 6000, worstOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, 5900, worstOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, 6100, worstOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.ascendOrderList(BID, 5800, worstOrderID) == [orderId5, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, 5950, bestOrderID) == [orderId5, longTo32Bytes(0)])
    order = {
        "orderID": longTo32Bytes(6),
        "type": BID,
        "fxpAmount": fix('1'),
        "price": 5900,
        "sender": tester.a0,
        "outcome": outcomeID,
        "moneyEscrowed": fix('5900'),
        "sharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": "0"
    }
    orderId6 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["moneyEscrowed"], order["sharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId6 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == orderId5)
    assert(worstOrderID == orderId6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, 6000, bestOrderID) == [orderId5, orderId6])
    assert(ordersFetcher.descendOrderList(BID, 5900, bestOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, 6100, bestOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.descendOrderList(BID, 5800, bestOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, 5950, bestOrderID) == [orderId5, orderId6])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, 6000, worstOrderID) == [orderId5, orderId6])
    assert(ordersFetcher.ascendOrderList(BID, 5900, worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, 6100, worstOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.ascendOrderList(BID, 5800, worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, 5950, bestOrderID) == [orderId5, orderId6])
    order = {
        "orderID": longTo32Bytes(7),
        "type": BID,
        "fxpAmount": fix('1'),
        "price": 5950,
        "sender": tester.a0,
        "outcome": outcomeID,
        "moneyEscrowed": fix('5950'),
        "sharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": "0"
    }
    orderId7 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["moneyEscrowed"], order["sharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId7 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(BID, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(BID, market.address, outcomeID)
    assert(bestOrderID == orderId5)
    assert(worstOrderID == orderId6)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(BID, 6000, bestOrderID) == [orderId5, orderId7])
    assert(ordersFetcher.descendOrderList(BID, 5900, bestOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(BID, 6100, bestOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.descendOrderList(BID, 5800, bestOrderID) == [orderId6, longTo32Bytes(0)])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(BID, 6000, worstOrderID) == [orderId5, orderId7])
    assert(ordersFetcher.ascendOrderList(BID, 5900, worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(BID, 6100, worstOrderID) == [longTo32Bytes(0), orderId5])
    assert(ordersFetcher.ascendOrderList(BID, 5800, worstOrderID) == [orderId6, longTo32Bytes(0)])
    assert(orders.removeOrder(orderId5) == 1), "Remove order 5"
    assert(orders.removeOrder(orderId6) == 1), "Remove order 6"
    assert(orders.removeOrder(orderId7) == 1), "Remove order 7"

def test_walkOrderList_asks(contractsFixture, market):
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']
    outcomeID = 1
    order = {
        "orderID": longTo32Bytes(8),
        "type": ASK,
        "fxpAmount": fix('1'),
        "price": 6000,
        "sender": tester.a0,
        "outcome": outcomeID,
        "moneyEscrowed": fix('6000'),
        "sharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": "0"
    }
    orderId8 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["moneyEscrowed"], order["sharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId8 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == orderId8)
    assert(worstOrderID == orderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, 6000, bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, 5900, bestOrderID) == [longTo32Bytes(0), orderId8])
    assert(ordersFetcher.descendOrderList(ASK, 6100, bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, 5800, bestOrderID) == [longTo32Bytes(0), orderId8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, 6000, worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, 5900, worstOrderID) == [longTo32Bytes(0), orderId8])
    assert(ordersFetcher.ascendOrderList(ASK, 6100, worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, 5800, worstOrderID) == [longTo32Bytes(0), orderId8])
    order = {
        "orderID": longTo32Bytes(9),
        "type": ASK,
        "fxpAmount": fix('1'),
        "price": 5900,
        "sender": tester.a0,
        "outcome": outcomeID,
        "moneyEscrowed": fix('5900'),
        "sharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": "0"
    }
    orderId9 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["moneyEscrowed"], order["sharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId9 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == orderId9)
    assert(worstOrderID == orderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, 6000, bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, 5900, bestOrderID) == [orderId9, orderId8])
    assert(ordersFetcher.descendOrderList(ASK, 6100, bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, 5800, bestOrderID) == [longTo32Bytes(0), orderId9])
    assert(ordersFetcher.descendOrderList(ASK, 5950, bestOrderID) == [orderId9, orderId8])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, 6000, worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, 5900, worstOrderID) == [orderId9, orderId8])
    assert(ordersFetcher.ascendOrderList(ASK, 6100, worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, 5800, worstOrderID) == [longTo32Bytes(0), orderId9])
    assert(ordersFetcher.ascendOrderList(ASK, 5950, bestOrderID) == [orderId9, orderId8])
    order = {
        "orderID": longTo32Bytes(10),
        "type": ASK,
        "fxpAmount": fix('1'),
        "price": 5950,
        "sender": tester.a0,
        "outcome": outcomeID,
        "moneyEscrowed": fix('5950'),
        "sharesEscrowed": 0,
        "betterOrderID": longTo32Bytes(0),
        "worseOrderID": longTo32Bytes(0),
        "tradeGroupID": "0"
    }
    orderId10 = orders.saveOrder(order["type"], market.address, order["fxpAmount"], order["price"], order["sender"], order["outcome"], order["moneyEscrowed"], order["sharesEscrowed"], order["betterOrderID"], order["worseOrderID"], order["tradeGroupID"])
    assert(orderId10 != bytearray(32)), "Save order"
    bestOrderID = orders.getBestOrderId(ASK, market.address, outcomeID)
    worstOrderID = orders.getWorstOrderId(ASK, market.address, outcomeID)
    assert(bestOrderID == orderId9)
    assert(worstOrderID == orderId8)
    # walk down order list starting from bestOrderID
    assert(ordersFetcher.descendOrderList(ASK, 6000, bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, 5900, bestOrderID) == [orderId9, orderId10])
    assert(ordersFetcher.descendOrderList(ASK, 6100, bestOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.descendOrderList(ASK, 5800, bestOrderID) == [longTo32Bytes(0), orderId9])
    # walk up order list starting from worstOrderID
    assert(ordersFetcher.ascendOrderList(ASK, 6000, worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, 5900, worstOrderID) == [orderId9, orderId10])
    assert(ordersFetcher.ascendOrderList(ASK, 6100, worstOrderID) == [orderId8, longTo32Bytes(0)])
    assert(ordersFetcher.ascendOrderList(ASK, 5800, worstOrderID) == [longTo32Bytes(0), orderId9])
    assert(orders.removeOrder(orderId8) == 1), "Remove order 8"
    assert(orders.removeOrder(orderId9) == 1), "Remove order 9"
    assert(orders.removeOrder(orderId10) == 1), "Remove order 10"

@mark.parametrize('where, orderType, hints', [
    ('best', BID, True),
    ('middle', BID, True),
    ('worst', BID, True),
    ('best', BID, False),
    ('middle', BID, False),
    ('worst', BID, False),
    ('best', ASK, True),
    ('middle', ASK, True),
    ('worst', ASK, True),
    ('best', ASK, False),
    ('middle', ASK, False),
    ('worst', ASK, False),
])
def test_orderBidSorting(where, orderType, hints, contractsFixture, market):
    orders = contractsFixture.contracts['Orders']
    ordersFetcher = contractsFixture.contracts['OrdersFetcher']

    # setup pre-existing orders
    worstPrice = 6000 if orderType == BID else 6600
    bestPrice = 6600 if orderType == BID else 6000
    worstOrderId = orders.saveOrder(orderType, market.address, fix('1'), worstPrice, tester.a0, YES, worstPrice, 0, longTo32Bytes(0), longTo32Bytes(0), "0")
    bestOrderId = orders.saveOrder(orderType, market.address, fix('1'), bestPrice, tester.a0, YES, bestPrice, 0, longTo32Bytes(0), longTo32Bytes(0), "0")

    # validate that our setup went smoothly
    assert orders.getBestOrderId(orderType, market.address, YES) == bestOrderId
    assert orders.getWorstOrderId(orderType, market.address, YES) == worstOrderId
    assert orders.getWorseOrderId(bestOrderId) == worstOrderId
    assert orders.getWorseOrderId(worstOrderId) == longTo32Bytes(0)
    assert orders.getBetterOrderId(worstOrderId) == bestOrderId
    assert orders.getBetterOrderId(bestOrderId) == longTo32Bytes(0)

    # insert our new order
    if where == 'best':
        orderPrice = 6700 if orderType == BID else 5900
        betterOrderId = longTo32Bytes(0)
        worseOrderId = bestOrderId if hints else longTo32Bytes(0)
    if where == 'middle':
        orderPrice = 6300
        betterOrderId = bestOrderId if hints else longTo32Bytes(0)
        worseOrderId = worstOrderId if hints else longTo32Bytes(0)
    if where == 'worst':
        orderPrice = 5900 if orderType == BID else 6700
        betterOrderId = worstOrderId if hints else longTo32Bytes(0)
        worseOrderId = longTo32Bytes(0)
    insertedOrder = orders.saveOrder(orderType, market.address, fix('1'), orderPrice, tester.a0, YES, orderPrice, 0, betterOrderId, worseOrderId, "0")

    # validate the new order was inserted correctly
    assert orders.getBetterOrderId(insertedOrder) == longTo32Bytes(0) if where == 'best' else bestOrderId
    assert orders.getWorseOrderId(insertedOrder) == longTo32Bytes(0) if where == 'worst' else worstOrderId
    assert orders.getBestOrderId(orderType, market.address, YES) == insertedOrder if where == 'best' else bestOrderId
    assert orders.getWorstOrderId(orderType, market.address, YES) == insertedOrder if where == 'worst' else worstOrderId

def test_saveOrder(contractsFixture, market):
    orders = contractsFixture.contracts['Orders']

    orderId1 = orders.saveOrder(BID, market.address, fix(10), 5000, tester.a1, NO, 0, fix(10), longTo32Bytes(0), longTo32Bytes(0), "1")
    assert(orderId1 != bytearray(32)), "saveOrder wasn't executed successfully"
    orderId2 = orders.saveOrder(ASK, market.address, fix(10), 5000, tester.a2, NO, fix('10', '5000'), 0, longTo32Bytes(0), longTo32Bytes(0), "1")
    assert(orderId2 != bytearray(32)), "saveOrder wasn't executed successfully"

    assert(orders.getAmount(orderId1) == fix(10)), "amount for order1 should be set to 10"
    assert(orders.getAmount(orderId2) == fix(10)), "amount for order2 should be set to 10"

    assert(orders.getPrice(orderId1) == 5000), "price for order1 should be set to 5000 wei"
    assert(orders.getPrice(orderId2) == 5000), "price for order2 should be set to 5000 wei"

    assert(orders.getOrderCreator(orderId1) == bytesToHexString(tester.a1)), "orderOwner for order1 should be tester.a1"
    assert(orders.getOrderCreator(orderId2) == bytesToHexString(tester.a2)), "orderOwner for order2 should be tester.a2"

    assert orders.getOrderMoneyEscrowed(orderId1) == 0, "money escrowed should be 0"
    assert orders.getOrderMoneyEscrowed(orderId2) ==  fix('10', '5000'), "money escrowed should be 50000 ETH"

    assert orders.getOrderSharesEscrowed(orderId1) == fix(10), "shares escrowed should be fix(10)"
    assert orders.getOrderSharesEscrowed(orderId2) == 0, "shares escrowed should be 0"

    assert orders.getBetterOrderId(orderId1) == longTo32Bytes(0), "better order id should be 0"
    assert orders.getBetterOrderId(orderId2) == longTo32Bytes(0), "better order id should be 0"

    assert orders.getWorseOrderId(orderId1) == longTo32Bytes(0), "worse order id should be 0"
    assert orders.getWorseOrderId(orderId2) == longTo32Bytes(0), "worse order id should be 0"

    assert(orders.removeOrder(orderId1) == 1), "Remove order 1"
    assert(orders.removeOrder(orderId2) == 1), "Remove order 2"

def test_recordFillOrder(contractsFixture, market):
    orders = contractsFixture.contracts['Orders']

    orderId1 = orders.saveOrder(BID, market.address, fix(10), 5000, tester.a1, NO, 0, fix(10), longTo32Bytes(0), longTo32Bytes(0), "1")
    assert(orderId1 != bytearray(32)), "saveOrder wasn't executed successfully"
    orderId2 = orders.saveOrder(BID, market.address, fix(10), 5000, tester.a2, NO, fix('10', '5000'), 0, longTo32Bytes(0), longTo32Bytes(0), "1")
    assert(orderId2 != bytearray(32)), "saveOrder wasn't executed successfully"

    # orderID, fill, money, shares
    with raises(TransactionFailed):
        orders.recordFillOrder(orderId1, fix(11), "0")
    with raises(TransactionFailed):
        orders.recordFillOrder(orderId1, 0, fix('1'))
    with raises(TransactionFailed):
        orders.recordFillOrder(orderId1, fix(10), fix('1'))
    # fully fill
    assert(orders.recordFillOrder(orderId1, fix(10), 0) == 1), "fillOrder wasn't executed successfully"
    # prove all
    assert orders.getAmount(orderId1) == 0
    assert orders.getPrice(orderId1) == 0
    assert orders.getOrderCreator(orderId1) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderId1) == 0
    assert orders.getOrderSharesEscrowed(orderId1) == 0
    assert orders.getBetterOrderId(orderId1) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderId1) == longTo32Bytes(0)
    # test partial fill
    assert(orders.recordFillOrder(orderId2, 0, fix('3', '5000')) == 1), "fillOrder wasn't executed successfully"
    # confirm partial fill
    assert orders.getAmount(orderId2) == fix('7')
    assert orders.getPrice(orderId2) == 5000
    assert orders.getOrderCreator(orderId2) == bytesToHexString(tester.a2)
    assert orders.getOrderMoneyEscrowed(orderId2) == fix('7', '5000')
    assert orders.getOrderSharesEscrowed(orderId2) == 0
    assert orders.getBetterOrderId(orderId2) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderId2) == longTo32Bytes(0)
    # fill rest of order2
    assert(orders.recordFillOrder(orderId2, 0, fix('7', '5000')) == 1), "fillOrder wasn't executed successfully"
    assert orders.getAmount(orderId2) == 0
    assert orders.getPrice(orderId2) == 0
    assert orders.getOrderCreator(orderId2) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderId2) == 0
    assert orders.getOrderSharesEscrowed(orderId2) == 0
    assert orders.getBetterOrderId(orderId2) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderId2) == longTo32Bytes(0)

def test_removeOrder(contractsFixture, market):
    orders = contractsFixture.contracts['Orders']

    orderId1 = orders.saveOrder(BID, market.address, fix('10'), 5000, tester.a1, NO, 0, fix('10'), longTo32Bytes(0), longTo32Bytes(0), "1")
    assert(orderId1 != bytearray(32)), "saveOrder wasn't executed successfully"
    orderId2 = orders.saveOrder(BID, market.address, fix('10'), 5000, tester.a2, NO, fix('10', '5000'), 0, longTo32Bytes(0), longTo32Bytes(0), "1")
    assert(orderId2 != bytearray(32)), "saveOrder wasn't executed successfully"
    orderId3 = orders.saveOrder(BID, market.address, fix('10'), 5000, tester.a1, YES, 0, fix('10'), longTo32Bytes(0), longTo32Bytes(0), "1")
    assert(orderId3 != bytearray(32)), "saveOrder wasn't executed successfully"
    assert orders.getAmount(orderId3) == fix('10')
    assert orders.getPrice(orderId3) == 5000
    assert orders.getOrderCreator(orderId3) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(orderId3) == 0
    assert orders.getOrderSharesEscrowed(orderId3) == fix('10')
    assert orders.getBetterOrderId(orderId3) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderId3) == longTo32Bytes(0)
    assert(orders.removeOrder(orderId3) == 1), "removeOrder wasn't executed successfully"
    assert orders.getAmount(orderId3) == 0
    assert orders.getPrice(orderId3) == 0
    assert orders.getOrderCreator(orderId3) == longToHexString(0)
    assert orders.getOrderMoneyEscrowed(orderId3) == 0
    assert orders.getOrderSharesEscrowed(orderId3) == 0
    assert orders.getBetterOrderId(orderId3) == longTo32Bytes(0)
    assert orders.getWorseOrderId(orderId3) == longTo32Bytes(0)
    assert(orders.removeOrder(orderId1) == 1), "Remove order 1"
    assert(orders.removeOrder(orderId2) == 1), "Remove order 2"
