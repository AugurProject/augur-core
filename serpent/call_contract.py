#!/usr/bin/python
import warnings; warnings.simplefilter('ignore')
from load_contract import GethRPC
from pyepm.api import abi_data
from colorama import init, Style, Fore
import json
import sys
import re

contracts = {
    'cash' : '0xc00329685aceba16e4bb622c9afc38aee6aa19eb',
    'info' : '0xdff1e97c3d2885a843a985bcd9e0f078c20b24b9',
    'branches' : '0xc00329685aceba16e4bb622c9afc38aee6aa19eb',
    'events' : '0x947b07180469b17c6c299bc70c16fcd9ee9d5acc',
    'expiringEvents' : '0x2491dee375afde12d3b443d0b3f9d686a1382158',
    'fxpFunctions' : '0x82695a58b84bbcc90372d06e9b1d599ca2dd60cd',
    'markets' : '0xdff1e97c3d2885a843a985bcd9e0f078c20b24b9',
    'reporting' : '0x2491dee375afde12d3b443d0b3f9d686a1382158',
    'createEvent' : '0x3c17de81765a65e39923084732697971dfa42071',
    'createMarket' : '0x143ee2baa908ee3641e07c0bed464e7e2b1ad5a4',
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
        sender=coinbase, gas=hex(3*10**4), to=c, data=data)
    print json.dumps(result, sort_keys=True, indent=4)
    print json.dumps(rpc.eth_getTransactionByHash(result['result']),
                     sort_keys=True,
                     indent=4)
    print json.dumps(rpc.eth_call('pending', sender=coinbase, gas=3000000, to=c, data=data),
                     sort_keys=True,
                     indent=4)
