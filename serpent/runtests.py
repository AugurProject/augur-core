#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This software (Augur) allows buying and selling event options in Ethereum.

Copyright (c) 2014 Chris Calderon, Joey Krug, Scott Leonard, Alan Lu, Jack Peterson

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Questions?  Please contact jack@tinybike.net or joeykrug@gmail.com.

"""
from __future__ import division
import sys
import json
from pprint import pprint
import numpy as np
import pandas as pd
try:
    from colorama import Fore, Style, init
except ImportError:
    pass
from pyethereum import tester as t
from pyconsensus import Oracle

# np.set_printoptions(linewidth=500)
np.set_printoptions(linewidth=225,
                    suppress=True,
                    formatter={"float": "{: 0.6f}".format})

pd.set_option("display.max_rows", 25)
pd.set_option("display.width", 1000)
pd.set_option('display.float_format', lambda x: '%.8f' % x)

# max_iterations: number of blocks required to complete PCA
max_iterations = 25
tolerance = 0.05
variance_threshold = 0.85
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

def single_input_example():
    print BW("Testing with a single input")
    print BW("===========================")
    reports = np.array([[ NO, ]])
    reputation = [10000,]
    scaled = [0,]
    scaled_max = [ YES,]
    scaled_min = [  NO,]
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

def randomized_inputs(num_reports=50, num_events=25):
    print BW("Testing with randomized inputs")
    print BW("==============================")
    reports = np.random.randint(-1, 2, (num_reports, num_events))
    reputation = np.random.randint(1, 100, num_reports)
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

def main():
    """
    To run consensus, you should call the Serpent functions in consensus.se
    in this order:
    
    interpolate
    center
    pca_loadings (this should be called once for each PCA iteration --
                  in tests, it seems that 5 iterations is sufficient.
                  each iteration takes the previous iteration's
                  loading_vector output as its input.)
    pca_scores
    calibrate_sets
    calibrate_wsets
    pca_adjust
    smooth
    consensus
    participation

    Final results (event outcomes and updated reputation values) are returned
    as fixed-point (base 2^64) values from the participation function.

    """
    examples = (
        binary_input_example,
        # single_input_example,
        # scalar_input_example,
        # randomized_inputs,
    )
    for example in examples:   
        reports, reputation, scaled, scaled_max, scaled_min = example()

        print BR("Forming new test genesis block")
        s = t.state()
        t.gas_limit = 100000000
        s = t.state()
        filename = "consensus.se"
        print BB("Testing contract:"), BG(filename)
        c = s.abi_contract(filename, gas=70000000)
        
        num_reports = len(reputation)
        num_events = len(reports[0])
        v_size = num_reports * num_events

        reputation_fixed = map(fix, reputation)
        reports_fixed = map(fix, reports.ravel())
        scaled_max_fixed = map(fix, scaled_max)
        scaled_min_fixed = map(fix, scaled_min)

        # display(np.array(reports_fixed), "reports (raw):", refold=num_events, show_all=True)

        arglist = [reports_fixed, reputation_fixed, scaled, scaled_max_fixed, scaled_min_fixed]
        result = c.interpolate(*arglist)
        result = np.array(result)
        reports_filled = result[0:v_size].tolist()
        reports_mask = result[v_size:].tolist()

        # display(reports_filled, "reports (filled):", refold=num_events, show_all=True)

        # center and initiate multistep pca loading vector
        arglist = [reports_filled, reputation_fixed, scaled,
                   scaled_max_fixed, scaled_min_fixed, max_iterations]
        result = c.center(*arglist)
        result = np.array(result)
        weighted_centered_data = result[0:v_size].tolist()

        lv = np.array(map(unfix, result[v_size:-1]))
        wcd = np.array(fold(map(unfix, weighted_centered_data), num_events))
        wcd_init = wcd
        rep = map(unfix, reputation_fixed)
        R = np.diag(rep)

        # Get "Satoshi" (integer) Reputation values
        # Python
        tokens = np.array([int(r * 1e6) for r in rep])
        alltokens = np.sum(tokens)
        # Serpent
        reptokens = c.tokenize(reputation, num_reports)
        print BR("Tokens:")
        print BW("  Python: "), tokens
        print BW("  Serpent:"), np.array(map(unfix, reptokens)).astype(int)
        print

        # Total variance
        # Python
        covmat = wcd.T.dot(np.diag(tokens)).dot(wcd) / float(alltokens - 1)
        totalvar = np.trace(covmat)
        # Serpent
        variance = c.total_variance(weighted_centered_data,
                                    reptokens,
                                    num_reports,
                                    num_events)
        print BR("Total variance:")
        print BW("  Python: "), totalvar
        print BW("  Serpent:"), unfix(variance)
        print

        # Calculate the first row of the covariance matrix
        # Python
        Crow = np.zeros(num_events)
        wcd_x_tokens = wcd[:,0] * tokens
        for i in range(num_events):
            Crow[i] = wcd_x_tokens.dot(wcd[:,i]) / (alltokens-1)
        # Serpent
        covmatrow = c.covariance_matrix_row(weighted_centered_data,
                                            reptokens,
                                            num_reports,
                                            num_events)
        print BR("Covariance matrix row:")
        print BW("  Python: "), Crow
        print BW("  Serpent:"), np.array(map(unfix, covmatrow))
        print

        #######
        # PCA #
        #######

        # Python
        print BR("Python PCA")

        iv = result[v_size:]
        variance_explained = 0
        num_components = 0
        nc = np.zeros(num_reports)
        negative = False

        while variance_explained < variance_threshold:

            # Calculate loading vector
            lv = np.array(map(unfix, iv[:-1]))
            for i in range(max_iterations):
                lv = R.dot(wcd).dot(lv).dot(wcd)
                lv /= np.sqrt(lv.dot(lv))

            # Calculate the eigenvalue for this eigenvector
            E = Crow.dot(lv) / lv[0]

            # Cumulative variance explained
            variance_explained += E / totalvar

            # Projection onto new axis: nonconformity vector
            if num_components == 0 and lv[0] < 0:
                negative = True
            if negative:
                lv *= -1
            nc += E * wcd.dot(lv)

            print BW("  Eigenvector %d:" % num_components), np.round(np.array(lv), 6)
            print BW("  Eigenvalue %d: " % num_components), E, "(%s%% variance explained)" % np.round(variance_explained * 100, 3)
            print BW("  Nonconformity: "), np.round(nc, 6)
            print

            # Deflate the data matrix
            wcd = wcd - wcd.dot(np.outer(lv, lv))

            num_components += 1

        # Serpent
        print BR("Serpent PCA")

        init_vector = iv.tolist()
        data = weighted_centered_data
        scores = map(int, np.zeros(num_reports).tolist())
        var_exp = 0
        num_comps = 0

        while var_exp < variance_threshold:

            # Calculate loading vector
            loading_vector = init_vector
            while loading_vector[num_events] > 0:
                loading_vector = c.pca_loadings(loading_vector,
                                                data,
                                                reputation_fixed,
                                                num_reports,
                                                num_events)

            # Calculate the eigenvalue (latent factor) for this eigenvector
            latent = c.pca_latent(covmatrow, loading_vector, num_events)

            # Total variance explained
            var_exp += unfix(latent) / unfix(variance)

            # Deflate the data matrix
            data = c.deflate(loading_vector[:-1],
                             data,
                             num_reports,
                             num_events)

            # Project data onto this component and add to weighted scores
            scores = c.nonconformity(scores,
                                     loading_vector,
                                     weighted_centered_data,
                                     latent,
                                     num_reports,
                                     num_events)

            print BW("  Eigenvector %d:" % num_comps), np.array(map(unfix, loading_vector[:-1]))
            print BW("  Eigenvalue %d: " % num_comps), unfix(latent), "(%s%% variance explained)" % np.round(var_exp * 100, 3)
            print BW("  Nonconformity: "), np.array(map(unfix, scores))
            print

            if unfix(latent) / unfix(variance) < sys.float_info.epsilon:
                break

            num_comps += 1

        arglist = [scores, num_reports, num_events]
        result = c.calibrate_sets(*arglist)
        result = np.array(result)
        set1 = result[0:num_reports].tolist()
        set2 = result[num_reports:].tolist()
        assert(len(set1) == len(set2))
        assert(len(result) == 2*num_reports)

        # display(set1, "set1:", show_all=True)
        # display(set2, "set2:", show_all=True)

        arglist = [set1, set2, reputation_fixed, reports_filled, num_reports, num_events]
        result = c.calibrate_wsets(*arglist)
        result = np.array(result)
        old = result[0:num_events].tolist()
        new1 = result[num_events:(2*num_events)].tolist()
        new2 = result[(2*num_events):].tolist()
        assert(len(result) == 3*num_events)
        assert(len(old) == len(new1) == len(new2))

        # display(old, "old:", show_all=True)
        # display(new1, "new1:", show_all=True)
        # display(new2, "new2:", show_all=True)

        arglist = [old, new1, new2, set1, set2, scores, num_reports, num_events]
        adjusted_scores = c.pca_adjust(*arglist)

        # display(adjusted_scores, "adjusted_scores:", show_all=True)

        arglist = [adjusted_scores, reputation_fixed, num_reports, num_events]
        smooth_rep = c.smooth(*arglist)

        # display(reports_filled, "reports_filled:", show_all=True)
        # display(reports_filled,"reports_filled:",refold=num_events, show_all=True)
        # display(smooth_rep, "smooth_rep:", show_all=True)

        arglist = [smooth_rep, reports_filled, scaled, scaled_max_fixed,
                   scaled_min_fixed, num_reports, num_events]
        result = c.consensus(*arglist)

        result = np.array(result)
        outcomes_final = result[0:num_events].tolist()

        # outcomes_final[i] *= self.event_bounds[i]["max"] - self.event_bounds[i]["min"]
        # outcomes_final[i] += self.event_bounds[i]["min"]

        arglist = [outcomes_final, smooth_rep, reports_mask, num_reports, num_events]
        reporter_bonus = c.participation(*arglist)

        # display(loading_vector, "Loadings:", show_all=True)
        # display(adjusted_scores, "Adjusted scores:")
        # display(scores, "Scores:")
        # display(smooth_rep, "Updated reputation:")
        # display(outcomes_final, "Outcomes (final):")
        # display(reporter_bonus, "Reporter bonus:")

        # Compare to pyconsensus results
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
                           algorithm="fixed-variance",
                           variance_threshold=variance_threshold,
                           verbose=True).consensus()
        serpent_results = {
            'reputation': map(unfix, smooth_rep),
            'outcomes': map(unfix, outcomes_final),
        }
        python_results = {
            'reputation': pyresults['agents']['smooth_rep'],
            'outcomes': np.array(pyresults['events']['outcomes_final']),
        }
        comparisons = {}
        for m in ('reputation', 'outcomes'):
            comparisons[m] = abs((python_results[m] - serpent_results[m]) / python_results[m])

        pyresults = Oracle(reports=reports,
                           reputation=reputation,
                           event_bounds=event_bounds,
                           algorithm="absolute",
                           variance_threshold=variance_threshold,
                           verbose=True).consensus()
        serpent_results = {
            'reputation': map(unfix, smooth_rep),
            'outcomes': map(unfix, outcomes_final),
        }
        python_results = {
            'reputation': pyresults['agents']['smooth_rep'],
            'outcomes': np.array(pyresults['events']['outcomes_final']),
        }
        comparisons = {}
        for m in ('reputation', 'outcomes'):
            comparisons[m] = abs((python_results[m] - serpent_results[m]) / python_results[m])

        for key, value in comparisons.items():
            try:
                assert((value < tolerance).all())
            except Exception as e:
                print BW("Tolerance exceeded for ") + BR("%s:" % key)
                print "Serpent:    ", np.array(serpent_results[key])
                print "Python:     ", python_results[key]
                print "Difference: ", comparisons[key]

if __name__ == "__main__":
    main()
