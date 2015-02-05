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
max_iterations = 10
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

# reports = np.array([[ 1,  1, -1, -1 ],
#                     [ 1, -1, -1, -1 ],
#                     [ 1,  1, -1, -1 ],
#                     [ 1,  1,  1, -1 ],
#                     [-1, -1,  1,  1 ],
#                     [-1, -1,  1,  1 ]])

reports = np.array([[ 1,  1, -1, -1, 233, 16027.59],
                    [ 1, -1, -1, -1, 199,     0.  ],
                    [ 1,  1, -1, -1, 233, 16027.59],
                    [ 1,  1,  1, -1, 250,     0.  ],
                    [-1, -1,  1,  1, 435,  8001.00],
                    [-1, -1,  1,  1, 435, 19999.00]])
reputation = [1, 1, 1, 1, 1, 1]

# pyconsensus bounds format:
#     event_bounds = [
#         {"scaled": True, "min": 0.1, "max": 0.5},
#         {"scaled": True, "min": 0.2, "max": 0.7},
#         {"scaled": False, "min": 0, "max": 1},
#         {"scaled": False, "min": 0, "max": 1},
#     ]
scaled = [0, 0, 0, 0, 1, 1]
scaled_max = [1, 1, 1, 1, 435, 20000]
scaled_min = [-1, -1, -1, -1, 0, 8000]
# scaled = [1, 1, 0, 0]
# scaled_max = [0.5, 0.7, 1, 1]
# scaled_min = [0.1, 0.2, 0, 0]
# scaled = [0, 0, 0, 0]
# scaled_max = [1, 1, 1, 1]
# scaled_min = [0, 0, 0, 0]

# num_voters = 25
# num_events = 25
# reports = np.random.randint(-1, 2, (num_voters, num_events))
# reputation = np.random.randint(1, 100, num_voters)
# scaled = np.random.randint(0, 2, num_events).tolist()
# scaled_max = np.ones(num_events)
# scaled_min = -np.ones(num_events)
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

def display(arr, description=None):
    if description is not None:
        print(BB(description))
    print(pd.DataFrame({
        'result': arr,
        'base 16': map(hex, arr),
        'base 2^64': map(unfix, arr),
    }))

def serpent_function(s, c, name, signature, args=[]):
    sys.stdout.write("  " + BG(name) + " ")
    sys.stdout.flush()
    profile = s.profile(t.k0, c, 0, name, signature, args)
    print "%i gas (%d seconds)" % (profile['gas'], profile['time'])
    return s.call(t.k0, c, 0, name, signature, args)

def test_contract(contract):
    s = t.state()
    filename = contract + ".se"
    print BB("Testing contract:"), BG(filename)
    c = s.contract(filename)

    num_voters = len(reputation)
    num_events = len(reports[0])
    v_size = num_voters * num_events

    reputation_fixed = map(fix, reputation)
    reports_fixed = map(fix, reports.flatten())
    scaled_max_fixed = map(fix, scaled_max)
    scaled_min_fixed = map(fix, scaled_min)

    arglist = [reports_fixed, reputation_fixed, scaled, scaled_max_fixed, scaled_min_fixed]
    result = serpent_function(s, c, "interpolate", "aaaaa", args=arglist)
    result = np.array(result)
    votes_filled = result[0:v_size].tolist()
    votes_mask = result[v_size:(2*v_size)].tolist()
    del result

    arglist = [votes_filled, reputation_fixed, scaled, scaled_max_fixed, scaled_min_fixed]
    weighted_centered_data = serpent_function(s, c, "center", "aaaaa", args=arglist)

    s = t.state()
    c = s.contract(filename)

    # multistep pca
    arglist = [num_events, max_iterations]
    loading_vector = serpent_function(s, c, "pca_init", "ii", args=arglist)

    while (loading_vector[num_events] > 0):
        arglist = [loading_vector, weighted_centered_data, reputation_fixed, num_voters, num_events]
        loading_vector = serpent_function(s, c, "pca_loadings", "aaaii", args=arglist)

    arglist = [loading_vector, weighted_centered_data, num_voters, num_events]
    scores = serpent_function(s, c, "pca_scores", "aaii", args=arglist)

    s = t.state()
    c = s.contract(filename)

    arglist = [scores, num_voters, num_events]
    result = serpent_function(s, c, "calibrate_sets", "aii", args=arglist)
    result = np.array(result)
    set1 = result[0:num_voters].tolist()
    set2 = result[num_voters:(2*num_voters)].tolist()
    assert(len(set1) == len(set2))
    assert(len(result) == 2*num_voters)
    del result

    arglist = [set1, set2, reputation_fixed, votes_filled, num_voters, num_events]
    result = serpent_function(s, c, "calibrate_wsets", "aaaaii", args=arglist)
    result = np.array(result)
    old = result[0:num_events].tolist()
    new1 = result[num_events:(2*num_events)].tolist()
    new2 = result[(2*num_events):(3*num_events)].tolist()
    assert(len(result) == 3*num_events)
    assert(len(old) == len(new1) == len(new2))
    del result

    arglist = [old, new1, new2, set1, set2, scores, num_voters, num_events]
    adj_prin_comp = serpent_function(s, c, "pca_adjust", "aaaaaaii", args=arglist)

    arglist = [adj_prin_comp, reputation_fixed, num_voters, num_events]
    smooth_rep = serpent_function(s, c, "smooth", "aaii", args=arglist)

    arglist = [smooth_rep, reputation_fixed, votes_filled, num_voters, num_events]
    result = serpent_function(s, c, "consensus", "aaaii", args=arglist)
    result = np.array(result)
    outcomes_final = result[0:num_events].tolist()
    consensus_reward = result[num_events:(2*num_events)].tolist()
    assert(len(outcomes_final) == len(consensus_reward))
    del result

    arglist = [outcomes_final, consensus_reward, smooth_rep, votes_mask, num_voters, num_events]
    result = serpent_function(s, c, "participation", "aaaaii", args=arglist)

    display(result, "Results:")

def main():
    global s
    print BR("Forming new test genesis block")
    s = t.state()
    contracts = [
        "consensus",
    ]
    for contract in contracts:
        test_contract(contract)

if __name__ == "__main__":
    main()
