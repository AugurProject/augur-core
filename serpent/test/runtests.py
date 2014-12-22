#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from pprint import pprint
import numpy as np
try:
    from colorama import Fore, Style, init
except ImportError:
    pass
from pyethereum import tester as t

np.set_printoptions(linewidth=500)
                    # precision=5,
                    # suppress=True,
                    # formatter={"float": "{: 0.3f}".format})
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

def fix(x):
    return int(x * 0x10000000000000000)

def unfix(x):
    return x / 0x10000000000000000

def test_contract(contract):
    filename = contract + ".se"
    print BB("Testing contract:"), BG(filename)
    c = s.contract(filename)
    if contract == "dot":
        num_signals = 10   # columns
        num_samples = 5    # rows
        data = (np.random.rand(num_samples, num_signals) * 10).astype(int)
        for i in range(num_signals):
            for j in range(num_signals):
                expected = np.dot(data[:,i], data[:,j])
                actual = s.send(t.k0, c, 0, funid=0, abi=(list(data[:,i]),))
                try:
                    assert(actual - expected < tolerance)
                except:
                    print(actual)
    elif contract == "mean":
        num_signals = 10      # columns
        num_samples = 5       # rows
        data = (np.random.rand(num_samples, num_signals) * 10).astype(int)
        expected = np.mean(data, 0)
        for i in range(num_signals):
            result = s.send(t.k0, c, 0, funid=0, abi=(list(data[:,i]),))
            actual = unfix(result[0])
            try:
                assert(actual - expected[i] < tolerance)
            except:
                print(actual)
    elif contract == "interpolate":
        result = s.send(t.k0, c, 0, funid=0, abi=[])
        actual = map(unfix, result)
        expected = [0.94736842105263164, 0.30769230769230776, 0.38461538461538469, 0.33333333333333337]
        try:
            assert((np.asarray(actual) - np.asarray(expected) < tolerance).all())
        except:
            print(actual)
    elif contract in ("../consensus", "../consensus-readable"):
        # old: true=10, false=0, indeterminate=5, no response=-1
        # reports = np.array([[10, 10,  0, -1],
        #                     [10,  0,  0,  0],
        #                     [10, 10,  0,  0],
        #                     [10, 10, 10,  0],
        #                     [-1,  0, 10, 10],
        #                     [ 0,  0, 10, 10]])
        # reports = np.array([[10, 10,  0, 10],
        #                     [10,  0,  0,  0],
        #                     [10, 10,  0,  0],
        #                     [10, 10, 10,  0],
        #                     [10,  0, 10, 10],
        #                     [ 0,  0, 10, 10]])
        # new: true=1, false=-1, indeterminate=0.5, no response=0
        reports = np.array([[  1,  1, -1,  0],
                            [  1, -1, -1, -1],
                            [  1,  1, -1, -1],
                            [  1,  1,  1, -1],
                            [  0, -1,  1,  1],
                            [ -1, -1,  1,  1]])
        # reports = np.array([[  1,  1, -1,  1],
        #                     [  1, -1, -1, -1],
        #                     [  1,  1, -1, -1],
        #                     [  1,  1,  1, -1],
        #                     [  1, -1,  1,  1],
        #                     [ -1, -1,  1,  1]])
        reputation = [2, 10, 4, 2, 7, 1]
        result = s.send(t.k0, c, 0, funid=0, abi=[map(fix, reports.flatten()), map(fix, reputation), 5])
        try:
            assert(result == [1])
        except:
            try:
                assert(map(unfix, result) == [1])
            except:
                if len(result) < 4:
                    print "result:   ", result
                    print "base 16:  ", map(hex, result)
                    print "base 2^64:", map(unfix, result)
                else:
                    print "result:   "
                    pprint(result)
                    print "base 16:  "
                    pprint(map(hex, result))
                    print "base 2^64:"
                    pprint(map(unfix, result))
    else:
        result = s.send(t.k0, c, 0, funid=0, abi=[])
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
    global s
    print BR("Forming new test genesis block")
    s = t.state()
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
        "catch",
        "get_weight",
        "interpolate",
        "fixedpoint",
        "../consensus",
        # "../consensus-readable",
    ]
    for contract in contracts:
        test_contract(contract)

if __name__ == "__main__":
    main()
