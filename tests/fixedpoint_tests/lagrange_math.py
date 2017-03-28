#!/usr/bin/python2
from test_suite import *
from collections import OrderedDict
import numpy as np
import scipy
import scipy.interpolate

LN2 = hex(int(gmpy2.log(2.0)*10**18)).strip('L')
LOG2E = hex(int(gmpy2.log2(gmpy2.exp(1))*10**18)).strip('L')

def log_interp(n):
    xs = np.linspace(1, 2, n+2)
    p = scipy.interpolate.lagrange(xs, map(gmpy2.log2, xs))
    coeffs = [hex(int(a_i*10**18)).strip('L') for a_i in list(reversed(p.coeffs))]
    code = '''
def log{0}(x):
    y = ilog2(x)
    z = x / 2^y
    return((y*10^18 + log2_{0}(z))*10^18/{1})

macro log2_{0}($x):
    with $xpow = 10^18:
        with $result = 0:
'''
    code = code.format(n, LOG2E)
    T = ' '*12
    for a_i in coeffs[:-1]:
        code += T + '$result += %s*$xpow/10^18\n'%a_i
        code += T + '$xpow = $xpow*$x/10^18\n'
    code += T + '$result + %s*$xpow/10^18\n'%coeffs[-1]
    return code

def log_test_code(max_n):
    ilog2 = '''
macro ilog2($x):
    with $y = $x / 10^18:
        with $lo = 0:
            with $hi = 191:
                with $mid = ($lo + $hi)/2:
                    while $lo < $hi:
                        if 2^$mid > $y:
                            $hi = $mid - 1
                        else:
                            $lo = $mid + 1
                        $mid = ($lo + $hi)/2
                    $lo
'''
    return ilog2 + ''.join(map(log_interp, range(1, max_n+1)))

def exp_interp(n):
    xs = np.linspace(0, 1, n+2)
    p = scipy.interpolate.lagrange(xs, map(gmpy2.exp2, xs))
    coeffs = [hex(int(a_i*10**18)).strip('L') for a_i in list(reversed(p.coeffs))[1:]]
    code = '''
def exp{0}(x):
    y = x * 10^18 / {1}
    z = y % 10^18
    return(2^(y / 10^18)*lpow2_{0}(z))

macro lpow2_{0}($x):
    with $xpow = $x:
        with $result = 10^18:
'''
    code = code.format(n, LN2)
    T = ' '*12
    for a_i in coeffs[:-1]:
        code += T + '$result += %s*$xpow/10^18\n'%a_i
        code += T + '$xpow = $xpow*$x/10^18\n'
    code += T + '$result + %s*$xpow/10^18\n' % coeffs[-1]
    return code

def exp_test_code(max_n):
    return ''.join(map(exp_interp, range(1, max_n+1)))

def main():
    with timer():
        max_n = 14
        ecode = exp_test_code(max_n)
        lcode = log_test_code(max_n)
        trials = 100

        efunc_dict = OrderedDict()
        exp_max = 128
        for i in range(1,max_n+1):
            efunc_dict['exp%d'%i] = ([0, exp_max], gmpy2.exp)

        lfunc_dict = OrderedDict()
        log_max = gmpy2.exp(128)
        for i in range(1,max_n+1):
            lfunc_dict['log%d'%i] = ([0, log_max], gmpy2.log)

        print "Testing exp code"
        test_code(ecode, efunc_dict, trials)
        print "Testing log code"
        test_code(lcode, lfunc_dict, trials)

if __name__ == '__main__':
    main()
