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

def test_file(*abi, **kwds):
    print BB("  contract:"), BG(kwds["filename"])
    print BB("  function:"), BG(kwds["funid"]), kwds["function"]
    print BB("  input:   "), abi
    state = kwds.get("state", None)
    if state is None:
        state = tester.state()
    filename = kwds.get("filename", None)
    if filename is not None:
        contract_address = state.contract(filename)
        result = state.send(tester.k0, contract_address, 0,  funid=kwds["funid"], abi=abi)
        print BB("  output:  "), result
        return result

def test_mean():
    print(BR("Testing mean"))
    num_signals = 25     # columns
    num_samples = 500    # rows
    data = np.random.randn(num_samples, num_signals)
    expected_mean = np.mean(data, 0)
    for i in range(num_signals):
        actual_mean = cumulants.mean(data[:,i], num_samples)
        assert(actual_mean - expected_mean[i] < tolerance)

def main():
    global s, c
    print BR("Forming new test genesis block")
    s = tester.state()
    FILENAME = "linalg.se"
    print BR("Compiling " + FILENAME)
    c = s.contract(FILENAME)
    print BR("Testing " + FILENAME)
    # mean
    u = [1, 4, 4, 2]
    test_file(u, len(u), filename=FILENAME, funid=0, function="mean")

if __name__ == "__main__":
    main()
