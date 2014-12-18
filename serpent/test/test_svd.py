#!/usr/bin/env python2

from pyethereum import tester as t
import math
import numpy as np

def BR(string): #bright red
    return '\033[1;31m' + string + '\033[0m'

def main():
    np.random.seed(1)
    global s
    global c
    print BR('Forming new test genesis block')
    s = t.state()
    print BR('Compiling emwpca.se')
    c = s.contract('emwpca.se')
    print s.send(t.k0, c, 0, funid=1, abi=[1234])

    # data = np.random.rand(3, 3)
    # weights = np.random.rand(3)
    # weights = np.ones(40)

    data = np.array([[  1,  1, -1,  1],
                     [  1, -1, -1, -1],
                     [  1,  1, -1, -1],
                     [  1,  1,  1, -1],
                     [  1, -1,  1,  1],
                     [ -1, -1,  1,  1]])
    # data = np.array([[  1,  1, -1,  0],
    #                  [  1, -1, -1, -1],
    #                  [  1,  1, -1, -1],
    #                  [  1,  1,  1, -1],
    #                  [  0, -1,  1,  1],
    #                  [ -1, -1,  1,  1]])
    weights = np.array([2, 10, 4, 2, 7, 1])

    print '=== INPUTS ==='
    print data
    print weights

    print '=== MEANS ==='
    means = np.mean(data, axis=0)
    print means

    print '=== CENTERED DATA ===' 
    centered_data = data - means
    print centered_data

    print '=== WEIGHTED MEANS ==='
    weighted_means = np.average(data, axis=0, weights=weights)
    print weighted_means

    print '=== WEIGHTED CENTERED DATA ===' 
    weighted_centered_data = data - weighted_means
    print weighted_centered_data

    print '=== COVARIANCES ==='
    covariances = np.cov(data, rowvar=0, bias=0)
    print covariances
    print 'trace:', np.trace(covariances)

    print '=== WEIGHTED COVARIANCES ==='
    weighted_covariances = 1 / float(np.sum(weights) - 1) * np.multiply(weighted_centered_data.T, weights).dot(weighted_centered_data)
    print weighted_covariances
    print 'trace:', np.trace(weighted_covariances)

    w_cov_eig = np.linalg.eig(weighted_covariances)
    w_cov_svd = np.linalg.svd(weighted_covariances)
    w_cov_svd_rsv = w_cov_svd[2]

    print '=== COVARIANCE EIGENVALUE DECOMPOSITION ==='
    cov_eig = np.linalg.eig(covariances)
    print cov_eig[0]
    print cov_eig[1]

    print '=== FROM SINGULAR VALUE DECOMPOSITION OF CENTERED DATA ==='
    data_svd = np.linalg.svd(centered_data)
    print data_svd[1]
    print data_svd[2]

    print '=== EIGENVALUE DECOMPOSITION OF WEIGHTED COVARIANCE MATRIX ==='
    print w_cov_eig[0]
    print w_cov_eig[1]
    print 'sum:', sum(w_cov_eig[0])

    print '=== FROM SINGULAR VALUE DECOMPOSITION OF WEIGHTED COVARIANCE MATRIX ==='
    print w_cov_svd[1]
    print w_cov_svd[2]
    print 'sum:', sum(w_cov_svd[1])

    # iterative computation of principal components
    print '=== FROM ITERATIVE ALGO ==='
    num_loadings = 1
    loadings = emwpca(data, weights, num_loadings)

    print loadings
    print 'basis error in degrees:', [ math.degrees(math.acos(np.clip(w_cov_svd_rsv[i].dot(loadings[i]), -1, 1)))
        for i in xrange(num_loadings) ]

def emwpca(data, weights, num_loadings):
    num_params = data.shape[1]
    weighted_centered_data = data - np.average(data, axis=0, weights=weights)
    print weighted_centered_data
    loadings = np.zeros(num_params)
    loadings[0] = 1.
    loadings = np.tile(loadings, (num_loadings, 1))
    for i in xrange(num_loadings):
        for j in xrange(5):
            s = np.zeros(num_params)
            for datum, weight in zip(weighted_centered_data, weights):
                s -= datum.dot(loadings[i]) * datum * weight
            loadings[i] = s / math.sqrt(s.dot(s))
        if i < num_loadings - 1:
            for j, datum in enumerate(weighted_centered_data):
                weighted_centered_data[j] -= loadings[i].dot(datum) * loadings[i]
    return loadings

if __name__ == '__main__':
    main()