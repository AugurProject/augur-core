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
from pyrpc import GETHRPC, DB, COINBASE
import leveldb
import serpent
import json
import sys
import os

TEMPLATE = '''\
%(sig)s
macro %(name)s:
    %(addr)s
'''
CODEPATH = os.path.abspath('src')
ERROR = Style.BRIGHT + Fore.RED + 'ERROR!'
GAS = hex(25*10**5)
TRIES = 5

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
    for d, s, f in os.walk('src'):
        for F in f:
            if F[:-3] == name:
                return os.path.join(d, F)
    raise ValueError('No such name: '+name)

def is_old_info(info):
    return os.path.getmtime(get_full_name(info['name'])) > info['mtime']

def get_info(name):
    try:
        info = json.loads(DB.Get(name))
    except:
        compile(name)
        return json.loads(DB.Get(name))
    else:
        if is_old_info(info):
            compile(name)
            return json.loads(DB.Get(name))
        else:
            return info

def broadcast_code(evm):
    return GETHRPC.eth_sendTransaction(sender=COINBASE, data=evm, gas=GAS)

def compile(name):
    fullname = get_full_name(name)
    new_code = []
    for line in open(fullname):
        if line.startswith('import'):
            _, n = line.split(' ')
            info = get_info(n)
            new_code.append(info['sig'])
            new_code.append(TEMPLATE % info)
        else:
            new_code.append(line.rstrip())
    new_code = '\n'.join(new_code)
    sig = serpent.mk_signature(new_code)
    sig = sig.replace('main', name, 1)
    fullsig = serpent.mk_full_signature(new_code)
    evm = '0x' + serpent.compile(new_code).encode('hex')
    result = broadcast_code(evm)
    if 'error' in result:
        raise ValueError('Bad RPC response!: ' + json.dumps(result, indent=4))
    address = result['result']
    mtime = os.path.getmtime(fullname)
    DB.Put(name,
           json.dumps({
               'sig':sig,
               'fullsig':fullsig,
               'address':address,
               'mtime':mtime,
               'name':name}))
    
def main():
    for d, s, f in os.walk('src'):
        for F in f:
            if F.endswith('.se'):
                compile(F[:-3])
    return 0

if __name__ == '__main__':
    sys.exit(main())
