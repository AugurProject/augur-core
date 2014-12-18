#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
np.set_printoptions(linewidth=500,
                    precision=5,
                    suppress=True,
                    formatter={"float": "{: 0.3f}".format})

if matplotlib.is_interactive():
    plt.ioff()

tolerance = 1e-12
init()

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

def characterize(contract):
    filename = contract + ".se"
    print BB("Contract:"), BG(filename)

    MAX_SIZE = 25
    np.random.seed(0)

    print BR("Events fixed, varying reporters")
    reporters_gas_used = []
    sizes = range(2, MAX_SIZE+1)
    reporters_sizes_used = []
    reporters_errors = []
    num_events = 4
    for k in sizes:
        s = t.state()
        c = s.contract(filename)
        print(str(k) + 'x' + str(num_events))
        reports = np.random.randint(-1, 2, (k, num_events))
        reputation = np.random.randint(1, 100, k)
        try:
            gas_used = s.send(t.k0, c, 0, funid=0, abi=[map(fix, reports.flatten()), map(fix, reputation), 0, 5])
            reporters_gas_used.append(gas_used[0] - gas_used[1])
            reporters_sizes_used.append(k)
        except Exception as exc:
            print(exc)
            break

    print BR("Reporters fixed, varying events")
    sizes = range(2, MAX_SIZE+1)
    events_gas_used = []
    events_sizes_used = []
    num_reporters = 4
    for k in sizes:
        s = t.state()
        c = s.contract(filename)
        print(str(num_reporters) + 'x' + str(k))
        reports = np.random.randint(-1, 2, (num_reporters, k))
        reputation = np.random.randint(1, 100, num_reporters)
        try:
            result = s.send(t.k0, c, 0, funid=0, abi=[map(fix, reports.flatten()), map(fix, reputation), 0, 5])
            events_gas_used.append(result[0] - result[1])
            events_sizes_used.append(k)
        except Exception as exc:
            print(exc)
            break

    print BR("Reporters and events fixed, varying PCA iterations")
    num_reporters = 6
    num_events = 4
    pca_iter_sizes = range(1, 21)
    voter_bonus_rmsd = []
    author_bonus_rmsd = []
    pca_iter_sizes_used = []
    for k in pca_iter_sizes:
        s = t.state()
        c = s.contract(filename)
        print k, "iterations"
        reports = np.random.randint(-1, 2, (num_reporters, num_events))
        reputation = np.random.randint(1, 100, num_reporters)
        try:
            voter_bonus = np.array(map(unfix, s.send(t.k0, c, 0, funid=0, abi=[map(fix, reports.flatten()), map(fix, reputation), 1, k])))
            author_bonus = np.array(map(unfix, s.send(t.k0, c, 0, funid=0, abi=[map(fix, reports.flatten()), map(fix, reputation), 2, k])))
            # compare to pyconsensus results
            outcome = Oracle(votes=reports, reputation=reputation).consensus()
            voter_bonus_rmsd.append(np.mean((voter_bonus - np.array(outcome["agents"]["voter_bonus"]))**2))
            author_bonus_rmsd.append(np.mean((author_bonus - np.array(outcome["events"]["author_bonus"]))**2))
            pca_iter_sizes_used.append(k)
        except Exception as exc:
            print(exc)
            break

    plt.figure()

    plt.subplot(311)
    plt.plot(reporters_sizes_used, reporters_gas_used, 'o-', linewidth=1.5, color="steelblue")
    plt.axis([1, np.max(reporters_sizes_used)+1, np.min(reporters_gas_used)/1.1, np.max(reporters_gas_used)*1.1])
    plt.xlabel("# reporters (" + str(num_events) + " events)")
    plt.ylabel("gas used")
    plt.grid(True)

    plt.subplot(312)
    plt.plot(events_sizes_used, events_gas_used, 'o-', linewidth=1.5, color="steelblue")
    plt.axis([1, np.max(events_sizes_used)+1, np.min(events_gas_used)/1.1, np.max(events_gas_used)*1.1])
    plt.xlabel("# events (" + str(num_reporters) + " reporters)")
    plt.ylabel("gas used")
    plt.grid(True)

    plt.subplot(313)
    plt.plot(pca_iter_sizes_used, voter_bonus_rmsd, 'o-', linewidth=1.5, color="steelblue")
    plt.plot(pca_iter_sizes_used, author_bonus_rmsd, 'o-', linewidth=1.5, color="red")
    # plt.axis([1, np.max(events_sizes_used)+1, np.min(events_gas_used)/1.1, np.max(events_gas_used)*1.1])
    plt.title("red: author bonus (cash/bitcoin), blue: voter bonus (reputation)")
    plt.xlabel("# pca iterations")
    plt.ylabel("RMSD")
    plt.grid(True)

    plt.savefig("parameters.png")
    plt.show()

def main():
    characterize("../consensus")

if __name__ == "__main__":
    main()
