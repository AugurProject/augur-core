#!/usr/bin/env python

from __future__ import division
import os
import sys
import json
import iocapture
import ethereum.tester
import utils

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir)
src = os.path.join(ROOT, "src")

WEI_TO_ETH = 10**18
TWO = 2*WEI_TO_ETH
HALF = WEI_TO_ETH/2

def test_consensusData(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
    c = contracts.consensusData
    branch1 = 1010101
    period1 = contracts.branches.getVotePeriod(branch1)
    event1 = 1234
    address2 = long(t.a2.encode("hex"), 16)
    cashAddr = long(contracts.cash.address.encode("hex"), 16)

    def test_baseReporting():
        assert(c.getBaseReportersLastPeriod(branch1) == 6), "default should be 6"
        assert(c.setBaseReportersLastPeriod(branch1, 10) == 1), "Didn't successfully execute setBaseReportersLastPeriod"
        assert(c.getBaseReportersLastPeriod(branch1) == 10), "baseReportersLastPeriod should be 10 at this point"
        assert(c.setBaseReportersLastPeriod(branch1, 6) == 1), "setBaseReportersLastPeriod wasn't executed successfully"
        assert(c.getBaseReportersLastPeriod(branch1) == 6), "baseReportersLastPeriod should be 6 at this point"

    def test_slashed():
        assert(c.getSlashed(branch1, period1, address2) == 0), "slashed should be 0 by default"
        assert(c.setSlashed(branch1, period1, address2) == 1), "setSlashed wasn't executed successfully"
        assert(c.getSlashed(branch1, period1, address2) == 1), "slashed Should be 1 at this point"

    def test_feeFirst():
        assert(c.getFeeFirst(branch1, period1) == 0), "feeFirst should be 0 by default"
        assert(c.setFeeFirst(branch1, period1, 100) == 1), "setFeeFirst wasn't executed successfully"
        assert(c.getFeeFirst(branch1, period1) == 100), "feeFirst should be set to 100 at this point"
        assert(c.setFeeFirst(branch1, period1, 0) == 1), "setFeeFirst wasn't executed successfully"
        assert(c.getFeeFirst(branch1, period1) == 0), "feeFirst should be 0 at this point"

    def test_periodBalance():
        assert(c.getPeriodBalance(branch1, period1) == 0), "periodBalance should be 0 by default"
        assert(c.setPeriodBalance(branch1, period1, 100) == 1), "setPeriodBalance wasn't executed successfully"
        assert(c.getPeriodBalance(branch1, period1) == 100), "periodBalance should be set to 100"
        assert(c.setPeriodBalance(branch1, period1, 0) == 1), "setPeriodBalance wasn't executed successfully"
        assert(c.getPeriodBalance(branch1, period1) == 0), "periodBalance should be 0 at this point"

    def test_denominator():
        assert(c.getDenominator(branch1, period1) == 0), "denominator should be 0 by default"
        assert(c.increaseDenominator(branch1, period1, 200) == 1), "increaseDenominator wasn't executed successfully"
        assert(c.getDenominator(branch1, period1) == 200), "denominator should be 200 at this point"
        assert(c.decreaseDenominator(branch1, period1, 200) == 1), "decreaseDenominator wasn't executed successfully"
        assert(c.getDenominator(branch1, period1) == 0), "denominator should be 0 at this point"

    def test_collections():
        # $currency Fees
        assert(c.getFeesCollected(branch1, address2, period1, cashAddr) == 0), "feesCollected for cash should be set to 0 by default"
        assert(c.setFeesCollected(branch1, address2, period1, cashAddr) == 1), "setFeesCollected wasn't executed successfully"
        assert(c.getFeesCollected(branch1, address2, period1, cashAddr) == 1), "feesCollected for cash should be set to 1"
        # REP
        assert(c.getRepCollected(branch1, address2, period1) == 0), "repCollected should be set to 0 by default"
        assert(c.setRepCollected(branch1, address2, period1) == 1), "setRepCollected wasn't executed successfully"
        assert(c.getRepCollected(branch1, address2, period1) == 1), "repCollected should be set to 1"

    def test_penalization():
        assert(c.getPenalized(branch1, period1, address2, event1) == 0), "penalized should be set to 0 by default"
        assert(c.setPenalized(branch1, period1, address2, event1) == 1), "setPenalized wasn't executed successfully"
        assert(c.getPenalized(branch1, period1, address2, event1) == 1), "penalized should be set to 1"

        assert(c.getPenalizedNum(branch1, period1, address2) == 0), "penalizedNum should be 0 by default"
        assert(c.increasePenalizedNum(branch1, period1, address2, 1) == 1), "increasePenalizedNum wasn't executed successfully"
        assert(c.getPenalizedNum(branch1, period1, address2) == 1), "penalizedNum should be 1"

        assert(c.getPenalizedUpTo(branch1, address2) == 0), "penalizedUpTo should be set to 0 by default"
        assert(c.setPenalizedUpTo(branch1, address2, (period1 - 5)) == 1), "setPenalizedUpTo wasn't executed successfully"
        assert(c.getPenalizedUpTo(branch1, address2) == (period1 - 5)), "penalizedUpTo wasn't set to the expected period"
        assert(c.getRepRedistributionDone(branch1, address2) == 0), "repRedistributionDone should return 0 when we aren't caught up to the branch votePeriod"
        assert(c.setPenalizedUpTo(branch1, address2, (period1 - 1)) == 1), "setPenalizedUpTo wasn't executed successfully"
        assert(c.getPenalizedUpTo(branch1, address2) == (period1 - 1)), "penalizedUpTo isn't the votePeriod - 1 as expected"
        assert(c.getRepRedistributionDone(branch1, address2) == 1), "getRepRedistributionDone should return 1 when we are caught up to the branch votePeriod"

        assert(c.getNotEnoughPenalized(branch1, address2, period1) == 0), "notEnoughReportsPenalized should be set to 0 by default"
        assert(c.setNotEnoughPenalized(branch1, address2, period1) == 1), "setNotEnoughPenalized wasn't executed successfully"
        assert(c.getNotEnoughPenalized(branch1, address2, period1) == 1), "notEnoughReportsPenalized should be set to 1"

    def test_assertZeroValue():
        # first get the starting balance for account 0 and account 2
        acc0Bal = s.block.get_balance(t.a0)
        acc2Bal = s.block.get_balance(t.a2)

        assert(c.setRefund(t.a0, 100, value=100, sender=t.k0) == 1), "setRefund wasn't executed successfully"
        assert(s.block.get_balance(t.a0) == acc0Bal - 100), "account 0 balance should have reduced by 100 from the original balance"
        assert(c.doRefund(t.a2, t.a0) == 1), "doRefund wasn't executed successfully"
        assert(s.block.get_balance(t.a2) == acc2Bal + 100), "account 2 should have had it's balance increase by 100 from the original balance"
        # confirm that if we try to refund again it should fail due to lack of funds...
        try:
            raise Exception(c.doRefund(t.a2, t.a0))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "doRefund should fail if there aren't enough funds to send"

    test_baseReporting()
    test_slashed()
    test_feeFirst()
    test_periodBalance()
    test_denominator()
    test_collections()
    test_penalization()
    test_assertZeroValue()

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_consensusData(contracts)
