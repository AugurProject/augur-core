try:
    from colorama import init as _init
    _init()
except ImportError:
    pass

from cStringIO import StringIO as _StringIO
from contextlib import contextmanager as _contextmanager
from collections import OrderedDict
from bitcoin import encode, decode
from sha3 import sha3_256 as sha3
import logging
import types
import time
import sys
STDOUT = sys.stdout
STDERR = sys.stderr

@_contextmanager
def silence():
    sys.stdout = _StringIO()
    sys.stderr = _StringIO()
    yield
    sys.stdout = STDOUT
    sys.stderr = STDERR

with silence():
    from pyethereum import tester as _tester

_tester.gas_limit = 10**8
addresses = _tester.accounts
keys = _tester.keys
addr2key = OrderedDict(zip(addresses, keys))
key2addr = OrderedDict(zip(keys, addresses))

class Contract(object):
    def __init__(self, filename, **kwds):
        self._state = _tester.state()
        self.gas_limit = kwds.pop('gas_limit', 10**8)
        self._state.block.gas_limit = self.gas_limit
        self._state.block.gas_used = 0
        self.quiet = kwds.pop('quiet', False)
        if self.quiet:
            with silence():
                try:
                    self._contract = self._state.abi_contract(filename, **kwds)
                except Exception as exc:
                    logging.exception(exc)
                    sys.exit(1)
        else:
            self._contract = self._state.abi_contract(filename)
        self.mine(1)

    def mine(self, n=1):
        self._state.mine(n)
        self._state.block.gas_limit = _tester.gas_limit
        
    def __getattr__(self, name, default=None):
        obj = getattr(self._contract, name, default)
        if isinstance(obj, types.FunctionType):
            self.mine(1)
        if self.quiet and isinstance(obj, types.FunctionType):
            def wrapper(*args, **kwds):
                with silence():
                    result = obj(*args, **kwds)
                    if isinstance(result, (int, long)):
                        return result%2**256
                    elif isinstance(result, list):
                        return [i%2**256 for i in result]
                    elif isinstance(result, dict):
                        if isinstance(result['output'], (int, long)):
                            result['output'] %= 2**256
                        elif isinstance(result['output'], list):
                            result['output'] = [i%2**256 for i in result['output']]
                        return result
                    return result
            return wrapper
        return obj

def _sanitize(x):
    if isinstance(x, str):
        return x
    if isinstance(x, float):
        return "%f" % x
    if isinstance(x, complex):
        r = x.real
        i = x.imag
        return "%+f%+fj" % (r, i)
    return str(x)

def _colorize(color, *strings):
    chunk_end = '\033[0m'
    strings = map(_sanitize, strings)
    return color + (chunk_end+color).join(strings) + chunk_end

def green(*strings):
    return _colorize('\033[1;32m', *strings)

def red(*strings):
    return _colorize('\033[1;31m', *strings)

def yellow(*strings):
    return _colorize('\033[1;33m', *strings)

def cyan(*strings):
    return _colorize('\033[1;36m', *strings)

def dim_red(*strings):
    return _colorize('\033[0;31m', *strings)

def dim_yellow(*strings):
    return _colorize('\033[1;33m', *strings)

def title(string, dim=True):
    string = (' '+string+' ').center(80, '#')
    if dim:
        return dim_red(string)
    else:
        return red(string)

def pretty_address(addr):
    if isinstance(addr, (int, long)) and not (0>=addr>=-4):
        addr = hex(addr % 2**256).replace('0x', '').replace('L', '')
    if isinstance(addr, str):
        return cyan(addr[:4] + '...')
    return red(addr)

@_contextmanager
def timer():
    start = time.time()
    yield
    result = dim_yellow('Finished in %f seconds.')
    print result % (time.time() - start)

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
