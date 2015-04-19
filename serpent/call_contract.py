#!/usr/bin/python
import warnings; warnings.simplefilter('ignore')
from load_contract import GethRPC
from pyepm.api import abi_data
from colorama import init, Style, Fore
import json
import sys
import re

contracts = {
    'cash' : '0x70e1ca88480a4b5f719a0add9b557779b9691764',
    'info' : '0x7f8bab7072ba2acc779dbb96d625bc73f6e6ccaf',
    'branches' : '0x148a56efa88437f52b9b22020bf0e9fdc75350e1',
    'events' : '0x45b5293570e78207f1c6dc41ca3e171c76b3d6db',
    'expiringEvents' : '0xf20cfeb17a3266f640077c7426b0d4c5081ecf43',
    'fxpFunctions' : '0x82695a58b84bbcc90372d06e9b1d599ca2dd60cd',
    'markets' : '0xaee8391634b73b8cf9ea27ca1c0ca251a3ad184b',
    'reporting' : '0xaab1a136fc3f3fce92fa1f8fe740e5e45ce6cde6',
    'checkQuorum' : '0x7d687123131b7a931521adfc79cddff084e855f4',
    'buy&sellShares' : '0x2094d578e8d7f20947f401328eec2eab7b07de06',
    'createBranch' : '0xaad25f1fa3429929e682be94ef823257c877bbc3',
    'p2pWagers' : '0x85e782b1ce91a1c0d8fdf93b0e9dfe52dc6ee5ef',
    'sendReputation' : '0x8d4bb333a4b859c776994967ed6223b01dcd3a74',
    'transferShares' : '0x63ee2b82fe40e1e103d130b4c2209d68cf047c93',
    'makeReports' : '0xf45288dc3235e71e2504fd760ff745a4085584ad',
    'createEvent' : '0xf3b7172641e46b28737cad3f07285d9f759054b9',
    'createMarket' : '0x4f188693e4e67fa11ee25f83da0782f859daf02a',
    'closeMarket' : '0xfd7baeaae87c0a9833d1d9840d8f4be554f4a9fa',
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
