#!/usr/bin/env python

from ethereum.tools.tester import TransactionFailed
from pytest import raises

def test_mutex(contractsFixture):
    mutex = contractsFixture.contracts['Mutex']

    assert mutex.acquire() == True
    with raises(TransactionFailed):
        mutex.acquire()
    assert mutex.release() == True
