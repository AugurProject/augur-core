#!/usr/bin/python2
import warnings; warnings.simplefilter('ignore')
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
USE_JACKS_LAME_SHIT = False

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

def wait(seconds):
    sys.stdout.write('Waiting %f seconds' % seconds)
    sys.stdout.flush()
    for i in range(10):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(seconds/10.)
    print

def broadcast_code(evm, address=None):
    '''Sends compiled code to the network, and returns the address.'''
    while True:
        response = RPC.eth_sendTransaction(sender=COINBASE, data=evm, gas=GAS)
        if 'result' in response:
            address = response['result']
            break
        else:
            assert 'error' in response and response['error']['code'] == -32603, 'Weird JSONRPC response: ' + str(response)
            if address is None:
                wait(BLOCKTIME)
            else:
                break
    tries = 0
    while tries < TRIES:
        wait(BLOCKTIME)
        check = RPC.eth_getCode(address)['result']
        if check != '0x' and check[2:] in evm:
            return address
        tries += 1
    return broadcast_code(evm, address)

def get_compile_order():
    # topological sorting! :3
    nodes = {}
    avail = set()
    # for each node, build a list of it's incoming edges
    for directory, subdirs, files in os.walk('src'):
        for f in files:
            incoming_edges = set() 
            for line in open(os.path.join(directory, f)):
                if line.startswith('import'):
                    name = line.split(' ')[1]
                    incoming_edges.add(name)
            if incoming_edges:
                nodes[f[:-3]] = incoming_edges
            else:
                avail.add(f[:-3])
    sorted_nodes = []
    while avail:
        curr = avail.pop()
        sorted_nodes.append(curr)
        for item, edges in nodes.items():
            if curr in edges:
                edges.remove(curr)
            if not edges:
                avail.add(item)
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
    DB.sync()

def main():
    global BLOCKTIME
    deps = get_compile_order()
    start = 0
    for arg in sys.argv:
        if arg.startswith('--BLOCKTIME='):
            BLOCKTIME = float(arg.split('=')[1])
        if arg.startswith('--contract='):
            start = deps.index(arg.split('=')[1])
    for i in range(start, len(deps)):
        fullname = get_fullname(deps[i])
        print "compiling", fullname
        compile(fullname)
    return 0

if __name__ == '__main__':
    main()
