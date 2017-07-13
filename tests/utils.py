#!/usr/bin/env python

from json import loads
from decimal import Decimal

def fix(n, m = 1):
    return long(Decimal(n) * Decimal(m) * 10**18)

def unfix(n):
    return n // 10**18

def longToHexString(value):
    hexstr = hex(value)[2:-1]
    if len(hexstr) % 2 != 0:
        hexstr = '0' + hexstr
    return hexstr

def bytesToLong(value):
    return long(value.encode('hex'), 16)

def bytesToHexString(value):
    return longToHexString(bytesToLong(value))

def captureFilteredLogs(state, contract, logs):
    def captureLog(contract, logs, message):
        translated = contract.translator.listen(message)
        if not translated: return
        logs.append(translated)
    state.block.log_listeners.append(lambda x: captureLog(contract, logs, x))
