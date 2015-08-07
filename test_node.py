#!/usr/bin/env python
'''\
Usage: ./test_node [<option> [<arg>]] ...

Starts a geth node for use with testing.

Options:
  [-p | --port] "9696"          Specifies the port to use for the node's rpc.

  [-H | --host] "localhost"     Specifies the host to use for the node's rpc.

  [-h | --help]                 Shows this help message.

  [-l | --log]                  Specify a file to redirect the node's stdout
                                and stderr to.

  [-g | --genesis-nonce] "27"   Genesis nonce to use for node.

  [-n | --networkid] "1337"     Network id to use for node.
'''
################################################################################
#        1         2         3         4         5         6         7         8
from colorama import Style, init; init()
import subprocess
import socket
import signal
import shutil
import time
import sys
import os

HOST = 'localhost'
PORT = '9696' #default rpc port value is different from standard geth
              #to avoid port conflicts
LOG = None
GENESIS_NONCE = '27'
NETWORKID = '1337'

def read_options():
    global HOST
    global PORT
    global LOG
    global GENESIS_NONCE
    global NETWORKID

    opts = sys.argv[1:]
    i = 0

    while i < len(opts):

        opt = opts[i]
        if opt in ('-h', '--help'):
            print __doc__
            sys.exit(0)

        if i + 1 == len(opts):
            print "{} opt must have a specified valued!"
            print __doc__
            sys.exit(1)

        val = opts[i + 1]
        if opt in ('-p', '--port'):
            try:
                PORT = int(val)
            except Exception:
                print '{} value must be int: {}'.format(opt, val)
                sys.exit(1)
            if not 0 < PORT < (1 << 16):
                print '{} value not in correct range: {}'.format(opt, val)
                sys.exit(1)

        elif opt in ('-H', '--host'):
            HOST = val

        elif opt in ('-l', '--log'):
            LOG = open(val, 'w')

        elif opt in ('-g', '--genesis-nonce'):
            try:
                int(val)
            except:
                print '{} value must be int: {}'.format(opt, val)
            GENESIS_NONCE = val

        elif opt in ('-n', '--networkid'):
            try:
                int(val)
            except:
                print '{} value must be int: {}'.format(opt, val)
            NETWORKID = val

        else:
            print "unknown option: {}".format(opt)
            print __doc__
            sys.exit(1)

        i += 2

def setup_environment():
    global GETH_PATH
    global DATA_DIR
    global PASSWORD
    global COMMAND
    
    print Style.BRIGHT + 'Setting up node environment.'
    null = open(os.devnull, 'w')
    old_dir = os.getcwd()

    USER = os.path.expanduser('~')
    AUGUR_TEST = os.path.join(USER, '.augur_test')
    if not os.path.isdir(AUGUR_TEST):
        os.mkdir(AUGUR_TEST)

    PASSWORD = os.path.join(AUGUR_TEST, 'eth_pass.txt')
    if not os.path.isfile(PASSWORD):
        with open(PASSWORD, 'w') as passfile:
            print >>passfile, os.urandom(32).encode('hex')

    DATA_DIR = os.path.join(AUGUR_TEST, 'node_data')
    if os.path.isdir(DATA_DIR):
        print '  Removing old datadir'
        shutil.rmtree(DATA_DIR)
        os.mkdir(DATA_DIR)

    GO_ETHEREUM = os.path.join(AUGUR_TEST, 'go-ethereum')
    if not os.path.isdir(GO_ETHEREUM):
        os.chdir(AUGUR_TEST)
        print '  Cloning go-ethereum'
        subprocess.call(['git', 'clone', 'https://github.com/ethereum/go-ethereum.git'], stdout=null, stderr=null)
    
    os.chdir(GO_ETHEREUM)
    if subprocess.check_output(['git', 'branch']) != 'release/0.9.36\n':
        subprocess.call(['git', 'checkout', 'release/0.9.36'], stdout=null, stderr=null)

    GETH_PATH = os.path.join(GO_ETHEREUM, 'build', 'bin', 'geth')
    if (not os.path.isfile(GETH_PATH)) or ('--genesisnonce' not in subprocess.check_output([GETH_PATH, '-h'])):
        print '  Building geth'
        subprocess.call(['make', 'geth'], stdout=null, stderr=null)

    COMMAND = [GETH_PATH,
               '--rpc',
               '--rpcport', PORT,
               '--rpcaddr', HOST,
               #rpcapi lets you connect to the node
               '--rpcapi', 'admin,db,eth,debug,miner,net,shh,txpool,personal,web3',
               '--datadir', DATA_DIR,
               '--password', PASSWORD,
               '--genesisnonce', GENESIS_NONCE,
               '--networkid', NETWORKID,
               #hard coded alternative network port
               #lets a legit geth node run simultaneously
               '--port', '40404']

    os.chdir(old_dir)
    null.close()
    print '  Done' + Style.RESET_ALL

def get_kwds():
    kwds = {}
    if LOG:
        kwds['stdout'] = LOG
        kwds['stderr'] = LOG
    return kwds

def make_address():
    subprocess.call(COMMAND + ['account', 'new'],
                    **get_kwds())

def start_node():
    START_NODE = COMMAND + [
        '--mine',
        '--minerthreads', '2',
        '--unlock', '0',
        '--etherbase', '0']
    msg = 'Starting node. Connect to rpc at {}:{}'
    print Style.BRIGHT + msg.format(HOST, PORT) + Style.RESET_ALL
    node = subprocess.Popen(START_NODE, **get_kwds())
    while True:
        try:
            socket.create_connection((HOST, PORT), 0.5)
        except:
            pass
        else:
            break
    return node

def main():
    read_options()
    setup_environment()
    make_address()
    node = start_node()

    try:
        node.wait()
    except:
        sys.stdout.write('\r')
        sys.stdout.flush()
        node.send_signal(signal.SIGINT)
        node.wait()

if __name__ == '__main__':
    main()
