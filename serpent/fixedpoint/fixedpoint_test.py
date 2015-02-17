#!/usr/bin/python2
from test_suite import *

def main():
    with timer():
        func_dict = {
            'exp_e':  ([0, 128], gmpy2.exp),
            'ln':  ([0, int(gmpy2.exp(128))], gmpy2.log),
        }
        trials = 100
        test_code('fixedpoint.se', func_dict, trials)

if __name__ == '__main__':
    main()
