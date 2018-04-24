#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import fix, longTo32Bytes
from constants import LONG, YES, NO


def test_escapeHatch(contractsFixture, cash, market):
    controller = contractsFixture.contracts['Controller']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    trade = contractsFixture.contracts['Trade']
    tradingEscapeHatch = contractsFixture.contracts['TradingEscapeHatch']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    initialTester1ETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialTester2ETH = contractsFixture.chain.head_state.get_balance(tester.a2)

    # create order with cash
    orderID = createOrder.publicCreateOrder(contractsFixture.contracts['Constants'].ASK(), fix(1), 6000, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1, value=fix('1', '4000'))
    assert orderID

    # fill order with cash using on-chain matcher
    assert trade.publicFillBestOrder(LONG, market.address, YES, fix(1), 6000, sender=tester.k2, value=fix('1', '6000')) == 0

    # assert starting values
    assert cash.balanceOf(market.address) == fix('10000')
    assert noShareToken.balanceOf(tester.a1) == fix(1)
    assert yesShareToken.balanceOf(tester.a2) == fix(1)
    with raises(TransactionFailed):
        tradingEscapeHatch.claimSharesInUpdate(market.address)

    # emergency stop and then have everyone liquidate their position
    controller.emergencyStop()

    curTester1Balance = contractsFixture.chain.head_state.get_balance(tester.a1)
    assert tradingEscapeHatch.getFrozenShareValueInMarket(market.address, sender = tester.k1) == initialTester1ETH - curTester1Balance

    assert tradingEscapeHatch.claimSharesInUpdate(market.address, sender = tester.k1)
    assert tradingEscapeHatch.claimSharesInUpdate(market.address, sender = tester.k2)

    # assert final values (should be a zero sum game)
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialTester1ETH
    assert contractsFixture.chain.head_state.get_balance(tester.a2) == initialTester2ETH
    assert cash.balanceOf(market.address) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
