#!/usr/bin/env python

from json import loads
from decimal import Decimal
import struct

def fix(n, m = 1):
    return long(Decimal(n) * Decimal(m) * 10**18)

def unfix(n):
    return n // 10**18

def stringToBytes(value):
    return value.ljust(32, '\x00')

def longTo32Bytes(value):
    return struct.pack(">l", value).rjust(32, '\x00')

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
