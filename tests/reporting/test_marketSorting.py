#!/usr/bin/env python

from ethereum import tester
from ethereum.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises
from utils import bytesToHexString, longToHexString, bytesToLong, fix, captureFilteredLogs


YES = 1
NO = 0

BUY = 1
SELL = 2

def test_market_creation(contractsFixture):
    branch = contractsFixture.branch
    cash = contractsFixture.cash
    completeSets = contractsFixture.contracts['completeSets']
    orders = contractsFixture.contracts['orders']

    market1 = contractsFixture.binaryMarket
    scalarMarket = contractsFixture.scalarMarket
    categoricalMarket = contractsFixture.categoricalMarket

    yesShareToken1 = contractsFixture.applySignature('shareToken', market1.getShareToken(YES))
    noShareToken1 = contractsFixture.applySignature('shareToken', market1.getShareToken(NO))

    reportingWindow = contractsFixture.applySignature('reportingWindow', market1.getReportingWindow())

    market2 = contractsFixture.createReasonableBinaryMarket(branch, cash)
    yesShareToken2 = contractsFixture.applySignature('shareToken', market2.getShareToken(YES))
    noShareToken2 = contractsFixture.applySignature('shareToken', market2.getShareToken(NO))

    assert reportingWindow.getNumMarkets() == 4

    AssertOrder(market1, categoricalMarket, scalarMarket, market2, reportingWindow=reportingWindow)

    assert not cash.balanceOf(tester.a1)
    assert not cash.balanceOf(market2.address)
    assert not yesShareToken2.totalSupply()
    assert not noShareToken2.totalSupply()

    cash.publicDepositEther(value = fix('10000'), sender = tester.k1)
    cash.approve(completeSets.address, fix('10000'), sender=tester.k1)
    assert completeSets.publicBuyCompleteSets(market2.address, fix('1000'), sender=tester.k1)

    assert yesShareToken2.totalSupply()
    assert noShareToken2.totalSupply()

    AssertOrder(market2, market1, categoricalMarket, scalarMarket, reportingWindow=reportingWindow)

def AssertOrder(*args, **kwargs):
    reportingWindow = kwargs["reportingWindow"]
    curMarket = reportingWindow.getMarketsHead()
    for market in args:
        assert curMarket == market.address
        curMarket = reportingWindow.tryGetPrevMarket(curMarket)