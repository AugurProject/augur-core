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
from pyrpctools import RPC_Client, DB
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

GETHRPC = RPC_Client(default='GETH')
COINBASE = GETHRPC.eth_coinbase()['result']
CODEPATHS = get_code_paths()
ERROR = Style.BRIGHT + Fore.RED + 'ERROR!'
GAS = hex(3*10**6)
TRIES = 10
BLOCKTIME = 12
INFO = {}

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
    '''Takes a short name from an import statement and returns a real path to that contract.'''
    for path in CODEPATHS:
        for d, s, f in os.walk(path):
            for F in f:
                if F[:-3] == name:
                    return os.path.join(d, F)
    raise ValueError('No such name: '+name)

def get_info(name):
    '''Returns metadata about a contract.'''
    if name in INFO:
        return INFO[name]
    else:
        compile(name)
        return INFO[name]

def broadcast_code(evm):
    '''Sends compiled code to the network, and returns the address.'''
    address = GETHRPC.eth_sendTransaction(sender=COINBASE, data=evm, gas=GAS)['result']
    tries = 0
    while tries < TRIES:
        check = GETHRPC.eth_getCode(address)['result']
        if check != '0x':
            return address
        time.sleep(BLOCKTIME)
    raise ValueError('CODE COULD NOT GET ON CHAIN!!!')

def translate_code(fullname):
    new_code = []
    shared_code = []
    sigs = []
    for line in open(fullname):
        line = line.replace('\t', ' '*4).rstrip()
        if line.startswith('import'):
            line = line.split(' ')
            name, sub = line[1], line[3]
            info = get_info(name)
            sigs.append(info['sig'])
            shared_code.append(sub + ' = ' + info['address'])
        else:
            new_code.append(line)
    if shared_code:
        new_code = sigs + shared_code + new_code
    return new_code

def compile(name):
    fullname = get_full_name(name)
    print 'Processing', fullname
    new_code = '\n'.join(translate_code(fullname))
    fullsig = serpent.mk_full_signature(new_code)
    evm = '0x' + serpent.compile(new_code).encode('hex')
    sig = serpent.mk_signature(new_code).replace('main', name, 1)
    address = broadcast_code(evm)
    INFO[name] = {
        'sig':sig,
        'fullsig':fullsig,
        'address':address,
        'name':name}

def serpent_files():
    for path in CODEPATHS:
        for d, s, f in os.walk(path):
            for F in f:
                if F.endswith('.se'):
                    yield d, F

def main():
    for d, f in serpent_files():
        get_info(f[:-3])
    print 'DUMPING INFO TO DB'
    for name, info in INFO.items():
        print 'DUMPING', name, 'INFO TO DB'
        DB[name] = json.dumps(info)
    return 0

if __name__ == '__main__':
    sys.exit(main())
