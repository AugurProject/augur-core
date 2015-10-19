#!/usr/bin/env python
from warnings import simplefilter; simplefilter('ignore')
from pyrpctools import RPC_Client, MAXGAS
from test_node import TestNode
from test_contract import Contract
from colorama import Style, Fore, init; init()
import time
import math
import serpent
import sha3
import json
import os
    
def setup_accounts(rpc, n, minBal, unlockDuration):
    '''Create n accounts on a local geth node, unlock them, and mine.

Blocks until all account have minBal wei.'''

    accounts = []
    for i in xrange(n):
        password = os.urandom(32).encode('hex')
        result = rpc.personal_newAccount(password)
        assert 'result' in result, json.dumps(result, indent=4, sort_keys=True)
        account = result['result']
        rpc.personal_unlockAccount(account, password, hex(unlockDuration))
        accounts.append(account)
        print 'Created and unlocked account:', account
    print

    gas_price = int(rpc.eth_gasPrice()['result'], 16)
    print 'mining...'
    rpc.miner_start(2)
    while int(rpc.eth_getBalance(accounts[0])['result'], 16) < len(accounts)*minBal*gas_price:
        time.sleep(0.5)
    print 'done mining'
    for account in accounts[1:]:
        rpc.eth_sendTransaction(sender=accounts[0], to=account, value=('0x' + hex(minBal)))
        time.sleep(2)

    return accounts

def test_whitelist():
    top_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    whitelist_code = open(os.path.join(top_dir, 
                                       'src', 
                                       'data and api', 
                                       'reporting.se.whitelist')).read().split('\n')

    # change the period length of votes so testing is feasible
    old_period = whitelist_code.index('macro PERIOD: 1800')
    whitelist_code[old_period] = 'macro PERIOD: 100'
    whitelist_code = '\n'.join(whitelist_code)

    # start the geth node
    node = TestNode(verbose=False)
    node.start()

    # create rpc client and initialize accounts
    rpc = RPC_Client((node.rpchost, node.rpcport), 0)
    accounts = setup_accounts(rpc, 10, int(MAXGAS, 16), 60*60)
    
    # compile code
    print 'compiling and submitting code'
    evm = '0x' + serpent.compile(whitelist_code).encode('hex')
    fullsig = json.loads(serpent.mk_full_signature(whitelist_code))
    response = rpc.eth_sendTransaction(sender=accounts[0], data=evm, gas=MAXGAS)
    txhash = response['result']
    
    while True:
        response = rpc.eth_getTransactionReceipt(txhash)
        receipt = response.get('result', False)
        if receipt:
            blocknumber = receipt.get('blockNumber', False)
            if blocknumber:
                address = receipt['contractAddress']
                break
    print 'done.'

    contract = Contract(address, fullsig, rpc)

    for account in accounts:
        while True:
            try:
                contract.addReporter(1010101,
                                     int(account, 16),
                                     send=True,
                                     sender=account,
                                     receipt=True) #this option forces blocking until included in a block
            except AssertionError as exc:
                error = json.loads(exc.message)['error']
                code = error['code']
                if code != -32603:
                    raise exc
                print 'nonce too low for account', account
                print 'trying again'
                time.sleep(10)
            else:
                break
        
        print 'account', account, 'added as reporter'
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
