import warnings; warnings.simplefilter('ignore')
from colorama import init, Fore, Back, Style
from contextlib import contextmanager
from pyethereum import tester as _t
from collections import OrderedDict
from bitcoin import encode, decode
from sha3 import sha3_256 as sha3
from cStringIO import StringIO
from types import FunctionType
from time import clock
import traceback
import sys
import os

@context_manager
def suppressed_output():
    temp, sys.stdout, sys.stderr = (sys.stdout, sys.stderr), StringIO(), StringIO()
    yield temp, sys.stdout, sys.stderr
    sys.stdout, sys.stderr = temp

def _sane_output(result):
    if isinstance(result, list):
        return map(_sane_output, result)
    elif isinstance(result, dict):
        result['output'] = _sane_output(result['output'])
        return result
    elif isinstance(result, int):
        return result % 2**256
    else:
        return result

class SilentContract(object):
    '''An abi_contract wrapper that supresses random prints'''
    def __init__(self, state, filename):
        self._contract = state.abi_contract(filename)

    def __getattr__(self, name):
        obj = getattr(self._contract, name)
        if isinstance(obj, FunctionType):
            def wrapper(*args, **kwds):
                with suppressed_output() as io_parts:
                    try:
                        result = obj(*args, **kwds)
                    except Exception as exc:
                        traceback.print_exc(file=io_parts[0][0])
                        sys.exit(1)
                return _sane_output(result)
            return wrapper
        return obj

class CachedCodeState(_t.state):
    def abi_contract(me, code, sender=k0, endowment=0, language='serpent', gas=None):

        class _abi_contract():

            def __init__(self, _state, code, sender=k0,
                         endowment=0, language='serpent'):

                if language not in _t.languages:
                    _t.languages[language] = __import__(language)
                language = _t.languages[language]

                if os.path.exists(code) and os.path.exists('.' + code + '_cache'):
                    cache_created_time = os.path.getmtime('.' + code + '_cache')
                    code_modified_time = os.path.getmtime(code)
                    if code_modified_time > cache_created_time:
                        evm = language.compile(code)
                        cache = open('.' + code + '_cache', 'wb')
                        cache.write(evm)
                        cache.close()
                    else:
                        cache = open('.' + code + '_cache', 'rb')
                        evm = cache.read()
                        cache.close()
                else:
                    evm = language.compile(code)

                self.address = _t.encode_hex(me.evm(evm, sender, endowment, gas))
                assert len(me.block.get_code(self.address)), \
                    "Contract code empty"
                sig = language.mk_full_signature(code)
                self._translator = _t.abi.ContractTranslator(sig)

                def kall_factory(f):

                    def kall(*args, **kwargs):
                        _state.block.log_listeners.append(
                            lambda log: self._translator.listen(log))
                        o = _state._send(kwargs.get('sender', k0),
                                         self.address,
                                         kwargs.get('value', 0),
                                         self._translator.encode(f, args),
                                         **dict_without(kwargs, 'sender',
                                                        'value', 'output'))
                        _state.block.log_listeners.pop()
                        # Compute output data
                        if kwargs.get('output', '') == 'raw':
                            outdata = o['output']
                        elif not o['output']:
                            outdata = None
                        else:
                            outdata = self._translator.decode(f, o['output'])
                            outdata = outdata[0] if len(outdata) == 1 \
                                else outdata
                        # Format output
                        if kwargs.get('profiling', ''):
                            return _t.dict_with(o, output=outdata)
                        else:
                            return outdata
                    return kall

                for f in self._translator.function_data:
                    vars(self)[f] = kall_factory(f)

        return _abi_contract(me, code, sender, endowment, language)

class AugurTest(object):
    test_code = '../augur.se'
    def __init__(self, filename, **kwds):
        self._state = CachedCodeState()
        self.gas_limit = kwds.pop('gas_limit', 10**8)
        self._state.block.gas_limit = self.gas_limit
        self._state.block.gas_used = 0
        with suppressed_output():
            self._contract = SilentContract(self._state, AugurTest.test_code)

    def mine(self, n=1):
        self._state.mine(n)
        self._state.block.gas_limit = _tester.gas_limit

    def new_keypair(self, blocks=0):
        privkey = decode(os.urandom(32), 256)
        addr = _tester.u.privtoaddr(privkey)
        self._state.mine(blocks, coinbase=addr)
        return addr, privkey

    def new_keypairs(self, n, blocks=0):
        return OrderedDict(self.new_keypair(blocks) for i in range(n))
        
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
