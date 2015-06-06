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

def get_shortname(fullname):
    return os.path.split(fullname)[-1][:-3]

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
    return broadcast_code(evm)

def get_compile_order():
    # topological sorting! :3
    nodes = {}
    avail = []
    # for each node, build a list of it's incoming edges
    for directory, subdirs, files in os.walk('src'):
        for f in files:
            incoming_edges = [] 
            for line in open(os.path.join(directory, f)):
                if line.startswith('import'):
                    name = line.split(' ')[1]
                    incoming_edges.append(name)
            if incoming_edges:
                nodes[f[:-3]] = incoming_edges
            else:
                avail.append(f[:-3])
    sorted_nodes = []
    while avail:
        curr = avail.pop()
        sorted_nodes.append(curr)
        for item, edges in nodes.items():
            if curr in edges:
                edges.remove(curr)
            if not edges:
                avail.append(item)
                nodes.pop(item)
    return sorted_nodes

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

def compile(fullname):
    new_code = translate_code(fullname)
    evm = '0x' + serpent.compile(new_code).encode('hex')
    new_address = broadcast_code(evm)
    short_name = os.path.split(fullname)[-1][:-3]
    new_sig = serpent.mk_signature(new_code).replace('main', short_name, 1)
    fullsig = serpent.mk_full_signature(new_code)
    new_info = {'address':new_address, 'sig':new_sig, 'fullsig':fullsig}
    DB[short_name] = json.dumps(new_info)

def main(contract):
    deps = get_compile_order()
    start = deps.index(contract)
    for contract in deps[start:]:
        fullname = get_fullname(contract)
        compile(fullname)
    return 0

if __name__ == '__main__':
    main(sys.argv[1])
