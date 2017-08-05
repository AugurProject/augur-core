#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises

@mark.parametrize('a, b, c', [
    (1, 1, 1)
])
def test_mul(a, b, c, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.mul(a, b) == c
    print SafeMathInt256Tester.mul(a, b)

@mark.parametrize('a, b, c', [
    (1, 1, 1)
])
def test_div(a, b, c, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.div(a, b) == c
    print SafeMathInt256Tester.div(a, b)

@mark.parametrize('a, b, c', [
    (1, 1, 0)
])
def test_sub(a, b, c, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.sub(a, b) == c
    print SafeMathInt256Tester.sub(a, b)

@mark.parametrize('a, b, c', [
    (1, 1, 2)
])
def test_add(a, b, c, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.add(a, b) == c
    print SafeMathInt256Tester.add(a, b)

def test_getInt256Min(contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.getInt256Min() == -2**(255)
    print SafeMathInt256Tester.getInt256Min()

def test_getInt256Max(contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.getInt256Max() == (2**(255) - 1)
    print SafeMathInt256Tester.getInt256Max()