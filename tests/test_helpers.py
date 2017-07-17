#!/usr/bin/env python

from ethereum.tools import tester as tester
from ethereum.abi import ContractTranslator
from ethereum.tools.tester import ABIContract
from ethereum import utils as u
from ethereum.config import config_metropolis, Env
from ethereum.tools.tester import TransactionFailed
from ethereum.exceptions import InsufficientBalance
from os import path
from pytest import raises, fixture
from utils import fix

config_metropolis['BLOCK_GAS_LIMIT'] = 2**60

def test_assertNoValue(block, assertNoValue):
    balanceBefore = 0
    balanceAfter = 0
    chain = assertNoValue[0]

    balanceBefore = chain.head_state.get_balance(tester.a2)
    startingGasUsed = chain.head_state.gas_used

    assertNoValue[1].assertNoValue(sender=tester.k2)
    with raises(TransactionFailed):
        assertNoValue[1].assertNoValue(value=500*10**18, sender=tester.k2)

    balanceAfter = chain.head_state.get_balance(tester.a2)
    assert balanceBefore == balanceAfter

def test_add(floatTest):
    assert(floatTest.add(5, 10)==15)
    assert(floatTest.add(500, 100)==600)
    assert(floatTest.add(2**200, 2**20)==2**200 + 2**20)
    with raises(TransactionFailed):
        floatTest.add(5, -10)
    with raises(TransactionFailed):
        floatTest.add(-15, 11)
    with raises(TransactionFailed):
        floatTest.add(2**255-1, 50)

def test_subtract(floatTest):
    assert(floatTest.subtract(2**255-1, 50)==(2**255-1 - 50))
    assert(floatTest.subtract(500, 50)==450)
    assert(floatTest.subtract(2**222, 47) == (2**222 - 47))
    with raises(TransactionFailed):
        floatTest.subtract(5, -10)
    with raises(TransactionFailed):
        floatTest.subtract(-15, 11)
    with raises(TransactionFailed):
        floatTest.subtract(0, 1)

def test_multiply(floatTest):
    assert(floatTest.multiply(2**200, 50) == (2**200 * 50))
    assert(floatTest.multiply(500, 50) == 25000)
    assert(floatTest.multiply(2**222, 47) == 2**222 * 47)
    assert(floatTest.multiply(0, 47) == 0)
    with raises(TransactionFailed):
        floatTest.multiply(2**255-1, 3)
    with raises(TransactionFailed):
        floatTest.multiply(2**255-1, -10)

def test_fxp_multiply(floatTest):
    assert(floatTest.fxpMultiply(fix('3'), fix('5')) == fix('15'))
    assert(floatTest.fxpMultiply(fix('500'), fix('50')) == fix('25000'))
    assert(floatTest.fxpMultiply(fix('-44'), fix('2')) == fix('-88'))
    assert(floatTest.fxpMultiply(0, fix('47')) == 0)
    with raises(TransactionFailed):
        floatTest.fxpMultiply(2**255-1, fix('3'))
    with raises(TransactionFailed):
        floatTest.fxpMultiply(2**255-1, fix('-10'))

def test_divide(floatTest):
    assert(floatTest.divide(2**200, 50) == (2**200 / 50))
    assert(floatTest.divide(500, 50) == 10)
    assert(floatTest.divide(2**222, 47) == 2**222 / 47)
    assert(floatTest.divide(0, 47) == 0)
    with raises(TransactionFailed):
        floatTest.divide(2**255-1, 0)
    with raises(TransactionFailed):
        floatTest.divide(2**22-1, 0)

def test_fxp_divide(floatTest):
    assert(floatTest.fxpDivide(fix('3'), fix('5')) == fix('3')/5)
    assert(floatTest.fxpDivide(fix('500'), fix('50')) == fix('10'))
    assert(floatTest.fxpDivide(fix('-44'), fix('2')) == fix('-22'))
    assert(floatTest.fxpDivide(0, fix('47')) == 0)
    with raises(TransactionFailed):
        floatTest.fxpDivide(fix('30'), 0)
    with raises(TransactionFailed):
        floatTest.fxpDivide(2**250, fix('-10'))

@fixture(scope="session")
def chain():
    return tester.Chain(env=Env(config=config_metropolis))

@fixture(scope="session")
def block(chain):
    return chain.block

SERPENT_TEST_HELPERS = path.join(path.dirname(path.realpath(__file__)), "serpent_test_helpers")

@fixture(scope="session")
def assertNoValue(chain):
    return chain, chain.contract(path.join(SERPENT_TEST_HELPERS, "assertNoValue.se"), language="serpent", startgas=long(6.7 * 10**6))

@fixture(scope="session")
def floatTest(chain):
    return chain.contract(path.join(SERPENT_TEST_HELPERS, "safeMath.se"), language="serpent", startgas=long(6.7 * 10**6))
