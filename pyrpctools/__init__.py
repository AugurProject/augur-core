from rpc import rpc
import bsddb
GETHRPC = rpc(default='GETH')
DB = bsddb.hashopen('build')
COINBASE = GETHRPC.eth_coinbase()['result']
