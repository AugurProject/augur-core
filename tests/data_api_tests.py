#!/usr/bin/env python
from __future__ import division
from ethereum import tester as t
from load_contracts import ContractLoader
import math
import random
import os
import time
import binascii
from pprint import pprint

ONE = 10**18
TWO = 2*ONE
HALF = ONE/2

def test_backstops(c, s, t):
    event1 = 1234
    event2 = 5678
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)

    def test_disputedOverEthics():
        assert(c.getDisputedOverEthics(event1) == 0), "disputedOverEthics isn't defaulted to 0"
        c.setDisputedOverEthics(event1)
        assert(c.getDisputedOverEthics(event1) == 1), "setDisputedOverEthics didn't set event properly"
        try:
            raise Exception(c.setDisputedOverEthics(event1, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "setDisputedOverEthics should throw if msg.sender isn't whitelisted"

    def test_forkBondPoster():
        assert(c.getForkBondPoster(event1) == 0), "forkBondPoster isn't defaulted to 0"
        assert(c.setForkBondPoster(event1, t.a1) == 1), "Didn't set forkBondPoster correctly"
        assert(c.getForkBondPoster(event1) == address1), "Didn't set the forkBondPoster to the expected address"
        try:
            raise Exception(c.setForkBondPoster(event1, t.a2, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "setForkBondPoster should throw if msg.sender isn't whitelisted"

    def test_forkedOverEthicality():
        assert(c.getForkedOverEthicality(event1) == 0), "forkedOverEthicality isn't defaulted to 0"
        assert(c.setForkedOverEthicality(event1) == 1), "setForkedOverEthicality isn't returning 1 as expected when msg.sender is whitelisted"
        assert(c.getForkedOverEthicality(event1) == 1), "forkedOverEthicality wasn't set correctly"
        try:
            assert(c.getForkedOverEthicality(event2) == 0), "forkedOverEthicality isn't defaulted to 0"
            raise Exception(c.setForkedOverEthicality(event2, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "setForkedOverEthicality should throw if msg.sender isn't whitelisted"

    test_disputedOverEthics()
    test_forkBondPoster()
    test_forkedOverEthicality()

    print "data_api/backstops.se unit tests completed"

# def test_branches(c, s, t):
#     branch = 1010101
#     def test_incrementPeriod():
#
#         assert(c.getVotePeriod(branch) == 94064891)
#         c.incrementPeriod(branch)
#         assert(c.getVotePeriod(branch) == 95065892)
#     test_incrementPeriod()

if __name__ == '__main__':
    src = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'src')
    contracts = ContractLoader(src, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'], '', 0)
    state = contracts.state
    t = contracts._ContractLoader__tester
    test_backstops(contracts.backstops, state, t)
    # test_branches(contracts.branches, state, t)


    # data_api/backstops.se
    # data_api/branches.se
    # data_api/consensusData.se
    # data_api/events.se
    # data_api/expiringEvents.se
    # data_api/fxpFunctions.se
    # data_api/info.se
    # data_api/markets.se
    # data_api/mutex.se
    # data_api/orders.se
    # data_api/register.se
    # data_api/reporting.se
    # data_api/reportingThreshold.se
    # data_api/topics.se

    print "DONE TESTING DATA_API"
