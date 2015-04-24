#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Augur consensus tests.

To run consensus, call the Serpent functions in this order:

interpolate
center
tokenize
covariance
loop max_components:
    blank
    loop max_iterations:
        loadings
    latent
    deflate
    score
reputation_delta
weighted_delta
select_scores
smooth
resolve
payout

Final results (event outcomes and updated reputation values) are returned
as fixed-point (base 2^64) values from the payout function.

"""
from __future__ import division
import os
import sys
import json
import getopt
from pprint import pprint
import numpy as np
import pandas as pd
try:
    from colorama import Fore, Style, init
except ImportError:
    pass
from ethereum import tester as t
from pyconsensus import Oracle

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                    os.pardir, os.pardir, "consensus")

np.set_printoptions(linewidth=225,
                    suppress=True,
                    formatter={"float": "{: 0.6f}".format})

pd.set_option("display.max_rows", 25)
pd.set_option("display.width", 1000)
pd.set_option('display.float_format', lambda x: '%.8f' % x)

# max_iterations: number of blocks required to complete PCA
verbose = False
max_iterations = 5
tolerance = 0.05
variance_threshold = 0.85
max_components = 5
init()

YES = 2.0
NO = 1.0
BAD = 1.5
NA = 0.0

def BR(string): # bright red
    return "\033[1;31m" + str(string) + "\033[0m"

def BB(string): # bright blue
    return Fore.BLUE + Style.BRIGHT + str(string) + Style.RESET_ALL

def BW(string): # bright white
    return Fore.WHITE + Style.BRIGHT + str(string) + Style.RESET_ALL

def BG(string): # bright green
    return Fore.GREEN + Style.BRIGHT + str(string) + Style.RESET_ALL

def BC(string): # bright cyan
    return Fore.CYAN + Style.BRIGHT + str(string) + Style.RESET_ALL

def binary_input_example():
    print BW("Testing with binary inputs")
    print BW("==========================")
    reports = np.array([[ YES, YES,  NO, YES],
                        [ YES,  NO,  NO,  NO],
                        [ YES, YES,  NO,  NO],
                        [ YES, YES, YES,  NO],
                        [ YES,  NO, YES, YES],
                        [  NO,  NO, YES, YES]])
    reputation = [2, 10, 4, 2, 7, 1]
    scaled = [0, 0, 0, 0]
    scaled_max = [YES, YES, YES, YES]
    scaled_min = [NO, NO, NO, NO]
    return (reports, reputation, scaled, scaled_max, scaled_min)

def scalar_input_example():
    print BW("Testing with binary and scalar inputs")
    print BW("=====================================")
    reports = np.array([[ YES, YES,  NO,  NO, 233, 16027.59 ],
                        [ YES,  NO,  NO,  NO, 199,     0.   ],
                        [ YES, YES,  NO,  NO, 233, 16027.59 ],
                        [ YES, YES, YES,  NO, 250,     0.   ],
                        [  NO,  NO, YES, YES, 435,  8001.00 ],
                        [  NO,  NO, YES, YES, 435, 19999.00 ]])
    reputation = [1, 1, 1, 1, 1, 1]
    scaled = [0, 0, 0, 0, 1, 1]
    scaled_max = [ YES, YES, YES, YES, 435, 20000 ]
    scaled_min = [  NO,  NO,  NO,  NO, 0,    8000 ]
    return (reports, reputation, scaled, scaled_max, scaled_min)

def randomized_inputs(num_reports=10, num_events=5):
    print BW("Testing with randomized inputs")
    print BW("==============================")
    reports = np.random.randint(-1, 2, (num_reports, num_events)).astype(float)
    reputation = np.random.randint(1, 100, num_reports).tolist()
    scaled = np.random.randint(0, 2, num_events).tolist()
    scaled_max = np.ones(num_events)
    scaled_min = -np.ones(num_events)
    for i in range(num_events):
        if scaled[i]:
            scaled_max[i] = np.random.randint(1, 100)
            scaled_min[i] = np.random.randint(0, scaled_max[i])
    scaled_max = scaled_max.astype(int).tolist()
    scaled_min = scaled_min.astype(int).tolist()
    return (reports, reputation, scaled, scaled_max, scaled_min)

def fix(x):
    return int(x * 0x10000000000000000)

def unfix(x):
    return x / 0x10000000000000000

def fold(arr, num_cols):
    folded = []
    num_rows = len(arr) / float(num_cols)
    if num_rows != int(num_rows):
        raise Exception("array length (%i) not divisible by %i" % (len(arr), num_cols))
    num_rows = int(num_rows)
    for i in range(num_rows):
        row = []
        for j in range(num_cols):
            row.append(arr[i*num_cols + j])
        folded.append(row)
    return folded

def display(arr, description=None, show_all=None, refold=False):
    if description is not None:
        print(BW(description))
    if refold and type(refold) == int:
        num_rows = len(arr) / float(refold)
        if num_rows == int(num_rows) and len(arr) > refold:
            print(np.array(fold(map(unfix, arr), refold)))
        else:
            refold = False
    if not refold:
        if show_all is not None:
            print(pd.DataFrame({
                'result': arr,
                'base 16': map(hex, arr),
                'base 2^64': map(unfix, arr),
            }))
        else:
            print(json.dumps(map(unfix, arr), indent=3, sort_keys=True))

def rmsd(forecast, actual, fixed=True):
    if fixed:
        if len(forecast) > 1:
            forecast = np.array(map(unfix, forecast))
        else:
            forecast = unfix(np.array(forecast).squeeze())
    return np.sqrt(np.mean((actual - forecast)**2))

def tol(forecast, actual, fixed=True):
    r = rmsd(forecast, actual, fixed=fixed)
    try:
        assert(r < tolerance)
    except Exception as err:
        print "Forecast:", np.array(map(unfix, forecast))
        print "Actual:", actual
        print "RMSD tolerance exceeded:", r, ">=", tolerance
        raise

def init_chain(gas_limit=700000000):
    print(BR("Creating new test chain ") + "(gas limit: %s)" % gas_limit)
    s = t.state()
    t.gas_limit = gas_limit
    return t.state()

def compile_contract(state, filename, root=ROOT, gas=70000000):
    print(BG(filename) + " (%s gas)" % gas)
    return state.abi_contract(os.path.join(root, filename), gas=gas)

def profile(contract, fn, *args, **kwargs):
    sys.stdout.write(BW("  - %s:" % fn))
    sys.stdout.flush()
    result = getattr(contract, fn)(*args, profiling=True)
    print(" %i gas (%s seconds)" % (result['gas'], result['time']))
    return result['output']

def test_consensus(example, verbose=False):

    reports, reputation, scaled, scaled_max, scaled_min = example()

    num_reports = len(reputation)
    num_events = len(reports[0])
    flatsize = num_reports * num_events
    reputation_fixed = map(fix, reputation)
    reports_fixed = map(fix, reports.ravel())
    scaled_max_fixed = map(fix, scaled_max)
    scaled_min_fixed = map(fix, scaled_min)
    if verbose:
        display(np.array(reports_fixed), "reports (raw):", refold=num_events, show_all=True)

    s = init_chain()

    c = compile_contract(s, "interpolate.se")
    result = profile(c, "interpolate", reports_fixed,
                                       reputation_fixed,
                                       scaled,
                                       scaled_max_fixed,
                                       scaled_min_fixed)
    result = np.array(result)
    reports_filled = result[0:flatsize].tolist()
    reports_mask = result[flatsize:].tolist()
    if verbose:
        display(reports_filled, "reports_filled:", refold=num_events, show_all=True)

    c = compile_contract(s, "center.se")
    result = profile(c, "center", reports_filled,
                                  reputation_fixed,
                                  scaled,
                                  scaled_max_fixed,
                                  scaled_min_fixed,
                                  max_iterations,
                                  max_components)
    result = np.array(result)
    weighted_centered_data = result[0:flatsize].tolist()
    if verbose:
        display(weighted_centered_data, "Weighted centered data:", refold=num_events, show_all=True)

    lv = np.array(map(unfix, result[flatsize:-2]))
    wcd = np.array(fold(map(unfix, weighted_centered_data), num_events))
    wcd_init = wcd
    rep = map(unfix, reputation_fixed)
    R = np.diag(rep)

    # Get "Satoshi" (integer) Reputation values
    # Python
    tokens = np.array([int(r * 1e6) for r in rep])
    alltokens = np.sum(tokens)
    # Serpent
    
    reptokens = profile(c, "tokenize", reputation_fixed, num_reports, nparray=False)
    if verbose:
        print BR("Tokens:")
        print BW("  Python: "), tokens
        print BW("  Serpent:"), np.array(map(unfix, reptokens)).astype(int)

    # Calculate the first row of the covariance matrix
    # Python
    covmat = wcd.T.dot(np.diag(tokens)).dot(wcd) / float(alltokens - 1)
    totalvar = np.trace(covmat)
    Crow = np.zeros(num_events)
    wcd_x_tokens = wcd[:,0] * tokens
    Crow = wcd_x_tokens.dot(wcd) / (alltokens-1)
    # Serpent
    covrow = profile(c, "covariance", weighted_centered_data,
                                      reptokens,
                                      num_reports,
                                      num_events)
    if verbose:
        print BR("Covariance matrix row")
        print BW("  Python: "), Crow
        print BW("  Serpent:"), np.array(map(unfix, covrow))
    tol(covrow, Crow)

    #######
    # PCA #
    #######

    # Python
    iv = result[flatsize:]
    variance_explained = 0
    nc = np.zeros(num_reports)
    negative = False

    for j in range(min(max_components, num_events)):

        # Calculate loading vector
        lv = np.array(map(unfix, iv[:-2]))
        for i in range(max_iterations):
            lv = R.dot(wcd).dot(lv).dot(wcd)
            lv /= np.sqrt(lv.dot(lv))

        # Calculate the eigenvalue for this eigenvector
        for k in range(num_events):
            if lv[k] != 0:
                break
        E = covmat[k,:].dot(lv) / lv[k]

        # Cumulative variance explained
        variance_explained += E / totalvar

        # Projection onto new axis: nonconformity vector
        slv = lv
        if slv[0] < 0:
            slv *= -1
        nc += E * wcd.dot(slv)

        if verbose:
            print BW("  Loadings %d:" % j), np.round(np.array(lv), 6)
            print BW("  Latent %d:  " % j), E, "(%s%% variance explained)" % np.round(variance_explained * 100, 3)

        # Deflate the data matrix
        wcd = wcd - wcd.dot(np.outer(lv, lv))

    if verbose:
        print BW("  Nonconformity: "), np.round(nc, 6)

    # Serpent
    loading_vector = result[flatsize:].tolist()
    data = weighted_centered_data
    scores = map(int, np.zeros(num_reports).tolist())
    var_exp = 0
    num_comps = 0

    c = compile_contract(s, "score.se")

    while True:
        print(BC("  COMPONENT %s" % str(num_comps + 1)))

        # Loading vector (eigenvector)
        #   - Second-to-last element: number of iterations remaining
        #   - Last element: number of components remaining
        loading_vector = profile(c, "blank", loading_vector[-1],
                                             max_iterations,
                                             num_events)
        sys.stdout.write(BW("  - loadings"))
        sys.stdout.flush()
        lv_gas = []
        lv_time = []
        while loading_vector[num_events] > 0:
            sys.stdout.write(BW("."))
            sys.stdout.flush()
            result = c.loadings(loading_vector,
                                data,
                                reputation_fixed,
                                num_reports,
                                num_events,
                                profiling=True)
            loading_vector = result['output']
            lv_gas.append(result['gas'])
            lv_time.append(result['time'])
        print(" %i gas (%s seconds)" % (np.mean(lv_gas), np.mean(lv_time)))

        # Latent factor (eigenvalue; check sign bit)
        latent = profile(c, "latent", covrow, loading_vector, num_events)

        # Deflate the data matrix
        data = profile(c, "deflate", loading_vector, data, num_reports, num_events)

        # Project data onto this component and add to weighted scores
        scores = profile(c, "score", scores,
                                     loading_vector,
                                     weighted_centered_data,
                                     latent,
                                     num_reports,
                                     num_events)
        if verbose:
            printable_loadings = np.array(map(unfix, loading_vector[:-2]))
            if printable_loadings[0] < 0:
                printable_loadings *= -1
            print BW("Component %d [%s]:\t" %
                     (num_comps, np.round(unfix(latent), 4))), printable_loadings
        num_comps += 1
        if loading_vector[num_events + 1] == 0:
            break
    tol(scores, nc)

    c = compile_contract(s, "adjust.se")
    result = profile(c, "reputation_delta", scores, num_reports, num_events)
    result = np.array(result)
    set1 = result[0:num_reports].tolist()
    set2 = result[num_reports:].tolist()
    assert(len(set1) == len(set2))
    assert(len(result) == 2*num_reports)
    if verbose:
        display(set1, "set1:", show_all=True)
        display(set2, "set2:", show_all=True)

    result = profile(c, "weighted_delta", set1,
                                          set2,
                                          reputation_fixed,
                                          reports_filled,
                                          num_reports,
                                          num_events)
    result = np.array(result)
    old = result[0:num_events].tolist()
    new1 = result[num_events:(2*num_events)].tolist()
    new2 = result[(2*num_events):].tolist()
    assert(len(result) == 3*num_events)
    assert(len(old) == len(new1) == len(new2))
    if verbose:
        display(old, "old:", show_all=True)
        display(new1, "new1:", show_all=True)
        display(new2, "new2:", show_all=True)

    adjusted_scores = profile(c, "select_scores", old,
                                                  new1,
                                                  new2,
                                                  set1,
                                                  set2,
                                                  scores,
                                                  num_reports,
                                                  num_events)

    c = compile_contract(s, "resolve.se")
    smooth_rep = profile(c, "smooth", adjusted_scores,
                                      reputation_fixed,
                                      num_reports,
                                      num_events)
    event_outcomes = profile(c, "resolve", smooth_rep,
                                           reports_filled,
                                           scaled,
                                           scaled_max_fixed,
                                           scaled_min_fixed,
                                           num_reports,
                                           num_events)

    c = compile_contract(s, "payout.se")
    reporter_payout = profile(c, "payout", event_outcomes,
                                           smooth_rep,
                                           reports_mask,
                                           num_reports,
                                           num_events)
    reporter_payout = np.array(reporter_payout)
    if verbose:
        print BW("Nonconformity scores:"), np.array(map(unfix, scores))
        print BW("Raw reputation:      "), np.array(map(unfix, smooth_rep))
        print BW("Adjusted scores:     "), np.array(map(unfix, adjusted_scores))
        print BW("Reporter payout:     "), np.array(map(unfix, reporter_payout))
        print BW("Event outcomes:      "), np.array(map(unfix, event_outcomes))

    # Compare to pyconsensus

    print BG("pyconsensus")

    event_bounds = []
    for i, s in enumerate(scaled):
        event_bounds.append({
            'scaled': 0 if s == False else 1,
            'min': scaled_min[i],
            'max': scaled_max[i],
        })
    for j in range(num_events):
        for i in range(num_reports):
            if reports[i,j] == 0:
                reports[i,j] = np.nan

    pyresults = Oracle(reports=reports,
                       reputation=reputation,
                       event_bounds=event_bounds,
                       algorithm="big-five",
                       variance_threshold=variance_threshold,
                       max_components=max_components,
                       verbose=False).consensus()
    serpent_results = {
        'reputation': map(unfix, smooth_rep),
        'outcomes': map(unfix, event_outcomes),
    }
    python_results = {
        'reputation': pyresults['agents']['smooth_rep'],
        'outcomes': np.array(pyresults['events']['outcomes_final']),
    }
    comparisons = {}
    for m in ('reputation', 'outcomes'):
        comparisons[m] = abs((python_results[m] - serpent_results[m]) / python_results[m])

    fails = 0
    for key, value in comparisons.items():
        try:
            assert((value < tolerance).all())
        except Exception as e:
            fails += 1
            print BW("Tolerance exceeded for ") + BR("%s:" % key)
            print "Serpent:    ", np.array(serpent_results[key])
            print "Python:     ", python_results[key]
            print "Difference: ", comparisons[key]
    if fails == 0:
        print BC("Tests passed!")

def test_redeem(example, verbose=False):
    branch = 1
    period = 1
    reports, reputation, scaled, scaled_max, scaled_min = example()
    num_reports = len(reputation)
    num_events = len(reports[0])
    flatsize = num_reports * num_events
    reputation_fixed = map(fix, reputation)
    reports_fixed = map(fix, reports.ravel())
    scaled_max_fixed = map(fix, scaled_max)
    scaled_min_fixed = map(fix, scaled_min)
    mock = 0 if example.__name__ == "binary_input_example" else 1

    s = init_chain(gas_limit=750000000)
    c = compile_contract(s, "redeem_full.se", gas=700000000)
    output = profile(c, "redeem", branch, period, num_events, num_reports, flatsize, mock)
    print np.array(map(unfix, output))
    display(output, "Refolded:", refold=num_events)

def test_dispatch(example, verbose=False):
    branch = 1
    period = 1
    reports, reputation, scaled, scaled_max, scaled_min = example()
    num_reports = len(reputation)
    num_events = len(reports[0])
    flatsize = num_reports * num_events
    reputation_fixed = map(fix, reputation)
    reports_fixed = map(fix, reports.ravel())
    scaled_max_fixed = map(fix, scaled_max)
    scaled_min_fixed = map(fix, scaled_min)
    mock = 0 if example.__name__ == "binary_input_example" else 1

    s = init_chain(gas_limit=750000000)
    c = compile_contract(s, r"../function files/dispatch-tester.se", gas=700000000)
    profile(c, "dispatch", branch, mock)

def runtests(verbose=False, full=False, redeem=False, dispatch=False):
    examples = (
        binary_input_example,
        scalar_input_example,
        # randomized_inputs,
    )
    for example in examples:   
        if full:
            test_consensus(example, verbose=verbose)
            test_redeem(example, verbose=verbose)
            test_dispatch(example, verbose=verbose)
        elif redeem:
            test_redeem(example, verbose=verbose)
        elif dispatch:
            test_dispatch(example, verbose=verbose)
        else:
            test_consensus(example, verbose=verbose)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        short_opts = 'hvfrd'
        long_opts = ['help', 'verbose', 'full', 'redeem', 'dispatch']
        opts, vals = getopt.getopt(argv[1:], short_opts, long_opts)
    except getopt.GetoptError as e:
        sys.stderr.write(e.msg)
        sys.stderr.write("for help use --help")
        return 2
    parameters = {
        'verbose': False,
        'full': False,
        'redeem': False,
        'dispatch': False,
    }
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            return 0
        elif opt in ('-v', '--verbose'):
            parameters['verbose'] = True
        elif opt in ('-f', '--full'):
            parameters['full'] = True
        elif opt in ('-r', '--redeem'):
            parameters['redeem'] = True
        elif opt in ('-d', '--dispatch'):
            parameters['dispatch'] = True

    # Run tests
    runtests(**parameters)

if __name__ == '__main__':
    sys.exit(main())
