#!/usr/bin/python2
import gmpy2
#import matplotlib.pyplot as plt
import os
import bisect
from numpy import linspace
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
FX_ONE = 1 << 64
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
    min_err, max_err = float('inf'), float('-inf')
    for i in range(trials):
        random_input = random()*(b - a) + a
        expected = ref_func(random_input) * 2**64
        result = fx_func(int(random_input * 2**64))
        diff = result - expected
        if diff < min_err:
            min_err = diff
        if max_err < diff:
            max_err = diff
        bisect.insort(errors, diff*100/expected)
    return sum(map(abs, errors[trials/4:3*trials/4]))*4/trials, min(errors), max(errors), errors[len(errors)/2], max_err, min_err

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
    exp_min, exp_max = 0, 128

    datastr = ',\n\t\t'.join([
        'avg_abs_mid_50:%E%%', 'min_rel:%E%%', 
        'max_rel:%E%%', 'median_rel:%E%%',
        'max_diff:%E%%', 'min_diff:%E%%'
    ])
    errstr = '\terror in fx_log:\n\t\t'
    errstr += datastr
    errstr += '\n\terror in fx_exp:\n\t\t'
    errstr += datastr

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

def graph_errors(*range_args):
    exp_min, exp_max = 0, 4
    exp_xs = map(gmpy2.mpfr, linspace(exp_min, exp_max, 10000))
    exp_ys = map(gmpy2.exp, exp_xs)

    log_min, log_max = 1, gmpy2.exp(exp_max)
    log_xs = map(gmpy2.mpfr, linspace(log_min, log_max, 10000))
    log_ys = map(gmpy2.log, log_xs)

    funcs = [
        (fx_exp, gmpy2.exp2, 0, 1, exp_xs, exp_ys, 'exp'),
        (fx_log, gmpy2.log2, 1, 2, log_xs, log_ys, 'log'),
    ]

    for i in range(*range_args):
        for func_items in funcs:
            fx_func, interp_func = func_items[:2]
            interp_min, interp_max = func_items[2:4]
            ref_xs, ref_ys = func_items[4:6]
            name = func_items[6]
            p_i = make_fx_poly(
                optimal_interp(
                    interp_func,
                    i,
                    interp_min,
                    interp_max
                )
            )
            fx_f = lambda x: fx_func(int(x * 2**64), p_i)/gmpy2.mpfr(1 << 64)
            fx_ys = map(fx_f, ref_xs)
            first_diff = map(lambda a, b: b - a, fx_ys[:-1], fx_ys[1:])
            fig, axes = plt.subplots(3, sharex=True)
            axes[0].set_title('$\\%s(x)$ and $\\%s_{fx}(x)$' % (name, name))
            axes[0].plot(ref_xs, ref_ys, label=('$\\%s$' % name))
            axes[0].plot(ref_xs, fx_ys, label=('$\\%s_{fx}$' % name))
            axes[1].set_title('$(\\%s_{fx} - \\%s)(x)$' % (name, name))
            axes[1].plot(ref_xs, map(lambda a, b: a-b, fx_ys, ref_ys))
            axes[2].set_title('$\\frac{d}{dx}(\\%s_{fx})$' % name)
            axes[2].plot(ref_xs[:-1], first_diff)
            fig.savefig('chebyshev-%s-%d.png'%(name, i))

            if any(map(lambda a: 1 if a < 0 else 0, first_diff)):
                print "\033[1;31mBAD FIRST DIFF!!!!! fx_%s with %d nodes\033[0m" % (name, i)

def generate_serpent(*range_args):
    exp_code = '''\
macro fx_exp2_small($x):
    with $result = %s0x{poly[0]:X}:
        with $temp = $x:
            {interp_code}

macro fx_exp2($x):
    with $y = $x / 0x{FX_ONE:X}:
        with $z = $x %% 0x{FX_ONE:X}:
            fx_exp2_small($z) * 2**y

macro fx_exp($x):
    fx_exp2($x * 0x{FX_ONE:X} / 0x{FX_LN2:X})
'''

    log_code = '''
macro fx_floor_log2($x):
    with $y = $x / 0x{FX_ONE:X}:
        with $lo = 0:
            with $hi = 191:
                with $mid = ($hi + $lo)/2:
                    while ($lo + 1) != $hi:
                        if $y < 2**$mid:
                            $hi = $mid
                        else:
                            $lo = $mid
                        $mid = ($hi + $lo)/2
                    $lo

macro fx_log2_small($x):
    with $result = %s0x{poly[0]:X}:
        with $temp = $x:
            {interp_code}

macro fx_log2($x):
    with $y = fx_floor_log2($x):
        with $z = $x / 2**$y:
            $y * 0x{FX_ONE:X} + fx_log2_small($z)

macro fx_log($x):
    fx_log2($x) * 0x{FX_ONE:X} / 0x{FX_LOG2E:X}
'''

    code_items = [
        (exp_code, gmpy2.exp2, 0, 1),
        (log_code, gmpy2.log2, 1, 2),
    ]

    tab = ' '*12
    for i in range(*range_args):
        full_code = ''
        for code, ref_func, a, b in code_items:
            poly = make_fx_poly(optimal_interp(ref_func, i, a, b))
            interp_code = ''
            for j, a_j in enumerate(poly[1:-1]):
                piece = '$result %%s= 0x{poly[%d]:X}*$temp / 0x{FX_ONE:X}' % (j + 1)
                if a_j > 0:
                    interp_code += piece % '+'
                else:
                    interp_code += piece % '-'
                interp_code += '\n' + tab
                interp_code += '$temp = $temp*$x / 0x{FX_ONE:X}'
                interp_code += '\n' + tab
            if poly[0] > 0:
                this_code = code % '+'
            else:
                this_code = code % '-'
            if poly[-1] > 0:
                interp_code += '$result + 0x{poly[%d]:X}*$temp / 0x{FX_ONE:X}' % (len(poly) - 1)
            else:
                interp_code += '$result - 0x{poly[%d]:X}*$temp / 0x{FX_ONE:X}' % (len(poly) - 1)
            poly = map(abs, poly)
            fmt_args = globals().copy()
            fmt_args.update(locals())
            this_code = this_code.format(**fmt_args).format(**fmt_args)
            full_code += this_code
        f = open('fx_macros_%d.se'%i, 'w')
        f.write(full_code)
        f.close()

if __name__ == '__main__':
#    graph_errors(15, 21)
    generate_serpent(15, 21)
