#!/usr/bin/python
from colorama import init, Style, Fore; init()
import warnings; warnings.simplefilter('ignore')
from pyrpctools import GETHRPC, DB, COINBASE
from pyepm.api import abi_data
import json
import time
import sys
import re

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
    c = json.loads(DB[sys.argv[1]])['address']
    func = sys.argv[2]
    args = map(safe_eval, sys.argv[3:])
    sig = reduce(lambda a, b: a+get_sym(b), args, '')
    data = abi_data(func, sig, args)
    result = GETHRPC.eth_sendTransaction(
        sender=COINBASE, gas=hex(3000000), to=c, data=data)
    GETHRPC.eth_call('pending', sender=COINBASE, gas=hex(3000000), to=c, data=data)
    print 'Waiting (maybe forever) to get on chain...'
    while True:
        result = GETHRPC.eth_getTransactionByHash(result['result'])
        if result['result'] != None:
            break
