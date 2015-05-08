from rpc import rpc
import leveldb
GETHRPC = rpc(default='GETH')
DB = leveldb.LevelDB('build')
COINBASE = GETHRPC.eth_coinbase()['result']
