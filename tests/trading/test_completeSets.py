#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import bytesToHexString, fix, captureFilteredLogs
from constants import YES, NO

def test_publicBuyCompleteSets(contractsFixture, universe, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    orders = contractsFixture.contracts['Orders']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    logs = []

    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()
    assert universe.getOpenInterestInAttoEth() == 0

    cost = 10 * market.getNumTicks()
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    assert completeSets.publicBuyCompleteSets(market.address, 10, sender=tester.k1, value=cost)

    assert logs == [
        {
            "_event_type": "BuyCompleteSets",
            "sender": bytesToHexString(tester.a1),
            "amount": 10L,
            "numOutcomes": 2L,
            "market": market.address
        },
    ]
    assert yesShareToken.balanceOf(tester.a1) == 10, "Should have 10 shares of outcome 1"
    assert noShareToken.balanceOf(tester.a1) == 10, "Should have 10 shares of outcome 2"
    assert cash.balanceOf(tester.a1) == 0, "Sender's cash balance should be 0"
    assert cash.balanceOf(market.address) == cost, "Increase in market's cash should equal the cost to purchase the complete set"
    assert yesShareToken.totalSupply() == 10, "Increase in yes shares purchased for this market should be 10"
    assert noShareToken.totalSupply() == 10, "Increase in yes shares purchased for this market should be 10"
    assert universe.getOpenInterestInAttoEth() == cost, "Open interest in the universe increases by the cost in ETH of the sets purchased"

def test_publicBuyCompleteSets_failure(contractsFixture, universe, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    orders = contractsFixture.contracts['Orders']

    amount = 10
    cost = 10 * market.getNumTicks()

    # Permissions exceptions
    with raises(TransactionFailed):
        completeSets.buyCompleteSets(tester.a1, market.address, amount, sender=tester.k1, value=cost)

    # buyCompleteSets exceptions
    with raises(TransactionFailed):
        completeSets.publicBuyCompleteSets(tester.a1, amount, sender=tester.k1, value=cost)

def test_publicSellCompleteSets(contractsFixture, universe, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    orders = contractsFixture.contracts['Orders']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    cash.transfer(0, cash.balanceOf(tester.a9), sender = tester.k9)
    logs = []

    assert not cash.balanceOf(tester.a0)
    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()

    cost = 10 * market.getNumTicks()
    assert universe.getOpenInterestInAttoEth() == 0
    completeSets.publicBuyCompleteSets(market.address, 10, sender = tester.k1, value = cost)
    assert universe.getOpenInterestInAttoEth() == 10 * market.getNumTicks()
    captureFilteredLogs(contractsFixture.chain.head_state, orders, logs)
    initialTester1ETH = contractsFixture.contracts['Utils'].getETHBalance(tester.a1)
    initialTester0ETH = contractsFixture.contracts['Utils'].getETHBalance(tester.a0)
    result = completeSets.publicSellCompleteSets(market.address, 9, sender=tester.k1)
    assert universe.getOpenInterestInAttoEth() == 1 * market.getNumTicks()

    assert logs == [
        {
            "_event_type": "SellCompleteSets",
            "sender": bytesToHexString(tester.a1),
            "reportingFee": fix('0.0009'),
            "amount": 9,
            "creatorFee": fix('0.09'),
            "numOutcomes": 2,
            "market": market.address
        },
    ]
    assert yesShareToken.balanceOf(tester.a1) == 1, "Should have 1 share of outcome yes"
    assert noShareToken.balanceOf(tester.a1) == 1, "Should have 1 share of outcome no"
    assert yesShareToken.totalSupply() == 1
    assert noShareToken.totalSupply() == 1
    assert contractsFixture.contracts['Utils'].getETHBalance(tester.a1) == initialTester1ETH + fix('8.9091')
    assert cash.balanceOf(market.address) == fix('1')
    assert contractsFixture.contracts['Utils'].getETHBalance(tester.a0) == initialTester0ETH + fix('0.09')
    assert cash.balanceOf(market.getReportingWindow()) == fix('0.0009')

def test_publicSellCompleteSets_failure(contractsFixture, universe, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    orders = contractsFixture.contracts['Orders']

    cost = 10 * market.getNumTicks()
    completeSets.publicBuyCompleteSets(market.address, 10, sender = tester.k1, value = cost)

    # Permissions exceptions
    with raises(TransactionFailed):
        completeSets.sellCompleteSets(tester.a1, market.address, 10, sender=tester.k1)

    # sellCompleteSets exceptions
    with raises(TransactionFailed):
        completeSets.publicSellCompleteSets(market.address, 10 + 1, sender=tester.k1)
