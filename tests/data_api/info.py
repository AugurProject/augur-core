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

def test_info(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
    c = contracts.info
    branch1 = 1010101
    branch2 = 2020202
    cashAddr = long(contracts.cash.address.encode("hex"), 16)
    cashWallet = contracts.branches.getBranchWallet(branch1, cashAddr)
    address0 = t.a0.encode("hex")
    address1 = t.a1.encode("hex")
    WEI_TO_ETH = 10**18
    expectedCreationFee = 10 * WEI_TO_ETH
    nullAddress = '0000000000000000000000000000000000000000';

    def test_defaults():
        assert(c.getCreator(branch1) == address0), "creator of default branch wasn't the expected address"
        assert(c.getDescription(branch1) == 'Root branch'), "description for default branch should be 'Root branch'"
        assert(c.getDescriptionLength(branch1) == 11), "descriptionLength should be 11 by default"
        assert(c.getCreationFee(branch1) == expectedCreationFee), "the creation fee for the default branch wasn't the expected creation fee (10 * WEI_TO_ETH)"
        assert(c.getCurrency(branch1) == 0), "the default currency for the default branch should be set to 0 by default"
        assert(c.getWallet(branch1) == 0), "the default wallet for the default branch should be set to 0 by default"

    def test_currency():
        assert(c.getCurrency(branch1) == 0), "the default currency for the default branch should be set to 0 by default"
        assert(c.getWallet(branch1) == 0), "the default wallet for the default branch should be set to 0 by default"
        assert(c.setCurrencyAndWallet(branch1, cashAddr, cashWallet) == 1), "setCurrencyAndWallet wasn't executed successfully"
        assert(c.getCurrency(branch1) == cashAddr), "currency for default branch didn't get set to the cash address as expected"
        assert(c.getWallet(branch1) == cashWallet), "wallet for the default branch wasn't set to the cash wallet as expected"

    def test_setInfo():
        assert(c.setInfo(branch1, 'Hello World', long(address0, 16), expectedCreationFee, cashAddr, cashWallet) == 0), "default branch already exists, so this shouldn't change anything and return 0"
        assert(c.getDescription(branch1) == 'Root branch'), "Confirm that the description hasn't changed because setInfo should have failed and returned 0"
        assert(c.getCreator(branch2) == nullAddress), "branch2 shouldn't have been added to info yet and the creator should be set to 0."
        assert(c.setInfo(branch2, 'Test Branch', long(address1, 16), expectedCreationFee, cashAddr, cashWallet) == 1), "setInfo wasn't successfully executed when it should have been"
        assert(c.getCreator(branch2) == address1), "creator of branch2 wasn't the expected address"
        assert(c.getDescription(branch2) == 'Test Branch'), "description for branch2 should be 'Test Branch'"
        assert(c.getDescriptionLength(branch2) == 11), "descriptionLength should be 11 by default"
        assert(c.getCreationFee(branch2) == expectedCreationFee), "the creation fee for branch2 wasn't the expected creation fee (10 * WEI_TO_ETH)"
        assert(c.getCurrency(branch2) == cashAddr), "the currency for the branch2 should be set to the cash currency address"
        assert(c.getWallet(branch2) == cashWallet), "the wallet for branch2 should be set to the cash wallet address"

    test_defaults()
    test_currency()
    test_setInfo()

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_info(contracts)
