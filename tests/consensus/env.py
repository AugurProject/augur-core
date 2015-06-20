from __future__ import division
import os
import sys
import json
from pprint import pprint
import numpy as np
import pandas as pd
from ethereum import tester as t
from pyconsensus import Oracle

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir, "src")

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

YES = 2.0
NO = 1.0
BAD = 1.5
NA = 0.0

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

s = t.state()
t.gas_limit = 750000000
s = t.state()

# reports = np.array([[ YES, YES, YES, YES, YES, YES ],
#                     [ YES, YES, YES,  NO,  NA,  NA ],
#                     [ YES, YES, YES,  NA,  NA,  NO ]])
reports = np.array([[ YES, YES, YES, YES, YES, YES ],
                    [ YES, YES, YES,  NO,  NO,  NO ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ]])
reports = np.array([[ YES, YES, YES, YES, YES, YES ],
                    [ YES, YES, YES,  NO,  NO,  NO ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ],
                    [  NA,  NA,  NA,  NA,  NA,  NA ]])

# reports = np.array([[ YES, YES, YES, YES, YES, YES ],
#                     [ YES, YES, YES,  NO,  NO,  NO ],
#                     [ YES, YES, YES, YES, YES, YES ]])
reputation = [47] * len(reports)
scaled = [0, 0, 0, 0, 0, 0]
scaled_max = np.array([YES, YES, YES, YES, YES, YES]).astype(int).tolist()
scaled_min = np.array([ NO,  NO,  NO,  NO,  NO,  NO]).astype(int).tolist()

# bigger!
# reports = np.array([[ YES, YES, YES, YES, YES, YES,  YES, YES, YES, YES, YES, YES,  YES, YES, YES, YES, YES, YES,  YES, YES, YES, YES, YES, YES,  YES, YES, YES, YES, YES, YES,  YES, YES, YES, YES, YES, YES ],
#                     [ YES, YES, YES,  NO,  NO,  NO,  YES, YES, YES,  NO,  NO,  NO,  YES, YES, YES,  NO,  NO,  NO,  YES, YES, YES,  NO,  NO,  NO,  YES, YES, YES,  NO,  NO,  NO,  YES, YES, YES,  NO,  NO,  NO ],
#                     [  NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA ],
#                     [  NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA ],
#                     [  NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA ],
#                     [  NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA,   NA,  NA,  NA,  NA,  NA,  NA ]])
# reputation = [47, 47, 47, 47]
# scaled = np.zeros(36).astype(int).tolist()
# scaled_max = (np.zeros(36) + 2).astype(int).tolist()
# scaled_min = (np.zeros(36) + 1).astype(int).tolist()

num_events = len(reports[0])
num_reports = len(reputation)
flatsize = num_events * num_reports

print "Reports:"
print reports
print
print "Reputation:"
print reputation
print

reports = map(fix, reports.ravel())
reputation = map(fix, reputation)

c = s.abi_contract(os.path.join(ROOT, "consensus", "interpolate.se"))
# results = c.interpolate(reports, reputation, scaled, scaled_max, scaled_min, profiling=True)
results = c.interpolate(reports, reputation, profiling=True)
reports_interp = np.array(results["output"])
gas_used = results["gas"]
time_elapsed = results["time"]

print "Interpolate:"
print "Gas used:    ", gas_used
print "Time elapsed:", time_elapsed 
print

print "Output:"
print pprint(reports_interp)
print

reports_filled = np.array(fold(map(unfix, reports_interp[:flatsize]), num_events))
reports_mask = np.array(fold(reports_interp[flatsize:], num_events)).astype(float)

print "Reports filled:"
print reports_filled
print
print "Reports mask:"
print reports_mask
print

# outcomes_final = np.array([ 1.0000000, 1.0000000, 1.0000000,  0.50000000,  0.50000000,  0.50000000 ])
# smooth_rep = np.array([ 0.3666667, 0.3000000, 0.3333333 ])
# outcomes_final = map(fix, outcomes_final)
# smooth_rep = map(fix, smooth_rep)
# reports_mask = reports_interp[flatsize:].tolist()

# c = s.abi_contract(os.path.join(ROOT, "consensus", "payout.se"))
# reporter_bonus = c.payout(outcomes_final, smooth_rep, reports_mask, num_reports, num_events)
# try:
#     reporter_bonus = np.array(map(unfix, reporter_bonus))
# except:
#     reporter_bonus = unfix(reporter_bonus)

# print "Reporter bonus:"
# print reporter_bonus
# print
