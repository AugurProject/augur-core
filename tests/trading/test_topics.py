#!/usr/bin/env python

from ethereum import tester
from utils import fix, longToHexString, bytesToLong

NO = 0
YES = 1

def test_topics(contractsFixture):
    branch = contractsFixture.branch
    topics = contractsFixture.applySignature('topics', branch.getTopics())
    market = contractsFixture.binaryMarket
    cash = contractsFixture.cash
    trade = contractsFixture.contracts['trade']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']
    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))

    assert topics.count() == 0
    assert topics.updatePopularity('Politics'.ljust(32, '\x00'), 10)
    assert topics.count() == 1
    assert topics.getPopularity('Politics'.ljust(32, '\x00')) == 10

    # execute a trade against one of the default markets (Sports)
    assert cash.publicDepositEther(value=fix('1.2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('1.2', '0.6'), sender = tester.k1)
    trade.publicBuy(market.address, YES, fix('1.2'), fix('0.6'), 42, sender = tester.k1)
    assert cash.publicDepositEther(value=fix('1.2', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('1.2', '0.4'), sender = tester.k2)
    trade.publicSell(market.address, YES, fix('1.2'), fix('0.6'), 42, sender = tester.k2)

    # assert expected state
    assert topics.count() == 2
    assert topics.getPopularity('Politics'.ljust(32, '\x00')) == 10
    assert topics.getPopularity('Sports'.ljust(32, '\x00')) == fix('1.2')

    # execute another trade against the same market
    assert yesShareToken.approve(makeOrder.address, fix('1.2'), sender = tester.k1)
    trade.publicSell(market.address, YES, fix('1.2'), fix('0.6'), 42, sender = tester.k1)
    assert noShareToken.approve(takeOrder.address, fix('1.2'), sender = tester.k2)
    trade.publicBuy(market.address, YES, fix('1.2'), fix('0.6'), 42, sender = tester.k2)

    # assert expected state
    assert topics.count() == 2
    assert topics.getPopularity('Politics'.ljust(32, '\x00')) == 10
    assert topics.getPopularity('Sports'.ljust(32, '\x00')) == fix('2.4')
    assert {
        topics.getTopicByOffset(0): topics.getPopularityByOffset(0),
        topics.getTopicByOffset(1): topics.getPopularityByOffset(1),
    } == {
        bytesToLong('Sports'.ljust(32, '\x00')): fix('2.4'),
        bytesToLong('Politics'.ljust(32, '\x00')): 10,
    }
