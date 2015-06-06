#!/usr/bin/python2
import serpent
from pyrpctools import RPC_Client, DB
from collections import defaultdict
import os
import sys
import json
import time 

RPC = RPC_Client(default='GETH')
COINBASE = RPC.eth_coinbase()['result']
TRIES = 10
BLOCKTIME = 12
SRCPATH = 'src'
GAS = hex(3*10**6)

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
def get_fullname(name):
    '''
    Takes a short name from an import statement and
    returns a real path to that contract.
    '''
    for directory, subdirs, files in os.walk(SRCPATH):
        for f in files:
            if f[:-3] == name:
                return os.path.join(directory, f)
    raise ValueError('No such name: '+name)

def broadcast_code(evm):
    '''Sends compiled code to the network, and returns the address.'''
    address = RPC.eth_sendTransaction(sender=COINBASE, data=evm, gas=GAS)['result']
    tries = 0
    while tries < TRIES:
        check = RPC.eth_getCode(address)['result']
        if check != '0x':
            return address
        time.sleep(BLOCKTIME)
        tries += 1
    raise ValueError('CODE COULD NOT GET ON CHAIN!!!')

def build_dependencies():
    deps = defaultdict(list)
    for directory, subdirs, files in os.walk(SRCPATH):
        for f in files:
            for line in open(os.path.join(directory, f)):
                if line.startswith('import'):
                    name = line.split(' ')[1]
                    deps[name].append(f[:-3])
    return deps

def translate_code(fullname):
    new_code = []
    for line in open(fullname):
        line = line.rstrip()
        if line.startswith('import'):
            line = line.split(' ')
            name, sub = line[1], line[3]
            info = json.loads(DB[name])
            new_code.append(info['sig'])
            new_code.append(sub + ' = ' + info['address'])
        else:
            new_code.append(line)
    return '\n'.join(new_code)

def compile(fullname, deps):
    new_code = translate_code(fullname)
    evm = '0x' + serpent.compile(new_code).encode('hex')
    new_address = broadcast_code(evm)
    short_name = os.path.split(fullname)[-1][:-3]
    new_sig = serpent.mk_signature(new_code).replace('main', short_name, 1)
    fullsig = serpent.mk_full_signature(new_code)
    new_info = {'address':new_address, 'sig':new_sig, 'fullsig':fullsig}
    DB[short_name] = json.dumps(new_info)
    if short_name in deps:
        for dep in deps[short_name]:
            dep_fullname = get_fullname(dep)
            compile(dep_fullname, deps)

def main(contract_path):
    deps = build_dependencies()
    compile(contract_path, deps)

if __name__ == '__main__':
    main(sys.argv[1])
