#!/usr/bin/env python

from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import bytesToHexString, longToHexString, bytesToLong, fix, captureFilteredLogs

YES = 1
NO = 0

BUY = 1
SELL = 2

def test_publicBuyCompleteSets(fundedRepFixture):
    branch = fundedRepFixture.branch
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket
    completeSets = fundedRepFixture.contracts['completeSets']
    orders = fundedRepFixture.contracts['Orders']
    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))
    logs = []

    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()

    cash.depositEther(value = fix('10000'), sender = tester.k1)
    cash.approve(completeSets.address, fix('10000'), sender=tester.k1)
    captureFilteredLogs(fundedRepFixture.chain.head_state, orders, logs)
    assert completeSets.publicBuyCompleteSets(market.address, fix('10'), sender=tester.k1)

    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": bytesToHexString(tester.a1),
            "reportingFee": 0L,
            "orderType": BUY,
            "fxpAmount": fix('10'),
            "marketCreatorFee": 0L,
            "numOutcomes": 2L,
            "market": market.address
        },
    ]
    assert yesShareToken.balanceOf(tester.a1) == fix('10'), "Should have 10 shares of outcome 1"
    assert noShareToken.balanceOf(tester.a1) == fix('10'), "Should have 10 shares of outcome 2"
    assert cash.balanceOf(tester.a1) == fix('9990'), "Decrease in sender's cash should equal 10"
    assert cash.balanceOf(market.address) == fix('10'), "Increase in market's cash should equal 10"
    assert yesShareToken.totalSupply() == fix('10'), "Increase in yes shares purchased for this market should be 18"
    assert noShareToken.totalSupply() == fix('10'), "Increase in yes shares purchased for this market should be 18"

def test_publicBuyCompleteSets_failure(fundedRepFixture):
    branch = fundedRepFixture.branch
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket
    completeSets = fundedRepFixture.contracts['completeSets']
    orders = fundedRepFixture.contracts['Orders']

    fxpAmount = fix('10')
    cash.depositEther(value = fix('10000'), sender = tester.k1)
    cash.approve(completeSets.address, fix('10000'), sender=tester.k1)

    # Permissions exceptions
    with raises(TransactionFailed):
        completeSets.buyCompleteSets(tester.a1, market.address, fxpAmount, sender=tester.k1)

    # buyCompleteSets exceptions
    with raises(TransactionFailed):
        completeSets.publicBuyCompleteSets(tester.a1, fxpAmount, sender=tester.k1)
    with raises(TransactionFailed):
        completeSets.publicBuyCompleteSets(market.address, 0, sender=tester.k1)
    assert cash.approve(completeSets.address, fxpAmount - 1, sender=tester.k1) == 1, "Approve completeSets contract to spend slightly less cash than needed"
    with raises(TransactionFailed):
        completeSets.publicBuyCompleteSets(market.address, fxpAmount, sender=tester.k1)

def test_publicSellCompleteSets(fundedRepFixture):
    branch = fundedRepFixture.branch
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket
    completeSets = fundedRepFixture.contracts['completeSets']
    orders = fundedRepFixture.contracts['Orders']
    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))
    cash.transfer(0, cash.balanceOf(tester.a9), sender = tester.k9)
    logs = []

    assert not cash.balanceOf(tester.a0)
    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()

    cash.depositEther(value = fix('10000'), sender = tester.k1)
    cash.approve(completeSets.address, fix('10000'), sender = tester.k1)
    completeSets.publicBuyCompleteSets(market.address, fix('10'), sender = tester.k1)
    captureFilteredLogs(fundedRepFixture.chain.head_state, orders, logs)
    result = completeSets.publicSellCompleteSets(market.address, fix('9'), sender=tester.k1)

    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": bytesToHexString(tester.a1),
            "reportingFee": fix('0.0009'),
            "orderType": SELL,
            "fxpAmount": fix('9'),
            "marketCreatorFee": fix('0.09'),
            "numOutcomes": 2,
            "market": market.address
        },
    ]
    assert yesShareToken.balanceOf(tester.a1) == fix('1'), "Should have 1 share of outcome yes"
    assert noShareToken.balanceOf(tester.a1) == fix('1'), "Should have 1 share of outcome no"
    assert yesShareToken.totalSupply() == fix('1')
    assert noShareToken.totalSupply() == fix('1')
    assert cash.balanceOf(tester.a1) == fix('9998.9091')
    assert cash.balanceOf(market.address) == fix('1')
    assert cash.balanceOf(tester.a0) == fix('0.09')
    assert cash.balanceOf(market.getReportingWindow()) == fix('0.0009')

def test_exceptions(fundedRepFixture):
    branch = fundedRepFixture.branch
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket
    completeSets = fundedRepFixture.contracts['completeSets']
    orders = fundedRepFixture.contracts['Orders']
    cash.depositEther(value = fix('10000'), sender = tester.k1)

    cash.depositEther(value = fix('10000'), sender = tester.k1)
    cash.approve(completeSets.address, fix('10000'), sender = tester.k1)
    completeSets.publicBuyCompleteSets(market.address, fix('10'), sender = tester.k1)

    # Permissions exceptions
    with raises(TransactionFailed):
        completeSets.sellCompleteSets(tester.a1, market.address, fix('10'), sender=tester.k1)

    # sellCompleteSets exceptions
    with raises(TransactionFailed):
        completeSets.publicSellCompleteSets(market.address, 0, sender=tester.k1)
    with raises(TransactionFailed):
        completeSets.publicSellCompleteSets(market.address, fix('10') + 1, sender=tester.k1)
