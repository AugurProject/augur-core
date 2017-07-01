#!/usr/bin/env python

from __future__ import division
import os
import sys
import json
import iocapture
import ethereum.tester
import utils

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir)
src = os.path.join(ROOT, "src")

WEI_TO_ETH = 10**18
TWO = 2*WEI_TO_ETH
HALF = WEI_TO_ETH/2

def test_topics(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
    c = contracts.topics
    branch1 = 1010101
    # topic0 is the topic added from the markets tests
    topic0 = 'one'
    topic1 = 'augur'
    topic2 = 'predictions'
    longTopic0 = long('one'.encode('hex'), 16)
    longTopic1 = long(topic1.encode('hex'), 16)
    longTopic2 = long(topic2.encode('hex'), 16)
    WEI_TO_ETH = 10**18

    def test_defaults():
        assert(c.getNumTopicsInBranch(branch1) == 0), "numTopicsInBranch for branch1 should be 0 at this point"
        assert(c.getTopicsInBranch(branch1, 0, 5) == []), "topicsInBranch for branch1 ranging from topic 0 to 5 should return an array containing only topic0 from the markets tests"
        assert(c.getTopicsInfo(branch1, 0, 5) == []), "topicsInfo for branch1 should ranging from topic 0 to 5 should return only topic0 from the markets tests and its popularity"
        assert(c.getTopicPopularity(branch1, topic1) == 0), "topicPopularity for branch1 and topic1 should be 0 by default as topic1 shouldn't exist yet"

    def test_updateTopicPopularity():
        assert(c.updateTopicPopularity(branch1, topic1, WEI_TO_ETH) == 1), "updateTopicPopularity wasn't executed successfully"
        assert(c.getTopicPopularity(branch1, topic1) == WEI_TO_ETH), "topicPopularity for branch1, topic1 should be set to WEI_TO_ETH"
        assert(c.getNumTopicsInBranch(branch1) == 1), "numTopicsInBranch for branch1 should return 2"
        assert(c.getTopicsInBranch(branch1, 0, 5) == [longTopic1]), "topicsInBranch1 ranging from index 0 to 5 should return an array with topic0 and topic1 inside of it"
        assert(c.getTopicsInfo(branch1, 0, 5) == [longTopic1, WEI_TO_ETH]), "getTopicsInfo for branch1, index 0 to 5, should return topic0 and its popularity of WEI_TO_ETH*15 and topic1 and it's popularity of WEI_TO_ETH in a length 4 array"
        assert(c.getTopicPopularity(branch1, topic2) == 0), "topicPopularity for topic2 should be 0 as topic2 hasn't been added yet"
        assert(c.updateTopicPopularity(branch1, topic2, WEI_TO_ETH*4) == 1), "updateTopicPopularity wasn't executed successfully"
        assert(c.getTopicPopularity(branch1, topic2) == WEI_TO_ETH*4), "topicPopularity for topic2 should now be set to WEI_TO_ETH*4"
        assert(c.getNumTopicsInBranch(branch1) == 2), "numTopicsInBranch should be set to 3"
        assert(c.getTopicsInBranch(branch1, 0, 5) == [longTopic1, longTopic2]), "getTopicsInBranch for branch1, index 0 to 5 should return an array with topic0, topic1, and topic2 contained within"
        assert(c.getTopicsInfo(branch1, 0, 5) == [longTopic1, WEI_TO_ETH, longTopic2, WEI_TO_ETH*4]), "getTopicsInfo for branch1, index 0 to 5 should return a length 6 array with topic0 and it's popularity, topic1 and it's popularity, and topic2 and it's popularity"
        assert(c.updateTopicPopularity(branch1, topic1, WEI_TO_ETH*2) == 1), "updateTopicPopularity wasn't executed successfully"
        assert(c.updateTopicPopularity(branch1, topic2, -WEI_TO_ETH) == 1), "updateTopicPopularity wasn't executed successfully"
        assert(c.getTopicPopularity(branch1, topic1) == WEI_TO_ETH*3), "topicPopularity for branch1, topic1 should be set to WEI_TO_ETH*3"
        assert(c.getTopicPopularity(branch1, topic2) == WEI_TO_ETH*3), "topicPopularity for branch1, topic2 should be set to WEI_TO_ETH*3"
        assert(c.getTopicsInfo(branch1, 0, 5) == [longTopic1, WEI_TO_ETH*3, longTopic2, WEI_TO_ETH*3]), "getTopicsInfo for branch1, index 0 to 5, should return topic0 and it's popularity, topic1 and it's updated popularity, and topic2 and it's updated popularity"

    test_defaults()
    test_updateTopicPopularity()

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_topics(contracts)
