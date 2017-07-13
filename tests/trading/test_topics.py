#!/usr/bin/env python

from ethereum.tools import tester
from utils import fix, longToHexString, bytesToLong

NO = 0
YES = 1

POLITICS = 'Politics'.ljust(32, '\x00')
SPORTS = 'Sports'.ljust(32, '\x00')

def test_topics(contractsFixture):
    branch = contractsFixture.branch
    topics = contractsFixture.applySignature('topics', branch.getTopics())
    market = contractsFixture.binaryMarket
    cash = contractsFixture.cash
    completeSets = contractsFixture.contracts['completeSets']

    assert topics.count() == 0
    assert topics.updatePopularity(POLITICS, 10)
    assert topics.count() == 1
    assert topics.getPopularity(POLITICS) == 10

    # purchase a complete set for one of the default markets (Sports)
    assert cash.publicDepositEther(value = fix('1.2'), sender = tester.k1)
    assert cash.approve(completeSets.address, fix('1.2'), sender=tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender=tester.k1)

    # assert expected state
    assert topics.count() == 2
    assert topics.getPopularity(POLITICS) == 10
    assert topics.getPopularity(SPORTS) == fix('1.2')
    AssertOrder(SPORTS, POLITICS, topics=topics)

    # execute another trade against the same market
    assert cash.publicDepositEther(value = fix('1.2'), sender = tester.k2)
    assert cash.approve(completeSets.address, fix('1.2'), sender=tester.k2)
    assert completeSets.publicBuyCompleteSets(market.address, fix('1.2'), sender=tester.k2)

    # assert expected state
    assert topics.count() == 2
    assert topics.getPopularity(POLITICS) == 10
    assert topics.getPopularity(SPORTS) == fix('2.4')
    AssertOrder(SPORTS, POLITICS, topics=topics)

    # Increase POLITICS and confirm it is moved in position
    assert topics.updatePopularity(POLITICS, fix('3'))
    AssertOrder(POLITICS, SPORTS, topics=topics)

# This assumes unique popularity
def AssertOrder(*args, **kwargs):
    topics = kwargs["topics"]
    curTopic = topics.getTopicsHead()
    for topic in args:
        assert topics.getPopularity(curTopic) == topics.getPopularity(topic)
        curTopic = topics.tryGetPrevTopic(curTopic)