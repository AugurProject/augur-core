#!/usr/bin/python
'''
This script loads all serpent contracts onto the block chain using the geth RPC
    ./load_contracts.py
In order to use this script successfully, you need to prepare your geth node.
Start up a geth console using:
    geth --loglevel 0 console
Once there, make a new account if needed:
    admin.newAccount()
This will ask you to set a password, which you must remember!!!
If you don't have any money, you will have to mine for it:
    admin.miner.start()
You will also have to start the RPC server:
    admin.startRPC('127.0.0.1', 8545)
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
from collections import defaultdict
from tests.gethrpc import GethRPC
import leveldb
import serpent
import json
import sys
import os
import re

SRC_PATH = (
    'function files',
    'data and api files',
)

TEMPLATE = '''\
%(sig)s
macro %(name)s:
    %(addr)s
'''
IMPORTP = re.compile('^import (?P<name>\S+)$', re.M)
ERROR = Style.BRIGHT + Fore.RED + 'ERROR!'
RPC = GethRPC()
DB = leveldb.LevelDB('.build')
COINBASE = RPC.eth_coinbase()['result']
GAS = hex(25*10**5)
TRIES = 5

if COINBASE == '0x':
    print ERROR, 'no coinbase address'
    print 'ABORTING'
    sys.exit(1)

def get(name):
    try:
        return json.loads(DB.Get(name))
    except:
        return None

def put(name, info):
    DB.Put(name, json.dumps(info))

def import_repl(match):
    name = match.groupdict()['result']
    info = getinfo(name)
    info['name'] = name
    return TEMPLATE % info

def getfullname(name, memo={}):
    if name in memo:
        return memo[name]
    n = name + '.se'
    for path in SRC_PATH:
        for dir_, subdirs, files in os.walk(path):
            if n in files:
                memo[name] = os.path.join(dir_, n)
                return memo[name]
    raise ValueError('Can\'t find contract ' + name)

def new_enough(fullname, info):
    return os.path.getmtime(fullname) > info['mtime']

def getinfo(name):
    info = get(name)
    fullname = getfullname(name)
    if info and new_enough(fullname, info):
        return info
    else:
        code = IMPORTP.sub(import_repl, open(fullname).read())
        evm = '0x' + serpent.compile(code).encode('hex')
        sig = serpent.mk_signature(code)
        fullsig = serpent.mk_full_signature(code)
        address = RPC.eth_sendTransaction(sender=COINBASE, data=evm, gas=GAS)
        print Style.BRIGHT + "Waiting for " + name + " to get on chain..."
        check = RPC.eth_getCode(address)['result']
        tries = 1
        while check == '0x' and tries < TRIES:
            time.sleep(12)
            check = RPC.eth_getCode(address)['result']
            tries += 1
        if tries == TRIES and check == '0x':
            print ERROR, 'couldn\'t load contract to chain:', name
            print 'ABORTING'
            sys.exit(1)
        newinfo = {'addr':address, 'sig':sig, 'fullsig':fullsig, 'mtime':os.path.getmtime(fullname)}
        put(name, newinfo)
        return newinfo

def main():
    for path in SRC_PATH:
        for dir_, subdirs, files in os.walk(path):
            for name in files:
                if name.endswith('.se'):
                    getinfo(name.rstrip('.se'))

if __name__ == '__main__':
    main()
