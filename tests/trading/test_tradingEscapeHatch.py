#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import fix, longTo32Bytes
from constants import LONG, YES, NO


def test_escapeHatch(contractsFixture):
    controller = contractsFixture.controller
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    makeOrder = contractsFixture.contracts['MakeOrder']
    takeOrder = contractsFixture.contracts['TakeOrder']
    trade = contractsFixture.contracts['Trade']
    tradingEscapeHatch = contractsFixture.contracts['TradingEscapeHatch']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    # make order with cash
    orderID = makeOrder.publicMakeOrder(contractsFixture.constants.ASK(), 1, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), 42, sender=tester.k1, value=fix('100'))
    assert orderID

    # take order with cash using on-chain matcher
    assert trade.publicTakeBestOrder(LONG, market.address, YES, 1, fix('0.6'), sender=tester.k2, value=fix('100')) == 0

    # assert starting values
    assert cash.balanceOf(tester.a1) == fix('100') - fix('1', '0.4')
    assert cash.balanceOf(tester.a2) == fix('100') - fix('1', '0.6')
    assert cash.balanceOf(market.address) == fix('1')
    assert noShareToken.balanceOf(tester.a1) == 1
    assert yesShareToken.balanceOf(tester.a2) == 1
    with raises(TransactionFailed):
        tradingEscapeHatch.claimSharesInUpdate(market.address)

    # emergency stop and then have everyone liquidate their position
    controller.emergencyStop()
    assert tradingEscapeHatch.claimSharesInUpdate(market.address, sender = tester.k1)
    assert tradingEscapeHatch.claimSharesInUpdate(market.address, sender = tester.k2)

    # assert final values (should be a zero sum game)
    assert cash.balanceOf(tester.a1) == fix('100')
    assert cash.balanceOf(tester.a2) == fix('100')
    assert cash.balanceOf(market.address) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
