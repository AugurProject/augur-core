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

def test_branches(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
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
        assert(c.getMinTradingFee(branch1) == 2000000000000000), "minTradeFees should be .2%"
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

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_branches(contracts)
