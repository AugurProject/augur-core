'''Class for easy interaction with contracts via rpc.'''
from warnings import simplefilter; simplefilter('ignore')
import time
import json
import sha3
import sys

def int2abi(n):
    return hex(n % 2**256)[2:].rstrip('L').zfill(64)

def encode(args):
    static = []
    dynamic = []
    for arg in args:
        if isinstance(arg, int):
            static.append(int2abi(arg))
        if isinstance(arg, (list, str)):
            static.append(int2abi(32*len(args) + sum(map(len, dynamic))/2))
            dynamic.append(int2abi(len(arg)))
        if isinstance(arg, list):
            assert all(isinstance(e, int) for e in arg), 'Only lists of ints are supported!'
            dynamic.extend(map(int2abi, arg))
        if isinstance(arg, str):
            dynamic.append(arg.encode('hex'))
            if len(arg)%32:
                #padding
                dynamic.append('0'*(64 - 2*(len(arg)%32)))
    return ''.join(static + dynamic)

class Contract(object):
    def __init__(
            self, contract_address,
            caller_address, fullsig,
            rpc, default_gas):

        self.rpc = rpc
        self.caller_address = caller_address
        self.contract_address = contract_address
        self.default_gas = default_gas

        prefixes = {}
        types = {}
        for item in fullsig:
            if item['type'] == 'function':
                name, argtypes = item['name'].split('(')
                prefix = sha3.sha3_256(item['name'].encode('ascii')).hexdigest()[:8]
                prefixes[name] = prefix
                argtypes = argtypes.strip(')').split(',')
                if argtypes == ['']:
                    types[name] = ()
                else:
                    newtypes = []
                    for a in argtypes:
                        if '[' in a and ']' in a:
                            newtypes.append(list)
                        elif 'string' in a or 'bytes' in a or 'address' in a:
                            newtypes.append(str)
                        elif 'int' in a or 'real' in a:
                            newtypes.append(int)
                        else:
                            raise ValueError('Unsupported type! {}'.format(a))
                    types[name] = tuple(newtypes)

        self.types = types
        self.prefixes = prefixes

    def __getattr__(self, name):
        if name in self.prefixes:
            prefix = self.prefixes[name]
            types = self.types[name]

            def call(*args, **kwds):
                if len(args) != len(types) or not all(map(isinstance, args, types)):
                    raise TypeError('Bad argument types! <args {}> <types {}>'.format(args, types))

                if 'gas' in kwds:
                    gas = kwds['gas']
                else:
                    gas = self.default_gas
                
                tx = {
                    'to':self.contract_address,
                    'sender':self.caller_address,
                    'data':'0x' + prefix + encode(args),
                    'gas':self.default_gas,
                }

                if kwds.get('call', False):
                    result = self.rpc.eth_call(**tx)
                    assert 'error' not in result, json.dumps(result,
                                                             indent=4, 
                                                             sort_keys=True)
                    return result
                elif kwds.get('fastsend', False):
                    result = self.rpc.eth_sendTransaction(**tx)
                    assert 'error' not in result, json.dumps(result,
                                                             indent=4, 
                                                             sort_keys=True)
                    return result
                else:
                    result = self.rpc.eth_sendTransaction(**tx)
                    assert 'error' not in result, json.dumps(result,
                                                             indent=4, 
                                                             sort_keys=True)
                    txhash = result['result']

                    while True:
                        receipt = self.rpc.eth_getTransactionReceipt(txhash)
                        if receipt['result'] is not None:
                            return receipt
                        time.sleep(0.5)

            call.__name__ = name
            setattr(self, name, call)
            return call
        raise ValueError('No function with that name in this contract!')

def main():
    from warnings import simplefilter; simplefilter('ignore')
    from colorama import Style, Fore, init; init()
    from test_node import TestNode
    from pyrpctools import RPC_Client, MAXGAS
    import serpent
    import time

    svcoin = '''\
def init():
    sstore({my_address}, 10**10)

def send(to, amount):
    with my_bal = sload(msg.sender):
        if amount < my_bal:
            sstore(msg.sender, my_bal - amount)
            sstore(to, sload(to) + amount)
            return(1)
        return(-1)

def myBalance():
    return(sload(msg.sender))

def getBalance(address):
    return(sload(address))
'''
#    print serpent.mk_full_signature(svcoin)
#    sys.exit(0)
    node = TestNode(log=open('test_contract.log', 'w'))
    node.start()
    rpc = RPC_Client((node.rpchost, node.rpcport), 0)
    my_address = rpc.eth_coinbase()['result']
    svcoin = svcoin.format(my_address=my_address)
    compiled_code = serpent.compile(svcoin).encode('hex')
    fullsig = json.loads(serpent.mk_full_signature(svcoin))

    print Style.BRIGHT + 'Mining coins...' + Style.RESET_ALL

    balance = int(rpc.eth_getBalance(my_address)['result'], 16)
    gas_price = int(rpc.eth_gasPrice()['result'], 16)
    while balance/gas_price < int(MAXGAS, 16):
        balance = int(rpc.eth_getBalance(my_address)['result'], 16)
        time.sleep(1)

    txhash = rpc.eth_sendTransaction(sender=my_address,
                                     data=('0x' + compiled_code),
                                     gas=MAXGAS)['result']
    time.sleep(8)
    receipt = rpc.eth_getTransactionReceipt(txhash)['result']
    contract_address = receipt['contractAddress']
    contract = Contract(contract_address, my_address, fullsig, rpc, MAXGAS)
    print 'contract.myBalance() ->', int(contract.myBalance(call=True)['result'], 16)
    print 'contract.send(2, 100) ->', contract.send(2, 100)['result']
    print 'contract.myBalance() ->', int(contract.myBalance(call=True)['result'], 16)
    print 'contract.getBalance(2) ->', int(contract.getBalance(2, call=True)['result'], 16)

    node.shutdown()
    node.cleanup()

if __name__ == '__main__':
    main()
