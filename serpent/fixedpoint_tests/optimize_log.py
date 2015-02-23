#!/usr/bin/python2
import sys
import multiprocessing
import gmpy2
import scipy
import scipy.interpolate
import numpy
import random
import itertools

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
        x = random.randrange(max)
        expected = gmpy2.log(x) * 2**64
        result = fxp_ln(x << 64, coeffs)
        total_error += abs(result - expected)/expected
    return total_error/trials
 
def worker(work, results, updates, trials, max):
    coeffs = work.get()
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
    updates.put("Checked %d polynomials" % len(coeffs))
    results.put((min_err, min_cs))

def pretty_errors(error_pair):
    error, coeffs = error_pair
    print "%.6f%% error in %d terms." % (100*error, len(coeffs))
    print 'Coefficients:'
    print '\t' + '\n\t'.join(hex(a_i).strip("L") for a_i in coeffs)
    print

def rprint(string):
    sys.stdout.write('\r' + string)
    sys.stdout.flush()

def main():
    work = multiprocessing.Queue()
    results = multiprocessing.Queue()
    updates = multiprocessing.Queue()
    trials = 50
    max_input = int(gmpy2.exp(128))
    degree = int(sys.argv[2])
    num_points = int(sys.argv[1])
    print "Generating interpolation polynomials of degree %d" % degree
    xs = list(itertools.combinations(numpy.linspace(1, 2, num_points), degree))
    ys = [map(gmpy2.log2, x) for x in xs]
    polys = [scipy.interpolate.lagrange(x, y) for x, y in zip(xs, ys)]
    coeffs = [[int(a_i*2**64) for a_i in reversed(p.coeffs)] for p in polys]
    n = multiprocessing.cpu_count()
    processes = []
    proc_results = []
    print "Generated %d polynomials to check" % len(coeffs)
    for i in range(n):
        print "putting work"
        work.put(coeffs[i::n])
        proc = multiprocessing.Process(target=worker, args=(work, results, updates, trials, max_input))
        print "starting process %d" % i
        proc.start()
        processes.append(proc)
    for i in range(n):
        print updates.get()
    for i in range(n):
        proc_results.append(results.get())
        print "Got results!"
    for proc in processes:
        proc.join()
        print "joined a proc"
    pretty_errors(min(proc_results))

if __name__ == '__main__':
    main()
