#!/usr/bin/env python

import ethereum
from ethereum import tester as test
import math
import random
import os
import sys
import time
import binascii

SERPENT_TEST_HELPERS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "serpent_test_helpers")

WEI_TO_ETH = 10**18
TWO = 2*WEI_TO_ETH
HALF = WEI_TO_ETH/2

def nearly_equal(a, b, sig_fig=8):
    return(a == b or int(a * 10**sig_fig) == int(b * 10**sig_fig))

def isclose(a, b, rel_tol=1e-10, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def test_assertNoValue():
    state = test.state()
    c = state.abi_contract(os.path.join(SERPENT_TEST_HELPERS, "testAssertNoValue.se"))
    balanceBefore = 0
    balanceAfter = 0
    try:
        balanceBefore = state.block.get_balance(test.a2)
    except:
        balanceBefore = state.state.get_balance(test.a2)
    c.testAssertNoValue(sender=test.k2)
    try:
        raise Exception(c.testAssertNoValue(value=500*10**18, sender=test.k2))
    except Exception as exc:
        assert(isinstance(exc, ethereum.tester.TransactionFailed)), "throw if testAssertNoValue has value > 0"
    try:
        balanceAfter = state.block.get_balance(test.a2)
    except:
        balanceAfter = state.state.get_balance(test.a2)
    print balanceAfter
    print balanceBefore
    assert(isclose(balanceBefore, balanceAfter) == True)

def test_float():
    s = test.state()
    c = s.abi_contract(os.path.join(SERPENT_TEST_HELPERS, "floatTest.se"))
    def test_add():
        assert(c.add(5, 10)==15)
        assert(c.add(500, 100)==600)
        assert(c.add(2**200, 2**20)==2**200 + 2**20)
        try:
            raise Exception(c.add(5, -10))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
        try:
            raise Exception(c.add(-15, 11))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
        try:
            raise Exception(c.add(2**255-1, 50))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
    def test_subtract():
        assert(c.subtract(2**255-1, 50)==(2**255-1 - 50))
        assert(c.subtract(500, 50)==450)
        assert(c.subtract(2**222, 47) == (2**222 - 47))
        try:
            raise Exception(c.subtract(5, -10))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
        try:
            raise Exception(c.subtract(-15, 11))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
        try:
            raise Exception(c.subtract(0, 1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
    def test_multiply():
        assert(c.multiply(2**200, 50) == (2**200 * 50))
        assert(c.multiply(500, 50) == 25000)
        assert(c.multiply(2**222, 47) == 2**222 * 47)
        assert(c.multiply(0, 47) == 0)
        try:
            raise Exception(c.multiply(2**255-1, 3))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
        try:
            raise Exception(c.multiply(2**255-1, -10))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
    def test_fxp_multiply():
        assert(c.fxpMultiply(3*WEI_TO_ETH, 5*WEI_TO_ETH) == 15*WEI_TO_ETH)
        assert(c.fxpMultiply(500*WEI_TO_ETH, WEI_TO_ETH*50) == 25000*WEI_TO_ETH)
        assert(c.fxpMultiply(-44*WEI_TO_ETH, 2*WEI_TO_ETH) == -88*WEI_TO_ETH)
        assert(c.fxpMultiply(0, 47*WEI_TO_ETH) == 0)
        try:
            raise Exception(c.fxpMultiply(2**255-1*WEI_TO_ETH, 3*WEI_TO_ETH))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
        try:
            raise Exception(c.fxpMultiply(2**255-1, -10*WEI_TO_ETH))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
    def test_divide():
        assert(c.divide(2**200, 50) == (2**200 / 50))
        assert(c.divide(500, 50) == 10)
        assert(c.divide(2**222, 47) == 2**222 / 47)
        assert(c.divide(0, 47) == 0)
        try:
            raise Exception(c.divide(2**255-1, 0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
        try:
            raise Exception(c.divide(2**22-1, 0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
    def test_fxp_divide():
        assert(c.fxpDivide(3*WEI_TO_ETH, 5*WEI_TO_ETH) == 3*WEI_TO_ETH/5)
        assert(c.fxpDivide(500*WEI_TO_ETH, WEI_TO_ETH*50) == 10*WEI_TO_ETH)
        assert(c.fxpDivide(-44*WEI_TO_ETH, 2*WEI_TO_ETH) == -22*WEI_TO_ETH)
        assert(c.fxpDivide(0, 47*WEI_TO_ETH) == 0)
        try:
            raise Exception(c.fxpDivide(30*WEI_TO_ETH, 0))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
        try:
            raise Exception(c.fxpDivide(2**250, -10*WEI_TO_ETH))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"

    test_add()
    test_subtract()
    test_multiply()
    test_fxp_multiply()
    test_divide()
    test_fxp_divide()


# def test_controller(contracts, state, t):
    ### Useful for controller testing
        # from ethereum import tester as t
        # import ethereum
        # import serpent
        # import sha3
        # s = t.state()
        # c = s.abi_contract('functions/controller.se')
        # x = ethereum.abi.ContractTranslator(serpent.mk_full_signature('functions/controller.se'))
        # y = x.encode_function_call("setValue", [5])
        # sha3.sha3_256(y).hexdigest()

        # import binascii
        # binascii.hexlify()

if __name__ == '__main__':
    test_assertNoValue()
    test_float()
    # test_controller()
