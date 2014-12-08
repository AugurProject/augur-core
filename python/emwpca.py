#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import numpy as np

np.set_printoptions(linewidth=500)

def emwpca(data, weights, num_loadings):
    num_params = data.shape[1]
    weighted_centered_data = data - np.average(data, axis=0, weights=weights)
    loadings = np.zeros(num_params)
    loadings[0] = 1.
    loadings = np.tile(loadings, (num_loadings, 1))
    for i in xrange(num_loadings):
        for j in xrange(25):
            s = np.zeros(num_params)
            for datum, weight in zip(weighted_centered_data, weights):
                s += datum.dot(loadings[i]) * datum * weight
            loadings[i] = s / math.sqrt(s.dot(s))
        if i < num_loadings - 1:
            for j, datum in enumerate(weighted_centered_data):
                weighted_centered_data[j] -= loadings[i].dot(datum) * loadings[i]
    return loadings

if __name__ == "__main__":
    data = [[1, 1, 0, 0],
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 1]]
    weights = np.matrix([0.2, 0.15, 0.1, 0.2, 0.3, 0.1]).T
    weights /= np.sum(weights)
    num_loadings = 4
    print(emwpca(np.array(data), weights, num_loadings))
