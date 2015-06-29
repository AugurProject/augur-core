import os
from rpc_client import RPC_Client
import leveldb

PATH = os.path.dirname(os.path.realpath(__file__))
DB = leveldb.LevelDB(os.path.join(PATH, os.pardir, 'build.dat'))
