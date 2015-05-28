#!/usr/bin/python
import warnings; warnings.simplefilter('ignore')
from tests.gethrpc import GethRPC, dumps
from pyepm.api import abi_data
from colorama import init, Style, Fore
import sys
import re

contracts = {
    'cash' : '0xf1d413688a330839177173ce98c86529d0da6e5c',
    'info' : '0x3530bfdc65394687732d9c2becd6a3108271231b',
    'branches' : '0x13dc5836cd5638d0b81a1ba8377a7852d41b5bbe',
    'events' : '0xb71464588fc19165cbdd1e6e8150c40df544467b',
    'expiringEvents' : '0x61d90fd4c1c3502646153003ec4d5c177de0fb58',
    'fxpFunctions' : '0xdaf26192091449d14c03026f79272e410fce0908',
    'markets' : '0x3be9601854135c88bc085510a3abb7ea9c13e6cf',
    'reporting' : '0xa9ff1dd752b6669884cd58b93a7bb0e75aab1a6b',
    'createEvent' : '0xda062002b4cf172716e26b0dd4ef148b555a7087',
    'createMarket' : '0x32361732443f0cfd3ba47f76edafb4d6bd4e9262',
    'checkQuorum' : '0xe9aaab4aff0cf06e62d2442ae0f68660882e5a67',
    'buy&sellShares' : '0xda8c4eb4d2893657ed2105a52fcc81501fb97db5',
    'createBranch' : '0x4f61a99b4584d00243c3a23e0bad4a51f1018bc9',
    'sendReputation' : '0x049487d32b727be98a4c8b58c4eab6521791f288',
    'transferShares' : '0x78da82256f5775df22eee51096d27666772b592d',
    'makeReports' : '0x4dbde1b0890904e4c1a61efde63473502903d75f',
    'dispatch' : '0x3975c208cbab80321c14c845217fbf5a748e6d06',
}

def get_sym(arg):
    if type(arg) in (int, long):
        return 'i'
    if type(arg) == list:
        return 'a'
    else:
        return 's'

def safe_eval(thing):
    try:
        return eval(thing)
    except:
        return thing

if __name__ == '__main__':
    c = contracts[sys.argv[1]]
    func = sys.argv[2]
    args = map(safe_eval, sys.argv[3:])
    sig = reduce(lambda a, b: a+get_sym(b), args, '')
    data = abi_data(func, sig, args)

    rpc = GethRPC()
    coinbase = rpc.eth_coinbase()['result']
    result = rpc.eth_sendTransaction(
        sender=coinbase, gas=hex(3140000), to=c, data=data)
    rpc.eth_getTransactionByHash(result['result'])
    rpc.eth_call('pending', sender=coinbase, gas=hex(3140000), to=c, data=data)
