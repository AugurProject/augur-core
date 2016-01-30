import os
import sys
import math
import time
import json
from rpc_client import RPC_Client

ROOT = os.path.dirname(os.path.realpath(sys.argv[0]))
DBPATH = os.path.join(ROOT, 'build.json')
MAXGAS = hex(int(math.pi*1e6))

def get_db():
    with open(DBPATH) as dbfile:
        return json.load(dbfile)

def save_db(db):
    with open(DBPATH, 'w') as dbfile:
        json.dump(db, dbfile, sort_keys=True, indent=4)

def confirmed_send(
        to=None, sender=None, gas=MAXGAS,
        data=None, value=None, blocktime=12,
        rpc=None):
    if rpc is None:
        rpc = RPC_Client()

    response = rpc.eth_sendTransaction({'to':to,
                                        'from':sender,
                                        'gas':gas,
                                        'data':data,
                                        'value':value})
    assert 'error' not in response, json.dumps(response, indent=4, sort_keys=True)
    txhash = response['result']
    while True:
        receipt = rpc.eth_getTransactionReceipt(txhash)
        if receipt['result']:
            return receipt
        time.sleep(blocktime)
