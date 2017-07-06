#!/usr/bin/env python

from ContractsFixture import ContractsFixture
from ethereum.tester import TransactionFailed
from pytest import raises

def test_mutex():
    fixture = ContractsFixture()
    mutex = fixture.upload('../src/mutex.se')

    assert mutex.acquire() == 1
    with raises(TransactionFailed):
        mutex.acquire()
    assert mutex.release() == 1
