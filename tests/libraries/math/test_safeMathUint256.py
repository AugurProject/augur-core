#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises

@mark.parametrize('a, b, c', [
    (1, 1, 1)
])
def test_mul(a, b, c, contractsFixture):
    SafeMathUint256Tester = contractsFixture.contracts['SafeMathUint256Tester']
    assert SafeMathUint256Tester.mul(a, b) == c
    print SafeMathUint256Tester.mul(a, b)

@mark.parametrize('a, b, c', [
    (1, 1, 1)
])
def test_div(a, b, c, contractsFixture):
    SafeMathUint256Tester = contractsFixture.contracts['SafeMathUint256Tester']
    assert SafeMathUint256Tester.div(a, b) == c
    print SafeMathUint256Tester.div(a, b)

@mark.parametrize('a, b, c', [
    (1, 1, 0)
])
def test_sub(a, b, c, contractsFixture):
    SafeMathUint256Tester = contractsFixture.contracts['SafeMathUint256Tester']
    assert SafeMathUint256Tester.sub(a, b) == c
    print SafeMathUint256Tester.sub(a, b)

@mark.parametrize('a, b, c', [
    (1, 1, 2)
])
def test_add(a, b, c, contractsFixture):
    SafeMathUint256Tester = contractsFixture.contracts['SafeMathUint256Tester']
    assert SafeMathUint256Tester.add(a, b) == c
    print SafeMathUint256Tester.add(a, b)

def test_getUint256Min(contractsFixture):
    SafeMathUint256Tester = contractsFixture.contracts['SafeMathUint256Tester']
    assert SafeMathUint256Tester.getUint256Min() == -2**(255)
    print SafeMathUint256Tester.getUint256Min()

def test_getUint256Max(contractsFixture):
    SafeMathUint256Tester = contractsFixture.contracts['SafeMathUint256Tester']
    assert SafeMathUint256Tester.getUint256Max() == (2**(255) - 1)
    print SafeMathUint256Tester.getUint256Max()