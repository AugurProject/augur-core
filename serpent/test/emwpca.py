from __future__ import division
from pyethereum import tester as t
import math
import numpy as np

np.set_printoptions(linewidth=500)

contract_code = """
def emwpca(data:a, weights:a):
    num_obs = arglen(weights)
    num_params = arglen(data) / arglen(weights)

    # weighted_centered_data = data - np.average(data, axis=0, weights=weights)
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

    weighted_centered_data = array(arglen(data))
    i = 0
    while i < arglen(data):
        weighted_centered_data[i] = data[i] - weighted_means[i % num_params]
        i += 1

    # initialize the loading vector
    loading_vector = array(num_params)
    loading_vector[0] = 0x10000000000000000

    i = 0
    # for j in xrange(ITERATIONS_CAP):
    while i < 25:
        # s = np.zeros(num_params)
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

    return(loading_vector, num_params)
"""

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
                s -= datum.dot(loadings[i]) * datum * weight
            loadings[i] = s / math.sqrt(s.dot(s))
        if i < num_loadings - 1:
            for j, datum in enumerate(weighted_centered_data):
                weighted_centered_data[j] -= loadings[i].dot(datum) * loadings[i]
    return loadings

def get_weight(v):
    v = abs(v)
    sum_v = np.sum(v)
    if sum_v == 0:
        v += 1
    return v / sum_v

def catch(X):
    if X < 0.5 * (1 - 0.1):
        return 0
    elif X > 0.5 * (1 + 0.1):
        return 1
    else:
        return .5

def test_emwpca():
    def nparray2fixedlist(a):
        return map(lambda x: int(x), (a * 0x10000000000000000).tolist())

    def fixedlist2nparray(l):
        return np.array(l).astype(float) / 0x10000000000000000

    s = t.state()
    c = s.contract(contract_code)

    np.random.seed(0)
    shape = (3, 2)
    # data = np.random.rand(*shape)
    # weights = np.random.rand(shape[0])

    data = np.array([[10, 10,  0, 10],
                     [10,  0,  0,  0],
                     [10, 10,  0,  0],
                     [10, 10, 10,  0],
                     [10,  0, 10, 10],
                     [ 0,  0, 10, 10]])
    weights = np.array([2, 10, 4, 2, 7, 1])

    # print data
    # print weights
    # print nparray2fixedlist(data.flatten())
    # print nparray2fixedlist(weights)

    weighted_centered_data = data - np.average(data, axis=0, weights=weights)
    # print
    # print "WEIGHTED CENTERED DATA"
    # print weighted_centered_data

    loading = emwpca(data, weights, 1)[0]
    # print
    # print "LOADINGS"
    # print loading

    # print fixedlist2nparray(s.send(t.k0, c, 0, funid=0, abi=[ nparray2fixedlist(data.flatten()), nparray2fixedlist(weights) ]))

    scores = np.dot(weighted_centered_data, loading)
    # print
    # print "SCORES"
    # print scores

    set1 = scores + abs(min(scores))
    set2 = scores - max(scores)
    # print "set1:", set1
    # print "set2:", set2

    old = np.dot(weights, data)
    # print "old: ", old

    wset1 = get_weight(set1)
    wset2 = get_weight(set2)
    # wset1 = map(hex, map(long, wset1 * 0x10000000000000000))
    # wset2 = map(hex, map(long, wset2 * 0x10000000000000000))
    # print "wset1:", wset1
    # print "wset2:", wset2

    new1 = np.dot(wset1, data)
    new2 = np.dot(wset2, data)
    # print "new1:", new1
    # print "new2:", new2

    ref_ind = np.sum((new1 - old)**2) - np.sum((new2 - old)**2)
    if ref_ind <= 0:
        adj_prin_comp = set1
    if ref_ind > 0:
        adj_prin_comp = set2
    # print "adj_prin_comp:", adj_prin_comp

    row_reward_weighted = get_weight(weights)
    if max(abs(adj_prin_comp)) != 0:
        row_reward_weighted = get_weight(adj_prin_comp * (weights / np.mean(weights)).T)
    # print "row_reward_weighted:", row_reward_weighted

    alpha = 0.2
    smooth_rep = alpha*row_reward_weighted + (1-alpha)*get_weight(weights).T
    # print "smooth_rep:", smooth_rep

    event_outcomes_raw = np.dot(smooth_rep, data).squeeze() / 10
    # print "event_outcomes_raw:", event_outcomes_raw

    event_outcomes_final = np.array(map(catch, event_outcomes_raw))
    # print "event_outcomes_final:", event_outcomes_final

if __name__ == '__main__':
    test_emwpca()
