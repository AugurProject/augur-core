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

def func(n):
    return(fxp_exp(n))
inset('fxp_macros.se')
'''
    s = t.state()    
    printf('Compiling...\t')
    c = s.abi_contract(code)
    printf('Done.\n')

    total_error = 0
    for i in range(2,100,2):
        x = gmpy2.mpfr(i + 2*random.random())
        expected = int(gmpy2.exp(x)*2**64)
        result = c.func(int(x*2**64))[0]
        total_error += abs((result - expected))/float(expected)
    printf('average error = {:3.2%}\n'.format(total_error/49.0))

if __name__ == '__main__':
    main()
