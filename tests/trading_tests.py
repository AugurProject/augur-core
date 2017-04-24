#!/usr/bin/env python
'''
Trading tests:
functions/bidAndAsk.se
functions/cash.se
functions/claimMarketProceeds.se
functions/completeSets.se
functions/createEvent.se
functions/createMarket.se
functions/fillAskLibrary.se
functions/fillBidLibrary.se
functions/marketModifiers.se
functions/offChainTrades.se
functions/oneWinningOutcomePayouts.se
functions/shareTokens.se
functions/trade.se
functions/tradeAvailableOrders.se
functions/twoWinningOutcomePayouts.se
functions/wallet.se
'''

from __future__ import division
import ethereum
import os
import json
import iocapture
from load_contracts import ContractLoader

def hex2str(h):
    return hex(h)[2:-1]

def parseCapturedLogs(captured):
    return json.loads(captured.stdout.replace("'", '"').replace("L", "").replace('u"', '"'))

def test_cash(c, s, t):
    # t = ethereum.tester
    # t.gas_limit = 100000000
    # s = t.state()
    # c = s.abi_contract('../src/functions/cash.se')
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    initialEtherBalance2 = s.block.get_balance(t.a2)
    def test_init():
        assert(hex2str(c.getName()) == '4361736800000000000000000000000000000000000000000000000000000000'), "currency name"
        assert(c.getDecimals() == 18), "number of decimals"
        assert(hex2str(c.getSymbol()) == '4341534800000000000000000000000000000000000000000000000000000000'), "currency symbol"
    def test_depositEther():
        assert(c.depositEther(value=100, sender=t.k1) == 1), "deposit ether"
        assert(c.balanceOf(t.a1) == 100), "balance equal to deposit"
        assert(c.totalSupply() == 100), "totalSupply equal to deposit"
    def test_withdrawEther():
        assert(c.getInitiated(sender=t.k1) == 0), "withdraw not initiated"
        assert(c.withdrawEther(t.a2, 110, sender=t.k1) == 0), "withdraw fails, insufficient funds"
        assert(c.withdrawEther(t.a2, 30, sender=t.k1)), "initiate withdrawal"
        assert(c.getInitiated(sender=t.k1) == s.block.timestamp), "withdraw initiated"
        try:
            raise Exception(c.withdrawEther(t.a2, 30, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "withdraw should throw (3 days haven't passed)"
        s.block.timestamp += 259199
        try:
            raise Exception(c.withdrawEther(t.a2, 30, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "withdraw should throw (3 days still haven't passed)"
        s.block.timestamp += 1
        assert(c.withdrawEther(t.a2, 30, sender=t.k1)), "withdraw should succeed"
        assert(c.balanceOf(t.a1) == 70), "decrease sender's balance by 30"
        assert(c.balanceOf(t.a2) == 0), "receiver's cash balance still equals 0"
        assert(s.block.get_balance(t.a2) - initialEtherBalance2 == 30), "receiver's ether balance increased by 30"
        assert(c.totalSupply() == 70), "total supply decreased by 30"
        try:
            raise Exception(c.withdrawEther(t.a2, -10, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative withdraw should throw"
        assert(c.getInitiated(sender=t.k1) == 0), "withdraw no longer initiated"
    def test_transfer():
        with iocapture.capture() as captured:
            retval = c.transfer(t.a2, 5, sender=t.k1)
            logged = parseCapturedLogs(captured)
        assert(retval == 1), "transfer 5 cash to a2"
        assert(logged["_event_type"] == "Transfer")
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
        assert(logged["value"] == 5)
        assert(c.balanceOf(t.a1) == 65), "balance of a1 decreased by 5"
        assert(c.balanceOf(t.a2) == 5), "balance of a2 increased by 5"
        assert(c.totalSupply() == 70), "totalSupply unchanged"
        try:
            raise Exception(c.transfer(t.a2, 70, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transfer should throw if insufficient funds"
        try:
            raise Exception(c.transfer(t.a2, -5, sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.abi.ValueOutOfBounds)), "negative transfer should throw"
        with iocapture.capture() as captured:
            retval = c.transfer(t.a2, 0, sender=t.k1)
            logged = parseCapturedLogs(captured)
        assert(retval == 1), "transferFrom should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
        assert(logged["value"] == 0)
        assert(c.balanceOf(t.a1) == 65), "balance of a1 unchanged"
        assert(c.balanceOf(t.a2) == 5), "balance of a2 unchanged"
        assert(c.totalSupply() == 70), "totalSupply unchanged"
    def test_transferFrom():
        try:
            raise Exception(c.transferFrom(t.a1, t.a2, 7, sender=t.k2))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "transferFrom should throw, msg.sender is not approved"
    def test_approve():
        assert(c.allowance(t.a1, t.a2) == 0), "initial allowance is 0"
        with iocapture.capture() as captured:
            retval = c.approve(t.a2, 10, sender=t.k1)
            logged = parseCapturedLogs(captured)
        assert(retval == 1), "approve a2 to spend 10 cash from a1"
        assert(logged["_event_type"] == "Approval")
        assert(logged["owner"] == address1)
        assert(logged["spender"] == address2)
        assert(logged["value"] == 10)
        assert(c.allowance(t.a1, t.a2) == 10), "allowance is 10 after approval"
        with iocapture.capture() as captured:
            retval = c.transferFrom(t.a1, t.a2, 7, sender=t.k2)
            logged = parseCapturedLogs(captured)
        assert(retval == 1), "transferFrom should succeed"
        assert(logged["_event_type"] == "Transfer")
        assert(logged["to"] == address2)
        assert(logged["from"] == address1)
        assert(logged["value"] == 7)
    def test_commitSuicide():
        try:
            raise Exception(c.commitSuicide(sender=t.k1))
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "commit suicide should fail from non-whitelisted address"
    test_init()
    test_depositEther()
    test_withdrawEther()
    test_transfer()
    test_transferFrom()
    test_approve()
    test_commitSuicide()

if __name__ == '__main__':
    src = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'src')
    contracts = ContractLoader(src, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'], '', 0)
    # contracts.recompile('cash')
    state = contracts.state
    t = contracts._ContractLoader__tester
    test_cash(contracts.cash, state, t)
