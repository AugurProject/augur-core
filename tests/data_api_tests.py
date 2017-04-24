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
    event = 1234
    assert(c.getDisputedOverEthics(event) == 0), "disputedOverEthics isn't defaulted to 0"
    c.setDisputedOverEthics(event)

def test_branches(c, s, t):
    branch = 1010101
    def test_incrementPeriod():
        print "begin branches.incrementPeriod tests"
        print c.getVotePeriod(branch)
        c.incrementPeriod(branch)
        print c.getVotePeriod(branch)
        print "branches.incrementPeriod tests complete"
    test_incrementPeriod()

if __name__ == '__main__':
    src = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'src')
    contracts = ContractLoader(src, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'], '', 1)
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
