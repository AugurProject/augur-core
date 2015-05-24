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
from pyrpctools import GETHRPC, DB, COINBASE
from translate_externs import replace_names, show
import serpent
import json
import time
import sys
import os

CODEPATHS = map(os.path.abspath, sys.argv[1:]) if sys.argv[1:] else ('src',)
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
    for path in CODEPATHS:
        for d, s, f in os.walk(path):
            for F in f:
                if F[:-3] == name:
                    return os.path.join(d, F)
    raise ValueError('No such name: '+name)

def is_code_onchain(address):
    i = 0
    while i < TRIES:
        time.sleep(BLOCKTIME)
        result = GETHRPC.eth_getCode(address)
        if result['result'] != '0x':
            break
        i += 1
    return i != TRIES

def get_info(name):
    if name in INFO:
        return INFO[name]
    else:
        compile(name)
        return INFO[name]

def broadcast_code(evm):
    return GETHRPC.eth_sendTransaction(sender=COINBASE, data=evm, gas=GAS)

def translate_code(fullname):
    new_code = []
    imports = []
    init = 0
    for i, line in enumerate(open(fullname)):
        if line.startswith('def init():'):
            init = i
            new_code.append(line)
        elif line.startswith('import'):
            _, n = line.split(' ')
            n = n.strip()
            info = get_info(n)
            new_code.append(info['sig'] + '\n' + 'data ' + n)
            imports.append((n,info['address']))
        else:
            line, _ = replace_names(line, [n[0] for n in imports], lambda n: 'self.'+n)
            new_code.append(line.rstrip())
    if not init and not new_code[init].startswith('def init():') and imports:
        new_code = ['def init():'] + new_code
    new_code = new_code[:init+1]+[(' '*4+'self.%s = %s')%(n, a) for n, a in imports]+new_code[init+1:]
    return new_code

def compile(name):
    fullname = get_full_name(name)
    new_code = translate_code(fullname)
    show(new_code)
    print 'Processing', fullname
    new_code = '\n'.join(new_code)
    evm = '0x' + serpent.compile(new_code).encode('hex')
    sig = serpent.mk_signature(new_code)
    sig = sig.replace('main', name, 1)
    fullsig = serpent.mk_full_signature(new_code)
    result = broadcast_code(evm)
    if 'error' in result:
        raise ValueError('Bad RPC response!: ' + json.dumps(result, indent=4))
    address = result['result']
    if not is_code_onchain(address):
        raise ValueError('CODE NOT ON CHAIN AFTER %d TRIES, ABORTING' % TRIES) 
    mtime = os.path.getmtime(fullname)
    INFO[name] = {
        'sig':sig,
        'fullsig':fullsig,
        'address':address,
        'mtime':mtime,
        'name':name}

def pretty(dct):
    return json.dumps(dct, indent=4, sort_keys=True)

def serpent_files(path):
    for d, s, f in os.walk(path):
        for F in f:
            if F.endswith('.se'):
                yield d, F

def main():
    for path in CODEPATHS:
        for _, filename in serpent_files(path):
            print pretty(get_info(filename[:-3]))
    for name, info in INFO.items():
        DB[name] = json.dumps(info)
    return 0

if __name__ == '__main__':
    sys.exit(main())
