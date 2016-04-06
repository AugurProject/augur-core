from colorama import init, Fore, Style, Back; init()
import requests
import json

def pdumps(rpc):
    '''Turns an rpc dict into a pretty string.'''
    return json.dumps(rpc, sort_keys=True, indent=4) 

#color schemes for messages
info_fmt = Style.BRIGHT + Fore.BLACK + Back.WHITE + '{}' + Style.RESET_ALL
def info(message):
    return info_fmt.format(message)

class RPC_Client(object):
    '''A class for sending arbitrary rpc calls to an Ethereum node.'''
    def __init__(self, address=('localhost', 8545), verbosity=1):
        '''
        If address is specified, it must be a tuple. The default is ('localhost', 8545).
        If verbosity is greater than 0, then json will be printed to the terminal
        for every RPC call and response. The default is 1.
        '''
        
        self.info = 'http://{}:{}'.format(*address)
        self.id = 1
        self.verbose = verbosity > 0

    def _send_rpc(self, name, args, kwds):
        if 'sender' in kwds:
            kwds['from'] = kwds.pop('sender')
        params = []

        if kwds: params.append(kwds)
        if args: params.extend(list(args))

        rpc_data = {'jsonrpc':'2.0',
                    'id': self.id,
                    'method': name,
                    'params': params}

        if self.verbose:
            print info('Sending rpc:')
            print pdumps(rpc_data)
        
        response = requests.post(self.info, json=rpc_data).json()

        if self.verbose:
            print info('Got response:')
            print pdumps(response)

        self.id += 1
        return response

    def __getattr__(self, name):
        def rpc_func(*args, **kwds):
            return self._send_rpc(name, args, kwds)
        rpc_func.__name__ = name
        vars(self)[name] = rpc_func
        return rpc_func
