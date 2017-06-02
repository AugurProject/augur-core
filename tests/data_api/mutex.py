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

def test_mutex(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
    c = contracts.mutex
    assert(c.acquire() == 1), "acquire should return 1 if the mutex isn't already set."
    try:
        raise Exception(c.acquire())
    except Exception as exc:
        assert(isinstance(exc, t.TransactionFailed)), "mutex should already be set so attempting to call acquire again should fail"
    assert(c.release() == 1), "release shoud return 1 and release the mutex"

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_mutex(contracts)
