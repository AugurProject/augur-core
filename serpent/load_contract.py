#!/usr/bin/python
'''
This script loads serpent contracts onto the block chain using the geth RPC
To load a contract onto the chain, do something like:
    ./load_contract.py junk.se
This script will compile the file using serpent, and send it to a locally running geth node.
In order to use this script successfully, you need to prepare your geth node.
Start up a geth console using:
    geth --loglevel 0 console
Once there, make a new account if needed:
    admin.newAccount()
This will ask you to set a password, which you must remember!!!
If you don't have any money, you will have to mine for it:
    admin.miner.start()
You will also have to start the RPC server:
    admin.startRPC('127.0.0.1', 8545)
And then finally you will have to unlock your account:
    admin.unlock(eth.coinbase, undefined, 60*60*24*30*12)
This will prompt you for the password you chose earlier.
'''
import warnings; warnings.simplefilter('ignore')
from colorama import init, Fore, Style
from tests.gethrpc import GethRPC, dumps
import serpent
import sys

init()
rpc = GethRPC()
coinbase_data = rpc.eth_coinbase()
coinbase = coinbase_data['result']
evm = '0x' + serpent.compile(sys.argv[1]).encode('hex')
data = rpc.eth_sendTransaction(sender=coinbase, gas=hex(3000000), data=evm)
