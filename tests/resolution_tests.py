#!/usr/bin/env python

import ethereum
from ethereum import tester as test
import math
import random
import os
import sys
import time
import binascii
import iocapture
from pprint import pprint
import json

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))

from upload_contracts import ContractLoader

WEI_TO_ETH = 10**18
TWO = 2*WEI_TO_ETH
HALF = WEI_TO_ETH/2

def parseCapturedLogs(captured):
    return json.loads(captured.stdout.replace("'", '"').replace('u"', '"'))

def nearly_equal(a, b, sig_fig=8):
    return(a == b or int(a * 10**sig_fig) == int(b * 10**sig_fig))

def isclose(a, b, rel_tol=1e-10, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def test_refund(contracts, state, t):
    def test_refund_funds():
        balanceBefore = state.block.get_balance(t.a2)
        contracts.orders.commitOrder(5, value=500*10**18, sender=t.k2)
        balanceAfter = state.block.get_balance(t.a2)
        assert(isclose(balanceBefore, balanceAfter) == True)
    def test_caller_whitelisted():
        try:
            raise Exception(contracts.backstops.setDisputedOverEthics(5, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that checks whitelist should fail from a non-whitelisted address"
    def test_invalid():
        contracts.mutex.acquire()
        try:
            raise Exception(contracts.mutex.acquire())
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "a call that throws should actually throw the transaction so it fails"
    test_refund_funds()
    test_caller_whitelisted()
    test_invalid()

def test_float():
    s = test.state()
    c = s.abi_contract('floatTestContract.se')
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

def test_logReturn():
    s = test.state()
    c = s.abi_contract('logReturnTest.se')
    def test_logReturn():
        assert(c.testLogReturnContractCall(444) == 444)
        assert(c.testLogReturnContractCall(-444) == -444)
        with iocapture.capture() as captured:
            retval = c.testLogReturn(5)
            logged = parseCapturedLogs(captured)
            assert(logged["_event_type"] == u'tradeLogReturn')
            assert(logged["returnValue"] == 5)
        with iocapture.capture() as captured:
            retval = c.testLogArrayReturn([5, 10, 15])
            logged = parseCapturedLogs(captured)
            assert(logged["_event_type"] == u'tradeLogArrayeturn')
            assert(logged["returnArray"] == [5, 10, 15])
    test_logReturn()

def test_eventBondResolution(controller, state, t):
    s = test.state()
    c = s.abi_contract('floatTestContract.se')

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
    src = os.path.join(os.getenv('AUGUR_CORE', os.path.join(os.getenv('HOME', '/home/ubuntu'), 'workspace')), 'src')
    contracts = ContractLoader(src, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'])
    state = contracts._ContractLoader__state
    t = contracts._ContractLoader__tester
    test_refund(contracts, state, t)
    test_float()
    test_logReturn()
    test_eventBondResolution(contracts, state, t)
    # test_closeMarket(contracts, state, t)
    # test_controller(contracts, state, t)
    print "DONE TESTING RESOLUTION TESTS"

