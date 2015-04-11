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
    admin.newAccuont()
This will ask you to set a password, which you must remember!!!

If you don't have any money, you will have to mine for it:
    admin.miner.start()

You will also have to start the RPC server:
    admin.startRPC('127.0.0.1', 8545)

And then finally you will have to unlock your account:
    admin.unlock(eth.coinbase, undefined, 60*60*24*30*12)
This will prompt you for the password you chose earlier.

Finally, you will need to copy-pasta your address into this script's
coinbase variable, which you can see using the following command:
    eth.coinbase
'''

import serpent
import socket
import sys
import json

coinbase = '0x5437fb967926e559c08dcfcb39eb3a224fecadae'

data = json.dumps({
    'jsonrpc': '2.0',
    'method': 'eth_sendTransaction',
    'id': 1,
    'params':[
        {'from': coinbase,
         'gas': hex(10**6),
         'data': '0x'+serpent.compile(sys.argv[1]).encode('hex')}]})

request = '''\
POST / HTTP/1.1\r
User-Agent: augur-loader/0.0\r
Host: localhost:8545\r
Accept: */*\r
Content-Length: %d\r
Content-Type: application/json\r
\r
%s''' % (len(data), data)

c = socket.create_connection(('127.0.0.1', 8545))
c.sendall(request)
response = c.recv(4096)
print response
