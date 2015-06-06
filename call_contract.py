#!/usr/bin/python
from colorama import init, Style, Fore; init()
import warnings; warnings.simplefilter('ignore')
from pyrpctools import RPC_Client, DB
from pyepm.api import abi_data
import json
import time
import sys
import re

RPC = RPC_Client(default='GETH')
COINBASE = RPC.eth_coinbase()['result']
MAXTRIES = 10
BLOCKTIME = 12
GAS = hex(3*10**6)

def get_sym(arg):
    '''Get the symbol used for serpent signatures.'''
    if type(arg) in (int, long):
        return 'i'
    if type(arg) == list:
        return 'a'
    else:
        return 's'

def safe_eval(thing):
    '''Evaluates a string into a python object, or returns the string.'''
    if thing in ['--call', '--sendtx']:
        return None
    try:
        thing = eval(thing)
    except:
        return thing
    else:
        if type(thing) in (int, str, long):
            return thing
        elif type(thing) == list:
            if all([type(t)==int for t in thing]):
                return thing

def get_args():
    '''Turns command line arguments into python objects.'''
    return filter(lambda a: a is not None, map(safe_eval, sys.argv[3:]))

def get_sig(args):
    '''Creates the corresponding serpent signature for the given list of objects.'''
    return reduce(lambda a, b: a+get_sym(b), args, '')

def confirmed_send(**kwds):
    txhash = RPC.eth_sendTransaction(**kwds)['result']
    tries = 0
    while tries < MAXTRIES:
        time.sleep(BLOCKTIME)
        result = RPC.eth_getTransactionByHash(txhash)
        if result['result'] == None:
            return confirmed_send(**kwds)
        if result['result']['blockHash'] != None:
            break
        tries += 1
    return tries < MAXTRIES

if __name__ == '__main__':
    contract_name = sys.argv[1]
    contract_addr = json.loads(DB[contract_name])['address']
    args = get_args()
    sig = get_sig(args)
    funcname = sys.argv[2]
    abi = abi_data(funcname, sig, args)
    if '--call' in sys.argv:
        RPC.eth_call(sender=COINBASE, to=contract_addr, data=abi, gas=GAS)
    if '--sendtx' in sys.argv:
        result = confirmed_send(sender=COINBASE, to=contract_addr, data=abi, gas=GAS)
        if not result:
            raise ValueError('transaction failed!')
