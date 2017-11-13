#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises

@fixture(scope='session')
def testerSnapshot(sessionFixture):
    sessionFixture.upload('solidity_test_helpers/SafeMathUint256Tester.sol')
    return sessionFixture.createSnapshot()

@fixture
def testerContractsFixture(sessionFixture, testerSnapshot):
    sessionFixture.resetToSnapshot(testerSnapshot)
    return sessionFixture

@mark.parametrize('a, b, expectedResult', [
    ((2**(256) - 1), (2**(256) - 1), "TransactionFailed"),
    (1, 0, 0),
    (1, 1, 1),
    (1, 2, 2)
])
def test_mul(a, b, expectedResult, testerContractsFixture):
    testerContractsFixture.uploadAndAddToController("../tests/solidity_test_helpers/SafeMathUint256Tester.sol")
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            safeMathUint256Tester.mul(a, b)
    else:
        assert safeMathUint256Tester.mul(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    ((2**(256) - 1), (2**(256) - 1), 1),
    (1, 0, "TransactionFailed"),
    (1, 1, 1)
])
def test_div(a, b, expectedResult, testerContractsFixture):
    testerContractsFixture.uploadAndAddToController("../tests/solidity_test_helpers/SafeMathUint256Tester.sol")
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            safeMathUint256Tester.div(a, b)
    else:
        assert safeMathUint256Tester.div(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    ((2**(256) - 1), (2**(256) - 1), 0),
    (1, 0, 1),
    (1, 1, 0)
])
def test_sub(a, b, expectedResult, testerContractsFixture):
    testerContractsFixture.uploadAndAddToController("../tests/solidity_test_helpers/SafeMathUint256Tester.sol")
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            safeMathUint256Tester.sub(a, b)
    else:
        assert safeMathUint256Tester.sub(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    ((2**(256) - 1), (2**(256) - 1), "TransactionFailed"),
    (1, 0, 1),
    (1, 1, 2)
])
def test_add(a, b, expectedResult, testerContractsFixture):
    testerContractsFixture.uploadAndAddToController("../tests/solidity_test_helpers/SafeMathUint256Tester.sol")
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            safeMathUint256Tester.add(a, b)
    else:
        assert safeMathUint256Tester.add(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    (0, 0, 0),
    (0, 1, 0),
    (1, 0, 0),
    (1, 1, 1),
    (1, 2, 1),
    (2, 1, 1),
])
def test_min(a, b, expectedResult, testerContractsFixture):
    testerContractsFixture.uploadAndAddToController("../tests/solidity_test_helpers/SafeMathUint256Tester.sol")
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    assert safeMathUint256Tester.min(a, b) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    (0, 0, 0),
    (0, 1, 1),
    (1, 0, 1),
    (1, 1, 1),
    (1, 2, 2),
    (2, 1, 2),
])
def test_max(a, b, expectedResult, testerContractsFixture):
    testerContractsFixture.uploadAndAddToController("../tests/solidity_test_helpers/SafeMathUint256Tester.sol")
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    assert safeMathUint256Tester.max(a, b) == expectedResult

def test_getUint256Min(testerContractsFixture):
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    assert safeMathUint256Tester.getUint256Min() == 0

def test_getUint256Max(testerContractsFixture):
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    assert safeMathUint256Tester.getUint256Max() == (2**256)-1

@mark.parametrize('a, b, base, expectedResult', [
    ((2**(256) - 1), (2**(256) - 1), 10**18, "TransactionFailed"),
    (10**18, 0, 10**18, 0),
    (10**18, 1, 10**18, 1),
    (10**18, 2, 10**18, 2)
])
def test_fxpMul(a, b, base, expectedResult, testerContractsFixture):
    testerContractsFixture.uploadAndAddToController("../tests/solidity_test_helpers/SafeMathUint256Tester.sol")
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            safeMathUint256Tester.fxpMul(a, b, base)
    else:
        assert safeMathUint256Tester.fxpMul(a, b, base) == expectedResult

@mark.parametrize('a, b, base, expectedResult', [
    ((2**(256) - 1), (2**(256) - 1), 10**18, "TransactionFailed"),
    (1, 0, 10**18, "TransactionFailed"),
    (1, 1, 10**18, 10**18)
])
def test_fxpDiv(a, b, base, expectedResult, testerContractsFixture):
    testerContractsFixture.uploadAndAddToController("../tests/solidity_test_helpers/SafeMathUint256Tester.sol")
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            safeMathUint256Tester.fxpDiv(a, b, base)
    else:
        assert safeMathUint256Tester.fxpDiv(a, b, base) == expectedResult

@mark.parametrize('a, b, expectedResult', [
    (1, 1, True),
    (2, 1, True),
    (4, 2, True),
    (9, 3, True),
    (4, 3, False),
    (8, 5, False),
    (2 * 10 ** 18, 10 ** 18, True),
    (2 * 10 ** 18, 2, True),
    (1, 0, "TransactionFailed")
])
def test_isMultipleOf(a, b, expectedResult, testerContractsFixture):
    testerContractsFixture.uploadAndAddToController("../tests/solidity_test_helpers/SafeMathUint256Tester.sol")
    safeMathUint256Tester = testerContractsFixture.contracts['SafeMathUint256Tester']
    if (expectedResult == "TransactionFailed"):
        with raises(TransactionFailed):
            safeMathUint256Tester.isMultipleOf(a, b)
    else:
        assert safeMathUint256Tester.isMultipleOf(a, b) == expectedResult
