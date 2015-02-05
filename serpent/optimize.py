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
from pprint import pprint
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
try:
    from colorama import Fore, Style, init
except ImportError:
    pass
from pyethereum import tester as t
from pyconsensus import Oracle

pd.set_option("display.max_rows", 25)
pd.set_option("display.width", 1000)
pd.options.display.mpl_style = "default"
np.set_printoptions(linewidth=500)
                    # precision=5,
                    # suppress=True,
                    # formatter={"float": "{: 0.3f}".format})
tolerance = 1e-12
init()
if matplotlib.is_interactive():
    plt.ioff()

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

def consensus(reports, reputation, max_iterations=10):
    s = t.state()
    filename = "consensus.se"
    c = s.contract(filename)

    num_voters = len(reputation)
    num_events = len(reports[0])
    v_size = len(reports.flatten())

    reputation_fixed = map(fix, reputation)
    reports_fixed = map(fix, reports.flatten())

    # tx 1: consensus()
    result = s.send(t.k0, c, 0,
                    funid=0,
                    abi=[reports_fixed, reputation_fixed, max_iterations])

    result = np.array(result)
    weighted_centered_data = result[0:v_size]
    votes_filled = result[v_size:(2*v_size)]
    votes_mask = result[(2*v_size):(3*v_size)]

    # pca()
    s = t.state()
    c = s.contract(filename)
    scores = s.send(t.k0, c, 0,
                    funid=1,
                    abi=[weighted_centered_data.tolist(),
                         reputation_fixed,
                         num_voters,
                         num_events,
                         max_iterations])

    # consensus2()
    s = t.state()
    c = s.contract(filename)
    retval = s.send(t.k0, c, 0,
                    funid=2,
                    abi=[reputation_fixed,
                         scores,
                         votes_filled.tolist(),
                         votes_mask.tolist(),
                         num_voters,
                         num_events])

    outcome_final = retval[0:num_events]
    author_bonus = retval[num_events:(2*num_events)]
    voter_bonus = retval[(2*num_events):-2]

    return outcome_final, author_bonus, voter_bonus, retval[-2] - retval[-1]

def profile(contract):
    filename = contract + ".se"
    print BB("Contract:"), BG(filename)

    MAX_SIZE = 25
    np.random.seed(0)

    print BR("Events fixed, varying reporters")
    # s = t.state()
    # c = s.contract(filename)
    reporters_gas_used = []
    sizes = range(2, MAX_SIZE+1)
    reporters_sizes_used = []
    reporters_errors = []
    num_events = 4
    for k in sizes:
        print(str(k) + 'x' + str(num_events))
        reports = np.random.randint(-1, 2, (k, num_events))
        reputation = np.random.randint(1, 100, k)
        try:
            # gas_used = s.send(t.k0, c, 0,
            #                   funid=0,
            #                   abi=[map(fix, reports.flatten()),
            #                        map(fix, reputation),
            #                        5])
            gas_used = consensus(reports, reputation, max_iterations=5)[-1]
            reporters_gas_used.append(gas_used)
            reporters_sizes_used.append(k)
        except Exception as exc:
            print(exc)
            break

    print BR("Reporters fixed, varying events")
    # s = t.state()
    # c = s.contract(filename)
    sizes = range(2, MAX_SIZE+1)
    events_gas_used = []
    events_sizes_used = []
    num_reporters = 4
    for k in sizes:
        print(str(num_reporters) + 'x' + str(k))
        reports = np.random.randint(-1, 2, (num_reporters, k))
        reputation = np.random.randint(1, 100, num_reporters)
        try:
            # gas_used = s.send(t.k0, c, 0,
            #                   funid=0,
            #                   abi=[map(fix, reports.flatten()),
            #                        map(fix, reputation),
            #                        5])
            gas_used = consensus(reports, reputation, max_iterations=5)[-1]
            events_gas_used.append(gas_used)
            events_sizes_used.append(k)
        except Exception as exc:
            print(exc)
            break

    print BR("Reporters and events fixed, varying PCA iterations")
    num_reporters = 6
    num_events = 4
    pca_iter_sizes = range(1, 31)
    voter_bonus_rmsd = []
    author_bonus_rmsd = []
    outcome_rmsd = []
    pca_iter_sizes_used = []
    for k in pca_iter_sizes:
        # s = t.state()
        # c = s.contract(filename)
        print k, "iterations"
        reports = np.random.randint(-1, 2, (num_reporters, num_events))
        reputation = np.random.randint(1, 100, num_reporters)
        try:
            # retval = np.array(map(unfix, s.send(t.k0, c, 0, funid=0, abi=[map(fix, reports.flatten()), map(fix, reputation), k])))
            outcome_final, author_bonus, voter_bonus = consensus(reports, reputation, max_iterations=k)

            # compare to pyconsensus results
            outcome = Oracle(votes=reports, reputation=reputation).consensus()
            outcome_rmsd.append(np.mean((outcome_final - np.array(outcome["events"]["outcome_final"]))**2))
            voter_bonus_rmsd.append(np.mean((voter_bonus - np.array(outcome["agents"]["voter_bonus"]))**2))
            author_bonus_rmsd.append(np.mean((author_bonus - np.array(outcome["events"]["author_bonus"]))**2))
            pca_iter_sizes_used.append(k)
        except Exception as exc:
            print(exc)
            break

    plt.figure()

    plt.subplot(411)
    plt.plot(reporters_sizes_used, reporters_gas_used, 'o-', linewidth=1.5, color="steelblue")
    plt.axis([1, np.max(reporters_sizes_used)+1, np.min(reporters_gas_used)/1.1, np.max(reporters_gas_used)*1.1])
    plt.xlabel("# reporters (" + str(num_events) + " events)")
    plt.ylabel("gas used")
    plt.grid(True)

    plt.subplot(412)
    plt.plot(events_sizes_used, events_gas_used, 'o-', linewidth=1.5, color="steelblue")
    plt.axis([1, np.max(events_sizes_used)+1, np.min(events_gas_used)/1.1, np.max(events_gas_used)*1.1])
    plt.xlabel("# events (" + str(num_reporters) + " reporters)")
    plt.ylabel("gas used")
    plt.grid(True)

    plt.subplot(421)
    plt.plot(pca_iter_sizes_used, voter_bonus_rmsd, 'o-', linewidth=1.5, color="steelblue")
    plt.plot(pca_iter_sizes_used, author_bonus_rmsd, 'o-', linewidth=1.5, color="red")
    # plt.axis([1, np.max(events_sizes_used)+1, np.min(events_gas_used)/1.1, np.max(events_gas_used)*1.1])
    plt.title("red: author bonus (cash/bitcoin), blue: voter bonus (reputation)")
    plt.xlabel("# pca iterations")
    plt.ylabel("RMSD")
    plt.grid(True)

    plt.subplot(422)
    plt.plot(pca_iter_sizes_used, outcome_rmsd, 'o-', linewidth=1.5, color="steelblue")
    plt.title("outcome")
    plt.xlabel("# pca iterations")
    plt.ylabel("RMSD")
    plt.grid(True)

    plt.savefig("parameters.png")
    plt.show()

def main():
    profile("consensus")

if __name__ == "__main__":
    main()
