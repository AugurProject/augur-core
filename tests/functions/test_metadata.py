#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""augur-core unit tests

Unit tests for data and api/metadata.se.

@author Jack Peterson (jack@tinybike.net)

"""
import sys
import os
import unittest
from ethereum import tester

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir))

from contract import ContractTest

def bin2ascii(bytearr):
    return ''.join(map(chr, bytearr))

class TestComments(ContractTest):

    def setUp(self):
        ContractTest.setUp(self, "functions", "metadata.se")
        self.params = {
            "setMetadata": {
                "market": 0xdeadbeef,
                "tag1": "testing",
                "tag2": "Presidential Election",
                "tag3": "metadata etc",
                "source": "http://www.answers.com",
                "links": "https://api.github.com/gists/3a934aaf7aa54ec9d759debe6a0765b4"
            },
            "getMetadata": {
                "market": 0xdeadbeef
            },
        }

    def test_setMetadata(self):
        retval = self.contract.setMetadata(
            self.params["setMetadata"]["market"],
            self.params["setMetadata"]["tag1"],
            self.params["setMetadata"]["tag2"],
            self.params["setMetadata"]["tag3"],
            self.params["setMetadata"]["source"],
            self.params["setMetadata"]["links"]
        )
        assert(retval == 1)
        retval2 = self.contract.setMetadata(
            self.params["setMetadata"]["market"],
            self.params["setMetadata"]["tag1"],
            self.params["setMetadata"]["tag2"],
            self.params["setMetadata"]["tag3"],
            self.params["setMetadata"]["source"],
            self.params["setMetadata"]["links"]
        )
        assert(retval2 == 0)

    def test_getMetadata(self):
        retval = self.contract.setMetadata(
            self.params["setMetadata"]["market"],
            self.params["setMetadata"]["tag1"],
            self.params["setMetadata"]["tag2"],
            self.params["setMetadata"]["tag3"],
            self.params["setMetadata"]["source"],
            self.params["setMetadata"]["links"]
        )
        assert(retval == 1)
        metadata = self.contract.getMetadata(self.params["getMetadata"]["market"])
        tag1 = hex(metadata[0] % 2**256)
        tag2 = hex(metadata[1] % 2**256)
        tag3 = hex(metadata[2] % 2**256)
        assert(self.params["setMetadata"]["tag1"] == tag1[2:-1].decode("hex"))
        assert(self.params["setMetadata"]["tag2"] == tag2[2:-1].decode("hex"))
        assert(self.params["setMetadata"]["tag3"] == tag3[2:-1].decode("hex"))
        sourceLength = metadata[3]
        linksLength = metadata[4]
        assert(self.params["setMetadata"]["source"] == bin2ascii(metadata[6:6+sourceLength]))
        linkStart = 6 + sourceLength
        assert(self.params["setMetadata"]["links"] == bin2ascii(metadata[linkStart:]))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestComments)
    unittest.TextTestRunner(verbosity=2).run(suite)
