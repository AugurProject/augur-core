#!/usr/bin/python
'''
This script loads all serpent contracts onto the block chain using JSON RPC
    ./load_contracts.py
In order to use this script successfully, you need to prepare your geth node.
Start up a geth console using:
    geth --loglevel 0 --rpc console
Once there, make a new account if needed:
    admin.newAccount()
This will ask you to set a password, which you must remember!!!
If you don't have any money, you will have to mine for it (n is the
number of threads you wish to use for mining):
    admin.miner.start(n)
And then finally you will have to unlock your account:
    admin.unlock(eth.coinbase, undefined, 60*60*24*30*12)
This will prompt you for the password you chose earlier.

To simplify this process, you can add this alias to the appropriate file
(your .bashrc, .bash_profile, .profile, or .bash_aliases):
    alias geth='geth --loglevel 0 --rpc --unlock primary'

Then geth will automatically do all these things whenever you run it.
'''
import warnings; warnings.simplefilter('ignore')
from colorama import init, Fore, Style; init()
from pyrpctools import RPC, DB
from translate_externs import replace_names, show
from collections import defaultdict
from pyepm.api import abi_data
from sha3 import sha3_256
import serpent
import json
import time
import sys
import os

def get_code_paths():
    paths = []
    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            continue
        else:
            paths.append(os.path.abspath(arg))
    if paths:
        return paths
    return [os.path.abspath('src')]

GETHRPC = RPC(default='GETH')
COINBASE = GETHRPC.eth_coinbase()['result']
CODEPATHS = get_code_paths()
ERROR = Style.BRIGHT + Fore.RED + 'ERROR!'
GAS = hex(3*10**6)
TRIES = 10
BLOCKTIME = 12
INFO = {}
WHITELIST_CODE = '''\
    functions = []
    hash = div(calldataload(0), 2**224)
    i = 0
    l = len(functions)
    while i < l:
        if functions[i] == hash:
            if not whitelist.getAccess(self, msg.sender):
                return(text("PERMISSION DENIED"):str)
        i += 1
'''.split('\n')
WHITELIST_CALLS = defaultdict(list)
WHITELIST_ADDR = "0xb391d1f291dfa4874ced620ba0ad5f3e63fae0c9"
WHITELIST_SIG = 'extern whitelist: [getAccess:ii:i, getOwner:i:i, setAccess:iii:s, setOwner:i:s]'

if COINBASE == '0x':
    print ERROR, 'no coinbase address'
    print 'ABORTING'
    sys.exit(1)

def memoize(func):
    memo = {}
    def new_func(x):
        if x in memo:
            return memo[x]
        result = func(x)
        memo.__setitem__(x, result)
        return result
    new_func.__name__ = func.__name__
    return new_func

@memoize
def get_full_name(name):
    for path in CODEPATHS:
        for d, s, f in os.walk(path):
            for F in f:
                if F[:-3] == name:
                    return os.path.join(d, F)
    raise ValueError('No such name: '+name)

def get_short_name(fullname):
    return os.path.split(fullname)[-1][:-3]

def is_code_onchain(address):
    i = 0
    while i < TRIES:
        time.sleep(BLOCKTIME)
        result = GETHRPC.eth_getCode(address)
        if result['result'] != '0x':
            break
        i += 1
    return i != TRIES

def get_info(name, whitelisted):
    if name in INFO:
        return INFO[name]
    else:
        compile(name, whitelisted)
        return INFO[name]

def broadcast_code(evm):
    return GETHRPC.eth_sendTransaction(sender=COINBASE, data=evm, gas=GAS)

def get_func_name(line):
    return line.split(' ', 1)[1].split('(', 1)[0]

def translate_code(fullname, whitelisted):
    new_code = []
    shared_code = []
    sigs = []
    whitelisted_funcs = []
    is_whitelisted = fullname in whitelisted
    if is_whitelisted:
        new_code.append(WHITELIST_SIG)
    for line in open(fullname):
        if line.strip().startswith('#') or line.strip()=='':
            continue
        line = line.replace('\t', ' '*4).rstrip()
        if is_whitelisted and line.startswith('def set'):
            new_code.append(line)
            whitelisted_funcs.append(get_func_name(line))
        elif is_whitelisted and new_code and new_code[-1].startswith('@whitelisted'):
            # the @whitelisted line should be above a def <name>(...) line
            new_code.pop()
            new_code.append(line)
            whitelisted_funcs.append(get_func_name(line))
        elif line.startswith('import'):
            _, n = line.split(' ')
            n = n.strip()
            if get_full_name(n) in whitelisted:
                WHITELIST_CALLS[n].append(get_short_name(fullname))
            info = get_info(n, whitelisted)
            sigs.append(info['sig'])
            shared_code.append(n+' = '+info['address'])
        else:
            new_code.append(line)
    if is_whitelisted:
        shared_code.append('whitelist = ' + WHITELIST_ADDR) 
        shared_code = shared_code + WHITELIST_CODE
    if shared_code:
        new_code = sigs + shared_code + new_code
    return new_code, whitelisted_funcs

def get_prefixes(funcs, fullsig):
    fullsig = json.loads(fullsig)
    prefixes = []
    for func in funcs:
        for funcsig in fullsig:
            if funcsig['name'].startswith(func):
                prefixes.append('0x' + sha3_256(str(funcsig['name'])).hexdigest()[:8])
    return '[' + ', '.join(prefixes) + ']'

def compile(name, whitelisted):
    fullname = get_full_name(name)
    new_code, whitelisted_funcs = translate_code(fullname, whitelisted)
    show(new_code)
    new_code = '\n'.join(new_code)
    fullsig = serpent.mk_full_signature(new_code)
    prefixes = get_prefixes(whitelisted_funcs, fullsig)
    new_code = new_code.replace('functions = []', 'functions = ' + prefixes, 1)
    show(new_code.split('\n'))
    print 'Processing', fullname
    print whitelisted_funcs, prefixes
    evm = '0x' + serpent.compile(new_code).encode('hex')
    sig = serpent.mk_signature(new_code)
    sig = sig.replace('main', name, 1)
    result = broadcast_code(evm)
    if 'error' in result:
        raise ValueError('Bad RPC response!: ' + json.dumps(result, indent=4))
    address = result['result']
    if not is_code_onchain(address):
        raise ValueError('CODE NOT ON CHAIN AFTER %d TRIES, ABORTING' % TRIES) 
    INFO[name] = {
        'sig':sig,
        'fullsig':fullsig,
        'address':address,
        'name':name}

def pretty(dct):
    return json.dumps(dct, indent=4, sort_keys=True)

def serpent_files(path):
    for d, s, f in os.walk(path):
        for F in f:
            if F.endswith('.se'):
                yield d, F

def get_whitelisted():
    for arg in sys.argv:
        if arg.startswith('--whitelisted='):
            return map(os.path.abspath, open(arg.split('=')[1]).read().split('\n'))
    return []

def safe_call(contract, funcname, sig, args):
    data = abi_data(funcname, sig, args)
    rpc_args = {'sender':COINBASE, 'gas':hex(3000000), 'data':data, 'to':contract}
    txhash = GETHRPC.eth_sendTransaction(**rpc_args)['result']
    tries = 0
    while tries < TRIES:
        time.sleep(BLOCKTIME)
        check = GETHRPC.eth_getTransactionByHash(txhash)
        if check['result'] == None:
            return safe_call(contract, funcname, sig, args)
        if check['result']['blockNumber'] != None:
            break
        tries += 1
    return tries < TRIES

def add_to_whitelists():
    print 'CALLING WHITELIST'
    for contract in WHITELIST_CALLS:
        print 'CREATING WHITELIST FOR ', contract
        contract_info = get_info(contract, [])
        check = safe_call(WHITELIST_ADDR, 'setOwner', 'i', [contract_info['address']])
        if not check:
            raise ValueError('Could not claim address: '+str(contract_info))
        for accessor in WHITELIST_CALLS[contract]:
            accessor_info = get_info(accessor, [])
            check2 = safe_call(WHITELIST_ADDR,
                               'setAccess',
                               'iii',
                               [contract_info['address'],
                                accessor_info['address'],
                                1])
            if not check2:
                raise ValueError(
                    'Could not set accessor permission: '+str(contract_info)+' '+str(accessor_info))

def main():
    whitelisted = get_whitelisted()
    for path in CODEPATHS:
        for _, filename in serpent_files(path):
            get_info(filename[:-3], whitelisted)
    print 'DUMPING INFO TO DB'
    for name, info in INFO.items():
        print name + ':'
        print pretty(info)
        DB[name] = json.dumps(info)
    add_to_whitelists()
    return 0

if __name__ == '__main__':
    sys.exit(main())
