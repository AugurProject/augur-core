#!/usr/bin/env python
'''Class for easy interaction with ethereum contracts via rpc.'''
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

__all__ = ["Contract"]

MAX = 2**256
def int2abi(n):
    '''Encode a python int according to the Ethereum ABI spec.'''
    return hex(n % MAX)[2:-1].zfill(64)

def encode(args):
    '''Encodes all arguments according to the Ethereum ABI spec.'''
    static = []
    dynamic = []
    for arg in args:
        if isinstance(arg, (int, long)):
            static.append(int2abi(arg))
        if isinstance(arg, (list, str)):
            static.append(int2abi(32*len(args) + sum(map(len, dynamic))/2))
            dynamic.append(int2abi(len(arg)))
        if isinstance(arg, list):
            assert all(isinstance(e, (int, long)) for e in arg), 'Only lists of ints are supported!'
            dynamic.extend(map(int2abi, arg))
        if isinstance(arg, str):
            dynamic.append(arg.encode('hex'))
            if len(arg)%32:
                #padding
                dynamic.append('0'*(64 - 2*(len(arg)%32)))
    return ''.join(static + dynamic)

def decode(result):
    '''Decodes the result of a contract call into the appropriate python type.'''
    if result.startswith('0x'):
        result = result[2:]
    if len(result) == 0:
        return None
    if len(result) == 64:
        return int(result, 16)
    if len(result) > 64:
        array_len = int(result[:64], 16)
        result = result[64:]
        if array_len == len(result)/64: #array_len is the number of 32 byte chunks.
            return [int(result[i:i+64], 16) for i in range(0, len(result), 64)]
        else: #array_len is the number of bytes, and each char is a half byte.
            return result[:2*array_len].decode('hex')

INT = (int, long)
def process_fullsig(fullsig):
    '''Transforms a signature to help with type checking

The full signature of a contract looks something like:
[{"type":"function",
  "name":"foo(int256)",
  ... ,
 }]

The Contract class uses the type information in the signature,
so that my_contract.foo(1) will work, but my_contract.foo('bar')
will not. After the transformation, the signature looks like this:

{"foo":[("4c970b2f",      # prefix
         ((int, long),),  # types
         "foo(int256)")]} # full name

A contract might have multiple functions with the same name, but
different input types, so the result dictionary maps a name to a list
of info for each function with that name.
'''
    names_to_info = {}
    for item in filter(lambda i: i['type']=='function', fullsig):
        sig_start = item['name'].find('(')
        if sig_start == -1:
            raise ValueError('Bad function name in fullsig: {}'.format(item['name']))

        name = item['name'][:sig_start]
        if name not in names_to_info:
            names_to_info[name] = []

        prefix = sha3.sha3_256(item['name'].encode('ascii')).hexdigest()[:8]
        if item['name'][sig_start + 1] == ')': #empty sig
            names_to_info[name].append((prefix, (), item['name']))
        else:
            sig = item['name'][sig_start + 1:-1].split(',')
            pysig = []
            for t in sig:
                if '[]' in t:
                    pysig.append(list)
                elif t.startswith('bytes') or t.startswith('string') or t=='address':
                    pysig.append(str)
                elif 'int' in t:
                    pysig.append(INT)
                else:
                    raise TypeError('unsupported type in fullsig: {}'.format(t))
            names_to_info[name].append((prefix, tuple(pysig), item['name']))
    return names_to_info

def gen_doc_from_info(name, address, info):
    '''Creates a doc string from the result of `process_fullsig`.

The Contract class generates functions for calling contract functions
"on the fly", and those functions need documentation! If the result
of `process_fullsig` looks like this:

{"foo":[("4c970b2f",      # prefix
         ((int, long),),  # types
         "foo(int256)")]} # full name

Then the docstring will look like this:
"""Calls functions named `foo` in the contract at address "address".

Contract functions:
  foo(int256) "4c970b2f" ((<type 'int'>, <type 'long'>),)
"""
'''
    start = '''\
Calls functions named `{name}` in the contract at address "{address}".

Contract functions::
'''.format(name=name, address=address)
    widths = [max(map(len, map(str, col))) for col in zip(*info)] 
    fmt = '  {2:<{widths[2]}} "{0:<{widths[0]}}" {1:<{widths[1]}}'
    return start + '\n'.join(fmt.format(a, b, c, widths=widths) for a,b,c in info) + '\n'

class Contract(object):

    def __init__(self, contract_address, fullsig, rpc_client):
        self.contract_address = contract_address
        self.names_to_info = process_fullsig(fullsig)
        self.rpc = rpc_client
        self.default_sender = self.rpc.eth_coinbase()['result']
        self.default_gas = int(MAXGAS, 16)

    def __getattr__(self, name):
        if name not in self.names_to_info:
            raise ValueError('{name} is not a function in the fullsig!'.format(name=name))
            
        info = self.names_to_info[name]
        default_sender = self.default_sender
        contract_address = self.contract_address
        default_gas = self.default_gas
        rpc = self.rpc
        def call(*args, **kwds):
            for prefix, types, fullname in info:
                if len(args) == len(types) and all(map(isinstance, args, types)):
                    break
            else:
                raise TypeError('''Bad argument types!
given: {args}
                expected: {info}'''.format(args=args, info=info))

            tx = {
                'to':contract_address,
                'sender':kwds.get('sender', default_sender),
                'data':'0x' + prefix + encode(args),
                'gas':hex(kwds.get('gas', default_gas)),
            }

            if kwds.get('call', False):
                result = rpc.eth_call(**tx)
                assert 'error' not in result, json.dumps(result,
                                                         indent=4, 
                                                         sort_keys=True)
                return decode(result['result'])
                
            elif kwds.get('send', False):
                result = self.rpc.eth_sendTransaction(**tx)
                assert 'error' not in result, json.dumps(result,
                                                         indent=4, 
                                                         sort_keys=True)
                txhash = result['result']
                if kwds.get('receipt', False):
                    while True:
                        receipt = self.rpc.eth_getTransactionReceipt(txhash)
                        if receipt['result'] is not None:
                            result = receipt['result']
                            if isinstance(result, dict):
                                if result.get('blockNumber', False):
                                    return result
                        time.sleep(0.5)
                else:
                    return txhash
            else:
                raise ValueError('Must use `call` or `send` keyword!')

        call.__name__ = name
        call.__doc__ = gen_doc_from_info(name, contract_address, info)
        return call

def main():
    svcoin = '''\
def init():
    sstore(tx.origin, 21*10**9)

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

    evm = '0x' + serpent.compile(svcoin).encode('hex')
    fullsig = json.loads(serpent.mk_full_signature(svcoin))

    node = TestNode(log=open(os.devnull, 'w'), verbose=False)
    node.start()

    rpc = RPC_Client((node.rpchost, node.rpcport), 0)
    password = os.urandom(32).encode('hex')
    account = rpc.personal_newAccount(password)['result']
    rpc.personal_unlockAccount(account, password, hex(500))
    rpc.miner_start(2)
    
    balance = 0
    while balance < int(MAXGAS, 16):
        balance = int(rpc.eth_getBalance(account)['result'], 16)
    
    txhash = rpc.eth_sendTransaction(sender=account, data=evm, gas=MAXGAS)['result']

    while True:
        response = rpc.eth_getTransactionReceipt(txhash)
        receipt = response.get('result', False)
        if receipt:
            blocknumber = receipt.get('blockNumber', False)
            if blocknumber:
                address = receipt['contractAddress']
                break

    contract = Contract(address, fullsig, rpc)
    print 'My balance is', contract.mySVCoinBalance(call=True)
    receipt = contract.sendSVCoins(2, 10000, send=True, receipt=True)
    print 'Sent coins to address 2, receipt:'
    print json.dumps(receipt, indent=4, sort_keys=True)
    print 'Balance at address 2 is', contract.getSVCoinBalance(2, call=True)

if __name__ == '__main__':
    main()
