#!/usr/bin/python
from tests.gethrpc import GethRPC, dumps
import sys
import re

kwd_p = re.compile(r'--(?P<key>\D{2,})=(?P<val>.*)')
def parse_args():
    args = []
    kwds = {}
    for arg in sys.argv[2:]:
        m = kwd_p.match(arg)
        if m:
            d = m.groupdict()
            kwds[d['key']] = d['val']
        else:
            args.append(arg)
    return args, kwds

if __name__ == '__main__':
    rpc = GethRPC()
    rpc_call = sys.argv[1]
    args, kwds = parse_args()
    result = getattr(rpc, rpc_call)(*args, **kwds)
