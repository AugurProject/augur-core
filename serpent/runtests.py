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

def test_mean():
    print BB("  function:"), BG(0), "mean"
    num_signals = 25      # columns
    num_samples = 10      # rows
    data = (np.random.rand(num_samples, num_signals) * 10).astype(int)
    expected_mean = np.mean(data, 0)
    for i in range(num_signals):
        result = s.send(tester.k0, c, 0, funid=0, abi=(list(data[:,i]),))
        actual_mean = result[0] + fracpart(result[1])
        assert(actual_mean - expected_mean[i] < tolerance)

def test_contract(contract):
    if contract == "dot":
        filename = contract + ".se"
        print BB("Testing contract:"), BG(filename)
        c = s.contract(filename)
        num_signals = 7    # columns
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
    else:
        filename = contract + ".se"
        print BB("Testing contract:"), BG(filename)
        c = s.contract(filename)
        result = s.send(tester.k0, c, 0, funid=0, abi=[])
        try:
            assert(result == [1])
        except:
            print(result)

def main():
    global s, c, FILENAME
    print BR("Forming new test genesis block")
    s = tester.state()
    FILENAME = "tests.se"
    print BR("Compiling " + FILENAME)
    c = s.contract(FILENAME)
    print BB("Testing contract:"), BG(FILENAME)
    test_mean()
    contracts = ["dot",
                 "outer",
                 "transpose",
                 "multiply",
                 "kron",
                 "diag",
                 "isnan",
                 "mask",
                 "any",
                 "hadamard"]
    for contract in contracts:
        test_contract(contract)

if __name__ == "__main__":
    main()
