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
from pyrpc import rpc
import leveldb
import serpent
import json
import sys
import os
import re

TEMPLATE = '''\
%(sig)s
macro %(name)s:
    %(addr)s
'''
CODEPATH = os.path.abspath('src')
IMPORTP = re.compile('^import (?P<name>\S+)$', re.M)
ERROR = Style.BRIGHT + Fore.RED + 'ERROR!'
RPC = rpc(default='GETH')
DB = leveldb.LevelDB('build')
COINBASE = RPC.eth_coinbase()['result']
GAS = hex(25*10**5)
TRIES = 5

if COINBASE == '0x':
    print ERROR, 'no coinbase address'
    print 'ABORTING'
    sys.exit(1)

def errstr(string):
    return ERROR + string + Style.RESET_ALL

def get(name):
    return json.loads(DB.Get(name))

def put(name, info):
    DB.Put(name, json.dumps(info))

def import_repl(match):
    name = match.groupdict()['result']
    info = get(name)
    info['name'] = name
    return TEMPLATE % info

def getfullname(name, memo={}):
    if name in memo:
        return memo[name]
    n = name + '.se'
    for dir, subdirs, files in os.walk(CODEPATH):
        if n in files:
            memo[name] = os.path.join(dir, n)
            return memo[name]
    raise ValueError(errstr('Can\'t find contract ' + name))

def new_enough(fullname, info):
    return os.path.getmtime(fullname) > info['mtime']

def makeinfo(addr, sig, fullsig, mtime):
    return locals()

def compile_and_load(filename):
    try:
        return get(filename)
    except:
        pass

if __name__ == '__main__':
    main()
