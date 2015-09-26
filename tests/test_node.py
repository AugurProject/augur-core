#!/usr/bin/env python
'''\
Usage: ./test_node [<option> [<arg>]] ...

Starts a geth node for use with testing.

Options:
  [-d | --dir] "~/.geth_test_node" Directory for storing node data.

  [-p | --rpcport] "9696"          Port to use for rpc.

  [-P | --netport] "40404"         Port to use for networking.

  [-H | --rpchost] "localhost"     Host to use for rpc.

  [-h | --help]                    Shows this help message.

  [-l | --log] stdout              Filename for node output redirection.

  [-g | --genesis-nonce] "27"      Genesis nonce to use for node.

  [-n | --networkid] "1337"        Network id to use for node.
'''
################################################################################
#        1         2         3         4         5         6         7         8
from colorama import Style, Fore, init; init()
import subprocess
import traceback
import shutil
import socket
import signal
import time
import json
import sys
import os

BAD = Style.BRIGHT + Fore.RED + '{}' + Style.RESET_ALL

def cmd(args):
    with open(os.devnull, 'w') as NULL:
        return subprocess.check_output(args, stderr=NULL)

class TestNode(object):
    '''Starts a geth node with on private chain, useful for dapp testing.'''

    def __init__(self, rpchost='localhost', rpcport='9696',
                 log=sys.stdout, genesis_nonce="27", netport='40404',
                 networkid="1337", datadir=os.path.expanduser('~/.geth_test_node'),
                 verbose=True):
        
        self.name = 'node-{}'.format(os.urandom(4).encode('hex'))
        self.log = log
        self.verbose = verbose
        self.rpcport = rpcport
        self.rpchost = rpchost

        datadir = os.path.realpath(datadir)

        if verbose:
            print Style.BRIGHT + 'Setting up node environment.'

        if not os.path.isdir(datadir):
            os.mkdir(datadir)

        node_data = os.path.join(datadir, self.name + '-data')
        os.mkdir(node_data)
        pidfile = os.path.join(datadir, self.name + '.pid')

        self.node_data = node_data
        self.pidfile = pidfile

        genesis_block_path = os.path.join(node_data, 'genesis_block.json')
        with open(genesis_block_path, 'w') as f:
            block_data = {
                "nonce": '0x' + genesis_nonce.zfill(16),
                "difficulty": "0x01",
                "alloc":{},
                "mixhash":'0x0000000000000000000000000000000000000000000000000000000000000000',
                "coinbase":'0x0000000000000000000000000000000000000000',
                "timestamp":"0x00",
                "parentHash":'0x0000000000000000000000000000000000000000000000000000000000000000',
                "extraData":"0xcafebabe",
                "gasLimit":"0x2fefd8"}
            json.dump(block_data, f)

        geth_repo = os.path.join(datadir, 'go-ethereum')
        try:
            if not os.path.isdir(geth_repo):
                if verbose:
                    print '  Cloning go-ethereum'
                cmd(['git', 
                     '-C', datadir,
                     'clone', 
                     'https://github.com/ethereum/go-ethereum.git'])
        except subprocess.CalledProcessError as exc:
            other_geth_repo = os.path.expanduser('~/go-ethereum')
            if not os.path.isdir(other_geth_repo):
                print BAD.format('No go-ethereum repo found')
                raise exc
            print '    Using fallback geth-repo. Cross your fingers!'
            shutil.copytree(other_geth_repo, geth_repo)
        
        if cmd(['git', '-C', geth_repo, 'branch']) != 'release/1.1.0\n':
            cmd(['git', '-C', geth_repo, 'checkout', 'release/1.1.0'])

        geth_bin = os.path.join(geth_repo, 'build', 'bin', 'geth')
        if not (os.path.isfile(geth_bin) and
                ('1.1.0' in cmd([geth_bin, '-h']))):
            if verbose:
                print '  Building geth'
            cmd(['make', '-C', geth_repo, 'geth'])

        self.popen_args = [
            geth_bin,
            '--rpc',
            '--rpcport', rpcport,
            '--rpcaddr', rpchost,
            '--rpcapi','admin,db,eth,debug,miner,net,shh,txpool,personal,web3',
            '--ipcdisable',
            '--datadir', node_data,
            '--networkid', networkid,
            '--port', netport,
            '--genesis', genesis_block_path]

        if verbose:
            print '  Done' + Style.RESET_ALL

    def start(self):
        if self.verbose:
            msg = '''\
Starting node. To open a console:
  geth attach rpc:http://{}:{}'''
            msg = msg.format(self.rpchost, self.rpcport)
            print Style.BRIGHT + msg + Style.RESET_ALL
        self.proc = subprocess.Popen(
            self.popen_args,
            stdout=self.log,
            stderr=self.log)

        with open(self.pidfile, 'w') as pf:
            print>>pf, self.proc.pid

        while True:
            try:
                socket.create_connection(
                    (self.rpchost, self.rpcport),
                    0.5)
            except:
                pass
            else:
                break

    def shutdown(self):
        self.proc.send_signal(signal.SIGINT)
        self.proc.wait()

    def cleanup(self):
        os.remove(self.pidfile)
        shutil.rmtree(self.node_data)

    def wait(self):
        self.proc.wait()

    def __del__(self):
        self.shutdown()
        self.cleanup()

def read_options():
    options = {}
    opts = sys.argv[1:]
    i = 0

    while i < len(opts):

        opt = opts[i]
        if opt in ('-h', '--help'):
            print __doc__
            sys.exit(0)

        if i + 1 == len(opts):
            print "{} must have a specified value!".format(opt)
            print __doc__
            sys.exit(1)

        val = opts[i + 1]
        if opt in ('-d', '--dir'):
            options['datadir'] = val
        
        elif opt in ('-p', '--rpcport'):
            try:
                port = int(val)
            except Exception:
                print '{} value must be int: {}'.format(opt, val)
                sys.exit(1)
            if not 0 < port < (1 << 16):
                print '{} value not in correct range: {}'.format(opt, val)
                sys.exit(1)
            options['rpcport'] = val

        elif opt in ('-P', '--netport'):
            try:
                port = int(val)
            except Exception:
                print '{} value must be int: {}'.format(opt, val)
                sys.exit(1)
            if not 0 < port < (1 << 16):
                print '{} value not in correct range: {}'.format(opt, val)
                sys.exit(1)
            options['netport'] = val

        elif opt in ('-H', '--rpchost'):
            options['rpchost'] = val

        elif opt in ('-l', '--log'):
            options['log'] = open(val, 'w')

        elif opt in ('-g', '--genesis-nonce'):
            try:
                int(val)
            except:
                print '{} value must be int: {}'.format(opt, val)
            options['genesis_nonce'] = val

        elif opt in ('-n', '--networkid'):
            try:
                int(val)
            except:
                print '{} value must be int: {}'.format(opt, val)
            options['networkid'] = val

        else:
            print "unknown option: {}".format(opt)
            print __doc__
            sys.exit(1)

        i += 2

    return options

def main():
    try:
        options = read_options()
        node = TestNode(**options)
        node.start()
        node.wait()
    except KeyboardInterrupt:
        sys.stdout.write('\r')
        sys.stdout.flush()
        print Style.BRIGHT + 'Shutting down node' + Style.RESET_ALL
        node.shutdown()
        node.cleanup()
        sys.exit(0)
    except Exception as exc:
        print BAD.format('BAD ERROR BRO')
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
