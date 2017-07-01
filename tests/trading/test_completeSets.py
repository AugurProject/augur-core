#!/usr/bin/env python

from ContractsFixture import ContractsFixture
from datetime import timedelta
from ethereum import tester
from ethereum.tester import TransactionFailed
from iocapture import capture
from pytest import raises
from utils import parseCapturedLogs, bytesToHexString, longToHexString, bytesToLong, fix

YES = 1
NO = 0

BUY = 1
SELL = 2

def captureLog(contract, logs, message):
    translated = contract.translator.listen(message)
    if not translated: return
    logs.append(translated)

def test_publicBuyCompleteSets():
    fixture = ContractsFixture()
    completeSets = fixture.initializeCompleteSets()
    orders = fixture.initializeOrders()
    branch = fixture.createBranch(3, 5)
    cash = fixture.getSeededCash()
    market = fixture.createReasonableBinaryMarket(branch, cash)
    yesShareToken = fixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('shareToken', market.getShareToken(NO))
    logs = []

    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()

    cash.publicDepositEther(value = fix(10000), sender = tester.k1)
    cash.approve(completeSets.address, fix(10000), sender=tester.k1)
    fixture.state.block.log_listeners.append(lambda x: captureLog(orders, logs, x))
    assert completeSets.publicBuyCompleteSets(market.address, fix(10), sender=tester.k1)

    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": bytesToHexString(tester.a1),
            "reportingFee": 0,
            "type": BUY,
            "fxpAmount": fix(10),
            "marketCreatorFee": 0,
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
    ]
    assert yesShareToken.balanceOf(tester.a1) == fix(10), "Should have 10 shares of outcome 1"
    assert noShareToken.balanceOf(tester.a1) == fix(10), "Should have 10 shares of outcome 2"
    assert cash.balanceOf(tester.a1) == fix(9990), "Decrease in sender's cash should equal 10"
    assert cash.balanceOf(market.address) == fix(10), "Increase in market's cash should equal 10"
    assert yesShareToken.totalSupply() == fix(10), "Increase in yes shares purchased for this market should be 18"
    assert noShareToken.totalSupply() == fix(10), "Increase in yes shares purchased for this market should be 18"

def test_publicBuyCompleteSets_failure():
    fixture = ContractsFixture()
    completeSets = fixture.initializeCompleteSets()
    orders = fixture.initializeOrders()
    branch = fixture.createBranch(3, 5)
    cash = fixture.getSeededCash()
    market = fixture.createReasonableBinaryMarket(branch, cash)

    fxpAmount = fix(10)
    cash.publicDepositEther(value = fix(10000), sender = tester.k1)
    cash.approve(completeSets.address, fix(10000), sender=tester.k1)

    # Permissions exceptions
    with raises(TransactionFailed):
        completeSets.buyCompleteSets(tester.a1, market.address, fxpAmount, sender=tester.k1)

    # buyCompleteSets exceptions
    with raises(TransactionFailed):
        completeSets.publicBuyCompleteSets(market.address + 1, fxpAmount, sender=tester.k1)
    with raises(TransactionFailed):
        completeSets.publicBuyCompleteSets(market.address, fix(-10), sender=tester.k1)
    with raises(TransactionFailed):
        completeSets.publicBuyCompleteSets(market.address, 0, sender=tester.k1)
    assert cash.approve(completeSets.address, fxpAmount - 1, sender=tester.k1) == 1, "Approve completeSets contract to spend slightly less cash than needed"
    with raises(TransactionFailed):
        completeSets.publicBuyCompleteSets(market.address, fxpAmount, sender=tester.k1)

def test_publicSellCompleteSets():
    fixture = ContractsFixture()
    completeSets = fixture.initializeCompleteSets()
    orders = fixture.initializeOrders()
    branch = fixture.createBranch(3, 5)
    cash = fixture.getSeededCash()
    market = fixture.createReasonableBinaryMarket(branch, cash)
    yesShareToken = fixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('shareToken', market.getShareToken(NO))
    cash.transfer(0, 1)
    logs = []

    assert not cash.balanceOf(tester.a0)
    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()

    cash.publicDepositEther(value = fix(10000), sender = tester.k1)
    cash.approve(completeSets.address, fix(10000), sender = tester.k1)
    completeSets.publicBuyCompleteSets(market.address, fix(10), sender = tester.k1)
    fixture.state.block.log_listeners.append(lambda x: captureLog(orders, logs, x))
    result = completeSets.publicSellCompleteSets(market.address, fix(9), sender=tester.k1)

    assert logs == [
        {
            "_event_type": "CompleteSets",
            "sender": bytesToHexString(tester.a1),
            "reportingFee": fix(0.0009),
            "type": SELL,
            "fxpAmount": fix(9),
            "marketCreatorFee": fix(0.09),
            "numOutcomes": 2,
            "market": longToHexString(market.address)
        },
    ]
    assert yesShareToken.balanceOf(tester.a1) == fix(1), "Should have 1 share of outcome yes"
    assert noShareToken.balanceOf(tester.a1) == fix(1), "Should have 1 share of outcome no"
    assert yesShareToken.totalSupply() == fix(1)
    assert noShareToken.totalSupply() == fix(1)
    assert cash.balanceOf(tester.a1) == fix(9998.9091)
    assert cash.balanceOf(market.address) == fix(1)
    assert cash.balanceOf(tester.a0) == fix(0.09)
    assert cash.balanceOf(market.getReportingWindow()) == fix(0.0009)

def test_exceptions():
    fixture = ContractsFixture()
    completeSets = fixture.initializeCompleteSets()
    orders = fixture.initializeOrders()
    branch = fixture.createBranch(3, 5)
    cash = fixture.getSeededCash()
    market = fixture.createReasonableBinaryMarket(branch, cash)
    cash.publicDepositEther(value = fix(10000), sender = tester.k1)

    cash.publicDepositEther(value = fix(10000), sender = tester.k1)
    cash.approve(completeSets.address, fix(10000), sender = tester.k1)
    completeSets.publicBuyCompleteSets(market.address, fix(10), sender = tester.k1)

    # Permissions exceptions
    with raises(TransactionFailed):
        completeSets.sellCompleteSets(tester.a1, market.address, fix(10), sender=tester.k1)

    # sellCompleteSets exceptions
    fixture.state.mine(1)
    with raises(TransactionFailed):
        completeSets.publicSellCompleteSets(market.address, fix(-10), sender=tester.k1)
    with raises(TransactionFailed):
        completeSets.publicSellCompleteSets(market.address, 0, sender=tester.k1)
    with raises(TransactionFailed):
        completeSets.publicSellCompleteSets(market.address, fix(10) + 1, sender=tester.k1)
