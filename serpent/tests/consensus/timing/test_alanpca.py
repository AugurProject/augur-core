#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Timing tests for AlanPCA (first eigenvector only)

"""
import sys
import time
import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

np.set_printoptions(linewidth=225,
                    suppress=True,
                    formatter={"float": "{: 0.6f}".format})
np.random.seed(0)

if matplotlib.is_interactive():
    plt.ioff()

MAX_SIZE = 100
PCA_ITERATIONS = 25
TIMER_ITERATIONS = 100

def fix(x):
    return int(x * 0x10000000000000000)

def unfix(x):
    return x / 0x10000000000000000

def array(size):
    return [0] * size

def emwpca(data, weights):
    num_obs = len(weights)
    num_params = len(data) / len(weights)

    # weighted_centered_data = data - numpy.average(data, axis=0, weights=weights)
    weighted_means = array(num_params)
    total_weight = 0
    i = 0
    while i < num_obs:
        j = 0
        while j < num_params:
            weighted_means[j] += weights[i] * data[i * num_params + j]
            j += 1
        total_weight += weights[i]
        i += 1

    j = 0
    while j < num_params:
        weighted_means[j] /= total_weight
        j += 1

    weighted_centered_data = array(len(data))
    i = 0
    while i < len(data):
        weighted_centered_data[i] = data[i] - weighted_means[i % num_params]
        i += 1

    # initialize the loading vector
    loading_vector = array(num_params)
    loading_vector[0] = 0x10000000000000000

    for i in range(PCA_ITERATIONS):
    # while i < 25:
        # s = numpy.zeros(num_params)
        s = array(num_params)
        # for wcdatum, weight in zip(weighted_centered_data, weights):
        j = 0
        while j < num_obs:
            # s -= wcdatum.dot(loadings[i]) * wcdatum * weight
            d_dot_lv = 0
            k = 0
            while k < num_params:
                d_dot_lv += weighted_centered_data[j * num_params + k] * loading_vector[k]
                k += 1
            d_dot_lv /= 0x10000000000000000
            k = 0
            while k < num_params:
                s[k] -= d_dot_lv * weighted_centered_data[j * num_params + k] * weights[j]
                k += 1
            j += 1
        # loading_vector = normalize(s)
        # (first rejig s to account for double fixed multiplication in loop)
        j = 0
        while j < num_params:
            s[j] /= 0x100000000000000000000000000000000
            j += 1
        # QQ
        s_dot_s = 0
        j = 0
        while j < num_params:
            s_dot_s += s[j] * s[j]
            j += 1
        s_dot_s /= 0x10000000000000000
        # QQ!!!!
        norm_s = s_dot_s / 2
        j = 0
        while j < 11:
            norm_s = (norm_s + s_dot_s*0x10000000000000000/norm_s) / 2
            j += 1
        # fuggin assign
        j = 0
        while j < num_params:
            loading_vector[j] = s[j]*0x10000000000000000/norm_s
            j += 1

        i += 1

    return loading_vector

def randomized_inputs(num_reports=50, num_events=25):
    reports = map(fix, np.random.randint(-1, 2, (num_reports, num_events)).ravel().tolist())
    reputation = map(fix, np.random.randint(1, 100, num_reports).ravel().tolist())
    return reports, reputation

def time_events():
    print "Timing AlanPCA (randomized inputs, events only)..."
    sizes = range(5, MAX_SIZE+1, 5)
    sizes_used = []
    mean_time_elapsed = []
    std_time_elapsed = []
    for k in sizes:
        sys.stdout.write("  %dx%d" % (20, k))
        sys.stdout.flush()
        data, weights = randomized_inputs(20, k)
        time_elapsed = []
        for i in range(TIMER_ITERATIONS):
            start_time = time.time() * 1000
            lv = emwpca(data, weights)
            time_elapsed.append(time.time() * 1000 - start_time)
        print "\t->", np.round(np.mean(time_elapsed), 4), "+/-",
        print np.round(np.std(time_elapsed), 4), "ms"
        mean_time_elapsed.append(np.mean(time_elapsed))
        std_time_elapsed.append(np.std(time_elapsed, ddof=1) / (TIMER_ITERATIONS - 1))
        sizes_used.append(str(k))
    
    mean_time_elapsed = np.array(mean_time_elapsed).astype(float)
    std_time_elapsed = np.array(std_time_elapsed).astype(float)
    sizes_used = np.array(sizes_used).astype(float)

    # Plot results and save to file
    plt.figure()
    plt.errorbar(sizes_used,
                 mean_time_elapsed,
                 yerr=std_time_elapsed,
                 fmt='o-',
                 linewidth=1.5,
                 color="steelblue")
    plt.axis([np.min(sizes_used)-1,
              np.max(sizes_used)+1,
              0,
              np.max(mean_time_elapsed)*1.1])
    plt.xlabel("number of events (number of reporters fixed)")
    plt.ylabel("time elapsed (ms)")
    plt.grid(True)
    plt.savefig("timing_alanpca_events_%d.png" % int(round(time.time())))
    plt.show()

def time_reporters():
    print "Timing AlanPCA (randomized inputs, reporters only)..."
    sizes = range(5, MAX_SIZE+1, 5)
    sizes_used = []
    mean_time_elapsed = []
    std_time_elapsed = []
    for k in sizes:
        sys.stdout.write("  %dx%d" % (k, 20))
        sys.stdout.flush()
        data, weights = randomized_inputs(k, 20)
        time_elapsed = []
        for i in range(TIMER_ITERATIONS):
            start_time = time.time() * 1000
            lv = emwpca(data, weights)
            time_elapsed.append(time.time() * 1000 - start_time)
        print "\t->", np.round(np.mean(time_elapsed), 4), "+/-",
        print np.round(np.std(time_elapsed), 4), "ms"
        mean_time_elapsed.append(np.mean(time_elapsed))
        std_time_elapsed.append(np.std(time_elapsed, ddof=1) / (TIMER_ITERATIONS - 1))
        sizes_used.append(str(k))
    
    mean_time_elapsed = np.array(mean_time_elapsed).astype(float)
    std_time_elapsed = np.array(std_time_elapsed).astype(float)
    sizes_used = np.array(sizes_used).astype(float)

    # Plot results and save to file
    plt.figure()
    plt.errorbar(sizes_used,
                 mean_time_elapsed,
                 yerr=std_time_elapsed,
                 fmt='o-',
                 linewidth=1.5,
                 color="steelblue")
    plt.axis([np.min(sizes_used)-1,
              np.max(sizes_used)+1,
              0,
              np.max(mean_time_elapsed)*1.1])
    plt.xlabel("number of reporters (number of events fixed)")
    plt.ylabel("time elapsed (ms)")
    plt.grid(True)
    plt.savefig("timing_alanpca_reporters_%d.png" % int(round(time.time())))
    plt.show()

def time_both():
    print "Timing AlanPCA (randomized inputs)..."
    sizes = range(5, MAX_SIZE+1, 5)
    sizes_used = []
    mean_time_elapsed = []
    std_time_elapsed = []
    for k in sizes:
        sys.stdout.write("  %dx%d" % (k, k))
        sys.stdout.flush()
        data, weights = randomized_inputs(k, k)
        time_elapsed = []
        for i in range(TIMER_ITERATIONS):
            start_time = time.time() * 1000
            lv = emwpca(data, weights)
            time_elapsed.append(time.time() * 1000 - start_time)
        print "\t->", np.round(np.mean(time_elapsed), 4), "+/-",
        print np.round(np.std(time_elapsed), 4), "ms"
        mean_time_elapsed.append(np.mean(time_elapsed))
        std_time_elapsed.append(np.std(time_elapsed, ddof=1) / (TIMER_ITERATIONS - 1))
        sizes_used.append(str(k + k))
    
    mean_time_elapsed = np.array(mean_time_elapsed).astype(float)
    std_time_elapsed = np.array(std_time_elapsed).astype(float)
    sizes_used = np.array(sizes_used).astype(float)

    # Plot results and save to file
    plt.figure()
    plt.errorbar(sizes_used,
                 mean_time_elapsed,
                 yerr=std_time_elapsed,
                 fmt='o-',
                 linewidth=1.5,
                 color="steelblue")
    plt.axis([np.min(sizes_used)-1,
              np.max(sizes_used)+1,
              0,
              np.max(mean_time_elapsed)*1.1])
    plt.xlabel("number of reporters + number of events")
    plt.ylabel("time elapsed (ms)")
    plt.grid(True)
    plt.savefig("timing_alanpca_%d.png" % int(round(time.time())))
    plt.show()

def main():
    time_both()
    time_reporters()
    time_events()

if __name__ == '__main__':
    main()
