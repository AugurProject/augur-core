import warnings; warnings.simplefilter('ignore')
from collections import OrderedDict, namedtuple
from colorama import init, Fore, Back, Style
from contextlib import contextmanager
from pyethereum import tester as _t
from bitcoin import encode, decode
from sha3 import sha3_256 as _sha3
from cStringIO import StringIO
from types import FunctionType
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

IOParts = namedtuple('IOParts', 'stdout stderr proxyout proxyerr')

@contextmanager
def suppressed_output():
    parts = IOParts(sys.stdout, sys.stderr, StringIO(), StringIO())
    sys.stdout, sys.stderr = parts[2:]
    yield parts
    sys.stdout, sys.stderr = parts[:2]    

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

class Contract(object):
    def __init__(self, state, code, sender, gas, endowment, language):
        if language not in _t.languages:
            _t.languages[language] = __import__(language)
        language = _t.languages[language]
        
        if os.path.exists(code):
            cached = code.replace('.se', '.sec')
            if os.path.exists(cached):
                cache_made = os.path.getmtime(cached)
                code_made = os.path.getmtime(code)
                if code_made > cache_made:
                    with open(cache, 'wb') as f:
                        evm = language.compile(code)
                        sig = language.mk_signature(code)
                        evm_len = encode(len(evm), 256, 2)
                        sig_len = encode(len(sig), 256, 2)
                        f.write(evm_len + evm + sig_len + sig)
                else:
                    with open(cache, 'rb') as f:
                        evm_len = decode(f.read(2), 256)
                        evm = f.read(evm_len)
                        sig_len = decode(f.read(2), 256)
                        sig = f.read(sig_len)
            else:
                with open(cache, 'wb') as f:
                    evm = language.compile(code)
                    sig = language.mk_signature(code)
                    evm_len = encode(len(evm), 256, 2)
                    sig_len = encode(len(sig), 256, 2)
                    f.write(evm_len + evm + sig_len + sig)

            self.address = _t.encode_hex(state.evm(evm, sender, endowment, gas))
            self._translator = _t.abi.ContractTranslator(sig)
                assert len(state.block.get_code(self.address)), \
                    "Contract code empty"

            def make_dispatcher(state, funcname):
                def dispatch(*args, **kwds):
                    state.block.log_listeners.append(
                        self._translator.listen)
                    o = state._send(
                        kwds.get('sender', sender),
                        self.address,
                        kwds.get('value', 0),
                        self._translator.encode(funcname, args),
                        **dict_without(
                            kwds,
                            'sender',
                            'value', 
                            'output'))
                    state.block.log_listeners.pop()
                    if kwds.get('output', '') == 'raw':
                        outdata = o['output']
                    elif not o['output']:
                        outdata = None
                    else:
                        outdata = self._translator.decode(f, o['output'])
                        outdata = outdata[0] if len(outdata) == 1 \
                                  else outdata
                    # Format output
                    if kwds.get('profiling', ''):
                        return _t.dict_with(o, output=outdata)
                    else:
                        return outdata
                dispatch.__name__ = funcname
                return suppressify(dispatch)

            for funcname in self._translator.function_data:
                vars(self)[funcname] = make_dispatcher(state, funcname)

class State(_t.state):
    '''A subclass of pyethereum.tester.state, with cached compiled code
and creates silent functions'''
    def abi_contract(self, code, sender=k0, endowment=0, language='serpent', gas=None):
        return Contract(self, code, sender, gas, endowment, language)

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
        self.proxy = StringIO()
        
    def write(self, s):
        return self.fileobj.write(reduce(lambda a, (b, c): b.sub(c, a), 
                                         [(addr_p,
                                           repl_addr),
                                          (num_p,
                                           repl_num),
                                          (err_p,
                                           repl_err)],
                                         Fore.YELLOW + s + Style.RESET_ALL))

    def __getattr__(self, name):
        return getattr(self.fileobj, name)

class TestType(type):
    '''Metaclass for the Test class'''
    def __new__(cls, name, bases, dct):
        pass

class Test(object):
    __metaclass__ = TestType

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
