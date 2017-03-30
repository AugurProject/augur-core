from colorama import init, Fore, Style, Back; init()
import httplib
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

class RPC_Client(object):
    '''A class for sending arbitrary rpc calls to an Ethereum node.'''
    def __init__(self, address, verbosity):
        '''
        If address is specified, it must be a tuple like ('localhost', 8080).
        If verbose is True, then debugging info will be printed out
        for every RPC call and response. It is True by default.
        '''
        
        self.info = address
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

        request_body = json.dumps({
            'jsonrpc':'2.0',
            'id': self.suffix + '-' + str(self.id),
            'method': name,
            'params': params})
        headers = { "Content-Type": "application/json" }
        conn = httplib.HTTPConnection(*self.info)
        conn.request("POST", "", request_body, headers)

        if self.verbose:
            print INFO + 'Request:' + Style.RESET_ALL
            print pdumps(json.loads(request_body))
            sys.stdout.flush()

        response = conn.getresponse()
        if response.status != 200:
            print 'Received failure response from server.  Code: ' + response.status + "  Reason: " + response.reason
            sys.exit(1)
        response_body = response.read()
        conn.close()
        self.id += 1
        try:
            result = json.loads(response_body)
            if self.verbose:
                print INFO + 'Result:' + Style.RESET_ALL
                print pdumps(result)
                sys.stdout.flush()
            return result
        except Exception as exc:
            print TRACE + traceback.format_exc() + Style.RESET_ALL
            print ERROR, 'COULDN\'T LOAD RESPONSE DATA'
            print dumps(response_body)
            sys.exit(1)

    def __getattr__(self, name):
        def rpc_func(*args, **kwds):
            return self._send_rpc(name, args, kwds)
        rpc_func.__name__ = name
        vars(self)[name] = rpc_func
        return rpc_func
