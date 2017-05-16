#!/usr/bin/env python

from ContractsFixture import ContractsFixture
from datetime import timedelta
from ethereum import tester
from ethereum.tester import TransactionFailed
from iocapture import capture
from pytest import raises
from utils import parseCapturedLogs, bytesToLong, fix

YES = 1
NO = 0

def test_publicBuyCompleteSets():
    fixture = ContractsFixture()
    completeSets = fixture.initializeCompleteSets()
    orders = fixture.initializeOrders()
    branch = fixture.createBranch(3, 5)
    cash = fixture.getSeededCash()
    market = fixture.createReasonableBinaryMarket(branch, cash)
    yesShareToken = fixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fixture.applySignature('shareToken', market.getShareToken(NO))

    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()

    cash.publicDepositEther(value = fix(10000), sender = tester.k1)
    cash.approve(completeSets.address, fix(10000), sender=tester.k1)
    with capture() as captured:
        assert completeSets.publicBuyCompleteSets(market.address, fix(10), sender=tester.k1)
        logs = parseCapturedLogs(captured.stdout)[-1]

    assert logs["_event_type"] == "CompleteSets", "Should emit a CompleteSets event"
    assert logs["sender"] == bytesToLong(tester.a1), "Logged sender should match input"
    assert logs["type"] == 1, "Logged type should be 1 (buy)"
    assert logs["fxpAmount"] == fix(10), "Logged fxpAmount should match input"
    assert logs["timestamp"] == fixture.state.block.timestamp, "Logged timestamp should match input"
    assert logs["numOutcomes"] == market.getNumberOfOutcomes(), "Logged numOutcomes should match event's number of outcomes"
    assert logs["marketCreatorFee"] == 0, "Market creator fees should be 0"
    assert logs["reportingFee"] == 0, "Reporting fees should be 0"
    assert logs["market"] == market.address, "Logged market should match input"
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

    assert not cash.balanceOf(tester.a0)
    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()

    cash.publicDepositEther(value = fix(10000), sender = tester.k1)
    cash.approve(completeSets.address, fix(10000), sender = tester.k1)
    completeSets.publicBuyCompleteSets(market.address, fix(10), sender = tester.k1)
    with capture() as captured:
        result = completeSets.publicSellCompleteSets(market.address, fix(9), sender=tester.k1)
        logs = parseCapturedLogs(captured.stdout)[-1]

    assert logs["_event_type"] == "CompleteSets", "Should emit a CompleteSets event"
    assert logs["sender"] == bytesToLong(tester.a1), "Logged sender should match input"
    assert logs["type"] == 2, "Logged type should be 2 (sell)"
    assert logs["fxpAmount"] == fix(9), "Logged fxpAmount should match input"
    assert logs["timestamp"] == fixture.state.block.timestamp, "Logged timestamp should match input"
    assert logs["numOutcomes"] == market.getNumberOfOutcomes(), "Logged numOutcomes should match event's number of outcomes"
    assert logs["marketCreatorFee"] == fix(0.09), "Market creator fees should be 0.09"
    assert logs["reportingFee"] == fix(0.0009), "Reporting fees should be 0.0009"
    assert logs["market"] == market.address, "Logged market should match input"
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
