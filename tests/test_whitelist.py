from warnings import simplefilter; simplefilter('ignore')
from pyrpctools import RPC_Client, MAXGAS
from test_node import TestNode
from test_contract import Contract
from colorama import Style, Fore, init; init()
import time
import serpent
import sha3
import json
import os

def make_accounts(rpc, n=10):
    '''Uses the 'personal' api to create several new accounts'''
    accounts = {} #address -> password
    for i in range(n):
        password = os.urandom(32).encode('hex')
        result  = rpc.personal_newAccount(password)
        assert 'result' in result, json.dumps(result, indent=4, sort_keys=True)
        account = result['result']
        accounts[account] = password
    return accounts

def unlock_accounts(rpc, accounts, duration):
    '''Uses the 'personal' api to unlock accounts. duration is in integer seconds.'''
    duration = int(duration)
    for account, password in accounts.items():
        rpc.personal_unlockAccount(account, password, '0x' + hex(duration))
    
def test_whitelist():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    log_file = os.path.join(test_dir, 'test_whitelist_node.log')
    whitelist_code = os.path.join(os.path.dirname(test_dir),
                                  os.path.join('src',
                                               'data and api',
                                               'reporting.se.whitelist'))

    node = TestNode(log=open(log_file, 'w'))
    node.start()
    rpc = RPC_Client((node.rpchost, node.rpcport), 0)
    accounts = make_accounts(rpc)
    unlock_accounts(rpc, accounts, 600)

    code = serpent.compile(whitelist_code).encode('hex')
    fullsig = json.loads(serpent.mk_full_signature(whitelist_code))
    my_address = rpc.eth_coinbase()['result']
    
    balance = int(rpc.eth_getBalance(my_address)['result'], 16)
    gas_price = int(rpc.eth_gasPrice()['result'], 16)

    print Style.BRIGHT + 'Mining coins...' + Style.RESET_ALL
    while balance/gas_price < int(MAXGAS, 16):
        balance = int(rpc.eth_getBalance(my_address)['result'], 16)
        time.sleep(1)

    txhash = rpc.eth_sendTransaction(sender=my_address,
                                     data=('0x'+code),
                                     gas=MAXGAS)['result']
    time.sleep(8)
    receipt = rpc.eth_getTransactionReceipt(txhash)['result']
    contract_address = receipt['contractAddress']

    contract = Contract(contract_address, my_address, fullsig, rpc, MAXGAS)
    
    # TODO test code here!!!

    node.shutdown()
    node.cleanup()
    os.remove(log_file)
    
if __name__ == '__main__':
    test_whitelist()
