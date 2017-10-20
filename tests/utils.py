#!/usr/bin/env python

from json import loads
from decimal import Decimal
from struct import pack

def fix(n, m = 1):
    return long(Decimal(n) * Decimal(m) * 10**18)

def unfix(n):
    return n // 10**18

def stringToBytes(value):
    return value.ljust(32, '\x00')

def longTo32Bytes(value):
    return pack(">l", value).rjust(32, '\x00')

def longToHexString(value, leftPad=40):
    # convert the value to a hex string, strip off the `0x`, strip off any trailing `L`, pad with zeros, prefix with `0x`
    return '0x' + hex(value)[2:].rstrip('L').zfill(leftPad)

def bytesToLong(value):
    return long(value.encode('hex'), 16)

def bytesToHexString(value):
    return longToHexString(bytesToLong(value))

def captureFilteredLogs(state, contract, logs):
    def captureLog(contract, logs, message):
        translated = contract.translator.listen(message)
        if not translated: return
        logs.append(translated)
    state.log_listeners.append(lambda x: captureLog(contract, logs, x))

class TokenDelta():
    
    def __init__(self, token, delta, account, err=""):
        self.account = account
        self.token = token
        self.delta = delta
        self.err = err

    def __enter__(self):
        self.originalBalance = self.token.balanceOf(self.account)
    
    def __exit__(self, *args):
        if args[1]:
            raise args[1]
        originalBalance = self.originalBalance
        newBalance = self.token.balanceOf(self.account)
        delta = self.delta
        resultDelta = newBalance - originalBalance
        assert resultDelta == delta, self.err + ". Delta EXPECTED: %i ACTUAL: %i DIFF: %i" % (delta, resultDelta, delta - resultDelta)

class ETHDelta():
    
    def __init__(self, delta, account, chain, err=""):
        self.account = account
        self.chain = chain
        self.delta = delta
        self.err = err

    def __enter__(self):
        self.originalBalance = self.chain.head_state.get_balance(self.account)
    
    def __exit__(self, *args):
        if args[1]:
            raise args[1]
        originalBalance = self.originalBalance
        newBalance = self.chain.head_state.get_balance(self.account)
        delta = self.delta
        resultDelta = newBalance - originalBalance
        assert resultDelta == delta, self.err + ". Delta EXPECTED: %i ACTUAL: %i DIFF: %i" % (delta, resultDelta, delta - resultDelta)

class PrintGasUsed():

    def __init__(self, fixture, action):
        self.fixture = fixture
        self.action = action
 
    def __enter__(self):
        self.startingGas = self.fixture.chain.head_state.gas_used
     
    def __exit__(self, *args):
        if args[1]:
            raise args[1]
        gasUsed = self.fixture.chain.head_state.gas_used - self.startingGas
        print "GAS USED WITH %s : %i" % (self.action, gasUsed)
