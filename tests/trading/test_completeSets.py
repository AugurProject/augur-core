#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import bytesToHexString, fix, AssertLog
from constants import YES, NO

def test_publicBuyCompleteSets(contractsFixture, universe, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    orders = contractsFixture.contracts['Orders']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()
    assert universe.getOpenInterestInAttoEth() == 0

    cost = 10 * market.getNumTicks()
    completeSetsPurchasedLog = {
        "universe": universe.address,
        "market": market.address,
        "account": bytesToHexString(tester.a1),
        "numCompleteSets": 10
    }
    with AssertLog(contractsFixture, "CompleteSetsPurchased", completeSetsPurchasedLog):
        assert completeSets.publicBuyCompleteSets(market.address, 10, sender=tester.k1, value=cost)

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

    assert not cash.balanceOf(tester.a0)
    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market.address)
    assert not yesShareToken.totalSupply()
    assert not noShareToken.totalSupply()

    cost = 10 * market.getNumTicks()
    assert universe.getOpenInterestInAttoEth() == 0
    completeSets.publicBuyCompleteSets(market.address, 10, sender = tester.k1, value = cost)
    assert universe.getOpenInterestInAttoEth() == 10 * market.getNumTicks()
    initialTester1ETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    initialTester0ETH = contractsFixture.chain.head_state.get_balance(tester.a0)

    completeSetsSoldLog = {
        "universe": universe.address,
        "market": market.address,
        "account": bytesToHexString(tester.a1),
        "numCompleteSets": 9
    }
    with AssertLog(contractsFixture, "CompleteSetsSold", completeSetsSoldLog):
        result = completeSets.publicSellCompleteSets(market.address, 9, sender=tester.k1)

    assert universe.getOpenInterestInAttoEth() == 1 * market.getNumTicks()

    assert yesShareToken.balanceOf(tester.a1) == 1, "Should have 1 share of outcome yes"
    assert noShareToken.balanceOf(tester.a1) == 1, "Should have 1 share of outcome no"
    assert yesShareToken.totalSupply() == 1
    assert noShareToken.totalSupply() == 1
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == initialTester1ETH + 88200
    assert cash.balanceOf(market.address) == 10000
    assert cash.balanceOf(market.getMarketCreatorMailbox()) == 900
    assert cash.balanceOf(universe.getNextFeeWindow()) == 900

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

def test_maliciousMarket(contractsFixture, universe, cash, market):
    completeSets = contractsFixture.contracts['CompleteSets']
    orders = contractsFixture.contracts['Orders']

    maliciousMarket = contractsFixture.upload('solidity_test_helpers/MaliciousMarket.sol', 'maliciousMarket', constructorArgs=[market.address])

    with raises(TransactionFailed):
        completeSets.publicBuyCompleteSets(maliciousMarket.address, 10**18, sender = tester.k1, value=10**18)
