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
                "tag2": "meta",
                "tag3": "data etc",
                "source": "http://www.this-is-only-a-test.com",
                "details": "Insert very long description here!",
                "link1": "http://www.testing.com",
                "link2": "http://www.google.com",
                "link3": "http://fail.com"
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
            self.params["setMetadata"]["details"],
            self.params["setMetadata"]["link1"],
            self.params["setMetadata"]["link2"],
            self.params["setMetadata"]["link3"]
        )
        assert(retval == 1)

    def test_getMetadata(self):
        retval = self.contract.setMetadata(
            self.params["setMetadata"]["market"],
            self.params["setMetadata"]["tag1"],
            self.params["setMetadata"]["tag2"],
            self.params["setMetadata"]["tag3"],
            self.params["setMetadata"]["source"],
            self.params["setMetadata"]["details"],
            self.params["setMetadata"]["link1"],
            self.params["setMetadata"]["link2"],
            self.params["setMetadata"]["link3"]
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
        detailsLength = metadata[4]
        link1Length = metadata[5]
        link2Length = metadata[6]
        link3Length = metadata[7]
        assert(self.params["setMetadata"]["source"] == bin2ascii(metadata[8:8+sourceLength]))
        assert(self.params["setMetadata"]["details"] == bin2ascii(metadata[8+sourceLength:8+sourceLength+detailsLength]))
        linkStart = 8 + sourceLength + detailsLength
        assert(self.params["setMetadata"]["link1"] == bin2ascii(metadata[linkStart:linkStart+link1Length]))
        assert(self.params["setMetadata"]["link2"] == bin2ascii(metadata[linkStart+link1Length:linkStart+link1Length+link2Length]))
        assert(self.params["setMetadata"]["link3"] == bin2ascii(metadata[linkStart+link1Length+link2Length:]))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestComments)
    unittest.TextTestRunner(verbosity=2).run(suite)
