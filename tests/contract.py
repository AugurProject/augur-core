#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""augur-core unit tests:

Contract testing base class.

@author Jack Peterson (jack@tinybike.net)

"""
import os
import unittest
from ethereum import tester

GAS_LIMIT = 700000000

class ContractTest(unittest.TestCase):

    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "src")

    def setUp(self, group, name):
        addr = os.path.join(self.ROOT, group, name)
        tester.state()
        tester.gas_limit = GAS_LIMIT
        self.state = tester.state()
        self.contract = self.state.abi_contract(addr, gas=tester.gas_limit)
        assert(self.state is not None)
        assert(self.contract is not None)

    def tearDown(self):
        del self.state
