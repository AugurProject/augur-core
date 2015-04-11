#!/usr/bin/python2
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
