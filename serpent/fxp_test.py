#!/usr/bin/python2
from pyethereum import tester as t
import gmpy2
import random
import sys

gmpy2.get_context().precision = 256

def printf(stuff):
    sys.stdout.write(stuff)
    sys.stdout.flush()

def main():
    code = '''\
def init():
    fxp_init(0)

def ln(x):
    return(fxp_log(x))

inset('fxp_macros.se')
'''
    s = t.state()
    printf('Compiling...\t')
    c = s.abi_contract(code)
    printf('Done.\n')
    s.mine(1)

    total_error = 0
    for i in range(30):
        print i
        x = random.randrange(int(gmpy2.exp(100)))
        expected = int(gmpy2.log(x) * 2**64)
        print len(bin(x)) - 2
        result = c.ln(x << 64)
        total_error += abs((result - expected))/float(expected)
    printf('average log error = {:3.4%}\n'.format(total_error/49.0))        

if __name__ == '__main__':
    main()
