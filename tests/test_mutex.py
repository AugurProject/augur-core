#!/usr/bin/env python

from ethereum.tester import TransactionFailed
from pytest import raises

def test_mutex(contractsFixture):
    mutex = contractsFixture.contracts['mutex']

    assert mutex.acquire() == 1
    with raises(TransactionFailed):
        mutex.acquire()
    assert mutex.release() == 1
