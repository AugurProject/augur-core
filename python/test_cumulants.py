#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cumulant tensors and statistics.  Semi-compatible with Serpent.

"""
from __future__ import division
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy import signal
from sklearn.decomposition import FastICA, PCA
import cumulants

pd.set_option("display.max_rows", 25)
pd.set_option("display.width", 1000)
pd.options.display.mpl_style = "default"
np.set_printoptions(linewidth=500)

if matplotlib.is_interactive():
    plt.ioff()

tolerance = 1e-5

def calibrate(reports):
    reps = np.array(reports)
    covmat = np.cov(reps.T, bias=1)
    svd_results = np.linalg.svd(covmat)

    # First loading
    L = svd_results[0].T[0]

    # First score
    centers = reps - np.mean(reps, 0)
    S = np.dot(centers, svd_results[0]).T[0]

    # Unweighted
    covmat = np.dot(centers.T, centers) / num_voters

    # PCA
    pca = PCA(n_components=3)
    pc = pca.fit_transform(reports)
    comps = pca.components_

def test_reports():
    # Mixing matrix
    A = np.array([[ 1. ,  1. ,  1. ],
                  [ 0.5,  2. ,  1. ],
                  [ 1.5,  1. ,  2. ]])

    # Observations
    X = np.array([[-0.74486315, -0.91401507, -1.81570038],
                  [ 0.03932519,  1.06492993, -1.58715033],
                  [-0.40766041,  0.39786915, -1.90998106],
                  [ 0.03378855,  0.96729768, -1.01487154],
                  [-0.1791563 ,  0.69517577, -1.49117203],
                  [-0.21862343,  0.97899468, -1.78466729],
                  [-1.42994489, -0.69517222, -3.74990271],
                  [-0.37958269,  0.63853667, -2.03932666],
                  [-0.09768426,  0.23365333, -1.25356991],
                  [ 0.28911204,  1.54498045, -0.7261127 ]])

    H = PCA().fit_transform(X)
    S_ = FastICA(n_components=3).fit_transform(X)

def weighted_cov(reports, reputation):
    rep_coins = (np.abs(np.copy(reputation)) * 10**6).astype(int)

    # Compute the weighted mean (of all voters) for each decision
    weighted_mean = np.ma.average(reports,
                               axis=0,
                               weights=rep_coins.squeeze())

    # Each vote's difference from the mean of its decision (column)
    mean_deviation = np.matrix(reports - weighted_mean)

    # Compute the unbiased weighted population covariance
    # (for uniform weights, equal to np.cov(reports.T, bias=1))
    covariance_matrix = 1/float(np.sum(rep_coins)-1) * np.ma.multiply(mean_deviation, rep_coins).T.dot(mean_deviation)

    return covariance_matrix, mean_deviation

def weighted_PCA(reports):
    covariance_matrix, mean_deviation = weighted_cov(reports)
    U = np.linalg.svd(covariance_matrix)[0]
    first_loading = U.T[0]
    first_score = np.dot(mean_deviation, U).T[0]
    return first_loading, first_score

def test_ICA():
    np.random.seed(0)
    n_samples = 2000
    time = np.linspace(0, 8, n_samples)

    s1 = np.sin(2 * time)  # Signal 1 : sinusoidal signal
    s2 = np.sign(np.sin(3 * time))  # Signal 2 : square signal
    s3 = signal.sawtooth(2 * np.pi * time)  # Signal 3: saw tooth signal

    S = np.c_[s1, s2, s3]
    S += 0.2 * np.random.normal(size=S.shape)  # Add noise

    S /= S.std(axis=0)  # Standardize data
    # Mix data
    A = np.array([[1, 1, 1], [0.5, 2, 1.0], [1.5, 1.0, 2.0]])  # Mixing matrix
    X = np.dot(S, A.T)  # Generate observations

    # Compute ICA
    ica = FastICA(n_components=3)
    S_ = ica.fit_transform(X)  # Reconstruct signals
    A_ = ica.mixing_  # Get estimated mixing matrix

    # We can "prove" that the ICA model applies by reverting the unmixing.
    assert np.allclose(X, np.dot(S_, A_.T) + ica.mean_)

    # For comparison, compute PCA
    pca = PCA(n_components=3)
    H = pca.fit_transform(X)  # Reconstruct signals based on orthogonal components

    return X, S, S_, H

def plot_PCA_ICA(X, S, S_, H):
    plt.figure()

    models = [X, S, S_, H]
    names = ['Observations (mixed signal)',
             'True Sources',
             'ICA recovered signals', 
             'PCA recovered signals']
    colors = ['red', 'steelblue', 'orange']

    for ii, (model, name) in enumerate(zip(models, names), 1):
        plt.subplot(4, 1, ii)
        plt.title(name)
        for sig, color in zip(model.T, colors):
            plt.plot(sig, color=color)

    plt.subplots_adjust(0.09, 0.04, 0.94, 0.94, 0.26, 0.46)
    plt.show()

def test_mean():
    num_signals = 25     # columns
    num_samples = 500    # rows
    data = np.random.randn(num_samples, num_signals)
    expected_mean = np.mean(data, 0)
    for i in range(num_signals):
        actual_mean = cumulants.mean(data[:,i], num_samples)
        assert(actual_mean - expected_mean[i] < 1e-15)

def test_dot():
    num_signals = 25     # columns
    num_samples = 500    # rows
    data = np.random.randn(num_samples, num_signals)
    for i in range(num_signals):
        for j in range(num_signals):
            expected_product = np.dot(data[:,i], data[:,j])
            actual_product = cumulants.dot(data[:,i], data[:,j], num_samples)
            assert(actual_product - expected_product < 1e-12)

def test_outer():
    num_signals = 10     # columns
    num_samples = 50     # rows
    data = np.random.randn(num_samples, num_signals)
    for i in range(num_signals):
        for j in range(num_signals):
            expected_product = np.outer(data[:,i], data[:,j])
            actual_product = cumulants.outer(data[:,i], data[:,j], num_samples)
            assert((actual_product - expected_product < 1e-12).all())

def test_transpose():
    num_rows = 10
    num_cols = 50
    data = np.random.randn(num_rows, num_cols)
    assert((cumulants.transpose(data, num_rows, num_cols) == data.T).all())

def test_matrix_multiply():
    pass

def test_kron():
    num_signals = 10     # columns
    num_samples = 50     # rows
    data = np.random.randn(num_samples, num_signals)
    for i in range(num_signals):
        for j in range(num_signals):
            expected_product = np.kron(data[:,i], data[:,j])
            actual_product = cumulants.kron(data[:,i], data[:,j], num_samples)
            assert((actual_product - expected_product < 1e-15).all())

def test_cumulants():
    unbias = 0
    data = [[ 0.837698,  0.49452,  2.54352 ],
            [-0.294096, -0.39636,  0.728619],
            [-1.62089 , -0.44919,  1.20592 ],
            [-1.06458 , -0.68214, -1.12841 ],
            [ 2.14341 ,  0.7309 ,  0.644968],
            [-0.284139, -1.133  ,  1.98615 ],
            [ 1.19879 ,  2.55633, -0.526461],
            [-0.032277,  0.11701, -0.249265],
            [-1.02516 , -0.44665,  2.50556 ],
            [-0.515272, -0.578  ,  0.515139],
            [ 0.259474, -1.24193,  0.105051],
            [ 0.178546, -0.80547, -0.016838],
            [-0.607696, -0.21319, -1.40657 ],
            [ 0.372248,  0.93341, -0.667086],
            [-0.099814,  0.52698, -0.253867],
            [ 0.743166, -0.79375,  2.11131 ],
            [ 0.109262, -1.28021, -0.415184],
            [ 0.499346, -0.95897, -2.24336 ],
            [-0.191825, -0.59756, -0.63292 ],
            [-1.98255 , -1.5936 , -0.935766],
            [-0.317612,  1.33143, -0.46866 ],
            [ 0.666652, -0.81507,  0.370959],
            [-0.761136,  0.10966, -0.997161],
            [-1.09972 ,  0.28247, -0.846566]]
    rows = len(data)
    cols = len(data[0])
    
    cov_result = cumulants.cov(data, rows, cols, unbias)
    coskew_result = cumulants.coskew(data, rows, cols, unbias)
    cokurt_result = cumulants.cokurt(data, rows, cols, unbias)

    expected_cov = np.cov(np.array(data).T, bias=1)
    # expected_coskew = np.array([[
    #     [ 0.153993 ,  0.161605 ,   0.131816 ],
    #     [ 0.161605 ,  0.433037 ,  -0.035224 ],
    #     [ 0.131816 , -0.035224 ,   0.0136523],
    # ], [
    #     [ 0.161605 ,  0.433037 ,  -0.035224 ],
    #     [ 0.433037 ,  0.899048 ,  -0.314352 ],
    #     [-0.035224 , -0.314352 ,  -0.29955  ],
    # ], [
    #     [ 0.131816 ,  -0.035224,   0.0136523],
    #     [-0.035224 ,  -0.314352,  -0.29955  ],
    #     [ 0.0136523,  -0.29955 ,   1.06208  ],
    # ]])
    expected_coskew = np.array([[
        [ 0.147577 ,   0.154872 ,  0.126324  ],
        [ 0.154872 ,   0.414994 , -0.0337563 ],
        [ 0.126324 ,  -0.0337563,  0.0130835 ],
    ], [
        [ 0.154872 ,   0.414994 , -0.0337563 ],
        [ 0.414994 ,   0.861588 , -0.301254  ],
        [-0.0337563,  -0.301254 , -0.287068  ],
    ], [
        [ 0.126324 ,  -0.0337563,   0.0130835],
        [-0.0337563,  -0.301254 ,  -0.287068 ],
        [ 0.0130835,  -0.287068 ,   1.01782  ],
    ]])
    expected_cokurt = np.array([
        [[
            [ 2.12678  ,  1.11885   ,  0.474782  ],
            [ 1.11885  ,  1.12294   ,  0.187331  ],
            [ 0.474782 ,  0.187331  ,  1.15524   ],
        ], [
            [ 1.11885  ,   1.12294  ,   0.187331 ],
            [ 1.12294  ,   1.40462  ,  -0.0266349],
            [ 0.187331 ,  -0.0266349,   0.276558 ],
        ], [
            [ 0.474782 ,   0.187331 ,  1.15524   ],
            [ 0.187331 ,  -0.0266349,  0.276558  ],
            [ 1.15524  ,   0.276558 ,  0.178083  ],
        ]], [[
            [ 1.11885  ,   1.12294  ,   0.187331 ],
            [ 1.12294  ,   1.40462  ,  -0.0266349],
            [ 0.187331 ,  -0.0266349,   0.276558 ],
        ], [
            [ 1.12294  ,   1.40462  , -0.0266349 ],
            [ 1.40462  ,   3.10288  , -0.517198  ],
            [-0.0266349,  -0.517198 ,  0.779221  ],
        ], [
            [ 0.187331 ,  -0.0266349,  0.276558  ],
            [-0.0266349,  -0.517198 ,  0.779221  ],
            [ 0.276558 ,   0.779221 ,  0.218732  ],
        ]], [[
            [ 0.474782 ,  0.187331  ,  1.15524   ],
            [ 0.187331 , -0.0266349 ,  0.276558  ],
            [ 1.15524  ,  0.276558  ,  0.178083  ],
        ], [
            [ 0.187331 ,  -0.0266349,  0.276558  ],
            [-0.0266349,  -0.517198 ,  0.779221  ],
            [ 0.276558 ,   0.779221 ,  0.218732  ],
        ], [
            [ 1.15524  ,  0.276558  ,  0.178083  ],
            [ 0.276558 ,  0.779221  ,  0.218732  ],
            [ 0.178083 ,  0.218732  ,  5.98947   ],
        ]]
    ])

    assert((np.array(cov_result) - expected_cov < tolerance).all())
    assert((np.array(coskew_result) - expected_coskew < tolerance).all())
    assert((np.array(cokurt_result) - expected_cokurt < tolerance).all())

if __name__ == "__main__":
    reports = [[1, 1, 0, 0],
               [1, 0, 0, 0],
               [1, 1, 0, 0],
               [1, 1, 1, 0],
               [0, 0, 1, 1],
               [0, 0, 1, 1]]
    num_voters = len(reports)
    num_events = len(reports[0])
    calibrate(reports)
    test_mean()
    test_dot()
    test_outer()
    test_transpose()
    test_matrix_multiply()
    test_kron()
    test_cumulants()
    X, S, S_, H = test_ICA()
    # plot_PCA_ICA(X, S, S_, H)
