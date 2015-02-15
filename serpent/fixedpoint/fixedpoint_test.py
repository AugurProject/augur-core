#!/usr/bin/python2
from test_suite import *

def main():
    func_dict = {
        'exp':  ([0, 128], gmpy2.exp),
        'log':  ([0, int(gmpy2.exp(128))], gmpy2.log),
        'sqrt': ([0, int(gmpy2.exp(128))], gmpy2.sqrt)
    }
    trials = 100
    test_code('fixedpoint.se', func_dict, trials)

if __name__ == '__main__':
    main()
