#!/usr/bin/python2
import warnings; warnings.simplefilter('ignore')
import serpent
from pyrpctools import RPC_Client, DB
from collections import defaultdict
import os
import sys
import json
import time

FROM_DB = False
RPC = None
COINBASE = None
TRIES = 10
BLOCKTIME = 12
ROOT = os.path.dirname(os.path.realpath(__file__))
SRCPATH = os.path.join(ROOT, 'src')
GAS = hex(3*10**6)
USE_EXTERNS = False
INFO = {}

os.chdir(ROOT)

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

def broadcast_code(evm, txhash=None):
    '''Sends compiled code to the network, and returns the address.'''
    while True:
        response = RPC.eth_sendTransaction(sender=COINBASE, data=evm, gas=GAS)
        if 'result' in response:
            txhash = response['result']
            break
        else:
            assert 'error' in response and response['error']['code'] == -32603, 'Weird JSONRPC response: ' + str(response)
            if txhash is None:
                wait(BLOCKTIME)
            else:
                break
    tries = 0
    while tries < TRIES:
        wait(BLOCKTIME)
        receipt = RPC.eth_getTransactionReceipt(txhash)["result"]
        if receipt is not None and "contractAddress" in receipt:
            check = RPC.eth_getCode(receipt["contractAddress"])['result']
            if check != '0x' and check[2:] in evm:
                return receipt["contractAddress"]
            tries += 1
    return broadcast_code(evm, txhash=txhash)

def get_compile_order():
    # topological sorting! :3
    nodes = {}
    nodes_copy = {}
    avail = set()
    # for each node, build a list of it's incoming edges
    # incoming edges are dependencies
    for directory, subdirs, files in os.walk('src'):
        for f in files:
            if not f.endswith('.se'): continue
            incoming_edges = set() 
            for line in open(os.path.join(directory, f)):
                if USE_EXTERNS and line.startswith('extern'):
                    name = line[line.find(' ')+1:line.find(':')]
                    incoming_edges.add(name)
                if not USE_EXTERNS and line.startswith('import'):
                    name = line.split(' ')[1]
                    incoming_edges.add(name)
            nodes_copy[f[:-3]] = incoming_edges.copy()
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
    return sorted_nodes, nodes_copy

def get_info(name):
    if FROM_DB:
        return json.loads(DB.Get(name))
    else:
        return INFO[name]

def set_info(name, val):
    if FROM_DB:
        DB.Put(name, json.dumps(val))
    else:
        INFO[name] = val

def translate_code_with_imports(fullname):
    new_code = []
    for line in open(fullname):
        line = line.rstrip()
        if line.startswith('import'):
            line = line.split(' ')
            name, sub = line[1], line[3]
            info = get_info(name)
            new_code.append(info['sig'])
            new_code.append(sub + ' = ' + info['address'])
        else:
            new_code.append(line)
    return '\n'.join(new_code)

def translate_code_with_externs(fullname):
    new_code = []
    last_extern = float('+inf')
    for i, line in enumerate(open(fullname)):
        line = line.rstrip()
        if line.startswith('extern'):
            print line
            last_extern = i
            name = line[line.find(' ')+1:line.find(':')][:-3]
            info = get_info(name)
            new_code.append(info['sig'])
        elif i == last_extern + 1:
            sub = line.split(' ')[0]
            new_code.append(sub + ' = ' + info['address'])
        else:
            new_code.append(line)
    return '\n'.join(new_code)

def compile(fullname):
    if USE_EXTERNS:
        new_code = translate_code_with_externs(fullname)
    else:
        new_code = translate_code_with_imports(fullname)
    # print new_code
    evm = '0x' + serpent.compile(new_code).encode('hex')
    new_address = broadcast_code(evm)
    short_name = os.path.split(fullname)[-1][:-3]
    new_sig = serpent.mk_signature(new_code).replace('main', short_name, 1).replace(':,', ':_,').replace(':]', ':_]')
    fullsig = serpent.mk_full_signature(new_code)
    new_info = {'address':new_address, 'sig':new_sig, 'fullsig':fullsig}
    set_info(short_name, new_info)

def optimize_deps(deps, contract_nodes, contract):
    new_deps = [contract]
    for i in range(deps.index(contract) + 1, len(deps)):
        node = deps[i]
        for new_dep in new_deps:
            if new_dep in contract_nodes[node]:
                new_deps.append(node)
                break
    return new_deps

def main():
    global BLOCKTIME
    global USE_EXTERNS
    global RPC
    global COINBASE
    global FROM_DB
    start = 0
    verbose = False
    debug = False
    for arg in sys.argv:
        if arg.startswith('--BLOCKTIME='):
            BLOCKTIME = float(arg.split('=')[1])
        if arg.startswith('--contract='):
            FROM_DB = True
            start = arg.split('=')[1]
        if arg == '--use-externs':
            USE_EXTERNS = True
        if arg == '--verbose':
            verbose = True
        if arg == '--debug':
            debug = True
    deps, nodes = get_compile_order()
    if type(start) == str:
        deps = optimize_deps(deps, nodes, start)
        start = 0
    RPC = RPC_Client(default='GETH', verbose=verbose, debug=debug)
    COINBASE = RPC.eth_coinbase()['result']
    for i in range(start, len(deps)):
        fullname = get_fullname(deps[i])
        print "compiling", fullname
        compile(fullname)
    if not FROM_DB:
        print "dumping new addresses to build.dat & build.json..."
        with open(os.path.join(ROOT, "build.json"), "w") as json_file:
            print >> json_file, json.dumps(INFO, sort_keys=True, indent=4)
        for k, v in INFO.items():
            DB.Put(k, json.dumps(v))
    return 0

if __name__ == '__main__':
    main()
