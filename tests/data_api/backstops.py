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

def test_backstops(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
    c = contracts.backstops
    event1 = 1234
    event2 = 5678
    branch1 = 1010101
    branch2 = 2020202
    period1 = 1000
    period2 = 2000
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)

    def test_disputedOverEthics():
        assert(c.getDisputedOverEthics(event1) == 0), "disputedOverEthics isn't defaulted to 0"
        assert(c.setDisputedOverEthics(event1) == 1), "setDisputedOverEthics wasn't executed successfully"
        assert(c.getDisputedOverEthics(event1) == 1), "setDisputedOverEthics didn't set event properly"
        # try:
        #     assert(c.getDisputedOverEthics(event2) == 0), "disputedOverEthics isn't defaulted to 0"
        #     raise Exception(c.setDisputedOverEthics(event2, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setDisputedOverEthics should throw if msg.sender isn't whitelisted"
        #     assert(c.getDisputedOverEthics(event2) == 0), "disputedOverEthics was modified when it shouldn't have been"

    def test_forkBondPoster():
        assert(c.getForkBondPoster(event1) == 0), "forkBondPoster isn't defaulted to 0"
        assert(c.setForkBondPoster(event1, t.a1) == 1), "Didn't set forkBondPoster correctly"
        assert(c.getForkBondPoster(event1) == address1), "Didn't set the forkBondPoster to the expected address"
        # try:
        #     raise Exception(c.setForkBondPoster(event1, t.a2, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setForkBondPoster should throw if msg.sender isn't whitelisted"
        #     assert(c.getForkBondPoster(event1) == address1), "forkBondPoster was modified when it shouldn't have been"

    def test_forkedOverEthicality():
        assert(c.getForkedOverEthicality(event1) == 0), "forkedOverEthicality isn't defaulted to 0"
        assert(c.setForkedOverEthicality(event1) == 1), "setForkedOverEthicality isn't returning 1 as expected when msg.sender is whitelisted"
        assert(c.getForkedOverEthicality(event1) == 1), "forkedOverEthicality wasn't set correctly"
        # try:
        #     assert(c.getForkedOverEthicality(event2) == 0), "forkedOverEthicality isn't defaulted to 0"
        #     raise Exception(c.setForkedOverEthicality(event2, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setForkedOverEthicality should throw if msg.sender isn't whitelisted"
        #     assert(c.getForkedOverEthicality(event2) == 0), "forkedOverEthicality was modified when it shouldn't have been"

    def test_forkBondPaid():
        assert(c.getForkBondPaid(event1) == 0), "getForkBondPaid isn't defaulted to 0"
        assert(c.adjForkBondPaid(event1, 100) == 1), "adjForkBondPaid isn't successfully being called"
        assert(c.getForkBondPaid(event1) == 100), "getForkBondPaid wasn't adjusted correctly"
        # try:
        #     raise Exception(c.adjForkBondPaid(event1, 50, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setForkedOverEthicality should throw if msg.sender isn't whitelisted"
        #     assert(c.getForkBondPaid(event1) == 100), "ForkBondPaid was modified when it shouldn't have been"

    def test_bondAmount():
        assert(c.getBondAmount(event1) == 0), "bondAmount isn't defaulted to 0"
        assert(c.setBondAmount(event1, 100) == 1), "setBondAmount isn't successfully being called"
        assert(c.getBondAmount(event1) == 100), "bondAmount isn't being set properly"
        # try:
        #     raise Exception(c.setBondAmount(event1, 50, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setBondAmount should throw if msg.sender isn't whitelisted"
        #     assert(c.getBondAmount(event1) == 100), "bondAmount was modified when it shouldn't have been"

    def test_originalBranch():
        assert(c.getOriginalBranch(event1) == 0), "originalBranch not defaulted to 0"
        assert(c.setOriginalBranch(event1, branch1) == 1), "setOriginalBranch isn't successfully being called"
        assert(c.getOriginalBranch(event1) == branch1), "originalBranch isn't being set properly"
        # try:
        #     raise Exception(c.setOriginalBranch(event1, branch2, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setOriginalBranch should throw if msg.sender isn't whitelisted"
        #     assert(c.getOriginalBranch(event1) == branch1), "originalBranch was modifed when it shouldn't have been"

    def test_moved():
        assert(c.getMoved(event1) == 0), "moved not defaulted to 0"
        assert(c.setMoved(event1) == 1), "setMoved isn't successfully being called"
        assert(c.getMoved(event1) == 1), "moved isn't being set properly"
        # try:
        #     assert(c.getMoved(event2) == 0), "moved not defaulted to 0"
        #     raise Exception(c.setMoved(event2, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setMoved should throw if msg.sender isn't whitelisted"
        #     assert(c.getMoved(event2) == 0), "moved was modifed when it shouldn't have been"

    def test_resolved():
        assert(c.getResolved(branch1, period1) == 0), "resolved not defaulted to 0"
        assert(c.setResolved(branch1, period1, 100) == 1), "setResolved isn't successfully being called"
        assert(c.getResolved(branch1, period1) == 100), "resolved isn't being set properly"
        # try:
        #     assert(c.getResolved(branch2, period2) == 0), "resolved not defaulted to 0"
        #     raise Exception(c.setResolved(branch2, period2, 250, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setResolved should throw if msg.sender isn't whitelisted"
        #     assert(c.getResolved(branch2, period2) == 0), "resolved was modifed when it shouldn't have been"

    def test_round2BondPaid():
        assert(c.getBondPaid(event1) == 0), "roundTwo bondPaid not defaulted to 0"
        assert(c.increaseBondPaid(event1, 100) == 1), "increaseBondPaid isn't successfully being called"
        assert(c.getBondPaid(event1) == 100), "roundTwo bondPaid isn't being set properly"
        # try:
        #     raise Exception(c.increaseBondPaid(event1, -200))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "increaseBondPaid should throw if the amount to increase is negative"
        # try:
        #     assert(c.getBondPaid(event2) == 0), "roundTwo bondPaid not defaulted to 0"
        #     raise Exception(c.increaseBondPaid(event2, 250, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "increaseBondPaid should throw if msg.sender isn't whitelisted"
        #     assert(c.getBondPaid(event2) == 0), "roundTwo bondPaid was modifed when it shouldn't have been"

    def test_round2BondPoster():
        assert(c.getBondPoster(event1) == 0), "roundTwo bondPoster not defaulted to 0"
        assert(c.setBondPoster(event1, t.a1) == 1), "setBondPoster not successfully being called"
        assert(c.getBondPoster(event1) == address1), "roundTwo bondPoster not being set correctly"
        # try:
        #     assert(c.getBondPoster(event2) == 0), "roundTwo bondPoster not defaulted to 0"
        #     raise Exception(c.setBondPoster(event2, t.a2, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setBondPoster should throw if msg.sender isn't whitelisted"
        #     assert(c.getBondPoster(event2) == 0), "roundTwo bondPoster was modifed when it shouldn't have been"

    def test_final():
        assert(c.getFinal(event1) == 0), "final not defaulted to 0"
        assert(c.setFinal(event1) == 1), "setFinal not successfully being called"
        assert(c.getFinal(event1) == 1), "final not being set correctly"
        # try:
        #     assert(c.getFinal(event2) == 0), "final not defaulted to 0"
        #     raise Exception(c.setFinal(event2, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setFinal should throw if msg.sender isn't whitelisted"
        #     assert(c.getFinal(event2) == 0), "final was modifed when it shouldn't have been"

    def test_originalOutcome():
        assert(c.getOriginalOutcome(event1) == 0), "originalOutcome not defaulted to 0"
        assert(c.setOriginalOutcome(event1, 1) == 1), "setOriginalOutcome not successfully being called"
        assert(c.getOriginalOutcome(event1) == 1), "originalOutcome not being set correctly"
        # try:
        #     assert(c.getOriginalOutcome(event2) == 0), "originalOutcome not defaulted to 0"
        #     raise Exception(c.setOriginalOutcome(event2, 1, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setOriginalOutcome should throw if msg.sender isn't whitelisted"
        #     assert(c.getOriginalOutcome(event2) == 0), "originalOutcome was modifed when it shouldn't have been"

    def test_originalEthicality():
        assert(c.getOriginalEthicality(event1) == 0), "originalEthicality not defaulted to 0"
        assert(c.setOriginalEthicality(event1, 1) == 1), "setOriginalEthicality not successfully being called"
        assert(c.getOriginalEthicality(event1) == 1), "originalEthicality not being set correctly"
        # try:
        #     assert(c.getOriginalEthicality(event2) == 0), "originalEthicality not defaulted to 0"
        #     raise Exception(c.setOriginalEthicality(event2, 1, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setOriginalEthicality should throw if msg.sender isn't whitelisted"
        #     assert(c.getOriginalEthicality(event2) == 0), "originalEthicality was modifed when it shouldn't have been"

    def test_originalVotePeriod():
        assert(c.getOriginalVotePeriod(event1) == 0), "originalVotePeriod not defaulted to 0"
        assert(c.setOriginalVotePeriod(event1, period1) == 1), "setOriginalVotePeriod not successfully being called"
        assert(c.getOriginalVotePeriod(event1) == period1), "originalVotePeriod not being set correctly"
        # try:
        #     assert(c.getOriginalVotePeriod(event2) == 0), "originalVotePeriod not defaulted to 0"
        #     raise Exception(c.setOriginalVotePeriod(event2, period2, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setOriginalVotePeriod should throw if msg.sender isn't whitelisted"
        #     assert(c.getOriginalVotePeriod(event2) == 0), "originalVotePeriod was modifed when it shouldn't have been"

    def test_bondReturned():
        assert(c.getBondReturned(event1) == 0), "bondReturned not defaulted to 0"
        assert(c.setBondReturned(event1) == 1), "setBondReturned not successfully being called"
        assert(c.getBondReturned(event1) == 1), "bondReturned not being set correctly"
        # try:
        #     assert(c.getBondReturned(event2) == 0), "bondReturned not defaulted to 0"
        #     raise Exception(c.setBondReturned(event2, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setBondReturned should throw if msg.sender isn't whitelisted"
        #     assert(c.getBondReturned(event2) == 0), "bondReturned was modifed when it shouldn't have been"

    def test_roundTwo():
        assert(c.getRoundTwo(event1) == 0), "roundTwo not defaulted to 0"
        assert(c.setRoundTwo(event1, 1) == 1), "setRoundTwo not successfully being called"
        assert(c.getRoundTwo(event1) == 1), "roundTwo not being set correctly"
        # try:
        #     assert(c.getRoundTwo(event2) == 0), "roundTwo not defaulted to 0"
        #     raise Exception(c.setRoundTwo(event2, 1, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setRoundTwo should throw if msg.sender isn't whitelisted"
        #     assert(c.getRoundTwo(event2) == 0), "roundTwo was modifed when it shouldn't have been"

    def test_roundTwoRefund():
        assert(c.setRoundTwoRefund(event1, 10) == 1), "setRoundTwoRefund not being successfully called"
        # try:
        #     raise Exception(c.doRoundTwoRefund(t.a1, event1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "doRefund didn't throw when event had no funds to send"

    # def test_misc():
        # try:
        #     raise Exception(c.setController(t.a2, sender=t.k2))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "setController didn't throw when a non-controller sender attempted to set a new controller"
        # try:
        #     raise Exception(c.suicideFunds(t.a2, sender=t.k2))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "suicideFunds didn't throw when a non-controller sender attempted to set a new controller"

    test_disputedOverEthics()
    test_forkBondPoster()
    test_forkedOverEthicality()
    test_forkBondPaid()
    test_bondAmount()
    test_originalBranch()
    test_moved()
    test_resolved()
    test_round2BondPaid()
    test_round2BondPoster()
    test_final()
    test_originalOutcome()
    test_originalEthicality()
    test_originalVotePeriod()
    test_bondReturned()
    test_roundTwo()
    test_roundTwoRefund()
    # test_misc()

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_backstops(contracts)
