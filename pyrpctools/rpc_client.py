from colorama import Fore, Back, Style, init; init()
from http import read_message
import traceback
import socket
import json
import sys

# this helps keep code the right width
################################################################################
#        1         2         3         4         5         6         7         8


def pretty_dumps(rpc):
    '''Turns an rpc dict into a pretty string.'''
    return json.dumps(rpc, sort_keys=True, indent=4) 

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
    def __init__(self, address=('localhost', 8545), verbosity=0):
        '''
        `address` is the address of the RPC node you want to connect to. It 
        should be a tuple, like ('localhost', 8545) or ('127.0.0.1', 8080).
        `verbosity` changes how much is printed out while handling rpc requests.
        If it is set to 1, then the request and response json opbjects will be
        pretty printed. If it is set to 2, the HTTP request will be printed, 
        along with a json object containing the parsed HTTP response.
        '''
        self.verbosity = verbosity
        self.info = address
        self.conn = socket.create_connection(self.info)
        self._id = 1

    def _send_rpc(self, name, args, kwds):
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

        self._id += 1

        request = REQUEST.format(
            length=len(rpc_data),
            rpc_data=rpc_data,
            info=self.info)

        if self.verbosity > 0:
            print Fore.BLACK + Back.WHITE + 'Sending rpc:' + Style.RESET_ALL
            print pretty_dumps(json.loads(rpc_data))

        if self.verbosity > 1:
            print
            print request
            print

        self.conn.sendall(request)
        response = read_message(self.conn)

        if self.verbosity > 1:
            print
            print pretty_dumps(response)
            print 

        try:
            result = json.loads(response['body'])
            if self.verbosity > 0:
                print Fore.BLACK + Back.WHITE + 'Result:' + Style.RESET_ALL
                print pretty_dumps(result)
            return result
        except Exception as exc:
            print Fore.RED + Style.BOLD + 'COULDN\'T PARSE RESPONSE'
            print traceback.format_exc()
            print dumps(response) + Style.RESET_ALL
            sys.exit(1)

    def __getattr__(self, name):
        # generate rpc functions on the fly!
        def rpc_func(*args, **kwds):
            return self._send_rpc(name, args, kwds)
        rpc_func.__name__ = name
        vars(self)[name] = rpc_func
        return rpc_func
