#!/usr/bin/python2
import gmpy2
from pyethereum import tester as t
import random
import numpy as np
import scipy
import scipy.interpolate
from collections import namedtuple
import sys

gmpy2.get_context().precision = 256
TestResults = namedtuple('TestResults', 'average_error average_gas')

LN2 = hex(int(gmpy2.log(2.0)*2**64)).strip('L')
LOG2E = hex(int(gmpy2.log2(gmpy2.exp(1))*2**64)).strip('L')

def log_interp(n):
    xs = np.linspace(1, 2, n+2)
    p = scipy.interpolate.lagrange(xs, map(gmpy2.log2, xs))
    coeffs = [hex(int(a_i*2**64)).strip('L') for a_i in list(reversed(p.coeffs))]
    code = '''
def log{0}(x):
    y = ilog2(x)
    z = x / 2^y
    return((y*2^64 + log2_{0}(z))*2^64/{1})

macro log2_{0}($x):
    with $xpow = 2^64:
        with $result = 0:
'''
    code = code.format(n, LOG2E)
    T = ' '*12
    for a_i in coeffs[:-1]:
        code += T + '$result += %s*$xpow/2^64\n'%a_i
        code += T + '$xpow = $xpow*$x/2^64\n'
    code += T + '$result + %s*$xpow/2^64\n'%coeffs[-1]
    return code

def log_test_code(max_n):
    ilog2 = '''
macro ilog2($x):
    with $y = $x / 2^64:
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
    coeffs = [hex(int(a_i*2**64)).strip('L') for a_i in list(reversed(p.coeffs))[1:]]
    code = '''
def exp{0}(x):
    y = x * 2^64 / {1}
    z = y % 2^64
    return(2^(y / 2^64)*lpow2_{0}(z))

macro lpow2_{0}($x):
    with $xpow = $x:
        with $result = 2^64:
'''
    code = code.format(n, LN2)
    T = ' '*12
    for a_i in coeffs[:-1]:
        code += T + '$result += %s*$xpow/2^64\n'%a_i
        code += T + '$xpow = $xpow*$x/2^64\n'
    code += T + '$result + %s*$xpow/2^64\n' % coeffs[-1]
    return code

def exp_test_code(max_n):
    return ''.join(map(exp_interp, range(1, max_n+1)))

def test_thunk(thunk, trials):
    error = 0
    gas = 0
    for i in range(int(trials)):
        sys.stdout.write('Trials: %d\r'%i)
        sys.stdout.flush()
        expected, result = thunk()
        result['output'] /= float(2**64)
        error += abs(result['output'] - expected)/expected
        gas += result['gas']
    sys.stdout.write('\n')
    sys.stdout.flush()
    return TestResults(float(100*error/trials), gas/float(trials))

def main():
    max_n = 14
    trials = 100
    if len(sys.argv) < 2:
        print 'Usage:'
        print '\t./lagrange_math.py <func>'
        print 'Where func can be exp or log.'
        sys.exit(1)
    elif sys.argv[1] == 'exp':
        code = exp_test_code(max_n)
        ref_func = gmpy2.exp
    elif sys.argv[1] == 'log':
        code = log_test_code(max_n)
        ref_func = gmpy2.log
    else:
        print "not implemented"
        sys.exit(1)
    print code
    print 'Compiling...'
    s = t.state()
    c = s.abi_contract(code)
    for i in range(1, max_n+1):
        func = '%s%d' % (sys.argv[1], i)
        print 'Testing', func
        def thunk():
            x = random.random()*128
            testf = lambda x: vars(c)[func](int(x*2**64), profiling=True)
            return ref_func(x), testf(x)
        print test_thunk(thunk, trials)
    sys.exit(0)

if __name__ == '__main__':
    main()
