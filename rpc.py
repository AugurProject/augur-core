#!/usr/bin/python
'''A script for using interacting with a local Ethereum node using JSON RPC.'''
from pyrpctools import RPC_Client
import sys
import re

GETHRPC = RPC_Client(default='GETH', debug=True)
COINBASE = GETHRPC.eth_coinbase()['result']

kwd_p = re.compile(r'--(?P<key>\D{2,})=(?P<val>.*)')
def parse_args():
    args = []
    kwds = {}
    for arg in sys.argv[2:]:
        m = kwd_p.match(arg)
        if m:
            d = m.groupdict()
            if d['val'] == 'COINBASE':
                d['val'] = COINBASE
            kwds[d['key']] = d['val']
        else:
            args.append(arg)
    return args, kwds

if __name__ == '__main__':
    rpc_cmd = sys.argv[1]
    args, kwds = parse_args()
    result = getattr(GETHRPC, rpc_cmd)(*args, **kwds)
