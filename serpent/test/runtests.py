#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This software (Augur) allows buying and selling event options in Ethereum.

Copyright (c) 2014 Chris Calderon, Joey Krug, Alan Lu, Jack Peterson

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
from pprint import pprint
import numpy as np
import pandas as pd
try:
    from colorama import Fore, Style, init
except ImportError:
    pass
from pyethereum import tester as t

np.set_printoptions(linewidth=500)
pd.set_option("display.max_rows", 25)
pd.set_option("display.width", 1000)
pd.set_option('display.float_format', lambda x: '%.8f' % x)

# max_iterations: number of blocks required to complete PCA
max_iterations = 4
tolerance = 1e-12
init()

# true=1, false=-1, indeterminate=0.5, no response=0
# reports = np.array([[  1,  1, -1,  0],
#                     [  1, -1, -1, -1],
#                     [  1,  1, -1, -1],
#                     [  1,  1,  1, -1],
#                     [  0, -1,  1,  1],
#                     [ -1, -1,  1,  1]])
# reports = np.array([[  1,  1, -1,  1],
#                     [  1, -1, -1, -1],
#                     [  1,  1, -1, -1],
#                     [  1,  1,  1, -1],
#                     [  1, -1,  1,  1],
#                     [ -1, -1,  1,  1]])
# reputation = [2, 10, 4, 2, 7, 1]

reports = np.array([[ 1,  1, -1, -1 ],
                    [ 1, -1, -1, -1 ],
                    [ 1,  1, -1, -1 ],
                    [ 1,  1,  1, -1 ],
                    [-1, -1,  1,  1 ],
                    [-1, -1,  1,  1 ]])
reputation = [1, 1, 1, 1, 1, 1]

# pyconsensus bounds format:
#     event_bounds = [
#         {"scaled": True, "min": 0.1, "max": 0.5},
#         {"scaled": True, "min": 0.2, "max": 0.7},
#         {"scaled": False, "min": 0, "max": 1},
#         {"scaled": False, "min": 0, "max": 1},
#     ]
# scaled = [1, 1, 0, 0]
# scaled_max = [0.5, 0.7, 1, 1]
# scaled_min = [0.1, 0.2, 0, 0]
scaled = [0, 0, 0, 0]
scaled_max = [1, 1, 1, 1]
scaled_min = [0, 0, 0, 0]

# num_voters = 25
# num_events = 25
# reports = np.random.randint(-1, 2, (num_voters, num_events))
# reputation = np.random.randint(1, 100, num_voters)
# scaled = np.random.randint(0, 2, num_events).tolist()
# scaled_max = np.ones(num_events)
# scaled_min = np.zeros(num_events)
# for i in range(num_events):
#     if scaled[i]:
#         scaled_max[i] = np.random.randint(1, 100)
#         scaled_min[i] = np.random.randint(0, scaled_max[i])
# scaled_max = scaled_max.astype(int).tolist()
# scaled_min = scaled_min.astype(int).tolist()

def BR(string): # bright red
    return "\033[1;31m" + str(string) + "\033[0m"

def BB(string): # bright blue
    return Fore.BLUE + Style.BRIGHT + str(string) + Style.RESET_ALL

def BG(string): # bright green
    return Fore.GREEN + Style.BRIGHT + str(string) + Style.RESET_ALL

def blocky(*strings, **kwds):
    colored = kwds.get("colored", True)
    width = kwds.get("width", 108)
    bound = width*"#"
    fmt = "#{:^%d}#" % (width - 2)
    lines = [bound]
    for string in strings:
        lines.append(fmt.format(string))
    lines.append(bound)
    lines = "\n".join(lines)
    if colored:
        lines = BR(lines)
    return lines

def fix(x):
    return int(x * 0x10000000000000000)

def unfix(x):
    return x / 0x10000000000000000

def test_contract(contract):
    s = t.state()
    filename = contract + ".se"
    print BB("Testing contract:"), BG(filename)
    c = s.contract(filename)
    if contract == "dot":
        num_signals = 10   # columns
        num_samples = 5    # rows
        data = (np.random.rand(num_samples, num_signals) * 10).astype(int)
        for i in range(num_signals):
            for j in range(num_signals):
                expected = np.dot(data[:,i], data[:,j])
                actual = s.send(t.k0, c, 0, funid=0, abi=(list(data[:,i]),))
                try:
                    assert(actual - expected < tolerance)
                except:
                    print(actual)
    elif contract == "mean":
        num_signals = 10      # columns
        num_samples = 5       # rows
        data = (np.random.rand(num_samples, num_signals) * 10).astype(int)
        expected = np.mean(data, 0)
        for i in range(num_signals):
            result = s.send(t.k0, c, 0, funid=0, abi=(list(data[:,i]),))
            actual = unfix(result[0])
            try:
                assert(actual - expected[i] < tolerance)
            except:
                print(actual)
    elif contract == "interpolate":
        result = s.send(t.k0, c, 0, funid=0, abi=[])
        actual = map(unfix, result)
        expected = [0.94736842105263164,
                    0.30769230769230776,
                    0.38461538461538469,
                    0.33333333333333337]
        try:
            assert((np.asarray(actual) - np.asarray(expected) < tolerance).all())
        except:
            print(actual)
    elif contract == "../consensus":
        num_voters = len(reputation)
        num_events = len(reports[0])
        v_size = num_voters * num_events

        reputation_fixed = map(fix, reputation)
        reports_fixed = map(fix, reports.flatten())
        scaled_max_fixed = map(fix, scaled_max)
        scaled_min_fixed = map(fix, scaled_min)

        # tx 1: interpolate()
        print("interpolate")
        result = s.send(t.k0, c, 0, funid=0,
                        abi=[reports_fixed,
                             reputation_fixed,
                             scaled,
                             scaled_max_fixed,
                             scaled_min_fixed])
        print(pd.DataFrame({
            'result': result,
            'base 16': map(hex, result),
            'base 2^64': map(unfix, result),
        }))
        result = np.array(result)
        votes_filled = result[0:v_size].tolist()
        votes_mask = result[v_size:(2*v_size)].tolist()
        del result

        # tx 2: center()
        print("center")
        weighted_centered_data = s.send(t.k0, c, 0, funid=1,
                                        abi=[votes_filled,
                                             reputation_fixed,
                                             scaled,
                                             scaled_max_fixed,
                                             scaled_min_fixed])
        s = t.state()
        c = s.contract(filename)

        # multistep pca
        # pca_init()
        print("pca: loadings")
        loading_vector = s.send(t.k0, c, 0, funid=2,
                                abi=[num_events,
                                     max_iterations])

        # pca_loadings()
        while (loading_vector[num_events] > 0):
            loading_vector = s.send(t.k0, c, 0, funid=3,
                                    abi=[loading_vector,
                                         weighted_centered_data,
                                         reputation_fixed,
                                         num_voters,
                                         num_events])

        # pca_scores()
        print("pca: scores")
        scores = s.send(t.k0, c, 0, funid=4,
                        abi=[loading_vector,
                             weighted_centered_data,
                             num_voters,
                             num_events])

        s = t.state()
        c = s.contract(filename)

        print("calibrate_sets")
        # print(s.profile(t.k0, c, 0,
        #           funid=6,
        #           abi=[scores,
        #                num_voters,
        #                num_events]))
        result = s.send(t.k0, c, 0, funid=6,
                        abi=[scores,
                             num_voters,
                             num_events])
        result = np.array(result)
        set1 = result[0:num_voters].tolist()
        set2 = result[num_voters:(2*num_voters)].tolist()
        assert(len(set1) == len(set2))
        assert(len(result) == 2*num_voters)
        del result

        print("calibrate_wsets")
        result = s.send(t.k0, c, 0, funid=7,
                        abi=[set1,
                             set2,
                             reputation_fixed,
                             votes_filled,
                             num_voters,
                             num_events])
        result = np.array(result)
        old = result[0:num_events].tolist()
        new1 = result[num_events:(2*num_events)].tolist()
        new2 = result[(2*num_events):(3*num_events)].tolist()
        assert(len(result) == 3*num_events)
        assert(len(old) == len(new1) == len(new2))
        del result

        print("pca_adjust")
        adj_prin_comp = s.send(t.k0, c, 0, funid=8,
                               abi=[old,
                                    new1,
                                    new2,
                                    set1,
                                    set2,
                                    scores,
                                    num_voters,
                                    num_events])

        print("smooth")
        smooth_rep = s.send(t.k0, c, 0, funid=9,
                            abi=[adj_prin_comp,
                                 reputation_fixed,
                                 num_voters,
                                 num_events])

        print("consensus")
        result = s.send(t.k0, c, 0, funid=10,
                        abi=[smooth_rep,
                             reputation_fixed,
                             votes_filled,
                             num_voters,
                             num_events])
        result = np.array(result)
        outcomes_final = result[0:num_events].tolist()
        consensus_reward = result[num_events:(2*num_events)].tolist()
        assert(len(outcomes_final) == len(consensus_reward))
        del result

        print("participation")
        result = s.send(t.k0, c, 0,
                        funid=11,
                        abi=[outcomes_final,
                             consensus_reward,
                             smooth_rep,
                             votes_mask,
                             num_voters,
                             num_events])
        print(pd.DataFrame({
            'result': result,
            'base 16': map(hex, result),
            'base 2^64': map(unfix, result),
        }))

    elif contract == "../consensus-readable":
        result = s.send(t.k0, c, 0,
                        funid=0,
                        abi=[map(fix, reports.flatten()), map(fix, reputation), max_iterations])

        print(pd.DataFrame({
            'result': result,
            'base 16': map(hex, result),
            'base 2^64': map(unfix, result),
        }))

    else:
        result = s.send(t.k0, c, 0, funid=0, abi=[])
        try:
            assert(result == [1])
        except:
            try:
                assert(map(unfix, result) == [1])
            except:
                print(pd.DataFrame({
                    'result': result,
                    'base 16': map(hex, result),
                    'base 2^64': map(unfix, result),
                }))

def main():
    global s
    print BR("Forming new test genesis block")
    s = t.state()
    contracts = [
        # "sum",
        # "mean",
        # "catch",
        # "get_weight",
        "../consensus",
        # "../consensus-readable", 
    ]
    for contract in contracts:
        test_contract(contract)

if __name__ == "__main__":
    main()
