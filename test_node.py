#!/usr/bin/env python
'''\
Usage: ./test_node [<option> [<arg>]] ...

Starts a geth node for use with testing.

Options:
  [-p | --port] "9696"          Specifies the port to use for the node's rpc.

  [-H | --host] "localhost"     Specifies the host to use for the node's rpc.

  [-l | --log]                  Specify a file to redirect the node's stdout
                                and stderr to.

  [-g | --genesis-nonce] "27"   Genesis nonce to use for node.

  [-n | --networkid] "1337"     Network id to use for node.
'''
################################################################################
#        1         2         3         4         5         6         7         8
import subprocess
import socket
import signal
import shutil
import time
import sys
import os

HOST = 'localhost'
PORT = "9696" #default rpc port value is different from standard geth
              #to avoid port conflicts
LOG = None
GENESIS_NONCE = "27"
NETWORKID = "1337"

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
            LOG = val

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

def main():
    read_options()

    USER = os.path.expanduser('~')
    GETH_PATH = os.path.join(USER, 'go-ethereum', 'build', 'bin', 'geth')
    geth_not_found = 'No geth binary found at {}'.format(GETH_PATH)
    assert os.path.isfile(GETH_PATH), geth_not_found

    DATA = os.path.join(USER, '.tester')
    PASSWORD = os.path.join(DATA, 'ethpass.txt')
    COMMAND = [GETH_PATH,
               '--rpc',
               '--rpcport', PORT,
               '--rpcaddr', HOST,
               #rpcapi lets you connect to 
               '--rpcapi', 'admin,db,eth,debug,miner,net,shh,txpool,personal,web3',
               '--datadir', DATA,
               '--password', PASSWORD,
               '--genesisnonce', GENESIS_NONCE,
               '--networkid', NETWORKID,
               '--port', '40404'] #hard coded alternative network port
                                  #lets a legit geth node run simultaneously

    MAKE_ACCOUNT = COMMAND + ['account', 'new']
    RUN_NODE = COMMAND + [
        '--mine',
        '--minerthreads', '2',
        '--unlock', '0',
        '--etherbase', '0']

    if os.path.isdir(DATA):
        shutil.rmtree(DATA)

    os.mkdir(DATA)
    with open(PASSWORD, 'w') as passfile:
        print >>passfile, os.urandom(32).encode('hex')

    if LOG:
        log = open(LOG, 'w')
        subprocess.call(MAKE_ACCOUNT, stdout=log, stderr=log)
        node = subprocess.Popen(RUN_NODE, stdout=log, stderr=log)
    else:
        subprocess.call(MAKE_ACCOUNT)
        node = subprocess.Popen(RUN_NODE)
    
    try:
        node.wait()
    except KeyboardInterrupt:
        sys.stdout.write('\r')
        sys.stdout.flush()
        node.send_signal(signal.SIGINT)
        node.wait()
    
if __name__ == '__main__':
    main()
