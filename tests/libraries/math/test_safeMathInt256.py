#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises

@mark.parametrize('a, b, expectedResult', [
    (-2**(255), -2**(255), "TransactionFailed"),
    (-2**(255), (2**(255) - 1), "TransactionFailed"),
    ((2**(255) - 1), (2**(255) - 1), "TransactionFailed"),
    (-1, -1, 1),
    (-1, 1, -1),
    (1, 0, 0),
    (1, 1, 1)
])
def test_mul(a, b, expectedResult, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            SafeMathInt256Tester.mul(a, b)
    else:
        assert SafeMathInt256Tester.mul(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    (-2**(255), -2**(255), 1),
    (-2**(255), (2**(255) - 1), -1),
    ((2**(255) - 1), (2**(255) - 1), 1),
    (-1, -1, 1),
    (-1, 1, -1),
    (1, 0, "TransactionFailed"),
    (1, 1, 1)
])
def test_div(a, b, expectedResult, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            SafeMathInt256Tester.div(a, b)
    else:
        assert SafeMathInt256Tester.div(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    (-2**(255), -2**(255), 0),
    (-2**(255), (2**(255) - 1), "TransactionFailed"),
    ((2**(255) - 1), (2**(255) - 1), 0),
    (-1, -1, 0),
    (-1, 1, -2),
    (1, 0, 1),
    (1, 1, 0)
])
def test_sub(a, b, expectedResult, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            SafeMathInt256Tester.sub(a, b)
    else:
        assert SafeMathInt256Tester.sub(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    (-2**(255), -2**(255), "TransactionFailed"),
    (-2**(255), (2**(255) - 1), -1),
    ((2**(255) - 1), (2**(255) - 1), "TransactionFailed"),
    (-1, -1, -2),
    (-1, 1, 0),
    (1, 0, 1),
    (1, 1, 2)
])
def test_add(a, b, expectedResult, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            SafeMathInt256Tester.add(a, b)
    else:
        assert SafeMathInt256Tester.add(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    (-1, -2, -2),
    (-2, -1, -2),
    (-1, -1, -1),
    (-1, 0, -1),
    (0, -1, -1),
    (0, 0, 0),
    (0, 1, 0),
    (1, 0, 0),
    (1, 1, 1),
    (1, 2, 1),
    (2, 1, 1),
])
def test_min(a, b, expectedResult, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.min(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    (-1, -2, -1),
    (-2, -1, -1),
    (-1, -1, -1),
    (-1, 0, 0),
    (0, -1, 0),
    (0, 0, 0),
    (0, 1, 1),
    (1, 0, 1),
    (1, 1, 1),
    (1, 2, 2),
    (2, 1, 2),
])
def test_max(a, b, expectedResult, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.max(a, b) == expectedResult

def test_getInt256Min(contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.getInt256Min() == -2**(255)

def test_getInt256Max(contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    assert SafeMathInt256Tester.getInt256Max() == (2**(255) - 1)

@mark.parametrize('a, b, base, expectedResult', [
    (-2**(255), -2**(255), 10**18, "TransactionFailed"),
    (-2**(255), (2**(255) - 1), 10**18, "TransactionFailed"),
    ((2**(255) - 1), (2**(255) - 1), 10**18, "TransactionFailed"),
    (-10**18, -1, 10**18, 1),
    (-10**18, 1, 10**18, -1),
    (10**18, 0, 10**18, 0),
    (10**18, 1, 10**18, 1)
])
def test_fxpMul(a, b, base, expectedResult, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            SafeMathInt256Tester.fxpMul(a, b, base)
    else:
        assert SafeMathInt256Tester.fxpMul(a, b, base) == expectedResult

@mark.parametrize('a, b, base, expectedResult', [
    (-2**(255), -2**(255), 10**18, "TransactionFailed"),
    (-2**(255), (2**(255) - 1), 10**18, "TransactionFailed"),
    ((2**(255) - 1), (2**(255) - 1), 10**18, "TransactionFailed"),
    (-1, -1, 10**18, 10**18),
    (-1, 1, 10**18, -10**18),
    (1, 0, 10**18, "TransactionFailed"),
    (1, 1, 10**18, 10**18)
])
def test_fxpDiv(a, b, base, expectedResult, contractsFixture):
    SafeMathInt256Tester = contractsFixture.contracts['SafeMathInt256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            SafeMathInt256Tester.fxpDiv(a, b, base)
    else:
        assert SafeMathInt256Tester.fxpDiv(a, b, base) == expectedResult
