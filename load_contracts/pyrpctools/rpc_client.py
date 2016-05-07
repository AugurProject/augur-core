from colorama import init, Fore, Style, Back; init()
from http import read_message
import traceback
import socket
import json
import sys
import re
import os

def pdumps(rpc):
    '''Turns an rpc dict into a pretty string.'''
    return json.dumps(rpc, sort_keys=True, indent=4) 

#color schemes for messages
TRACE = Style.BRIGHT + Fore.BLACK + Back.RED
ERROR = Style.BRIGHT + Fore.RED + 'ERROR:'
INFO = Style.BRIGHT + Fore.BLACK + Back.WHITE

#Template for interacting with nodes via JSONRPC
REQUEST = '''\
POST / HTTP/1.1\r
User-Agent: augur-loader/1.0\r
Host: {info[0]}:{info[1]}\r
Accept: */*\r
Content-Length: {length}\r
Content-Type: application/json\r
\r
{rpc_data}'''

class RPC_Client(object):
    '''A class for sending arbitrary rpc calls to an Ethereum node.'''
    def __init__(self, address, verbosity):
        '''
        If default is specified it must be either 'GETH', 'ALETHZERO', or 'TESTRPC'.
        If address is specified, it must be a tuple like ('localhost', 8080).
        If verbose is True, then debugging info will be printed out
        for every RPC call and response. It is True by default.
        '''
        
        self.info = address
        self.conn = socket.create_connection(self.info)
        self.id = 1
        self.verbose = verbosity > 0
        self.debug = verbosity > 1
        self.suffix = os.urandom(5).encode('hex')

    def _send_rpc(self, name, args, kwds):
        if 'sender' in kwds:
            kwds['from'] = kwds.pop('sender')
        params = []

        if kwds: params.append(kwds)
        if args: params.extend(list(args))

        rpc_data = json.dumps({
            'jsonrpc':'2.0',
            'id': self.suffix + '-' + str(self.id),
            'method': name,
            'params': params})

        request = REQUEST.format(
            length=len(rpc_data),
            rpc_data=rpc_data,
            info=self.info,
        )
        if self.verbose:
            print INFO + 'Sending rpc:' + Style.RESET_ALL
            print pdumps(json.loads(rpc_data))

        if self.debug:
            print
            print request
            print
        self.conn.sendall(request)
        response = read_message(self.conn)
        if self.debug:
            print
            print pdumps(response)
            print 
        self.id += 1
        try:
            result = json.loads(response['body'])
            if self.verbose:
                print INFO + 'Result:' + Style.RESET_ALL
                print pdumps(result)
            return result
        except Exception as exc:
            print TRACE + traceback.format_exc() + Style.RESET_ALL
            print ERROR, 'COULDN\'T LOAD RESPONSE DATA'
            print dumps(response)
            sys.exit(1)

    def __getattr__(self, name):
        def rpc_func(*args, **kwds):
            return self._send_rpc(name, args, kwds)
        rpc_func.__name__ = name
        vars(self)[name] = rpc_func
        return rpc_func
