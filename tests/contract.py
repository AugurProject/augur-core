#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""augur-core unit tests:

Contract testing base class.

@author Jack Peterson (jack@tinybike.net)

"""
import sys
import os
import json
import unittest
from cStringIO import StringIO
from contextlib import contextmanager
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

    def format_json(self, jsonstr):
        print "format json:", jsonstr
        return jsonstr.replace("'", "\"").replace("L,", ",").replace("L}", "}")

    def parse_log(self, log):
        print "parse log:", log.getvalue()
        return json.loads(self.format_json(log.getvalue()))

    @contextmanager
    def capture_stdout(self):
        self.buf = sys.stdout
        sys.stdout = self.logger = StringIO()
        print "capturing stdout"
        yield self.logger
        sys.stdout = self.buf
