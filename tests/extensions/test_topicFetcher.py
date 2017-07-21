#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises

POLITICS = 'Politics'.ljust(32, '\x00')
SPORTS = 'Sports'.ljust(32, '\x00')
ENTERTAINMENT = 'Entertainment'.ljust(32, '\x00')

@fixture(scope="session")
def topicFetcherSnapshot(sessionFixture):
    topicFetcher = sessionFixture.upload('../src/extensions/topicFetcher.se')
    topicFetcher.initialize(sessionFixture.controller.address)
    sessionFixture.chain.mine(1)
    return sessionFixture.chain.snapshot()

@fixture
def topicFetcherContractsFixture(sessionFixture, topicFetcherSnapshot):
    sessionFixture.chain.revert(topicFetcherSnapshot)
    return sessionFixture

def test_topicFetcherHelperFunctions(topicFetcherContractsFixture):

    branch = topicFetcherContractsFixture.branch
    topicFetcher = topicFetcherContractsFixture.contracts['topicFetcher']

    # We can get the number of topics that currently exist in a branch
    assert topicFetcher.getNumTopicsInBranch(branch.address) == 0

    # If we request a topic that doesn't exist we raise an error
    with raises(TransactionFailed):
        topicFetcher.getTopicPopularity(branch.address, POLITICS)

    # We'll directly add a topic
    assert branch.updateTopicPopularity(POLITICS, 10)

    # We can get the popularity score for an individual topic in a branch
    assert topicFetcher.getTopicPopularity(branch.address, POLITICS) == 10

    # The number of topics is correctly 1 now
    assert topicFetcher.getNumTopicsInBranch(branch.address) == 1

def test_topicFetcherGetTopicsInfoNoResults(topicFetcherContractsFixture):

    branch = topicFetcherContractsFixture.branch
    topicFetcher = topicFetcherContractsFixture.contracts['topicFetcher']

    # Requesting topics when none exist simply returns an empty list
    assert len(topicFetcher.getTopicsInfo(branch.address)) == 0

    # We'll directly add a topic
    assert branch.updateTopicPopularity(POLITICS, 10)

    # Providing a start topic that doesn't exist will return an empty list as well
    assert len(topicFetcher.getTopicsInfo(branch.address, 42)) == 0

def test_topicFetcherGetTopicsInfoHappyPath(topicFetcherContractsFixture):

    branch = topicFetcherContractsFixture.branch
    topicFetcher = topicFetcherContractsFixture.contracts['topicFetcher']

    # We'll directly add a couple topics
    assert branch.updateTopicPopularity(POLITICS, 10)
    assert branch.updateTopicPopularity(SPORTS, 11)
    assert branch.updateTopicPopularity(ENTERTAINMENT, 12)

    # We can request topics and get back an array of topic/populariy virtual tuples
    topics = topicFetcher.getTopicsInfo(branch.address)
    assert len(topics) == 3 * 2
    assert topics[1] == 12
    assert topics[3] == 11
    assert topics[5] == 10

    # We can request topics only after a provided start topic
    topics = topicFetcher.getTopicsInfo(branch.address, ENTERTAINMENT)
    assert len(topics) == 2 * 2
    assert topics[1] == 11
    assert topics[3] == 10

    # We can request a specified number of topics
    topics = topicFetcher.getTopicsInfo(branch.address, 0, 2)
    assert len(topics) == 2 * 2
    assert topics[1] == 12
    assert topics[3] == 11

    # We can request a specified number of topics only after a provided start topic
    topics = topicFetcher.getTopicsInfo(branch.address, ENTERTAINMENT, 1)
    assert len(topics) == 1 * 2
    assert topics[1] == 11