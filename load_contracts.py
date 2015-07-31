#!/usr/bin/env python
'''\
Usage: python load_contracts.py [<option> ...]

  Compiles all serpent contracts in ./src, managing
dependency ordering and whitelisting.

Options:
  [-b | --blocktime] "12"        The next argument is the blocktime to
                                 use, in seconds. Can be a float.

  [-c | --contract] <name>       The name of a contract to recompile.
                                 This recompiles all necessary contracts.
                                 If this option is ommited, all contracts
                                 are recompiled.

  [-d | --dbfile] "build.json"   The name of the file to use as the database.
                                 When used with -c, the file must already exist
                                 and contain info on all of the dependencies
                                 required for compilation. If you aren't using
                                 -c, then all the new contract info will be
                                 dumped to this file.

  [-e | --externs]               By default, code is preprocessed to transform
                                 import syntax to native serpent externs.
                                 For example:
                                   import foo as FOO
                                 This gets translated into:
                                   extern foo.se:[bar:[int256]:int256]
                                   FOO = 0xdeadbeef
                                 This is much more convenient for new projects
                                 using more than one file, but it makes it
                                 harder to use with a large codebase that
                                 already uses externs. This option disables the
                                 preprocessing. Address variables need to have
                                 a space around the equal sign, and need to be
                                 right beneath their corresponding extern line.

  [-h | --help]                  Shows this help message.

  [-H | --rpchost] "localhost"   Host to use for rpc.

  [-p | --rpcport] "8545"        Port to use for rpc.

  [-v | --verbosity] "0"         The next argument should be 1 to see
                                 the RPC messages, or 2 to see the HTTP
                                 as well as the RPC messages.
'''
################################################################################
#        1         2         3         4         5         6         7         8
import warnings; warnings.simplefilter('ignore')
import serpent
import pyrpctools as rpc
from collections import defaultdict
import os
import sys
import json
import time

os.chdir(rpc.ROOT)
SOURCE = os.path.join(rpc.ROOT, 'src')
IMPORTS = True
VERBOSITY = 0
BLOCKTIME = 12
RPCHOST = "localhost"
RPCPORT = 8545
DB = {}
RPC = None
COINBASE = None
CONTRACT = None
TRIES = 10

def read_options():
    '''Reads user options and set's globals.'''
    global IMPORTS
    global VERBOSITY
    global BLOCKTIME
    global RPCHOST
    global RPCPORT
    global DB
    global RPC
    global COINBASE
    global CONTRACT

    opts = sys.argv[1:]
    i = 0
    bad_floats = map(float, (0, 'nan', '-inf', '+inf'))
    verb_vals = 1, 2

    while i < len(opts):

        if opts[i] in ('-e', '--exports'):
            IMPORTS = False
            i += 1

        elif opts[i] in ('-h', '--help'):
            print __doc__
            sys.exit(0)
            
        # -e and -h are the only options that can be the last arg
        # so if opts[i] isn't one of those or their long forms, then
        # I gotta check! if the next elif condition fails,
        # then the rest of the args are checked.

        elif (i + 1) == len(opts):
            print 'Invalid option use!', opts[i]
            print __doc__
            sys.exit(1)

        elif opts[i] in ('-b', '--blocktime'):
            try:
                b = float(opts[i+1])
            except ValueError as exc:
                print "The blocktime you provided is not a float!"
                sys.exit(1)
            if b in bad_floats:
                print 'Blocktime can not be 0, NaN, -inf, or +inf!'
                sys.exit(1)
            else:
                BLOCKTIME = b
            i += 2

        elif opts[i] in ('-c', '--contract'):
            CONTRACT = opts[i + 1]
            i += 2

        elif opts[i] in ('-d', '--dbfile'):
            rpc.DBPATH = os.path.join(rpc.ROOT, opts[i + 1])
            i += 2

        elif opts[i] in ('-H', '--rpchost'):
            RPCHOST = opts[i + 1]
            i += 2

        elif opts[i] in ('-p', '--rpcport'):
            try:
                RPCPORT = int(opts[i + 1])
            except:
                print "Bad Port!"
                sys.exit(1)
            i += 2

        elif opts[i] in ('-v', '--verbosity'):
            try:
                v = int(opts[i+1])
            except ValueError as exc:
                print "Error:", exc
                sys.exit(1)
            if v not in verb_vals:
                print 'Verbosity must be 1 or 2!'
                sys.exit(1)
            else:
                VERBOSITY = v
            i += 2

        else:
            print 'Invalid option!', opts[i]
            print __doc__
            sys.exit(1)

    if CONTRACT is not None:
        try:
            get_fullname(CONTRACT)
        except ValueError:
            print 'unknown contract name:', CONTRACT
            sys.exit(1)
        try:
            # When we are recompiling a single contract,
            # We use the existing DB to get address info.
            DB = rpc.get_db()
        except:
            print '--dbfile value does not exist: {}'.format(rpc.DBPATH)
            print __doc__
            sys.exit(1)

    RPC = rpc.RPC_Client((RPCHOST, RPCPORT), VERBOSITY)
    COINBASE = RPC.eth_coinbase()['result']

def get_fullname(shortname):
    '''
    Takes a short name from an import statement and
    returns a real path to that contract. The term
    "fullname" is used to refer to the full path of
    the contract file throughout this code. The term
    "shortname" is used to refer to the contract name
    alone, without the rest of the path info.
    '''
    for directory, subdirs, files in os.walk(SOURCE):
        for f in files:
            if f == shortname + '.se':
                return os.path.join(directory, f)
    raise ValueError('No such name: '+shortname)

def get_shortname(fullname):
    # the [:-3] is because all file names end in ".se"
    return os.path.basename(fullname)[:-3]

def wait(seconds):
    sys.stdout.write('Waiting %f seconds' % seconds)
    sys.stdout.flush()
    for i in range(10):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(seconds/10.)
    print

def broadcast_code(evm):
    '''Sends compiled code to the network, and returns the address.'''
    txhash = RPC.eth_sendTransaction(
        sender=COINBASE,
        data=evm,
        gas=rpc.MAXGAS)['result']

    tries = 0
    while tries < TRIES:
        #wait(BLOCKTIME)
        time.sleep(BLOCKTIME)
        receipt = RPC.eth_getTransactionReceipt(txhash)["result"]
        if receipt is not None:
            check = RPC.eth_getCode(receipt["contractAddress"])['result']
            if check != '0x' and check[2:] in evm:
                return receipt["contractAddress"]
        tries += 1
    user_input = raw_input("broadcast failed after %d tries! Try again? [Y/n]")
    if user_input in 'Yy':
        return broadcast_code(evm)
    print 'ABORTING'
    print json.dumps(DB, indent=4, sort_keys=True)
    sys.exit(1)

def get_compile_order():
    '''generates a list of contracts ordered by dependency'''
    # first build a list of all the contracts a.k.a. nodes
    contract_fullnames = []
    for directory, subdirs, files in os.walk(SOURCE):
        for f in files:
            if f.endswith('.se'):
                contract_fullnames.append(os.path.join(directory, f))

    # functions for extracting dependency info differ
    # depending on whether or not import syntax is used
    if IMPORTS:
        # import <dep> as ...
        line_check = lambda line: line.startswith('import')
        dependency_extractor = lambda line: line.split(' ')[1]
    else:
        # extern <dep>: ...
        line_check = lambda line: line.startswith('extern')
        dependency_extractor = lambda line: line[line.find(' ')+1:line.find(':')]

    # topological sorting! :3
    nodes = {}
    nodes_copy = {}
    avail = []
    # for each node, build a list of it's incoming edges.
    # contracts are nodes and dependencies are incoming edges.
    for fullname in contract_fullnames:
        shortname = get_shortname(fullname)
        incoming_edges = []
        for line in open(fullname):
            if line_check(line):
                incoming_edges.append(dependency_extractor(line))

        nodes_copy[shortname] = incoming_edges[:]

        if incoming_edges:
            nodes[shortname] = incoming_edges
        else:
            avail.append(shortname)

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
    return sorted_nodes, nodes_copy

def process_imports(fullname):
    new_code = []
    for line in open(fullname):
        line = line.rstrip()
        if line.startswith('import'):
            line = line.split(' ')
            name, sub = line[1], line[3]
            info = DB[name]
            new_code.append(info['sig'])
            new_code.append(sub + ' = ' + info['address'])
        else:
            new_code.append(line)
    return '\n'.join(new_code)

def process_externs(fullname):
    new_code = []
    last_extern = float('+inf')
    for i, line in enumerate(open(fullname)):
        line = line.rstrip()
        if line.startswith('extern'):
            print line
            last_extern = i
            name = line[line.find(' ')+1:line.find(':')][:-3]
            info = DB[name]
            new_code.append(info['sig'])
        elif i == last_extern + 1:
            sub = line.split(' ')[0]
            new_code.append(sub + ' = ' + info['address'])
        else:
            new_code.append(line)
    return '\n'.join(new_code)

def compile(fullname):
    global DB

    if IMPORTS:
        code = process_imports(fullname)
    else:
        code = process_externs(fullname)

    shortname = get_shortname(fullname)

    try:
        evm = '0x' + serpent.compile(code).encode('hex')
    except:
        traceback.print_exc()
        print 'Code that broke everything:'
        print code
        print 'DB dump:'
        print json.dumps(DB, indent=4, sort_keys=True)
        sys.exit(1)

    address = broadcast_code(evm)
    sig = serpent.mk_signature(code)
    # serpent makes the contract name in the sig "main"
    # if the code it compiles is in a string instead of a file.
    sig = sig.replace('main', shortname, 1)
    # Also, there is a serpent bug which can't handle multiple
    # return types in a function signature, which causes compilation
    # to fail. This is a workaround...
    sig = sig.replace(':,', ':_,').replace(':]', ':_]')
    fullsig = json.loads(serpent.mk_full_signature(code))
    DB[shortname] = {'address':address,
                      'sig':sig,
                      'fullsig':fullsig,
                      'code':code.split('\n')}

def optimize_deps(deps, contract_nodes):
    '''When a contract is specified for recompiling with -c, this is called
    to filter the compile order of the contracts so that only the specified
    contract, and every contract dependent on it, are recompiled.'''

    assert CONTRACT in deps, 'unknown contract specified!'

    new_deps = [CONTRACT]

    for i in range(deps.index(CONTRACT) + 1, len(deps)):
        node = deps[i]
        for new_dep in new_deps:
            if new_dep in contract_nodes[node]:
                new_deps.append(node)
                break

    return new_deps

def main():
    read_options()
    deps, nodes = get_compile_order()
    if CONTRACT is not None:
        deps = optimize_deps(deps, nodes)
    for fullname in map(get_fullname, deps):
        print "compiling", fullname
        compile(fullname)
    rpc.save_db(DB)

if __name__ == '__main__':
    main()
