#!/usr/bin/python2
import gmpy2
import pylab
import os
import bisect
# gmpy2 precision initialization
BITS = (1 << 10)
BYTES = BITS/8
gmpy2.get_context().precision = BITS # a whole lotta bits

def random():
    seed = int(os.urandom(BYTES).encode('hex'), 16)
    return gmpy2.mpfr_random(gmpy2.random_state(seed))

# Useful constants as mpfr
PI = gmpy2.acos(-1)
LOG2E = gmpy2.log2(gmpy2.exp(1))
LN2 = gmpy2.log(2)
# Same, as 192.64 fixedpoint
FX_PI = int(PI * 2**64)
FX_LOG2E = int(LOG2E * 2**64)
FX_LN2 = int(LN2 * 2**64)

## The index of a poly is the power of x,
## the val at the index is the coefficient.
##
## An nth degree poly is a list of len n + 1.
##
## The vals in a poly must all be floating point
## numbers.

def poly_add(p1, p2):
    if p1 == []:
        return p2
    if p2 == []:
        return p1
    return [p1[0]+p2[0]] + poly_add(p1[1:], p2[1:])

def poly_mul(p1, p2):
    new_len = len(p1) + len(p2) - 1
    new_p = [0]*new_len
    for i, a_i in enumerate(p1):
        for j, a_j in enumerate(p2):
            new_p[i+j] += a_i*a_j
    return new_p

def scalar_mul(s, p):
    return [s*a_i for a_i in p]

def scalar_div(p, s):
    return [a_i/s for a_i in p]

def lagrange_basis_denom(j, xs):
    result = 1
    x_j = xs[j]
    for m, x_m in enumerate(xs):
        if m!=j:
            result *= x_j - x_m
    return result

def lagrange_basis_numer(j, xs):
    result = [1]
    for m, x_m in enumerate(xs):
        if m!=j:
            result = poly_mul(result, [-x_m, 1])
    return result

def lagrange_basis(j, xs):
    return scalar_div(lagrange_basis_numer(j, xs),
                      lagrange_basis_denom(j, xs))

def lagrange_interp(xs, ys):
    result = []
    for j, y_j in enumerate(ys):
        result = poly_add(result,
                          scalar_mul(y_j,
                                     lagrange_basis(j, xs)))
    return result

def chebyshev_nodes(n, a, b):
    nodes = []
    for k in range(1, n + 1):
        x_k = ((a + b) + (b - a)*gmpy2.cos((2*k - 1)*PI/2/n))/2
        nodes.append(x_k)
    return nodes

def optimal_interp(func, n, a, b):
    xs = chebyshev_nodes(n, a, b)
    ys = map(func, xs)
    return lagrange_interp(xs, ys)

## fixedpoint functions, designed with 192.64 format in mind,
## though they should work with any n.64 format.
def make_fx_poly(poly):
    return [int(a_i*2**64) for a_i in poly]

def fx_poly_eval(p, x):
    result = p[0]
    temp = x
    for a_i in p[1:]:
        result += a_i*temp >> 64
        temp = temp*x >> 64
    return result

def fx_max_random_error(fx_func, ref_func, trials, a, b):
    max_err = 0
    for i in range(trials):
        random_input = random()*(b - a) + a
        expected = ref_func(random_input) * 2**64
        result = fx_func(int(random_input * 2**64))
        err = abs(result - expected)/expected
        if err > max_err:
            max_err = err
    return err*100

def fx_relative_random_error(fx_func, ref_func, trials, a, b):
    errors = []
    for i in range(trials):
        random_input = random()*(b - a) + a
        expected = ref_func(random_input) * 2**64
        result = fx_func(int(random_input * 2**64))
        bisect.insort(errors, (result - expected)*100/expected)
    return sum(errors[trials/4:3*trials/4])*4/trials, min(errors), max(errors), errors[len(errors)/2]

def fx_floor_log2(x):
    y = x >> 64
    lo = 0
    hi = 191
    mid = (lo + hi) >> 1
    while lo + 1 != hi:
        if (1 << mid) > y:
            hi = mid
        else:
            lo = mid
        mid = (lo + hi) >> 1 
    return lo

def fx_log2(x, log2_poly):
    y = fx_floor_log2(x)
    z = x >> y # z = x/2^y
    return (y << 64) + fx_poly_eval(log2_poly, z)

def fx_log(x, log2_poly):
    return (fx_log2(x, log2_poly) << 64) / FX_LOG2E

def fx_exp2(x, exp2_poly):
    y = x >> 64
    z = x % (1 << 64)
    return fx_poly_eval(exp2_poly, z) << y

def fx_exp(x, exp2_poly):
    return fx_exp2((x << 64)/FX_LN2, exp2_poly) 

## The tests combine the fixedpoint functions
## with the interpolation functions above, to
## test several different interpolations.

def test_interps_random(trials, *range_args):
    log_min, log_max = 1, gmpy2.exp(128)
    exp_min, exp_max = 0, 64

    errstr = '\terror in fx_log: avg_mid50:%f%%, min:%f%%, max:%f%%, median:%f%%'
    errstr += '\n\terror in fx_exp: avg_mid50:%f%%, min:%f%%, max:%f%%, median:%f%%'

    for i in range(*range_args):
        
        log2_poly = make_fx_poly(optimal_interp(gmpy2.log2, i, 1, 2))
        exp2_poly = make_fx_poly(optimal_interp(gmpy2.exp2, i, 0, 1))

        logf = lambda x: fx_log(x, log2_poly)
        expf = lambda x: fx_exp(x, exp2_poly)
        
        max_log_err = fx_relative_random_error(logf, gmpy2.log, trials, log_min, log_max)
        max_exp_err = fx_relative_random_error(expf, gmpy2.exp, trials, exp_min, exp_max)

        errs = max_log_err + max_exp_err
        print "Relative error using %d Chebyshev nodes:" % i
        print errstr % errs

#def graph_errors():
    

if __name__ == '__main__':
    test_interps_random(512, 5, 51, 5)
