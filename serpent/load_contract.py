#!/usr/bin/python2
'''
This script loads serpent contracts onto the block chain using the geth RPC
To load a contract onto the chain, do something like:
    ./load_contract.py junk.se
This script will compile the file using serpent, and send it to a locally running geth node.
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
'''
import warnings; warnings.simplefilter('ignore')
import serpent
import socket
import sys
import json


class GethRPC(object):
    HOST, PORT = '127.0.0.1', 8545
    REQUEST = '''\
POST / HTTP/1.1\r
User-Agent: augur-loader/0.0\r
Host: localhost:8545\r
Accept: */*\r
Content-Length: %d\r
Content-Type: application/json\r
\r
%s'''
    def __init__(self):
        self.conn = socket.create_connection((GethRPC.HOST, GethRPC.PORT))
        self._id = 1

    def __json(self, name, args):
        if 'sender' in args:
            args['from'] = args.pop('sender')
        if args == {}:
            args = []
        else:
            args = [args]
        rpc_data = json.dumps({
            'jsonrpc':'2.0',
            'id': self._id,
            'method': name,
            'params': args})
        request = GethRPC.REQUEST % (len(rpc_data), rpc_data)
        self.conn.sendall(request)
        response = self.conn.recv(4096)
        self._id += 1
        response_data = response.split('\r\n\r\n', 1)
        return json.loads(response_data[1])
        
    def __getattr__(self, name):
        return lambda **args: self.__json(name, args)

rpc = GethRPC()
coinbase = rpc.eth_coinbase()['result']
evm = '0x' + serpent.compile(sys.argv[1]).encode('hex')
data = rpc.eth_sendTransaction(sender=coinbase, gas=hex(3000000), data=evm)
print json.dumps(data, sort_keys=True, indent=4)
