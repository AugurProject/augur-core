#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
try:
    from colorama import Fore, Style, init
except ImportError:
    pass
from pyethereum import tester

np.set_printoptions(linewidth=500)
tolerance = 1e-12
init()

def BR(string): # bright red
    return "\033[1;31m" + str(string) + "\033[0m"

def BB(string): # bright blue
    return Fore.BLUE + Style.BRIGHT + str(string) + Style.RESET_ALL

def BG(string): # bright green
    return Fore.GREEN + Style.BRIGHT + str(string) + Style.RESET_ALL

def blocky(*strings, **kwds):
    colored = kwds.get("colored", True)
    width = kwds.get("width", 108)
    bound = width*"#"
    fmt = "#{:^%d}#" % (width - 2)
    lines = [bound]
    for string in strings:
        lines.append(fmt.format(string))
    lines.append(bound)
    lines = "\n".join(lines)
    if colored:
        lines = BR(lines)
    return lines

def fracpart(x):
    return float(x & (2**64 - 1)) / 2**64

def unfix(x):
    return x / 0x10000000000000000

def test_contract(contract):
    filename = contract + ".se"
    if contract == "dot":
        print BB("Testing contract:"), BG(filename)
        c = s.contract(filename)
        num_signals = 10   # columns
        num_samples = 5    # rows
        data = (np.random.rand(num_samples, num_signals) * 10).astype(int)
        for i in range(num_signals):
            for j in range(num_signals):
                expected = np.dot(data[:,i], data[:,j])
                actual = s.send(tester.k0, c, 0, funid=0, abi=(list(data[:,i]),))
                try:
                    assert(actual - expected < tolerance)
                except:
                    print(actual)
    elif contract == "mean":
        print BB("Testing contract:"), BG(filename)
        c = s.contract(filename)
        num_signals = 10      # columns
        num_samples = 5       # rows
        data = (np.random.rand(num_samples, num_signals) * 10).astype(int)
        expected = np.mean(data, 0)
        for i in range(num_signals):
            result = s.send(tester.k0, c, 0, funid=0, abi=(list(data[:,i]),))
            actual = unfix(result[0])
            try:
                assert(actual - expected[i] < tolerance)
            except:
                print(actual)
    else:
        print BB("Testing contract:"), BG(filename)
        c = s.contract(filename)
        result = s.send(tester.k0, c, 0, funid=0, abi=[])
        try:
            assert(result == [1])
        except:
            try:
                assert(map(unfix, result) == [1])
            except:
                print "result:   ", result
                print "base 16:  ", map(hex, result)
                print "base 2^64:", map(unfix, result)

def main():
    global s, FILENAME
    print BR("Forming new test genesis block")
    s = tester.state()
    contracts = [
        "sum",
        "mean",
        "normalize",
        "dot",
        "outer",
        "multiply",
        "kron",
        "hadamard",
        "transpose",
        "diag",
        "isnan",
        "mask",
        "any",
        "interpolate",
    ]
    for contract in contracts:
        test_contract(contract)

if __name__ == "__main__":
    main()
