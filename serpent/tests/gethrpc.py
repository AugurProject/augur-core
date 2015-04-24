from colorama import init, Fore, Style
import traceback
import socket
import json
import sys
import re

init()

def dumps(rpc):
    return json.dumps(rpc, sort_keys=True, indent=4) 

CHUNK = 4096

def read_n(conn, n, data=''):
    while len(data) < n:
        data += conn.recv(n - len(data))
    return data

#HTTP/1.1 200 OK
def parse_http_response(conn):
    first_line, data = conn.recv(CHUNK).split('\r\n', 1)
    headers, data = data.split('\r\n\r\n', 1)
    result = {}
    result['vers'] = first_line[5:8]
    result['code'] = first_line[9:12]
    result['msg']  = first_line[13:]

    result['headers'] = {}
    for header_line in headers.split('\r\n'):
        key, val = header_line.split(': ')
        result['headers'][key] = val

    if int(result['headers'].get('Content-Length', 0)) > len(data):
        n = int(result['headers']['Content-Length'])
        result['data'] = read_n(conn, n, data)

    elif result['headers'].get('Transfer-Encoding', '') == 'chunked':
        new_data = ''
        while data:
            i = data.find('\r\n')
            n, data = int(data[:i], 16), data[i+2:]
            if n:
                data = read_n(conn, n, data)
                new_data, data = new_data + data[:n], data[n:]
        result['data'] = new_data
    else:
        result['data'] = data
    return result

class GethRPC(object):
    HOST, PORT = 'localhost', 8545
    REQUEST = '''\
POST / HTTP/1.1\r
User-Agent: augur-loader/0.0\r
Host: localhost:8545\r
Accept: */*\r
Content-Length: %d\r
Content-Type: application/json\r
\r
%s'''
    def __init__(self, verbose=True):
        self.conn = socket.create_connection((GethRPC.HOST, GethRPC.PORT))
        self._id = 1
        self.verbose = verbose

    def __json(self, name, args, kwds):
        if 'sender' in kwds:
            kwds['from'] = kwds.pop('sender')
        params = []
        if kwds: params.append(kwds)
        if args: params.extend(list(args))
        rpc_data = json.dumps({
            'jsonrpc':'2.0',
            'id': self._id,
            'method': name,
            'params': params})
        request = GethRPC.REQUEST % (len(rpc_data), rpc_data)
        self.conn.sendall(request)
        response = parse_http_response(self.conn)
        self._id += 1
        if self.verbose:
            print Style.BRIGHT + Fore.RED + 'Sending rpc:'
            print Fore.WHITE + dumps(json.loads(rpc_data)) + Style.RESET_ALL
        
        try:
            result = json.loads(response['data'])
            if self.verbose:
                print Style.BRIGHT + Fore.RED + 'Result:'
                print Fore.WHITE + dumps(result) + Style.RESET_ALL
            return result
        except Exception as exc:
            print Style.BRIGHT + Fore.RED + traceback.format_exc()
            print 'COULDN\'T LOAD RESPONSE DATA'
            print dumps(response)
            sys.exit(1)

    def __getattr__(self, name):
        return lambda *args, **kwds: self.__json(name, args, kwds)
