from __future__ import division
from ethereum import tester as t
from load_contracts import ContractLoader
import math
import random
import os
import time
import binascii
from pprint import pprint

ONE = 10**18
TWO = 2*ONE
HALF = ONE/2

# def gas_use(s):
#     print "Gas Used:"
#     gas_used = s.block.gas_used - initial_gas
#     print gas_used
#     initial_gas = s.block.gas_used
#     return gas_used

def test_refund(contracts, state, t):
    print contracts.orders.commitOrder(5, value=500, sender=t.k2)
    contracts._ContractLoader__state.mine(20)
    print contracts.orders.checkHash(5, t.a2)
    print contracts.orders.getInfo(t.a2)

def test_x(contracts, state, t):
    print contracts.orders.checkHash(5, t.k2)

if __name__ == '__main__':
    src = os.path.join(os.getenv('AUGUR_CORE', os.path.join(os.getenv('HOME', '/home/ubuntu'), 'workspace')), 'src')
    contracts = ContractLoader(src, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'], '', 0)
    state = contracts._ContractLoader__state
    t = contracts._ContractLoader__tester
    test_refund(contracts, state, t)
    test_x(contracts, state, t)

    # functions/binaryMarketResolve.se
    # functions/nonBinaryMarketResolve.se
    # functions/resolveForkEvent.se
        # functions/binaryForkResolve.se
        # functions/nonBinaryForkResolve.se
    # functions/closeMarket.se
    # functions/controller.se
    # macros/refund.sem
    # macros/float.sem
    # macros/logReturn.sem

    print "DONE TESTING"

# state.block.get_balance(address)
### Useful for controller testing
    # from ethereum import tester as t
    # import ethereum
    # import serpent
    # import sha3
    # s = t.state()
    # c = s.abi_contract('functions/controller.se')
    # x = ethereum.abi.ContractTranslator(serpent.mk_full_signature('functions/controller.se'))
    # y = x.encode_function_call("setValue", [5])
    # sha3.sha3_256(y).hexdigest()

    # import binascii
    # binascii.hexlify()