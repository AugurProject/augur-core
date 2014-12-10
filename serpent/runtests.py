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

def test_file(*abi, **kwds):
    print BB("  contract:"), BG(kwds["filename"])
    print BB("  function:"), BG(kwds["funid"]), kwds["function"]
    print BB("  input:   "), abi
    # state = kwds.get("state", None)
    # if state is None:
    #     state = tester.state()
    filename = kwds.get("filename", None)
    if filename is not None:
        contract_address = s.contract(filename)
        result = s.send(tester.k0, contract_address, 0,  funid=kwds["funid"], abi=abi)
        print BB("  output:  "), result[0], fracpart(result[1])

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

def test_dot():
    funid = 1
    print BB("  function:"), BG(funid), "dot"
    num_signals = 25    # columns
    num_samples = 10    # rows
    data = (np.random.rand(num_samples, num_signals) * 10).astype(int)
    for i in range(num_signals):
        for j in range(num_signals):
            expected_product = np.dot(data[:,i], data[:,j])
            actual_product = s.send(tester.k0, c, 0, funid=funid, abi=(list(data[:,i]),))
            assert(actual_product - expected_product < tolerance)

def test_outer():
    funid = 2
    print BB("  function:"), BG(funid), "outer"
    result = s.send(tester.k0, c, 0, funid=funid, abi=[])
    print map(fracpart, result)

def test_transpose():
    funid = 3
    print BB("  function:"), BG(funid), "transpose"
    num_rows = 10
    num_cols = 50
    data = np.random.randn(num_rows, num_cols)
    # assert((cumulants.transpose(data, num_rows, num_cols) == data.T).all())

def test_multiply():
    funid = 4
    print BB("  function:"), BG(funid), "multiply"
    for i in range(2, 10):
        
        # square matrices
        A = np.matrix(np.random.randn(i, i))
        B = np.matrix(np.random.randn(i, i))
        expected_product = A * B
        actual_product = cumulants.matrix_multiply(A.tolist(), B.tolist())
        assert((actual_product - expected_product < 1e-12).all())
        
        # rectangular matrices
        j = np.random.randint(1, 10, 1)[0]
        A = np.matrix(np.random.randn(i, j))
        B = np.matrix(np.random.randn(j, i))
        expected_product = A * B
        actual_product = cumulants.matrix_multiply(A.tolist(), B.tolist())
        assert((actual_product - expected_product < 1e-12).all())

def test_kron():
    funid = 5
    print BB("  function:"), BG(funid), "kron"
    num_signals = 10     # columns
    num_samples = 50     # rows
    data = np.random.randn(num_samples, num_signals)
    for i in range(num_signals):
        for j in range(num_signals):
            expected_product = np.kron(data[:,i], data[:,j])
            actual_product = cumulants.kron(data[:,i], data[:,j], num_samples)
            assert((actual_product - expected_product < 1e-15).all())

def main():
    global s, c, FILENAME
    print BR("Forming new test genesis block")
    s = tester.state()
    FILENAME = "tests.se"
    print BR("Compiling " + FILENAME)
    c = s.contract(FILENAME)
    # print BR("Testing " + FILENAME)
    print BB("Testing contract:"), BG(FILENAME)
    # mean
    # u = [1, 4, 4, 2]
    # test_file(u, filename=FILENAME, funid=0, function="mean")
    test_mean()
    # test_dot()
    test_outer()
    # test_transpose()
    # test_multiply()
    # test_kron()

if __name__ == "__main__":
    main()
