#!/usr/bin/env python
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
    print "data_api/backstops.se unit tests completed"

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
        assert(c.getNumCurrencies(branch1) == 1)
        assert(c.updateNumCurrencies(branch1, 5) == 1)
        assert(c.getNumCurrencies(branch1) == 5)
        assert(c.updateNumCurrencies(branch1, 1) == 1)
        assert(c.getNumCurrencies(branch1) == 1)
        # add a currency
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getNumCurrencies(branch1) == 1), "numCurrencies should be 1 at this point"
        #     raise Exception(c.addCurrency(branch1, repAddr, rate, 0, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "addCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getNumCurrencies(branch1) == 1), "numCurrencies was modified when it shouldn't have been"
        # now with whitelist
        assert(c.addCurrency(branch1, repAddr, rate, 0) == 1)
        assert(c.getNumCurrencies(branch1) == 2)
        assert(c.getBranchWallet(branch1, repAddr) != 0)
        assert(c.getCurrencyByContract(branch1, repAddr) == 1)
        assert(c.getCurrencyRate(branch1, repAddr) == rate)
        # disable and reactivate currency
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getCurrencyActive(branch1, repAddr) == 1), "REP currency should be active at this point"
        #     raise Exception(c.disableCurrency(branch1, repAddr, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "disableCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getCurrencyActive(branch1, repAddr) == 1), "REP currency should be active still"
        # now with whitelist
        assert(c.getCurrencyActive(branch1, repAddr) == 1)
        assert(c.disableCurrency(branch1, repAddr) == 1)
        assert(c.getCurrencyActive(branch1, repAddr) == 0)
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getCurrencyActive(branch1, repAddr) == 0), "REP currency should be inactive at this point"
        #     raise Exception(c.reactivateCurrency(branch1, repAddr, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "reactivateCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getCurrencyActive(branch1, repAddr) == 0), "REP currency should be inactive still"
        # now with whitelist
        assert(c.reactivateCurrency(branch1, repAddr) == 1)
        assert(c.getCurrencyActive(branch1, repAddr) == 1)
        # modify a currencyRate
        assert(c.getCurrencyRate(branch1, repAddr) == rate)
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getCurrencyRate(branch1, repAddr) == rate), "REP currency should have a rate of 1"
        #     raise Exception(c.updateCurrencyRate(branch1, repAddr, (rate + 1), 0, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "updateCurrencyRate should throw if msg.sender isn't whitelisted"
        #     assert(c.getCurrencyRate(branch1, repAddr) == rate), "REP currency should still have a rate of 1"
        # now with whitelist
        assert(c.updateCurrencyRate(branch1, repAddr, (rate + 1), 0) == 1)
        assert(c.getCurrencyRate(branch1, repAddr) == (rate + 1))
        # replace currency
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getCurrencyRate(branch1, repAddr) == (rate + 1)), "REP currency should have a modified rate"
        #     raise Exception(c.replaceCurrency(branch1, 1, repAddr, rate, 0, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "replaceCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getCurrencyRate(branch1, repAddr) == (rate + 1)), "REP currency should still have a modified rate"
        # now with whitelist
        assert(c.replaceCurrency(branch1, 1, repAddr, rate, 0) == 1)
        assert(c.getCurrencyRate(branch1, repAddr) == rate)
        assert(c.getNumCurrencies(branch1) == 2)
        # remove last currency
        # try:
        #     # should fail if not whitelisted...
        #     assert(c.getBranchCurrency(branch1, 1) == repAddr), "REP currency should still be defined"
        #     raise Exception(c.removeLastCurrency(branch1, sender=t.k1))
        # except Exception as exc:
        #     assert(isinstance(exc, t.TransactionFailed)), "removeLastCurrency should throw if msg.sender isn't whitelisted"
        #     assert(c.getBranchCurrency(branch1, 1) == repAddr), "REP currency should still be defined"
        # now with whitelist
        assert(c.getBranchCurrency(branch1, 1) == repAddr)
        assert(c.getCurrencyRate(branch1, repAddr) == rate)
        assert(c.removeLastCurrency(branch1) == 1)
        assert(c.getNumCurrencies(branch1) == 1)
        assert(c.getCurrencyByContract(branch1, repAddr) == 0)
        assert(c.getBranchWallet(branch1, repAddr) == 0)
        assert(c.getBranchCurrency(branch1, 1) == 0)
        assert(c.getCurrencyRate(branch1, repAddr) == 0)

    def test_branching():
        # test branch addition and confirm expected state
        cashAddr = long(contracts.cash.address.encode("hex"), 16)
        assert(c.getNumBranches() == 1)
        assert(c.getBranches() == [branch1])
        assert(c.initializeBranch(branch2, period2, 15, 200000000000000000, period1, branch1, cashAddr, 0) == 1)
        assert(c.getNumBranches() == 2)
        assert(c.getBranches() == [branch1, branch2])
        assert(c.getParent(branch2) == branch1)
        assert(c.getParentPeriod(branch2) == period1)
        assert(c.getVotePeriod(branch2) == period2)
        assert(c.incrementPeriod(branch2) == 1)
        assert(c.getVotePeriod(branch2) == (period2 + 1))

    def test_edits():
        # test modifying the branches in various ways
        assert(c.getNumMarketsBranch(branch1) == 0)
        assert(c.getMarketIDsInBranch(branch1, 0, 5) == [0, 0, 0, 0, 0])
        assert(c.addMarketToBranch(branch1, 1) == 1)
        assert(c.getNumMarketsBranch(branch1) == 1)
        assert(c.getMarketIDsInBranch(branch1, 0, 5) == [1, 0, 0, 0, 0])
        # set forkperiod
        assert(c.getForkPeriod(branch1) == 0)
        assert(c.getForkTime(branch1) == 0)
        assert(c.setForkPeriod(branch1) == 1)
        assert(c.getForkPeriod(branch1) == c.getVotePeriod(branch1))
        assert(c.getForkTime(branch1) == s.block.timestamp)
        # most recent child
        assert(c.getMostRecentChild(branch2) == 0)
        assert(c.setMostRecentChild(branch2, 1) == 1)
        assert(c.getMostRecentChild(branch2) == 1)

    test_defaults()
    test_currency()
    test_branching()
    test_edits()
    print "data_api/branches.se unit tests completed"

if __name__ == '__main__':
    src = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'src')
    contracts = ContractLoader(src, 'controller.se', ['mutex.se', 'cash.se', 'repContract.se'])
    state = contracts._ContractLoader__state
    t = contracts._ContractLoader__tester
    print "BEGIN TESTING DATA_API"
    test_backstops(contracts, state, t)
    test_branches(contracts, state, t)
    # data_api/consensusData.se
    # data_api/events.se
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
