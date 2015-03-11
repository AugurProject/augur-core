import cStringIO
import sys

_ = sys.stderr
sys.stderr = cStringIO.StringIO()
from pyethereum import tester as t
sys.stderr = _

from contextlib import contextmanager
from collections import namedtuple
from bitcoin import encode, decode
import random
import gmpy2
import time

gmpy2.get_context().precision = 256

_TestResultBase = namedtuple('_TestResultBase', 'avg_error avg_gas')

class TestResults(_TestResultBase):
    def __str__(self):
      return 'TestResults(avg_error={:3.18%}%, avg_gas={})'.format(self[0], self[1])  

def suppress_output(thunk):
    old_stdout = sys.stdout
    sys.stdout = cStringIO.StringIO()
    try:
        result = thunk()
    except:
        old_stdout.write(sys.stdout.read())
        sys.exit(1)
    else:
        sys.stdout = old_stdout
        return result

def printf(fmt, *args):
    sys.stdout.write(fmt % args)
    sys.stdout.flush()

def test_thunk(thunk, trials):
    printf('Testing ' + thunk.__name__ + ':\n')
    error = 0
    gas = 0
    for i in range(int(trials)):
        printf('\tTrials: %d\r', i)
        expected, result = thunk()
        result['output'] /= gmpy2.mpfr(1 << 64)
        error += abs(result['output'] - expected)/expected
        gas += result['gas']
    printf('\n')
    return TestResults(float(error/trials), gas/float(trials))

def thunks(contract, func_dict):
    for name, (bounds, ref_func) in func_dict.items():
        def thunk(name=name, bounds=bounds, ref_func=ref_func):
            test_func = vars(contract)[name]
            x = random.random()*(bounds[1] - bounds[0]) + bounds[0]
            return ref_func(x), test_func(int(x*2**64), profiling=True)
        thunk.__name__ = name
        yield thunk

def compile(filename):
    s = t.state()
    start = time.time()
    printf('Compiling...\t')
    c = suppress_output(lambda: s.abi_contract(filename))
    printf('Done in %.1f seconds.\n', time.time() - start)
    return c

def test_code(filename, func_dict, trials):
    contract = compile(filename)
    for thunk in thunks(contract, func_dict):
        printf('\t' + str(test_thunk(thunk, trials)) + '\n')

@contextmanager
def timer():
    start = time.time()
    yield
    print
    print "Runtime: %.2f seconds" % (time.time() - start)
