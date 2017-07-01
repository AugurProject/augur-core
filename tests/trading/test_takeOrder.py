#!/usr/bin/env python

from ethereum import tester
from utils import fix, longToHexString, bytesToHexString

BID = 1
ASK = 2

NO = 0
YES = 1

BUY = 1
SELL = 2

def captureLog(contract, logs, message):
    translated = contract.translator.listen(message)
    if not translated: return
    logs.append(translated)

def test_publicTakeOrder_bid(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix(1.2*0.6), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix(1.2*0.6), sender = tester.k1)
    orderId = makeOrder.publicMakeOrder(BID, fix(1.2), fix(0.6), market.address, YES, 0, 0, 42, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix(1.2*0.4), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix(1.2*0.4), sender = tester.k2)
    contractsFixture.state.block.log_listeners.append(lambda x: captureLog(orders, logs, x))
    fillOrderId = takeOrder.publicTakeOrder(orderId, BID, market.address, YES, fix(1.2), sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix(1.2),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": BID,
            "orderId": longToHexString(orderId),
            "price": fix(0.6),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix(1.2*0.6),
            "takerShares": 0,
            "takerTokens": fix(1.2*0.4),
        },
    ]
    assert orders.getOrder(orderId, BID, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert fillOrderId == 0

def test_publicTakeOrder_ask(contractsFixture):
    cash = contractsFixture.cash
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    orders = contractsFixture.contracts['orders']
    market = contractsFixture.binaryMarket
    logs = []

    # create order
    assert cash.publicDepositEther(value=fix(1.2*0.4), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix(1.2*0.4), sender = tester.k1)
    orderId = makeOrder.publicMakeOrder(ASK, fix(1.2), fix(0.6), market.address, YES, 0, 0, 42, sender = tester.k1)

    # take best order
    assert cash.publicDepositEther(value=fix(1.2*0.6), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix(1.2*0.6), sender = tester.k2)
    contractsFixture.state.block.log_listeners.append(lambda x: captureLog(orders, logs, x))
    fillOrderId = takeOrder.publicTakeOrder(orderId, ASK, market.address, YES, fix(1.2), sender = tester.k2)

    # assert
    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": longToHexString(takeOrder.address),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix(1.2),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
        {
            "_event_type": "TakeOrder",
            "market": longToHexString(market.address),
            "outcome": YES,
            "type": ASK,
            "orderId": longToHexString(orderId),
            "price": fix(0.6),
            "maker": bytesToHexString(tester.a1),
            "taker": bytesToHexString(tester.a2),
            "makerShares": 0,
            "makerTokens": fix(1.2*0.4),
            "takerShares": 0,
            "takerTokens": fix(1.2*0.6),
        },
    ]
    assert orders.getOrder(orderId, BID, market.address, YES) == [0, 0, 0, 0, 0, 0, 0, 0]
    assert fillOrderId == 0
