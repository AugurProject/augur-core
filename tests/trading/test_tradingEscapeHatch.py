#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import fix

BID = 1
ASK = 2

LONG = 1
SHORT = 2

NO = 0
YES = 1

def test_escapeHatch(contractsFixture):
    controller = contractsFixture.controller
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    trade = contractsFixture.contracts['trade']
    tradingEscapeHatch = contractsFixture.contracts['tradingEscapeHatch']
    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))

    # make order with cash
    assert cash.depositEther(value=fix('100'), sender=tester.k1) == 1, "depositEther to account 1 should succeed"
    assert cash.approve(makeOrder.address, fix('10'), sender=tester.k1) == 1, "Approve makeOrder contract to spend cash from account 1"
    orderID = makeOrder.publicMakeOrder(ASK, fix('1'), fix('0.6'), market.address, YES, 42, sender=tester.k1)
    assert orderID

    # take order with cash using on-chain matcher
    assert cash.depositEther(value=fix('100'), sender=tester.k2) == 1, "depositEther to account 1 should succeed"
    assert cash.approve(takeOrder.address, fix('10'), sender=tester.k2) == 1, "Approve takeOrder contract to spend cash from account 2"
    assert trade.publicTakeBestOrder(LONG, market.address, YES, fix('1'), fix('0.6'), sender=tester.k2) == 0

    # assert starting values
    assert cash.balanceOf(tester.a1) == fix('100') - fix('1', '0.4')
    assert cash.balanceOf(tester.a2) == fix('100') - fix('1', '0.6')
    assert cash.balanceOf(market.address) == fix('1')
    assert noShareToken.balanceOf(tester.a1) == fix('1')
    assert yesShareToken.balanceOf(tester.a2) == fix('1')
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
