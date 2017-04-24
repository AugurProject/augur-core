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
    balanceBefore = state.block.get_balance(t.a2)
    print contracts.orders.commitOrder(5, value=500*10**18, sender=t.k2)
    balanceAfter = state.block.get_balance(t.a2)
    assert(isclose(balanceBefore, balanceAfter) == True)

    contracts.state.mine(20)
    print contracts.orders.checkHash(5, t.a2)
    print contracts.controller.addToWhitelist(t.a0, sender=t.k0)
    print contracts.controller.checkWhitelist(t.a0, sender=t.k1)
    # print contracts.controller.checkWhitelist(t.a0)
    print contracts.backstops.setDisputedOverEthics(5, sender=t.k0)

def nearly_equal(a, b, sig_fig=8):
    return(a == b or int(a * 10**sig_fig) == int(b * 10**sig_fig))

def isclose(a, b, rel_tol=1e-10, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


if __name__ == '__main__':
    src = os.path.join(os.getenv('AUGUR_CORE', os.path.join(os.getenv('HOME', '/home/ubuntu'), 'workspace')), 'src')
    contracts = ContractLoader(src, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'], '', 1)
    state = contracts.state
    t = contracts._ContractLoader__tester
    test_refund(contracts, state, t)

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