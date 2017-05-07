#!/usr/bin/env python

from __future__ import division
from ethereum import tester as t
import math
import random
import os
import sys
import time
import binascii
from pprint import pprint

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))

from upload_contracts import ContractLoader

ONE = 10**18
TWO = 2*ONE
HALF = ONE/2

def test_backstops(contracts, s, t):
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
        c.setDisputedOverEthics(event1)
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
    print("data_api/backstops.se unit tests completed")

def test_branches(contracts, s, t):
    c = contracts.branches
    branch1 = 1010101
    branch2 = 2020202
    period1 = c.getVotePeriod(branch1)
    period2 = period1 + 1
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    repAddr = long(contracts.repContract.address.encode("hex"), 16)
    rate = 1000000000000000000

    def test_defaults():
        assert(c.getNumBranches() == 1), "should only be 1 branch"
        assert(c.getBranchByNum(0) == branch1), "branch at index 0 should be the default branch"
        assert(c.getBranches() == [branch1]), "Expected an array with only the default branch returned"
        assert(c.getBranchesStartingAt(0) == [branch1]), "Expected an array with only the default branch returned"
        assert(c.getNumMarketsBranch(branch1) == 0), "there should be 0 markets on the branch"
        assert(c.getMarketIDsInBranch(branch1, 0, 5) == [0, 0, 0, 0, 0]), "Markets returned when there should be no markets on the branch"
        assert(c.getCreationDate(branch1) == s.block.timestamp), "creationDate not the expected timestamp"
        assert(c.getBaseReporters(branch1) == 6), "baseReporters should be 6"
        assert(c.getMinTradingFee(branch1) == 200000000000000000), "minTradeFees should be .2%"
        assert(c.getVotePeriod(branch1) == round((s.block.timestamp / 15) - 1)), "Voteperiod wasn't the expected period"
        assert(c.getPeriodLength(branch1) == 15), "period length should be 15"
        assert(c.getForkPeriod(branch1) == 0), "ForkPeriod should be 0"
        assert(c.getEventForkedOver(branch1) == 0), "eventForkedOver should be 0"
        assert(c.getNumCurrencies(branch1) == 1), "should be only 1 currency on the first branch"
        assert(c.getBranchCurrency(branch1, 0) != 0), "branch currency shouldn't be set to 0"
        cashCurrency = c.getBranchCurrency(branch1, 0)
        assert(c.getCurrencyActive(branch1, cashCurrency) == 1), "cash contract wasn't active by default"
        assert(c.getCurrencyByContract(branch1, cashCurrency) == 0), "cash contract wasn't the first currency on the branch"
        assert(c.getCurrencyRate(branch1, cashCurrency) == rate), "cash exchange rate should be 1"
        assert(c.getInitialBalance(branch1, c.getVotePeriod(branch1), cashCurrency) == 0), "the initial balance should be 0"
        assert(c.getBranchWallet(branch1, cashCurrency) != 0), "A wallet wasn't defined for cash currency"
        assert(c.getParent(branch1) == 0), "default branch parent should be set to 0"
        assert(c.getMostRecentChild(branch1) == 0), "default most recent child for default branch should be 0"
        assert(c.getParentPeriod(branch1) == 0), "parentPeriod of default branch should be 0"

    def test_currency():
        # adjust the number of currencies, then adjust it back
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getNumCurrencies(branch1) == 1), "numCurrencies should be 1 at this point"
        #     raise Exception(c.updateNumCurrencies(branch1, 3, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "updateNumCurrencies should throw if msg.sender isn't whitelisted"
        #     assert(c.getNumCurrencies(branch1) == 1), "numCurrencies was modified when it shouldn't have been"
        # now with whitelist
        assert(c.getNumCurrencies(branch1) == 1), "numCurrenceies should be 1 at this point"
        assert(c.updateNumCurrencies(branch1, 5) == 1), "updateNumCurrencies wasn't called successfully"
        assert(c.getNumCurrencies(branch1) == 5), "numCurrencies should be 5 at this point"
        assert(c.updateNumCurrencies(branch1, 1) == 1), "updateNumCurrencies wasn't called successfully"
        assert(c.getNumCurrencies(branch1) == 1), "numCurrenceies should be 1 at this point"
        # add a currency
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getNumCurrencies(branch1) == 1), "numCurrencies should be 1 at this point"
        #     raise Exception(c.addCurrency(branch1, repAddr, rate, 0, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "addCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getNumCurrencies(branch1) == 1), "numCurrencies was modified when it shouldn't have been"
        # now with whitelist
        assert(c.addCurrency(branch1, repAddr, rate, 0) == 1), "addCurreny wasn't successfully executed"
        assert(c.getNumCurrencies(branch1) == 2), "numCurrenceies should be 2 at this point"
        assert(c.getBranchWallet(branch1, repAddr) != 0), "There should be a wallet defined for the new currency"
        assert(c.getCurrencyByContract(branch1, repAddr) == 1), "the new currency should be indexed at the 1 position"
        assert(c.getCurrencyRate(branch1, repAddr) == rate), "the new currency should have returned the expected rate"
        # disable and reactivate currency
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getCurrencyActive(branch1, repAddr) == 1), "REP currency should be active at this point"
        #     raise Exception(c.disableCurrency(branch1, repAddr, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "disableCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getCurrencyActive(branch1, repAddr) == 1), "REP currency should be active still"
        # now with whitelist
        assert(c.getCurrencyActive(branch1, repAddr) == 1), "the new currency should be active"
        assert(c.disableCurrency(branch1, repAddr) == 1), "disableCurrency wasn't successfully executed"
        assert(c.getCurrencyActive(branch1, repAddr) == 0), "the new currency should be inactive"
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getCurrencyActive(branch1, repAddr) == 0), "REP currency should be inactive at this point"
        #     raise Exception(c.reactivateCurrency(branch1, repAddr, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "reactivateCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getCurrencyActive(branch1, repAddr) == 0), "REP currency should be inactive still"
        # now with whitelist
        assert(c.reactivateCurrency(branch1, repAddr) == 1), "reactivateCurrency wasn't called successfully"
        assert(c.getCurrencyActive(branch1, repAddr) == 1), "the new currency should be active again"
        # modify a currencyRate
        assert(c.getCurrencyRate(branch1, repAddr) == rate), "the new currency's rate should be the rate it was added at"
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getCurrencyRate(branch1, repAddr) == rate), "REP currency should have a rate of 1"
        #     raise Exception(c.updateCurrencyRate(branch1, repAddr, (rate + 1), 0, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "updateCurrencyRate should throw if msg.sender isn't whitelisted"
        #     assert(c.getCurrencyRate(branch1, repAddr) == rate), "REP currency should still have a rate of 1"
        # now with whitelist
        assert(c.updateCurrencyRate(branch1, repAddr, (rate + 1), 0) == 1), "updateCurrencyRate wasn't executed successfully"
        assert(c.getCurrencyRate(branch1, repAddr) == (rate + 1)), "New currency's rate wasn't it's previous rate + 1 as it should be at this point"
        # replace currency
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getCurrencyRate(branch1, repAddr) == (rate + 1)), "REP currency should have a modified rate"
        #     raise Exception(c.replaceCurrency(branch1, 1, repAddr, rate, 0, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "replaceCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getCurrencyRate(branch1, repAddr) == (rate + 1)), "REP currency should still have a modified rate"
        # now with whitelist
        assert(c.replaceCurrency(branch1, 1, repAddr, rate, 0) == 1), "replaceCurrency wasn't executed successfully"
        assert(c.getCurrencyRate(branch1, repAddr) == rate), "the new currency's rate should be it's original rate again"
        assert(c.getNumCurrencies(branch1) == 2), "numCurrencies should be 2 at this point"
        # remove last currency
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getBranchCurrency(branch1, 1) == repAddr), "REP currency should still be defined"
        #     raise Exception(c.removeLastCurrency(branch1, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "removeLastCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getBranchCurrency(branch1, 1) == repAddr), "REP currency should still be defined"
        # now with whitelist
        assert(c.getBranchCurrency(branch1, 1) == repAddr), "branch currency at position 1 should be the new currency"
        assert(c.getCurrencyRate(branch1, repAddr) == rate), "the rate for the new currency should be the original rate"
        assert(c.removeLastCurrency(branch1) == 1), "removeLastCurrency wasn't executed successfully"
        assert(c.getNumCurrencies(branch1) == 1), "numCurrencies should be 1 at this point"
        assert(c.getCurrencyByContract(branch1, repAddr) == 0), "the new currency should have been removed"
        assert(c.getBranchWallet(branch1, repAddr) == 0), "The new currency's wallet shouldn't be defined"
        assert(c.getBranchCurrency(branch1, 1) == 0), "branch currency at position 1 should be empty"
        assert(c.getCurrencyRate(branch1, repAddr) == 0), "new Currency Rate should return 0 since new currency should be removed at this point"

    def test_branching():
        # test branch addition and confirm expected state
        cashAddr = long(contracts.cash.address.encode("hex"), 16)
        assert(c.getNumBranches() == 1), "numBranches should be 1"
        assert(c.getBranches() == [branch1]), "getBranches should return only 1 branch"
        assert(c.initializeBranch(branch2, period2, 15, 200000000000000000, period1, branch1, cashAddr, 0) == 1), "initializeBranch wasn't executed successfully"
        assert(c.getNumBranches() == 2), "numBranches should be 2"
        assert(c.getBranches() == [branch1, branch2]), "getBranches should return 2 branches"
        assert(c.getParent(branch2) == branch1), "new branch parent should be the original branch"
        assert(c.getParentPeriod(branch2) == period1), "parentPeriod should be original branch's period"
        assert(c.getVotePeriod(branch2) == period2), "branch 2 didn't return the execpted votePeriod"
        assert(c.incrementPeriod(branch2) == 1), "incrementPeriod wasn't executed successfully"
        assert(c.getVotePeriod(branch2) == (period2 + 1)), "branch 2 should have it's period incremented by 1"

    def test_edits():
        # test modifying the branches in various ways
        assert(c.getNumMarketsBranch(branch1) == 0), "numMarkets should be 0"
        assert(c.getMarketIDsInBranch(branch1, 0, 5) == [0, 0, 0, 0, 0]), "getting the first 5 markets in branch 1 should return an array of 0s"
        assert(c.addMarketToBranch(branch1, 10987) == 1), "addMarketToBranch wasn't executed successfully"
        assert(c.getNumMarketsBranch(branch1) == 1), "numMarkets should be 1"
        assert(c.getMarketIDsInBranch(branch1, 0, 5) == [10987, 0, 0, 0, 0]), "getting the first 5 markets in branch 1 should return an array with 1 market set and 4 empty markets"
        # set forkperiod
        assert(c.getForkPeriod(branch1) == 0), "forkPeriod for branch 1 should be 0"
        assert(c.getForkTime(branch1) == 0), "forkTime for branch 1 should be 0"
        assert(c.setForkPeriod(branch1) == 1), "setForkPeriod wasn't executed successfully"
        assert(c.getForkPeriod(branch1) == c.getVotePeriod(branch1)), "branch 1 should have it's forkPeriod set to it's vote Period"
        assert(c.getForkTime(branch1) == s.block.timestamp), "branch 1 should have it's forkTime set to block.timestamp"
        # most recent child
        assert(c.getMostRecentChild(branch2) == 0), "branch 2 most recent child should be 0"
        assert(c.setMostRecentChild(branch2, 1) == 1), "setMostRecentChild wasn't executed successfully"
        assert(c.getMostRecentChild(branch2) == 1), "branch 2 should have a most recent child set to 1 at this point"

    test_defaults()
    test_currency()
    test_branching()
    test_edits()
    print("data_api/branches.se unit tests completed")

def test_consensusData(contracts, s, t):
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

    # TODO: setRefund - doRefund
    test_baseReporting()
    test_slashed()
    test_feeFirst()
    test_periodBalance()
    test_denominator()
    test_collections()
    test_penalization()
    print("data_api/consensusData.se unit tests completed")

def test_events(contracts, s, t):
    c = contracts.events
    event1 = 1234
    branch1 = 1010101
    branch2 = 2020202
    period1 = contracts.branches.getVotePeriod(branch1)
    expirationDate1 = (s.block.timestamp + 10)
    expirationDate2 = (s.block.timestamp + 20)
    address2 = long(t.a2.encode("hex"), 16)
    address3 = long(t.a3.encode("hex"), 16)
    address4 = long(t.a4.encode("hex"), 16)
    market1 = 56789
    ONE = 1000000000000000000
    TWO = 2000000000000000000
    PointTwo = 200000000000000000

    def test_initializeEvent():
        assert(c.getEventInfo(event1) == [0, 0, 0, 0, 0, 0, 0, 0]), "event1 shouldn't exist yet, should return an array of 0's"
        assert(c.initializeEvent(event1, branch1, expirationDate1, ONE, TWO, 2, "https://someresolution.eth", address2, address3, address4) == 1), "initializeEvent wasn't executed successfully"
        assert(c.getEventInfo(event1) == [branch1, expirationDate1, 0, ONE, TWO, 2, 0, address2]), "eventInfo wasn't set to the expected values for event1"
        assert(c.getForkResolveAddress(event1) == address4), "forkResolveAddress wasn't the expected address"
        assert(c.getResolveBondPoster(event1) == address3), "resolveBondPoster wasn't the expected address"
        assert(c.getResolutionAddress(event1) == address2), "resolutionAddress wasn't the expected address"
        assert(c.getEventResolution(event1) == 'https://someresolution.eth'), "eventResolution wasn't the expected string"
        assert(c.getResolutionLength(event1) == len('https://someresolution.eth')), "resolutionLength wasn't correctly set to 26"
        assert(c.getMinValue(event1) == ONE), "minValue wasn't set to ONE as expected"
        assert(c.getMaxValue(event1) == TWO), "maxValue wasn't set to TWO as expected"
        assert(c.getNumOutcomes(event1) == 2), "numOutcomes should be 2"

    def test_eventBranch():
        assert(c.getEventBranch(event1) == branch1), "event1 should be in branch1"
        assert(c.setBranch(event1, branch2) == 1), "setBranch wasn't executed successfully"
        assert(c.getEventBranch(event1) == branch2), "event1 should be in branch2 at this point"
        assert(c.setBranch(event1, branch1) == 1), "setBranch wasn't executed successfully"
        assert(c.getEventBranch(event1) == branch1), "event1 should be back in branch1 at this point"

    def test_creationTime():
        assert(c.getCreationTime(event1) == s.block.timestamp), "creationTime wasn't defaulted to block.timestamp"
        assert(c.setCreationTime(event1) == 1), "setCreationTime wasn't executed successfully"
        assert(c.getCreationTime(event1) == s.block.timestamp), "creationTime should be set to block.timestamp after calling setCreationTime"

    def test_challenged():
        assert(c.getChallenged(event1) == 0), "challenged should be 0 for event1 by default"
        assert(c.setChallenged(event1) == 1), "setChallenged wasn't executed successfully"
        assert(c.getChallenged(event1) == 1), "challenged should be set to 1"

    def test_outcomes():
        assert(c.getOutcome(event1) == 0), "outcome should be defaulted to 0"
        assert(c.getFirstPreliminaryOutcome(event1) == 0), "firstPreliminaryOutcome should be defaulted to 0"
        assert(c.getUncaughtOutcome(event1) == 0), "uncaughtOutcome should be defaulted to 0"

        assert(c.setOutcome(event1, ONE) == 1), "setOutcome wasn't executed successfully"
        assert(c.setFirstPreliminaryOutcome(event1, ONE) == 1), "setFirstPreliminaryOutcome wasn't executed successfully"
        assert(c.setUncaughtOutcome(event1, ONE) == 1), "setUncaughtOutcome wasn't executed successfully"

        assert(c.getOutcome(event1) == ONE), "outcome should be set to ONE"
        assert(c.getFirstPreliminaryOutcome(event1) == ONE), "firstPreliminaryOutcome should be set to ONE"
        assert(c.getUncaughtOutcome(event1) == ONE), "uncaughtOutcome should be set to ONE"

    def test_past24():
        assert(c.getPast24(period1) == 0), "past24 should be defaulted to 0"
        assert(c.addPast24(period1) == 1), "addPast24 wasn't executed successfully"
        assert(c.getPast24(period1) == 1), "past24 should now equal 1"
        assert(c.addPast24(period1) == 1), "addPast24 wasn't executed successfully"
        assert(c.getPast24(period1) == 2), "past24 should now equal 2"

    def test_expiration():
        assert(c.getExpiration(event1) == expirationDate1), "expiration should be defaulted to expirationDate1 (passed in initializeEvent earlier in tests)"
        assert(c.getOriginalExpiration(event1) == expirationDate1), "originalExpiration should be defaulted to expirationDate1 (passed in initializeEvent earlier in tests)"
        assert(c.setExpiration(event1, expirationDate2) == 1), "setExpiration wasn't executed successfully"
        assert(c.getExpiration(event1) == expirationDate2), "expiration should now be set to expirationDate2"
        assert(c.setOriginalExpiration(event1, expirationDate2) == 1), "setOriginalExpiration wasn't executed successfully"
        assert(c.getOriginalExpiration(event1) == expirationDate2), "originalExpiration should now be set to expirationDate2"
        assert(c.setOriginalExpiration(event1, expirationDate1) == 1), "setOriginalExpiration wasn't executed successfully"
        assert(c.getOriginalExpiration(event1) == expirationDate1), "originalExpiration should once again be set to expirationDate1"

    def test_ethics():
        assert(c.getEthics(event1) == 0), "ethics should be defaulted to 0"
        assert(c.setEthics(event1, ONE) == ONE), "setEthics wasn't executed successfully"
        assert(c.getEthics(event1) == ONE), "ethics should be set to ONE"

    def test_bonds():
        # check defaults are 0
        assert(c.getBond(event1) == 0), "bond should be defaulted to 0"
        assert(c.getEarlyResolutionBond(event1) == 0), "earlyResolutionBond should be defaulted to 0"
        assert(c.getExtraBond(event1) == 0), "extraBond should be defaulted to 0"
        assert(c.getExtraBondPoster(event1) == 0), "extraBondPoster should be defaulted to 0"
        # check all can be set successfully
        assert(c.setBond(event1, 1000) == 1), "setBond wasn't executed successfully"
        assert(c.setEarlyResolutionBond(event1, 3000) == 1), "setEarlyResolutionBond wasn't executed successfully"
        assert(c.setExtraBond(event1, 5000) == 1), "setExtraBond wasn't executed successfully"
        assert(c.setExtraBondPoster(event1, address4) == 1), "setExtraBondPoster wasn't executed successfully"
        # check updates
        assert(c.getBond(event1) == 1000), "bond should be set to 1000"
        assert(c.getEarlyResolutionBond(event1) == 3000), "earlyResolutionBond should be set to 3000"
        assert(c.getExtraBond(event1) == 5000), "extraBond should be set to 5000"
        assert(c.getExtraBondPoster(event1) == address4), "extraBondPoster wasn't set to the expected address"

    def test_pushing():
        assert(c.getEventPushedUp(event1) == 0), "pushedUp should be defaulted to 0"
        assert(c.setEventPushedUp(event1, 100) == 1), "setEventPushedUp wasn't executed successfully"
        assert(c.getEventPushedUp(event1) == 100), "pushedUp should be set to 100"

    def test_forking():
        # check defaults are 0
        assert(c.getForked(event1) == 0), "forked should be defaulted to 0"
        assert(c.getForkEthicality(event1) == 0), "forkEthicality should be defaulted to 0"
        assert(c.getForkOutcome(event1) == 0), "forkOutcome should be defaulted to 0"
        assert(c.getForkedDone(event1) == 0), "forkDone should be defaulted to 0"
        # check all can be successfully set
        assert(c.setForked(event1) == 1), "setForked wasn't executed successfully"
        assert(c.setForkEthicality(event1, ONE) == 1), "setForkEthicality wasn't executed successfully"
        assert(c.setForkOutcome(event1, TWO) == 1), "setForkOutcome wasn't executed successfully"
        assert(c.setForkDone(event1) == 1), "setForkDone wasn't executed successfully"
        # check updated values
        assert(c.getForked(event1) == 1), "forked should be set to 1"
        assert(c.getForkEthicality(event1) == ONE), "forkEthicality should be set to ONE"
        assert(c.getForkOutcome(event1) == TWO), "forkOutcome should be set to TWO"
        assert(c.getForkedDone(event1) == 1), "forkDone should be set to 1"

    def test_markets():
        assert(c.getMarkets(event1) == []), "Should have an empty array of markets by default"
        assert(c.getMarket(event1, 0) == 0), "should have no market at position 0 by default"
        assert(c.getNumMarkets(event1) == 0), "numMarkets should be set to 0 by default"

        assert(c.addMarket(event1, market1) == 1), "addMarket wasn't executed successfully"

        assert(c.getMarkets(event1) == [market1]), "expected an array with the new market as the only value"
        assert(c.getMarket(event1, 0) == market1), "expected the new market at position 0 in the markets array"
        assert(c.getNumMarkets(event1) == 1), "numMarkets should be 1 at this point"

    def test_reporting():
        assert(c.getReportingThreshold(event1) == 0), "reportingThreshold should be set to 0 by default"
        assert(c.getReportersPaidSoFar(event1) == 0), "reportersPaidSoFarForEvent should be set to 0 by default"

        assert(c.setThreshold(event1, TWO) == 1), "setThreshold wasn't executed successfully"
        assert(c.addReportersPaidSoFar(event1) == 1), "addReportersPaidSoFar wasn't executed successfully"

        assert(c.getReportingThreshold(event1) == TWO), "reportingThreshold should be set to TWO at this point"
        assert(c.getReportersPaidSoFar(event1) == 1), "reportersPaidSoFarForEvent should be 1 at this point"

    def test_mode():
        assert(c.getMode(event1) == 0), "mode should be set to 0 by default"
        assert(c.setMode(event1, 1000) == 1), "setMode wasn't executed successfully"
        assert(c.getMode(event1) == 1000), "mode should be set to 1000 at this point"

    def test_rejection():
        assert(c.getRejected(event1) == 0), "rejected should be set to 0 by default"
        assert(c.getRejectedPeriod(event1) == 0), "rejectedPeriod should be set to 0 by default"

        assert(c.setRejected(event1, period1) == 1), "setRejected wasn't executed successfully"

        assert(c.getRejected(event1) == 1), "rejected should be set to 1 at this point"
        assert(c.getRejectedPeriod(event1) == period1), "rejectedPeriod wasn't set to the expected period"

    test_initializeEvent()
    test_eventBranch()
    test_creationTime()
    test_challenged()
    test_outcomes()
    test_past24()
    test_expiration()
    test_ethics()
    test_bonds()
    test_forking()
    test_markets()
    test_reporting()
    test_mode()
    test_rejection()
    print("data_api/events.se unit tests completed")

def test_info(contracts, s, t):
    c = contracts.info
    branch1 = 1010101
    branch2 = 2020202
    cashAddr = long(contracts.cash.address.encode("hex"), 16)
    cashWallet = contracts.branches.getBranchWallet(branch1, cashAddr)
    address0 = long(t.a0.encode("hex"), 16)
    address1 = long(t.a1.encode("hex"), 16)
    ONE = 10**18
    expectedCreationFee = 10 * ONE

    def test_defaults():
        assert(c.getCreator(branch1) == address0), "creator of default branch wasn't the expected address"
        assert(c.getDescription(branch1) == 'Root branch'), "description for default branch should be 'Root branch'"
        assert(c.getDescriptionLength(branch1) == 11), "descriptionLength should be 11 by default"
        assert(c.getCreationFee(branch1) == expectedCreationFee), "the creation fee for the default branch wasn't the expected creation fee (10 * ONE)"
        assert(c.getCurrency(branch1) == 0), "the default currency for the default branch should be set to 0 by default"
        assert(c.getWallet(branch1) == 0), "the default wallet for the default branch should be set to 0 by default"

    def test_currency():
        assert(c.getCurrency(branch1) == 0), "the default currency for the default branch should be set to 0 by default"
        assert(c.getWallet(branch1) == 0), "the default wallet for the default branch should be set to 0 by default"
        assert(c.setCurrencyAndWallet(branch1, cashAddr, cashWallet) == 1), "setCurrencyAndWallet wasn't executed successfully"
        assert(c.getCurrency(branch1) == cashAddr), "currency for default branch didn't get set to the cash address as expected"
        assert(c.getWallet(branch1) == cashWallet), "wallet for the default branch wasn't set to the cash wallet as expected"

    def test_setInfo():
        assert(c.setInfo(branch1, 'Hello World', address0, expectedCreationFee, cashAddr, cashWallet) == 0), "default branch already exists, so this shouldn't change anything and return 0"
        assert(c.getDescription(branch1) == 'Root branch'), "Confirm that the description hasn't changed because setInfo should have failed and returned 0"
        assert(c.getCreator(branch2) == 0), "branch2 shouldn't have been added to info yet and the creator should be set to 0."
        assert(c.setInfo(branch2, 'Test Branch', address1, expectedCreationFee, cashAddr, cashWallet) == 1), "setInfo wasn't successfully executed when it should have been"
        assert(c.getCreator(branch2) == address1), "creator of branch2 wasn't the expected address"
        assert(c.getDescription(branch2) == 'Test Branch'), "description for branch2 should be 'Test Branch'"
        assert(c.getDescriptionLength(branch2) == 11), "descriptionLength should be 11 by default"
        assert(c.getCreationFee(branch2) == expectedCreationFee), "the creation fee for branch2 wasn't the expected creation fee (10 * ONE)"
        assert(c.getCurrency(branch2) == cashAddr), "the currency for the branch2 should be set to the cash currency address"
        assert(c.getWallet(branch2) == cashWallet), "the wallet for branch2 should be set to the cash wallet address"

    test_defaults()
    test_currency()
    test_setInfo()
    print("data_api/info.se unit tests completed")

def test_mutex(contracts, s, t):
    c = contracts.mutex
    assert(c.acquire() == 1), "acquire should return 1 if the mutex isn't already set."
    try:
        raise Exception(c.acquire())
    except Exception as exc:
        assert(isinstance(exc, t.TransactionFailed)), "mutex should already be set so attempting to call acquire again should fail"
    assert(c.release() == 1), "release shoud return 1 and release the mutex"
    print("data_api/mutex.se unit tests completed")

if __name__ == '__main__':
    src = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'src')
    contracts = ContractLoader(src, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'])
    state = contracts._ContractLoader__state
    t = contracts._ContractLoader__tester
    print "BEGIN TESTING DATA_API"
    test_backstops(contracts, state, t)
    test_branches(contracts, state, t)
    test_consensusData(contracts, state, t)
    test_events(contracts, state, t)
    test_info(contracts, state, t)
    test_mutex(contracts, state, t)
    # data_api/expiringEvents.se
    # data_api/fxpFunctions.se
    # data_api/info.se
    # data_api/markets.se
    # data_api/mutex.se
    # data_api/orders.se
    # data_api/register.se
    # data_api/reporting.se
    # data_api/reportingThreshold.se
    # data_api/topics.se
    print "FINISH TESTING DATA_API"
