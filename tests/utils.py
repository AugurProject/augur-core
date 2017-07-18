#!/usr/bin/env python

from json import loads
from decimal import Decimal

def fix(n, m = 1):
    return long(Decimal(n) * Decimal(m) * 10**18)

def unfix(n):
    return n // 10**18

def longToHexString(value):
    hexStr = hex(value)[2:-1]
    while len(hexStr) < leftPad:
        hexStr = '0' + hexStr
    if(hexStr[0:2] == '0x'):
        return hexStr
    else:
        return '0x' + hexStr

def bytesToLong(value):
    return long(value.encode('hex'), 16)

def bytesToHexString(value):
    hexStr = longToHexString(bytesToLong(value))
    if(hexStr[0:2] == '0x'):
        return hexStr
    else:
        return '0x' + hexStr

def captureFilteredLogs(state, contract, logs):
    def captureLog(contract, logs, message):
        translated = contract.translator.listen(message)
        if not translated: return
        logs.append(translated)
    state.log_listeners.append(lambda x: captureLog(contract, logs, x))
