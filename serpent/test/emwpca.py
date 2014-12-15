from pyethereum import tester as t
import math, numpy

numpy.set_printoptions(linewidth=500)

contract_code = """
def emwpca(data:a, weights:a):
    num_obs = arglen(weights)
    num_params = arglen(data) / arglen(weights)

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

    return(loading_vector, num_params)
"""

def emwpca(data, weights, num_loadings):
    num_params = data.shape[1]
    weighted_centered_data = data - numpy.average(data, axis=0, weights=weights)
    loadings = numpy.zeros(num_params)
    loadings[0] = 1.
    loadings = numpy.tile(loadings, (num_loadings, 1))
    for i in xrange(num_loadings):
        for j in xrange(25):
            s = numpy.zeros(num_params)
            for datum, weight in zip(weighted_centered_data, weights):
                s -= datum.dot(loadings[i]) * datum * weight
            loadings[i] = s / math.sqrt(s.dot(s))
        if i < num_loadings - 1:
            for j, datum in enumerate(weighted_centered_data):
                weighted_centered_data[j] -= loadings[i].dot(datum) * loadings[i]
    return loadings

def test_emwpca():
    def nparray2fixedlist(a):
        return map(lambda x: int(x), (a * 0x10000000000000000).tolist())

    def fixedlist2nparray(l):
        return numpy.array(l).astype(float) / 0x10000000000000000

    s = t.state()
    c = s.contract(contract_code)

    numpy.random.seed(0)
    shape = (3, 2)
    # data = numpy.random.rand(*shape)
    # weights = numpy.random.rand(shape[0])

    data = numpy.array([[10, 10,  0, 10],
                        [10,  0,  0,  0],
                        [10, 10,  0,  0],
                        [10, 10, 10,  0],
                        [10,  0, 10, 10],
                        [ 0,  0, 10, 10]])
    weights = numpy.array([2, 10, 4, 2, 7, 1])

    print data
    print weights

    print nparray2fixedlist(data.flatten())
    print nparray2fixedlist(weights)

    loading = emwpca(data, weights, 1)[0]

    print
    print "LOADINGS"
    print loading
    print fixedlist2nparray(s.send(t.k0, c, 0, funid=0, abi=[ nparray2fixedlist(data.flatten()), nparray2fixedlist(weights) ]))
    
    weighted_centered_data = data - numpy.average(data, axis=0, weights=weights)

    print
    print "SCORES"
    print numpy.dot(weighted_centered_data, loading)

    # print
    # print "WEIGHTED CENTERED DATA"
    # print weighted_centered_data

if __name__ == '__main__':
    test_emwpca()
