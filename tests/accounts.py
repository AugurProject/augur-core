#!/usr/bin/env python
"""augur-core unit tests: data and api/accounts.se"""
import sys
import os
import unittest
from ethereum import tester

SRC = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "src")

class TestAccounts(unittest.TestCase):

    PATH = os.path.join(SRC, "data and api", "accounts.se")

    def setUp(self):
        tester.state()
        tester.gas_limit = 700000000
        self.state = tester.state()
        self.contract = self.state.abi_contract(self.PATH, gas=tester.gas_limit)
        self.handle = 0xbe107c37e58872f783341369f6b221b7d394eba0a6facad7b3c195d19811d1cd
        self.account = {
            "privateKey": 0xa24ee972cb18558423456ff2bc609baab0dd5a0a4f0c566efeb9bf2429251976,
            "iv": 0x262ce8235b1a4155d87c9bb99d680ad3,
            "salt": 0xb3bd4935d13290fa7674ff8e757e5c3d76bc5cc6a118b7ef34cb93df50471125,
            "mac": 0xfa9c2a61b7b2ffcb6d29de02051916b04d2a76222b954dea960cde20c54c99be,
            "id": 0x360f5d691b1245c2a8a582db1e7c5213,
        }
        assert(self.state is not None)
        assert(self.contract is not None)

    def test_register(self):
        result = self.contract.register(self.handle,
                                        self.account["privateKey"],
                                        self.account["iv"],
                                        self.account["salt"],
                                        self.account["mac"],
                                        self.account["id"])
        assert(result == 1)
        result = self.contract.register(self.handle,
                                        self.account["privateKey"],
                                        self.account["iv"],
                                        self.account["salt"],
                                        self.account["mac"],
                                        self.account["id"])
        assert(result == 0)

    def test_getAccount(self):
        result = self.contract.register(self.handle,
                                        self.account["privateKey"],
                                        self.account["iv"],
                                        self.account["salt"],
                                        self.account["mac"],
                                        self.account["id"])
        assert(result == 1)
        account = self.contract.getAccount(self.handle)
        assert(len(account) == 5)
        account = [hex(a % 2**256) for a in account]
        for i, k in enumerate(["privateKey", "iv", "salt", "mac", "id"]):
            assert(hex(self.account[k]) == account[i])

    def tearDown(self):
        del self.state
        del self.contract


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAccounts)
    unittest.TextTestRunner(verbosity=2).run(suite)
