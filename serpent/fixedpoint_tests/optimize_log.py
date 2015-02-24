#!/usr/bin/python2
import sys
import multiprocessing
import gmpy2
import scipy
import scipy.interpolate
import numpy
import random
import itertools
import time

gmpy2.get_context().precision = 256

LOG2E = int(gmpy2.log2(gmpy2.exp(1))*2**64)

def fxp_ilog2(x):
    y = x >> 64
    lo = 0
    hi = 191
    mid = (lo + hi) >> 1
    while lo < hi:
        if (1 << mid) > y:
            hi = mid - 1
        else:
            lo = mid + 1
        mid = (lo + hi) >> 1
    return lo

def fxp_lagrange(x, coeffs):
    result = 0
    xpow = 1 << 64
    for a_i in coeffs:
        result += (a_i*xpow) >> 64
        xpow = (xpow * x) >> 64
    return result        

def fxp_ln(x, coeffs):
    y = fxp_ilog2(x)
    z = x >> y
    return (((y << 64) + fxp_lagrange(z, coeffs)) << 64)/LOG2E

def avg_error(coeffs, trials, max):
    gmpy2.get_context().precision = 256
    total_error = 0
    for i in range(trials):
        x = random.random()*max
        expected = gmpy2.log(x) * 2**64
        result = fxp_ln(int(x*2**64), coeffs)
        total_error += abs(result - expected)/expected
    return total_error/trials
 
def worker(xs, results, updates, trials, max):
    gmpy2.get_context().precision = 256
    ys = (map(gmpy2.log2, x) for x in xs)
    polys = (scipy.interpolate.lagrange(x, y) for x, y in itertools.izip(xs, ys))
    coeffs = [[int(a_i*2**64) for a_i in reversed(p.coeffs)] for p in polys]
    updates.put("Generated %d polynomials to test." % len(coeffs))
    min_err = float('inf')
    min_cs = None
    for cs in coeffs:
        try:
            err = avg_error(cs, trials, max)
            if err < min_err:
                min_err = err
                min_cs = cs
        except Exception as exc:
            updates.put(str(exc))
            results.put((float('inf'), None))
            return
    updates.put("Checked %d polynomials." % len(coeffs))
    results.put((min_err, min_cs))

def pretty_errors(error_pair):
    error, coeffs = error_pair
    print "%.6f%% error in %d terms." % (100*error, len(coeffs))
    print 'Coefficients:'
    print '\t' + '\n\t'.join(hex(a_i).strip("L") for a_i in coeffs)

def rprint(string):
    sys.stdout.write('\r' + string)
    sys.stdout.flush()

def main():
    start = time.time()
    results = multiprocessing.Queue()
    updates = multiprocessing.Queue()
    trials = 200
    max_input = int(gmpy2.exp(128))
    degree = int(sys.argv[2])
    num_points = int(sys.argv[1])
    n = multiprocessing.cpu_count()
    processes = []
    proc_results = []
    size = int(gmpy2.comb(num_points, degree)) / n
    combs = itertools.combinations(numpy.linspace(1, 2, num_points), degree)
    for i in range(n):
        xs = [x for _, x in zip(range(size), combs)]
        proc = multiprocessing.Process(target=worker, args=(xs, results, updates, trials, max_input))
        print "starting process %d" % i
        proc.start()
        processes.append(proc)
    for i in range(2*n):
        print updates.get()
    for i in range(n):
        proc_results.append(results.get())
    for proc in processes:
        proc.join()
    pretty_errors(min(proc_results))
    print "Time Elapsed: %.2f seconds." % (time.time() - start)
    
if __name__ == '__main__':
    main()
