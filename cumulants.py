#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cumulant tensors and statistics.  Semi-compatible with Serpent.

"""
from __future__ import division
import array as arr

def array(size, typecode='f'):
    # Emulates Serpent arrays.
    #
    # Args:
    #   size (int): number of elements in the array
    #   typecode (char): data type the array will hold (default: float)
    #
    a = arr.array(typecode, (0,)*size)
    return(a)

def mean(u, size):
    # Calculates the arithmetic mean.
    #
    # Args:
    #   u: numeric array (vector)
    #   size (int): number of elements in u
    #
    m = 0
    while i < size:
        m += u[i]
    m /= size
    return(m)

def dot(u, v, size):
    # Calculates the dot (inner) product.
    #
    # Args:
    #   u: numeric array (vector)
    #   v: numeric array (vector)
    #   size (int): number of elements in u
    #
    prod = 0
    i = 0
    while i < size:
        prod += u[i] * v[i]
        i += 1
    return(prod)

def transpose(a):
    m = len(a)
    n = len(a[0])
    at = []
    for i in range(n):
        at.append([zero] * m)
    for i in range(m):
        for j in range(n):
            at[j][i] = a[i][j]
    return at

def matrixmultiply(a, b, am, bm, an, bn):
    # am = len(a)
    # bm = len(b)
    # an = len(a[0])
    # bn = len(b[0])
    cm = am
    cn = bn
    if bn == 1:
        c[cm]
        # c = [zero] * cm
    else:
        c = []
        i = 0
        while i < cm:
            c[i][cn]
            i += 1
        # for k in range(cm):
        #     c.append([zero] * cn)
    for i in range(cm):
        for j in range(cn):
            for k in range(an):
                if bn == 1:
                    c[i] += a[i][k] * b[k]
                else:
                    c[i][j] += a[i][k] * b[k][j]
    return c


def cov(data, rows, cols, unbias):
    # Covariance matrix (second cumulant).
    #
    # Args:
    #   data: two-dimensional data matrix (signals = columns, samples = rows)
    #   rows: number of rows (samples per signal) in the data matrix
    #   cols: number of columns (signals) in the data matrix
    #
    tensor = [[]] * cols 
    i = 0
    while i < cols:
        j = 0
        tensor[i] = array(cols)
        while j < cols:
            u = 0
            row = 0
            while row < rows:
                i_mean = 0
                j_mean = 0
                r = 0
                while r < rows:
                    i_mean += data[r][i]
                    j_mean += data[r][j]
                    r += 1
                i_mean /= rows
                j_mean /= rows
                i_center = data[row][i] - i_mean
                j_center = data[row][j] - j_mean
                u += i_center * j_center
                row += 1
            tensor[i][j] = u / (rows - unbias)
            j += 1
        i += 1
    return tensor

def coskew(data, rows, cols, unbias):
    # Block-unfolded third cumulant tensor.
    #
    # Args:
    #   data: two-dimensional data matrix (signals = columns, samples = rows)
    #   rows: number of rows (samples per signal) in the data matrix
    #   cols: number of columns (signals) in the data matrix
    #
    tensor = [[]] * cols
    k = 0
    while k < cols:
        face = [[]] * cols
        i = 0
        while i < cols:
            j = 0
            face[i] = array(cols)
            while j < cols:
                u = 0
                row = 0
                while row < rows:
                    i_mean = 0
                    j_mean = 0
                    k_mean = 0
                    r = 0
                    while r < rows:
                        i_mean += data[r][i]
                        j_mean += data[r][j]
                        k_mean += data[r][k]
                        r += 1
                    i_mean /= rows
                    j_mean /= rows
                    k_mean /= rows
                    i_center = data[row][i] - i_mean
                    j_center = data[row][j] - j_mean
                    k_center = data[row][k] - k_mean
                    u += i_center * j_center * k_center
                    row += 1
                face[i][j] = u / (rows - unbias)
                j += 1
            tensor[k] = face
            i += 1
        k += 1
    return tensor

def cokurt(data, rows, cols, unbias):
    # Block-unfolded fourth cumulant tensor.
    #
    # Args:
    #   data: two-dimensional data matrix (signals = columns, samples = rows)
    #   rows: number of rows (samples per signal) in the data matrix
    #   cols: number of columns (signals) in the data matrix
    #
    tensor = [[]] * cols
    l = 0
    while l < cols:
        block = [[]] * cols
        k = 0
        while k < cols:
            face = [[]] * cols
            i = 0
            while i < cols:
                j = 0
                face[i] = array(cols)
                while j < cols:
                    u = 0
                    row = 0
                    while row < rows:
                        i_mean = 0
                        j_mean = 0
                        k_mean = 0
                        l_mean = 0
                        r = 0
                        while r < rows:
                            i_mean += data[r][i]
                            j_mean += data[r][j]
                            k_mean += data[r][k]
                            l_mean += data[r][l]
                            r += 1
                        i_mean /= rows
                        j_mean /= rows
                        k_mean /= rows
                        l_mean /= rows
                        i_center = data[row][i] - i_mean
                        j_center = data[row][j] - j_mean
                        k_center = data[row][k] - k_mean
                        l_center = data[row][l] - l_mean
                        u += i_center * j_center * k_center * l_center
                        row += 1
                    face[i][j] = u / (rows - unbias)
                    j += 1
                block[k] = face
                i += 1
            tensor[l] = block
            k += 1
        l += 1
    return tensor
