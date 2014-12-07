#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    import colorama
except ImportError:
    pass
from pyethereum import tester
from random import random
import math

def test_file(*stuff, **kwds):
    state = kwds.get("state", None)
    if state is None:
        state = tester.state()
    filename = kwds.get("filename", "test.se")
    contract_address = state.contract(filename)
    return state.send(tester.k0,
                      contract_address,
                      0, 
                      funid=kwds["funid"],
                      abi=stuff)

def BR(string): # bright red
    return "\033[1;31m" + string + "\033[0m"

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

def main():
    global s, c
    print(BR("Forming new test genesis block"))
    s = tester.state()
    FILENAME = "cumulants.se"
    print(BR("Compiling " + FILENAME))
    c = s.contract(FILENAME)
    result = test_file(1, filename=FILENAME, funid=1)
    print(result)

if __name__ == "__main__":
    main()
