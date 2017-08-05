#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises

def test_getInt256Min(contractsFixture):
    SafeMathUint256Tester = contractsFixture.contracts['SafeMathUint256Tester']
    SafeMathUint256Tester.getUint256Min()



@mark.parametrize('a, b, c', [
    (1, 1, 2)
])
def test_add(a, b, c, contractsFixture):
    SafeMathUint256Tester = contractsFixture.contracts['SafeMathUint256Tester']
    sum = SafeMathUint256Tester.add(a, b) 
    assert sum == c
