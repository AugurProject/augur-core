import warnings; warnings.simplefilter('ignore')
from colorama import init, Fore, Back, Style
from types import FunctionType, MethodType
from contextlib import contextmanager
from bitcoin import encode, decode
from sha3 import sha3_256 as _sha3
from cStringIO import StringIO
from time import clock
import traceback
import sys
import os
import re

def sha3(*args):
    data = ''
    for i in args:
        if isinstance(i, (int, long)):
            data += encode(i, 256, 32)
        if isinstance(i, (list, tuple)):
            data += ''.join(encode(j, 256, 32) for j in i)
        if isinstance(i, str):
            data += i
    result = decode(_sha3(data).digest(), 256)
    if result > 2**255:
        result  -= 2**256
    return result

def named(wrapper):
    def new_wrapper(func):
        new_func = wrapper(func)
        new_func.__name__ = func.__name__
        return new_func
    new_wrapper.__name__ = wrapper.__name__
    return new_wrapper

@named
def suppressify(func):
    def new_func(*args, **kwds):
        with suppressed_output() as parts:
            try:
                result = func(*args, **kwds)
            except Exception as exc:
                traceback.print_exc(file=parts.stdout)
                sys.exit(1)
            else:
                return result
    return new_func

@contextmanager
def timer():
    start = clock()
    yield
    print Fore.YELLOW + Style.BRIGHT + 'Done in %5.2f seconds.'%(clock() - start) + Style.RESET_ALL

def repl_addr(match):
    return Fore.CYAN + Style.BRIGHT + match.string.__getslice__(slice(*match.span()))[:4] + '...' + Fore.YELLOW

def repl_num(match):
    return Fore.CYAN + Style.BRIGHT + match.string.__getslice__(slice(*match.span())) + Fore.YELLOW

def repl_err(match):
    return Fore.RED + Style.BRIGHT + match.string.__getslice__(slice(*match.span())) + Fore.YELLOW

addr_p = re.compile(r'0x[a-f0-9]+L')
num_p = re.compile(r'-?(?!0x)(?![a-f]+)[0-9]+(?![a-f]+)L?|-?[0-9]+\.[0-9]+')
err_p = re.compile(r'-[1-5]\s?[.,]?')

class PrettyOut(object):
    '''A file object wrapper that colorizes writes.'''
    def __init__(self, fileobj):
        self.fileobj = fileobj
        
    def write(self, s):
        return self.fileobj.write(
            reduce(
                lambda a, (b, c): b.sub(c, a), 
                [
                    (
                        addr_p,
                        repl_addr),
                    (
                        num_p,
                        repl_num),
                    (
                        err_p,
                        repl_err)],
                Fore.YELLOW + s + Style.RESET_ALL))

    def __getattr__(self, name):
        return getattr(self.fileobj, name)

@named
def make_test(func):
    def new_func(*args, **kwds):
        print Fore.RED + func.__name__.split('_').capitalize().center(80, '#') + Style.RESET_ALL
        start = clock()
        result = func(*args, **kwds)
        print Fore.YELLOW + Style.BRIGHT + 'Done in %5.2f seconds.' % (clock() - start)
        return result
    return new_func

def missing(name):
    def thunk():
        raise NotImplementedError('function ' + name + ' not defined.')
    return thunk

def running(run, name):
    def wrapper(*args, **kwds):
        print Fore.RED + Style.BRIGHT + (" Running " + name + " ").center(80, '#') + Style.RESET_ALL
        with timer():
            return run(*args, **kwds)
    wrapper.__name__ = run.__name__
    return wrapper

class TestType(type):
    '''Metaclass for the Test class'''
    def __new__(cls, name, bases, dct):
        for k, v in dct.items():
            if isinstance(v, (FunctionType, MethodType)):
                if v.__name__.startswith('test_'):
                    dct[k] = make_test(v)
                if v.__name__ == 'run':
                    dct[k] = running(v, name) 
        return type.__new__(cls, name, bases, dct)

class ContractTest(object):
    __metaclass__ = TestType
    def __init__(self, test_order):
        self.test_order = test_order

    def run(self):
        for name in self.test_order:
            getattr(self, name, missing(name))()

def trade_pow(branch, market, address, trade_nonce, difficulty=10000):
    nonce = 0
    target = 2**254/difficulty
    address = decode(address, 16)
    data = [branch, market, address, trade_nonce]
    encoder = lambda x: encode(x, 256, 32)
    decoder = lambda x: decode(x, 256)
    first_hash = sha3(''.join(map(encoder, data))).digest()
    while True:
        h = decoder(sha3(first_hash+encoder(nonce)).digest())
        if h < target:
            return nonce
        nonce += 1
