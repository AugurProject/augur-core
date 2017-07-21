#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises
from utils import bytesToHexString, longToHexString, bytesToLong, fix, captureFilteredLogs

def test_market_sorting(contractsFixture):
    branch = contractsFixture.branch
    cash = contractsFixture.cash
    completeSets = contractsFixture.contracts['completeSets']

    market1 = contractsFixture.binaryMarket
    market2 = contractsFixture.createReasonableBinaryMarket(branch, cash)
    scalarMarket = contractsFixture.scalarMarket
    categoricalMarket = contractsFixture.categoricalMarket    

    assert branch.getNumMarkets() == 4

    AssertOrder(market1, categoricalMarket, scalarMarket, market2, branch=branch)

    assert cash.publicDepositEther(value = fix('10000'), sender = tester.k1)
    assert cash.approve(completeSets.address, fix('10000'), sender=tester.k1)

    # We buy 10 complete sets in the new binary market, causing it to move to the top of the list
    assert completeSets.publicBuyCompleteSets(market2.address, fix('10'), sender=tester.k1)
    AssertOrder(market2, market1, categoricalMarket, scalarMarket, branch=branch)

    # Buying 5 complete sets of the categorical market will move it ahead of market1 into second
    assert completeSets.publicBuyCompleteSets(categoricalMarket.address, fix('5'), sender=tester.k1)
    AssertOrder(market2, categoricalMarket, market1, scalarMarket, branch=branch)

    # Buying 3 complete sets of the first binary market will not change its order
    assert completeSets.publicBuyCompleteSets(market1.address, fix('3'), sender=tester.k1)
    AssertOrder(market2, categoricalMarket, market1, scalarMarket, branch=branch)

    # Selling 8 complete sets of the new binary market will move it into third place
    assert completeSets.publicSellCompleteSets(market2.address, fix('8'), sender=tester.k1)
    AssertOrder(categoricalMarket, market1, market2, scalarMarket, branch=branch)

def AssertOrder(*args, **kwargs):
    branch = kwargs["branch"]
    curMarket = branch.getMarketsHead()
    for market in args:
        assert curMarket == market.address
        curMarket = branch.tryGetPrevMarket(curMarket)