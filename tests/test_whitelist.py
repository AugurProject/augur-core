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
    whitelist_code = open(os.path.join(os.path.dirname(test_dir),
                                       'src',
                                       'data and api',
                                       'reporting.se.whitelist')).read().split('\n')
    old_period = whitelist_code.index('macro PERIOD: 1800')
    whitelist_code[old_period] = 'macro PERIOD: 50'
    node = TestNode(log=open(os.path.join(test_dir, 'test_whitelist.log'), 'w'))
    node.start()
    rpc = RPC_Client((node.rpchost, node.rpcport), 0)
    accounts = make_accounts(rpc)
    unlock_accounts(rpc, accounts, 3600)
    contract = Contract.from_code('\n'.join(whitelist_code), node=node, rpc=rpc, verbose=1)
    
    for account in accounts:
        contract.addReporter(1010101,
                             int(account, 16),
                             send=True,
                             sender=account,
                             receipt=True) #this option forces blocking until included in a block
        index = contract.repIDToIndex(1010101, int(account, 16), call=True)
        contract.setRep(1010101, index, 10000*2**64, send=True, sender=account, receipt=True)
        
    contract.setWhitelist(2, [1,3,4,5], send=True, receipt=True)
    ballot_hash = contract.propose_replacement(5, 6, call=True)
    contract.propose_replacement(5, 6, send=True, receipt=True)
    
    for account, _ in zip(accounts, range(6)):
        contract.whitelistVote(ballot_hash, sender=account)
    
    last_period = contract.getPeriod()
    while contract.getPeriod() == last_period:
        time.sleep(1)

    if contract.getWhitelist(2) == [1,3,4,6]:
        print 'TEST PASSED'
    else:
        print 'TEST FAILED'

if __name__ == '__main__':
    test_whitelist()
