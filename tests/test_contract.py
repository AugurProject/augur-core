#!/usr/bin/env python
'''Class for easy interaction with contracts via rpc.'''
from warnings import simplefilter; simplefilter('ignore')
from colorama import Style, Fore, Back, init; init()
from pyrpctools import RPC_Client, MAXGAS
from test_node import TestNode
import serpent
import time
import json
import sha3
import sys
import os

def int2abi(n):
    '''Encode a python int according to the Ethereum ABI spec.'''
    return hex(n % 2**256)[2:].rstrip('L').zfill(64)

def encode(args):
    '''Encodes all arguments according to the Ethereum ABI spec.'''
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
    def __init__(self, contract_address, fullsig, coinbase, rpc, node, default_gas, verbose):
        self.contract_address = contract_address
        self.fullsig = fullsig
        self.coinbase = coinbase
        self.rpc = rpc
        self.node = node
        self.default_gas = default_gas
        self.verbose = verbose

        self.prefixes = {}
        self.types = {}
        for item in self.fullsig:
            if item['type'] == 'function':
                name, argtypes = item['name'].split('(')
                prefix = sha3.sha3_256(item['name'].encode('ascii')).hexdigest()[:8]
                self.prefixes[name] = prefix
                argtypes = argtypes.strip(')').split(',')
                if argtypes == ['']:
                    self.types[name] = ()
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
                    self.types[name] = tuple(newtypes)
                if self.verbose:
                    print item['name']
                    print 'short name:', name
                    print 'types:', self.types[name]
                    print 'prefix:', self.prefixes[name]

    @staticmethod
    def __setup_env(rpc, node, default_gas, verbose):

        if node is None:
            node = TestNode(log=open(os.devnull, 'w'))
            node.start()

        if rpc is None:
            rpc = RPC_Client((node.rpchost, node.rpcport), verbose)

        if default_gas is None:
            default_gas = int(MAXGAS, 16)
        assert isinstance(default_gas, int), 'default_gas must be an int!'

        coinbase = rpc.eth_coinbase()['result']
        if not coinbase:
            password = os.urandom(32).encode('hex')
            coinbase = rpc.personal_newAccount(password)['result']
            rpc.personal_unlockAccount(coinbase, password, 365*24*60*60)

        mining = rpc.eth_mining()['result']
        if not mining:
            rpc.miner_start(2)

        gas_price = int(rpc.eth_gasPrice()['result'], 16)
        balance = int(rpc.eth_getBalance(coinbase)['result'], 16)

        if verbose:
            print Style.BRIGHT + 'Mining coins...' + Style.RESET_ALL

        while balance < default_gas * gas_price:
            time.sleep(0.5)
            balance = int(rpc.eth_getBalance(coinbase)['result'], 16)

        return (coinbase, rpc, node, default_gas, verbose)
    
    @classmethod
    def from_code(cls, filename, rpc=None, node=None, default_gas=None, verbose=0):
        args = cls.__setup_env(rpc, node, default_gas, verbose)
        coinbase, rpc, node, default_gas, verbose = args

        if verbose:
            print Style.BRIGHT + 'Submitting contract...' + Style.RESET_ALL
        
        code = serpent.compile(filename).encode('hex')
        txhash = rpc.eth_sendTransaction(sender=coinbase,
                                         data=('0x'+code),
                                         gas=hex(default_gas))['result']

        while True:
            receipt = rpc.eth_getTransactionReceipt(txhash)
            if receipt.get('result', False):
                if isinstance(receipt['result'], dict):
                    result = receipt['result']
                    if result.get('contractAddress', False) and result.get('blockNumber', False):
                        contract_address = receipt['result']['contractAddress']
                        break
            time.sleep(0.5)

        chain_code = rpc.eth_getCode(contract_address)['result']
        if chain_code[2:] not in code:
            raise ValueError('Code did not compile correctly!!!')

        if verbose:
            print ' '*4 + Style.BRIGHT + 'done.' + Style.RESET_ALL

        fullsig = json.loads(serpent.mk_full_signature(filename))
        if verbose:
            print json.dumps(fullsig, indent=4, sort_keys=True)

        return cls(*((contract_address, fullsig) + args))

    def __getattr__(self, name):
        if name in self.prefixes:
            prefix = self.prefixes[name]
            types = self.types[name]
            verbose = self.verbose

            def call(*args, **kwds):
                if len(args) != len(types) or not all(map(isinstance, args, types)):
                    raise TypeError('Bad argument types! <args {}> <types {}>'.format(args, types))

                if 'gas' in kwds:
                    gas = kwds['gas']
                else:
                    gas = self.default_gas
                
                tx = {
                    'to':self.contract_address,
                    'sender':self.coinbase,
                    'data':'0x' + prefix + encode(args),
                    'gas':hex(self.default_gas),
                }
                if verbose:
                    print 'calling', name
                    print 'prefix:', prefix
                    print 'args:', args
                    print 'call data:', tx['data']
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
                            result = receipt['result']
                            if isinstance(result, dict):
                                if result.get('blockNumber', False):
                                    return receipt
                        time.sleep(0.5)

            call.__name__ = name
            setattr(self, name, call)
            return call
        raise ValueError('No function with that name in this contract! <name: {}> <valid-names: {}>'.format(name, self.prefixes.keys()))

    def __del__(self):
        self.node.shutdown()
        self.node.cleanup()

def main():
    svcoin = '''\
def SVCoinFaucet():
    sstore(tx.origin, 10**10)

def setSVCoinBalance(amount):
    sstore(tx.origin, amount)
    return(1)

def sendSVCoins(to, amount):
    with my_bal = sload(msg.sender):
        if amount < my_bal:
            sstore(msg.sender, my_bal - amount)
            sstore(to, sload(to) + amount)
            return(1)
        return(-1)

def mySVCoinBalance():
    return(sload(msg.sender))

def getSVCoinBalance(address):
    return(sload(address))
'''
    contract = Contract.from_code(svcoin)
    print 'contract.SVCoinFaucet() ->', contract.SVCoinFaucet()['result']
    print 'contract.mySVCoinBalance() ->', contract.mySVCoinBalance(call=True)['result']
    print 'contract.sendSVCoins(2, 100) ->', contract.sendSVCoins(2, 100)['result']
    print 'contract.mySVCoinBalance() ->', contract.mySVCoinBalance(call=True)['result']
    print 'contract.getSVCoinBalance(2) ->', contract.getSVCoinBalance(2, call=True)['result']
    contract.__del__()

if __name__ == '__main__':
    main()
