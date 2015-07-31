import os, sys
from rpc_client import RPC_Client
from tester import start_node, close_node
import json
import math

MAXGAS = hex(int(math.pi * 1e6))
ROOT = os.path.dirname(os.path.realpath(sys.argv[0]))
DBPATH = os.path.join(ROOT, 'build.json')

def get_db():
    return json.load(DBPATH)

def save_db(db):
    with open(DBPATH, 'w') as db_file:
        json.dump(db, db_file, indent=4, sort_keys=True)
