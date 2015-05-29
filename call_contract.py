#!/usr/bin/python
from colorama import init, Style, Fore; init()
import warnings; warnings.simplefilter('ignore')
from pyrpctools import RPC, DB
from pyepm.api import abi_data
import json
import time
import sys
import re

GETHRPC = RPC(default='GETH')
COINBASE = GETHRPC.eth_coinbase()['result']

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

def call_contract(contract, funcname, args):
    sig = reduce(lambda a, b: a+get_sym(b), args, '')
    data = abi_data(funcname, sig, args)
    result = GETHRPC.eth_sendTransaction(
        sender=COINBASE, gas=hex(3000000), to=c, data=data)
    GETHRPC.eth_call('pending', sender=COINBASE, gas=hex(3000000), to=c, data=data)
    tries = 0
    while tries < 10:
        result = GETHRPC.eth_getTransactionByHash(result['result'])
        if result['result'] != None:
            return True
        tries += 1
    return False
    

if __name__ == '__main__':
    c = json.loads(DB[sys.argv[1]])['address']
    func = sys.argv[2]
    args = map(safe_eval, sys.argv[3:])
    call_contract(c, func, args)
