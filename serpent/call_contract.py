#!/usr/bin/python
import warnings; warnings.simplefilter('ignore')
from tests.gethrpc import GethRPC, dumps
from pyepm.api import abi_data
from colorama import init, Style, Fore
import sys
import re

contracts = {
    'cash' : '0xf1d413688a330839177173ce98c86529d0da6e5c',
    'info' : '0x910b359bb5b2c2857c1d3b7f207a08f3f25c4a8b',
    'branches' : '0x13dc5836cd5638d0b81a1ba8377a7852d41b5bbe',
    'events' : '0xb71464588fc19165cbdd1e6e8150c40df544467b',
    'expiringEvents' : '0xd85f31c7688577f21af4dd278a1c0ce31174b0ef',
    'fxpFunctions' : '0xdaf26192091449d14c03026f79272e410fce0908',
    'markets' : '0x65100915863c7c8d83cc3298d0b15880a01b1eda',
    'reporting' : '0xd1f7f020f24abca582366ec80ce2fef6c3c22233',
    'createEvent' : '0x4bef64bebfe3acb7c1f6a67c1abd17aad77a103f',
    'createMarket' : '0x79652f18f281c113fac20e8434e223228340e383',
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
        sender=coinbase, gas=hex(3000000), to=c, data=data)
    rpc.eth_getTransactionByHash(result['result'])
    rpc.eth_call('pending', sender=coinbase, gas=hex(3000000), to=c, data=data)
