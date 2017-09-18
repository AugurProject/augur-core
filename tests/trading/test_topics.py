#!/usr/bin/env python

from ethereum.tools import tester
from utils import fix, longToHexString, bytesToLong
from constants import YES, NO

def test_topics(fundedRepFixture):
    branch = fundedRepFixture.branch
    topics = fundedRepFixture.applySignature('Topics', branch.getTopics())
    market = fundedRepFixture.binaryMarket
    cash = fundedRepFixture.cash
    trade = fundedRepFixture.contracts['Trade']
    makeOrder = fundedRepFixture.contracts['MakeOrder']
    takeOrder = fundedRepFixture.contracts['TakeOrder']
    yesShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('ShareToken', market.getShareToken(NO))

    assert topics.count() == 0
    assert topics.updatePopularity('Politics'.ljust(32, '\x00'), 10)
    assert topics.count() == 1
    assert topics.getPopularity('Politics'.ljust(32, '\x00')) == 10

    # execute a trade against one of the default markets (Sports)
    assert cash.depositEther(value=fix('2', '0.6'), sender = tester.k1)
    assert cash.approve(makeOrder.address, fix('2', '0.6'), sender = tester.k1)
    trade.publicBuy(market.address, YES, 2, fix('0.6'), 42, sender = tester.k1)
    assert cash.depositEther(value=fix('2', '0.4'), sender = tester.k2)
    assert cash.approve(takeOrder.address, fix('2', '0.4'), sender = tester.k2)
    trade.publicSell(market.address, YES, 2, fix('0.6'), 42, sender = tester.k2)

    # assert expected state
    assert topics.count() == 2
    assert topics.getPopularity('Politics'.ljust(32, '\x00')) == 10
    assert topics.getPopularity('Sports'.ljust(32, '\x00')) == 2

    # execute another trade against the same market
    assert yesShareToken.approve(makeOrder.address, 2, sender = tester.k1)
    trade.publicSell(market.address, YES, 2, fix('0.6'), 42, sender = tester.k1)
    assert noShareToken.approve(takeOrder.address, 2, sender = tester.k2)
    trade.publicBuy(market.address, YES, 2, fix('0.6'), 42, sender = tester.k2)

    # assert expected state
    assert topics.count() == 2
    assert topics.getPopularity('Politics'.ljust(32, '\x00')) == 10
    assert topics.getPopularity('Sports'.ljust(32, '\x00')) == 4
    assert {
        topics.getTopicByOffset(0): topics.getPopularityByOffset(0),
        topics.getTopicByOffset(1): topics.getPopularityByOffset(1),
    } == {
        'Politics'.ljust(32, '\x00'): 10,
        'Sports'.ljust(32, '\x00'): 4,
    }
