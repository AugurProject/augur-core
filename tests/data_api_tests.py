#!/usr/bin/env python

from __future__ import division
from ethereum import tester as t
import os
import sys
import iocapture
import json
from pprint import pprint

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))

from upload_contracts import ContractLoader

ONE = 10**18
TWO = 2*ONE
HALF = ONE/2

def parseCapturedLogs(logs):
    arrayOfLogs = logs.strip().split("\n")
    arrayOfParsedLogs = []
    for log in arrayOfLogs:
        parsedLog = json.loads(log.replace("'", '"').replace("L", "").replace('u"', '"'))
        arrayOfParsedLogs.append(parsedLog)
    if len(arrayOfParsedLogs) == 0:
        return arrayOfParsedLogs[0]
    return arrayOfParsedLogs

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

    def test_refund():
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
    test_refund()
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

def test_expiringEvents(contracts, s, t):
    c = contracts.expiringEvents
    branch1 = 1010101
    branch2 = 2020202
    period0 = contracts.branches.getVotePeriod(branch1) - 1
    period1 = period0 + 1
    period2 = period1 + 1
    event1 = 123456789
    event2 = 987654321
    event3 = 333333333
    report0 = 1234567890
    report1 = 9876543210
    cashAddr = long(contracts.cash.address.encode("hex"), 16)
    cashWallet = contracts.branches.getBranchWallet(branch1, cashAddr)
    address0 = long(t.a0.encode("hex"), 16)
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    ONE = 10**18
    subsidy1 = 15*ONE

    def test_addEvent():
        assert(c.getEvents(branch1, period1) == []), "events should be an empty array"
        assert(c.getEventsRange(branch1, period1, 0, 5) == [0, 0, 0, 0, 0]), "events ranged 0 to 5 should have been an array of 0s"
        assert(c.getNumberEvents(branch1, period1) == 0), "number of events should be 0 by default"
        assert(c.getEventIndex(branch1, period1, event1) == 0), "event at event1 position should be 0 since it hasn't been added yet"
        assert(c.getEvent(branch1, period1, 0) == 0), "event 0 should be 0 as no event has been added"
        assert(c.addEvent(branch1, period1, event1, subsidy1, cashAddr, cashWallet, 0) == 1), "addEvent didn't execute successfully"
        assert(contracts.events.initializeEvent(event1, branch1, period1, ONE, ONE*2, 2, "https://someresolution.eth", address0, address1, address2) == 1), "events.initializeEvent didn't execute successfully"
        assert(c.addEvent(branch1, period1, event2, subsidy1, cashAddr, cashWallet, 0) == 1), "addEvent didn't execute successfully"
        assert(contracts.events.initializeEvent(event2, branch1, period1, ONE, ONE*4, 4, "https://someresolution.eth", address0, address1, address2) == 1), "events.initializeEvent didn't execute successfully"
        assert(c.getEvents(branch1, period1) == [event1, event2]), "events should be an array contianing event1 and event2"
        assert(c.getEventsRange(branch1, period1, 0, 5) == [event1, event2, 0, 0, 0]), "events ranging from 0 to 5 should include event1, event2, and then three 0s"
        assert(c.getNumberEvents(branch1, period1) == 2), "number of Events should be 2"
        assert(c.getEventIndex(branch1, period1, event1) == 0), "event1 should be at the 0 index"
        assert(c.getEventIndex(branch1, period1, event2) == 1), "event2 should be at the 1 index"
        assert(c.getEvent(branch1, period1, 0) == event1), "index 0 should return event1"
        assert(c.getEvent(branch1, period1, 1) == event2), "index 1 should return event2"

    def test_fees():
        assert(c.getFeeValue(branch1, period1) == 0), "fee should be 0 by default"
        assert(c.adjustPeriodFeeValue(branch1, period1, 100) == 1), "adjustPeriodFeeValue wasn't executed successfully"
        assert(c.getFeeValue(branch1, period1) == 100), "fee should be set to 100"

    def test_rep():
        assert(c.getBeforeRep(branch1, period1, address0) == 0), "beforeRep for address0 should be 0 by default"
        assert(c.getBeforeRep(branch1, period1, address1) == 0), "beforeRep for address1 should be 0 by default"
        assert(c.getPeriodDormantRep(branch1, period1, address0) == 0), "dormantRep for address0 should be 0 by default"
        assert(c.getPeriodDormantRep(branch1, period1, address1) == 0), "dormantRep for address1 should be 0 by default"
        assert(c.getNumActiveReporters(branch1, period1) == 0), "there should be 0 active reporters in period1 by default"
        assert(c.getActiveReporters(branch1, period1) == []), "getActiveReporters should return an empty array"
        assert(c.getAfterRep(branch1, period1, address0) == 0), "afterRep for address0 should be 0 by default"
        assert(c.getAfterRep(branch1, period1, address1) == 0), "afterRep for address1 should be 0 by default"

        assert(c.setBeforeRep(branch1, period1, 100, address0) == 100), "setBeforeRep wasn't executed successfully"
        assert(c.setBeforeRep(branch1, period1, 100, address1) == 100), "setBeforeRep wasn't executed successfully"
        assert(c.setPeriodDormantRep(branch1, period1, 200, address0) == 200), "setPeriodDormantRep wasn't executed successfully"
        assert(c.setPeriodDormantRep(branch1, period1, 200, address1) == 200), "setPeriodDormantRep wasn't executed successfully"
        assert(c.setAfterRep(branch1, period1, 100, address0) == 100), "setAfterRep wasn't executed successfully"
        assert(c.setAfterRep(branch1, period1, 100, address1) == 100), "setAfterRep wasn't executed successfully"

        assert(c.getBeforeRep(branch1, period1, address0) == 100), "beforeRep for address0 should be set to 100"
        assert(c.getBeforeRep(branch1, period1, address1) == 100), "beforeRep for address1 should be set to 100"
        assert(c.getPeriodDormantRep(branch1, period1, address0) == 200), "dormantRep for address0 should be set to 100"
        assert(c.getPeriodDormantRep(branch1, period1, address1) == 200), "dormantRep for address1 should be set to 100"
        assert(c.getAfterRep(branch1, period1, address0) == 100), "afterRep should be set to 100 for addresss0"
        assert(c.getAfterRep(branch1, period1, address1) == 100), "afterRep should be set to 100 for addresss1"
        assert(c.getNumActiveReporters(branch1, period1) == 2), "numActiveReporters should be set to 2"
        assert(c.getActiveReporters(branch1, period1) == [address0, address1]), "getActiveReporters should return an array with address0 and address1 in it"

    def test_reporting():
        assert(c.getPeriodRepWeight(branch1, period1, address0) == 0), "periodWeight for address0 should be set to 0"
        assert(c.setPeriodRepWeight(branch1, period1, address0, 10) == 1), "setPeriodRepWeight wasn't executed successfully"
        assert(c.getPeriodRepWeight(branch1, period1, address0) == 10), "periodWeight should return 10 for address0"

        assert(c.getEventWeight(branch1, period1, event1) == 0), "eventWeight for event1 should be 0 by default"
        assert(c.setEventWeight(branch1, period1, event1, 50) == 1), "setEventWeight wasn't executed successfully"
        assert(c.getEventWeight(branch1, period1, event1) == 50), "eventWeight should be set to 50 for event1"

        assert(c.getReport(branch1, period1, event1, address0) == 0), "report for event1 address0 should be 0"
        assert(c.setReport(branch1, period1, event1, report0, address0) == 1), "setReport wasn't executed successfully"
        assert(c.getReport(branch1, period1, event1, address0) == report0), "report for event1 and address0 should be set to report0"

        assert(c.getEthicReport(branch1, period1, event1, address0) == 0), "ethicReport for event1 address0 should be 0"
        assert(c.setEthicReport(branch1, period1, event1, ONE, address0) == 1), "setEthicReport wasn't executed successfully"
        assert(c.getEthicReport(branch1, period1, event1, address0) == ONE), "ethicReport for event1 address0 should be set to 10**18 (ONE)"

        assert(c.getNumReportsSubmitted(branch1, period1, address0) == 0), "numReportsSubmitted for address0 should be 0"
        assert(c.addReportToReportsSubmitted(branch1, period1, address0) == 1), "addReportToReportsSubmitted wasn't executed successfully"
        assert(c.getNumReportsSubmitted(branch1, period1, address0) == 1), "numReportsSubmitted for address0 should be 1"
        assert(c.getEventWeight(branch1, period1, event1) == 50), "event1 weight should be set to 50"
        assert(c.countReportAsSubmitted(branch1, period1, event1, address0, 50) == 1), "countReportAsSubmitted wasn't executed successfully"
        assert(c.getNumReportsSubmitted(branch1, period1, address0) == 2), "numReportsSubmitted for address0 should be 2"
        assert(c.getEventWeight(branch1, period1, event1) == 100), "event1 weight should be set to 100"

        assert(c.getWeightOfReport(period1, event1, report0) == 0), "weightOfReport for report0 on event1 should be 0"
        assert(c.addToWeightOfReport(period1, event1, report0, 100) == 1), "addToWeightOfReport wasn't executed successfully"
        assert(c.getWeightOfReport(period1, event1, report0) == 100), "weightOfReport for report0 on event1 should be set to 100"

        assert(c.getLesserReportNum(branch1, period1, event1) == 0), "lesserReportNum should be set to 0 for event1"
        assert(c.setLesserReportNum(branch1, period1, event1, 5) == 1), "setLesserReportNum wasn't executed successfully"
        assert(c.getLesserReportNum(branch1, period1, event1) == 5), "lesserReportNum for event1 should be set to 5"

        assert(c.getNumEventsToReportOn(branch1, period1) == 0), "numEventsToReport on for period1 should be set to 0 by default"
        assert(c.setNumEventsToReportOn(branch1) == 1), "setNumEventsToReportOn wasn't executed successfully"
        assert(c.getNumEventsToReportOn(branch1, period1) == 12), "numEventsToReport should now be set to 12"

        assert(c.getCurrentMode(period1, event2) == 0), "currentMode for event2 should be set to 0"
        assert(c.getCurrentModeItems(period1, event2) == 0), "currentModeItems for event2 should be set to 0"

        assert(c.setCurrentMode(period1, event2, 100) == 1), "setCurrentMode wasn't executed successfully"
        assert(c.setReport(branch1, period1, event2, report1, address0) == 1), "setReport wasn't executed successfully"
        assert(c.addToWeightOfReport(period1, event2, report1, 100) == 1), "addToWeightOfReport wasn't executed successfully"
        assert(c.setCurrentModeItems(period1, event2, report1) == 1), "setCurrentModeItems wasn't executed successfully"

        assert(c.getCurrentMode(period1, event2) == 100), "currentMode for event2 should be 100"
        assert(c.getCurrentModeItems(period1, event2) == 100), "currentModeItems for event2 should be set to 100"

        assert(c.getNumRoundTwo(branch1, period1) == 0), "numRoundTwo should be set to 0 by default"
        assert(c.addRoundTwo(branch1, period1) == 1), "addRoundTwo wasn't executed successfully"
        assert(c.getNumRoundTwo(branch1, period1) == 1), "numRoundTwo for period1 should be set to 1"

    def test_eventModification():
        # COST_FOR_EVENT_REPORT_CALCULATION is set to the current value found in expiringEvents.se
        COST_FOR_EVENT_REPORT_CALCULATION = 500000
        event3Subsidy = t.gas_price * COST_FOR_EVENT_REPORT_CALCULATION
        assert(c.addEvent(branch2, period0, event3, event3Subsidy, cashAddr, cashWallet, 0, value=event3Subsidy) == 1), "addEvent didn't execute successfully"
        assert(contracts.events.initializeEvent(event3, branch2, period0, ONE, ONE*4, 4, "https://someresolution.eth", address0, address1, address2) == 1), "events.initializeEvent wasn't executed successfully"
        assert(c.getEvents(branch1, period1) == [event1, event2]), "events in branch1 period1 should be an array with event1 and event2"
        assert(c.getEvents(branch2, period0) == [event3]), "events for branch2, period0 should be event3 in an array"
        assert(c.getEvent(branch1, period1, 0) == event1), "event at index 0 in branch1, period1 should be event1"
        assert(c.getEvent(branch1, period1, 1) == event2), "event at index 1 in branch1, period1 should be event2"
        assert(c.getEvent(branch2, period0, 0) == event3), "event at index 0 in branch2, period0 should be event3"
        assert(c.getNumberEvents(branch1, period1) == 2), "numberEvents in branch1, period1 should be 2"
        assert(c.getNumberEvents(branch2, period0) == 1), "numberEvents in branch2, period0 should be 1"

        assert(c.moveEvent(branch2, event3) == 1), "moveEvent wasn't executed successfully"
        assert(c.moveEvent(branch1, event2) == 0), "moveEvent executed Successfully when it shouldn't have"

        assert(c.getEvents(branch2, period2) == [event3]), "events in branch2, period2 should be an array with just event3"
        assert(c.getEvent(branch2, period2, 0) == event3), "event in branch2, period2 at index 0 should be set to event3"
        assert(c.getEvent(branch2, period0, 0) == event3), "event in branch2, period0 at index 0 should be set to event3"

        assert(c.deleteEvent(branch2, period0, event3) == 1), "deleteEvent wasn't executed successfully"
        assert(c.getEvent(branch2, period0, 0) == 0), "event at branch2, period0, index 0 should be set to 0"

        assert(c.getNumRemoved(branch1, period1) == 0), "numRemoved should be set to 0 by default"
        assert(c.removeEvent(branch1, period1) == 1), "removeEvent wasn't executed successfully"
        assert(c.getNumRemoved(branch1, period1) == 1), "numRemoved should be set to 1"

        assert(c.getRequired(event2, period1, branch1) == 0), "required for event2 in branch1, period1 should be set to 0"
        assert(c.getNumRequired(branch1, period1) == 0), "numRequired for branch1, period1 should be set to 0"

        assert(c.setEventRequired(branch1, period1, event2) == 1), "setEventRequired wasn't executed successfully"
        # confirm it returns 0 if we already have this event set to required
        assert(c.setEventRequired(branch1, period1, event2) == 0), "setEventRequired should have returned 0 since event2 is already set to required"

        assert(c.getRequired(event2, period1, branch1) == 1), "required for event2 in branch1, period1 should be set to 1"
        assert(c.getNumRequired(branch1, period1) == 1), "numRequired should be set to 1"

        assert(c.getAfterFork(branch1, period1) == 0), "afterFork for branch1, period1 should return 0"

        currAddr0Bal = s.block.get_balance(t.a0)
        event3sub = c.getSubsidy(branch2, period2, event3)
        assert(event3sub == event3Subsidy), "the subsidy for event3 after being moved should be = to event3subsidy"
        assert(c.refundCost(t.a0, branch2, period2, event3) == 1), "refundCost wasn't executed successfully"
        assert(s.block.get_balance(t.a0) == currAddr0Bal + event3sub), "address0 should have an updated balance of their pervious balance + subsidy1 thanks to refundCost execution"
        try:
            raise Exception(c.refundCost(t.a0, branch2, period2, event3))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "refundCost should fail if the contract doesn't have enough funds to refund"

    test_addEvent()
    test_fees()
    test_rep()
    test_reporting()
    test_eventModification()
    print("data_api/expiringEvents.se unit tests completed")

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

def test_markets(contracts, s, t):
    c = contracts.markets
    branch1 = 1010101
    market1 = 1111111111
    event1 = 12345678901
    period1 = contracts.branches.getVotePeriod(branch1)
    gasSubsidy1 = 10**14*234
    creationFee1 = 10**14*340
    twoPercent = 10**16*2
    ONE = 10**18
    expirationDate1 = s.block.timestamp + 15
    shareContractPath = os.path.join(src, 'functions/shareTokens.se')
    walletContractPath = os.path.join(src, 'functions/wallet.se')
    shareContract1 = s.abi_contract(shareContractPath, sender=t.k0)
    shareContract2 = s.abi_contract(shareContractPath, sender=t.k0)
    walletContract1 = s.abi_contract(walletContractPath, sender=t.k0)
    walletContract2 = s.abi_contract(walletContractPath, sender=t.k0)
    walletContract1.initialize(shareContract1.address)
    walletContract2.initialize(shareContract2.address)
    shareAddr1 = long(shareContract1.address.encode('hex'), 16)
    shareAddr2 = long(shareContract2.address.encode('hex'), 16)
    walletAddr1 = long(walletContract1.address.encode('hex'), 16)
    walletAddr2 = long(walletContract2.address.encode('hex'), 16)
    shareContracts = [shareContract1.address, shareContract2.address]
    walletContracts = [walletContract1.address, walletContract2.address]
    tag1 = 'one'
    tag2 = 'two'
    tag3 = 'three'
    longTag1 = long(tag1.encode('hex'), 16)
    longTag2 = long(tag2.encode('hex'), 16)
    longTag3 = long(tag3.encode('hex'), 16)
    orderID1 = 12340001
    orderID2 = 12340002
    orderID3 = 12340003
    orderID4 = 12340004
    address0 = long(t.a0.encode("hex"), 16)
    address1 = long(t.a1.encode("hex"), 16)

    def test_marketInialization():
        assert(c.getMarketsHash(branch1) == 0), "getMarketsHash for branch1 should be defaulted to 0"
        assert(c.initializeMarket(market1, event1, period1, twoPercent, branch1, tag1, tag2, tag3, ONE, 2, 'this is extra information', gasSubsidy1, creationFee1, expirationDate1, shareContracts, walletContracts, value=gasSubsidy1) == 1), "initializeMarket wasn't executed successfully"
        assert(c.getMarketsHash(branch1) != 0), "marketsHash should no longer be set to 0"
        assert(c.getBranch(market1) == branch1), "branch for market1 should be set to branch1"
        assert(c.getMarketEvent(market1) == event1), "marketEvent for market1 shoudl be event1"
        assert(c.getLastExpDate(market1) == expirationDate1), "lastExpDate for market1 should be set to expirationDate1"
        assert(c.getTags(market1) == [longTag1, longTag2, longTag3]), "tags for market1 should return an array with 3 tags"
        assert(c.getTopic(market1) == longTag1), "topic for market1 should be set to topic1"
        assert(c.getFees(market1) == creationFee1), "fees for market1 should be set to creationFee1"
        assert(c.getTradingFee(market1) == twoPercent), "tradingFee for market1 should be set to twoPercent"
        assert(c.getVolume(market1) == 0), "volumne for market1 should be set to 0 by default"
        assert(c.getExtraInfo(market1) == 'this is extra information'), "extraInfo for market1 should be set to 'this is extra information'"
        assert(c.getExtraInfoLength(market1) == 25), "extraInfoLength for market1 should be 25"
        assert(c.getGasSubsidy(market1) == gasSubsidy1), "gasSubsidy for market1 should be set to gasSubsidy1"
        assert(c.getMarketNumOutcomes(market1) == 2), "marketNumOutcomes for market1 should be 2"
        assert(c.getCumulativeScale(market1) == ONE), "cumulativeScale for market1 should be set to ONE"

    def test_marketOrders():
        assert(c.getOrderIDs(market1) == []), "orderIds for market1 should be an empty array"
        assert(c.getTotalOrders(market1) == 0), "totalOrders for market1 should be 0"
        assert(c.getLastOrder(market1) == 0), "lastOrder for market1 should be set to 0"

        assert(c.addOrder(market1, orderID1) == 1), "addOrder wasn't executed successfully"
        assert(c.addOrder(market1, orderID2) == 1), "addOrder wasn't executed successfully"
        assert(c.addOrder(market1, orderID3) == 1), "addOrder wasn't executed successfully"
        assert(c.addOrder(market1, orderID4) == 1), "addOrder wasn't executed successfully"

        assert(c.getOrderIDs(market1) == [orderID4, orderID3, orderID2, orderID1]), "orderIds for market1 should return an array of length four containing the orderIds ordered by addition to the array, with most recent addition in the 0 position for the array"
        assert(c.getTotalOrders(market1) == 4), "totalOrders for market1 should be 4"
        assert(c.getLastOrder(market1) == orderID4), "getLastOrder for market1 should return orderID4"
        assert(c.getPrevID(market1, orderID4) == orderID3), "getPrevID for orderID4 should return orderID3"
        assert(c.getPrevID(market1, orderID3) == orderID2), "getPrevID for orderID3 should return orderID2"
        assert(c.getPrevID(market1, orderID2) == orderID1), "getPrevID for orderID2 should return orderID1"
        assert(c.getPrevID(market1, orderID1) == 0), "getPrevId for orderID1 should return 0"

        assert(c.removeOrderFromMarket(market1, orderID2) == 1), "removeOrderFromMarket wasn't executed successfully"

        assert(c.getOrderIDs(market1) == [orderID4, orderID3, orderID1]), "getOrderIDs should now return only 3 topics in the array, ordered 4, 3, 1 after removing order 2"
        assert(c.getPrevID(market1, orderID3) == orderID1), "getPrevID for orderID3 should return orderID1 instead of orderID2 as orderID2 has been removed"
        assert(c.getPrevID(market1, orderID2) == 0), "getPrevID for orderID2 should return 0 as orderID2 was removed and not part of the orderbook"
        assert(c.getLastOrder(market1) == orderID4), "lastOrder for market1 should be orderID4"

        assert(c.removeOrderFromMarket(market1, orderID4) == 1), "removeOrderFromMarket wasn't executed successfully"

        assert(c.getOrderIDs(market1) == [orderID3, orderID1]), "getOrderIDs should now return an array with only 2 topics, 3 and 1 as both 4 and 2 have been removed"
        assert(c.getPrevID(market1, orderID4) == 0), "getPrevID for orderID4 should be set to 0 as it has been removed and is not part of the orderbook"
        assert(c.getLastOrder(market1) == orderID3), "lastOrder for market1 should now be set to orderID3 since orderID4 was removed"
        assert(c.getTotalOrders(market1) == 2), "totalOrders for market1 should be 2"

    def test_marketShares():
        assert(c.getSharesValue(market1) == 0), "shareValue for market1 should be set to 0 by default"
        assert(c.getMarketShareContracts(market1) == [shareAddr1, shareAddr2]), "marketShareContracts should be an array of length 2 with shareAddr1 and shareAddr2 contained within"
        assert(c.getTotalSharesPurchased(market1) == 0), "totalSharesPurchased for market1 should be set to 0"
        assert(c.getSharesPurchased(market1, 1) == 0), "sharesPurchased for market1, outcome 1 should be set to 0"
        assert(c.getSharesPurchased(market1, 2) == 0), "sharesPurchased for market1, outcome 2 should be set to 0"
        assert(c.getParticipantSharesPurchased(market1, address1, 1) == 0), "participantSharesPurchased for address1 on market1 for outcome 1 should be set to 0"
        assert(c.getParticipantSharesPurchased(market1, address1, 2) == 0), "participantSharesPurchased for address1 on market1 for outcome 2 should be set to 0"
        assert(c.modifySharesValue(market1, ONE) == 1), "modifySharesValue wasn't executed successfully"
        assert(c.getSharesValue(market1) == ONE), "getSharesValue for market1 should be set to ONE"
        assert(c.getVolume(market1) == 0), "volume for market1 should be set to 0"
        assert(c.modifyMarketVolume(market1, ONE*15) == 1), "modifyMarketVolume wasn't executed successfully"
        assert(c.getVolume(market1) == ONE*15), "volume for market1 should be set to ONE*15"
        assert(c.getOutcomeShareWallet(market1, 1) == walletAddr1), "outcomeShareWallet for market1, outcome 1 should return walletAddr1"
        assert(c.getOutcomeShareWallet(market1, 2) == walletAddr2), "outcomeShareWallet for market1, outcome 2 should return walletAddr2"
        assert(c.getOutcomeShareContract(market1, 1) == shareAddr1), "outcomeShareContract for market1, outcome 1 should return shareAddr1"
        assert(c.getOutcomeShareContract(market1, 2) == shareAddr2), "outcomeShareContract for market1, outcome 2 should return shareAddr2"

    def test_marketSettings():
        currentMarketHash = c.getMarketsHash(branch1)
        assert(c.addToMarketsHash(branch1, 123412341234) == 1), "addToMarketsHash wasn't executed successfully"
        assert(c.getMarketsHash(branch1) != currentMarketHash), "marketsHash shouldn't equal the marketHash prior to calling addToMarketsHash"

        assert(c.getFees(market1) == creationFee1), "fees for market1 should be set to creationFee1"
        assert(c.addFees(market1, 100) == 1), "addFees wasn't executed successfully"
        assert(c.getFees(market1) == creationFee1 + 100), "fees for market1 should be set to creationFee1 + 100"

        assert(c.getTradingPeriod(market1) == period1), "tradingPeriod for market1 should be set to period1"
        assert(c.getOriginalTradingPeriod(market1) == period1), "originalTradingPeriod for market1 should be set to period1"
        assert(c.setTradingPeriod(market1, period1 + 10) == 1), "setTradingPeriod wasn't executed successfully"
        assert(c.getOriginalTradingPeriod(market1) == period1), "originalTradingPeriod for market1 should be set to period1"
        assert(c.getTradingPeriod(market1) == period1 + 10), "tradingPeriod for market1 should be set to period1 + 10"

        assert(c.getTradingFee(market1) == twoPercent), "tradingFees should be set to twoPercent"
        assert(c.setTradingFee(market1, twoPercent + 10**13) == twoPercent + 10**13), "setTradingFee wasn't executed successfully"
        assert(c.getTradingFee(market1) == twoPercent + 10**13), "tradingFee should be set to twoPercent + 10**13"

        assert(c.getBondsMan(market1) == 0), "bondsMan for market1 should be set to 0 by default"
        assert(c.getPushedForward(market1) == 0), "pushedForward should be set to 0 for market1"
        assert(c.setPushedForward(market1, 1, address1) == 1), "setPushedForward wasn't executed successfully"
        assert(c.getPushedForward(market1) == 1), "pushedForward for market1 should be set to 1"
        assert(c.getBondsMan(market1) == address1), "bondsMan for market1 should be set to address1"

        assert(c.getLastOutcomePrice(market1, 1) == 0), "lastOutcomePrice for market1, outcome 1 should be 0"
        assert(c.getLastOutcomePrice(market1, 2) == 0), "lastOutcomePrice for market1, outcome 2 should be 0"
        assert(c.setPrice(market1, 1, 123) == 1), "setPrice wasn't executed successfully"
        assert(c.setPrice(market1, 2, 456) == 1), "setPrice wasn't executed successfully"
        assert(c.getLastOutcomePrice(market1, 1) == 123), "lastOutcomePrice for market1, outcome 1 should be set to 123"
        assert(c.getLastOutcomePrice(market1, 2) == 456), "lastOutcomePrice for market1, outcome 2 should be set to 456"

        assert(c.getMarketResolved(market1) == 0), "marketResolved for market1 shoudl be set to 0"
        assert(c.setMarketResolved(market1) == 1), "setMarketResolved wasn't executed successfully"
        assert(c.getMarketResolved(market1) == 1), "marketResolved for market1 shoudl be set to 1"

        addr1Bal = s.block.get_balance(t.a1)
        assert(s.block.get_balance(c.address) == gasSubsidy1), "the market contract balance was expected to be set to gasSubsidy1"
        assert(c.refundClosing(market1, address1) == 1), "refundClosing wasn't executed successfully"
        assert(s.block.get_balance(t.a1) == addr1Bal + gasSubsidy1), "the balance of address1 should now be it's previous balance + the gasSubsidy1 from market1"


    test_marketInialization()
    test_marketOrders()
    test_marketShares()
    test_marketSettings()
    print("data_api/markets.se unit tests complete")

def test_mutex(contracts, s, t):
    c = contracts.mutex
    assert(c.acquire() == 1), "acquire should return 1 if the mutex isn't already set."
    try:
        raise Exception(c.acquire())
    except Exception as exc:
        assert(isinstance(exc, t.TransactionFailed)), "mutex should already be set so attempting to call acquire again should fail"
    assert(c.release() == 1), "release shoud return 1 and release the mutex"
    print("data_api/mutex.se unit tests completed")

def test_orders(contracts, s, t):
    c = contracts.orders
    market1 = 1111111111
    address0 = long(t.a0.encode("hex"), 16)
    address1 = long(t.a1.encode("hex"), 16)
    address2 = long(t.a2.encode("hex"), 16)
    order1 = 123456789
    order2 = 987654321
    ONE = 10**18
    pointFive = 10**17*5

    def test_hashcommit():
        order = c.makeOrderHash(market1, 1, 1)
        assert(order != 0), "makeOrderHash for market1 shouldn't be 0"

        assert(c.commitOrder(order) == 1), "commitOrder wasn't executed successfully"
        try:
            raise Exception(c.checkHash(order, address0))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "checkHash for order should throw because that order was placed in the same block we are checking"
        # move the block.number up 1
        s.mine(1)
        assert(c.checkHash(order, address0) == 1), "checkHash for order should now be 1"

    def test_saveOrder():
        assert(c.saveOrder(order1, 1, market1, ONE*10, pointFive, address0, 1, 0, ONE*10) == 1), "saveOrder wasn't executed successfully"
        assert(c.saveOrder(order2, 2, market1, ONE*10, pointFive, address1, 1, ONE*5, 0) == 1), "saveOrder wasn't executed successfully"

        assert(c.getOrder(order1) == [order1, 1, market1, ONE*10, pointFive, address0, s.block.number, 1, 0, ONE*10]), "getOrder for order1 didn't return the expected array of data"
        assert(c.getOrder(order2) == [order2, 2, market1, ONE*10, pointFive, address1, s.block.number, 1, ONE*5, 0]), "getOrder for order2 didn't return the expected array of data"

        assert(c.getAmount(order1) == ONE*10), "amount for order1 should be set to ONE*10 (ONE = 10**18)"
        assert(c.getAmount(order2) == ONE*10), "amount for order2 should be set to ONE*10 (ONE = 10**18)"

        assert(c.getID(order1) == order1), "getID didn't return the expected order"
        assert(c.getID(order2) == order2), "getID didn't return the expected order"

        assert(c.getPrice(order1) == pointFive), "price for order1 should be set to pointFive (.5*ONE)"
        assert(c.getPrice(order2) == pointFive), "price for order2 should be set to pointFive (.5*ONE)"

        assert(c.getOrderOwner(order1) == address0), "orderOwner for order1 should be address0"
        assert(c.getOrderOwner(order2) == address1), "orderOwner for order2 should be address1"

        assert(c.getType(order1) == 1), "type for order1 should be set to 1"
        assert(c.getType(order2) == 2), "type for order2 should be set to 2"

    def test_fillOrder():
        # orderID, fill, money, shares
        try:
            raise Exception(c.fillOrder(order1, ONE*20, 0, 0))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "fillOrder should fail if fill is greated then the amount of the order"
        try:
            raise Exception(c.fillOrder(order1, ONE*10, 0, ONE*20))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "fillOrder should fail if shares is greater than the sharesEscrowed in the order"
        try:
            raise Exception(c.fillOrder(order1, ONE*10, ONE*20, 0))
        except Exception as exc:
            assert(isinstance(exc, t.TransactionFailed)), "fillOrder should fail if money is greater than the moneyEscrowed in the order"
        # fully fill
        assert(c.fillOrder(order1, ONE*10, 0, ONE*10) == 1), "fillOrder wasn't executed successfully"
        # prove all
        assert(c.getOrder(order1) == [order1, 1, market1, 0, pointFive, address0, s.block.number, 1, 0, 0]), "getOrder for order1 didn't return the expected data array"
        # test partial fill
        assert(c.fillOrder(order2, ONE*6, ONE*3, 0) == 1), "fillOrder wasn't executed successfully"
        # confirm partial fill
        assert(c.getOrder(order2) == [order2, 2, market1, ONE*4, pointFive, address1, s.block.number, 1, ONE*2, 0]), "getOrder for order2 didn't return the expected data array"
        # fill rest of order2
        assert(c.fillOrder(order2, ONE*4, ONE*2, 0) == 1), "fillOrder wasn't executed successfully"
        assert(c.getOrder(order2) == [order2, 2, market1, 0, pointFive, address1, s.block.number, 1, 0, 0]), "getOrder for order2 didn't return the expected data array"

    def test_removeOrder():
        order3 = 321321321
        assert(c.saveOrder(order3, 1, market1, ONE*10, pointFive, address0, 2, 0, ONE*10) == 1), "saveOrder wasn't executed successfully"
        assert(c.getOrder(order3) == [order3, 1, market1, ONE*10, pointFive, address0, s.block.number, 2, 0, ONE*10]), "getOrder for order3 didn't return the expected data array"
        assert(c.removeOrder(order3) == 1), "removeOrder wasn't executed successfully"
        assert(c.getOrder(order3) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), "getOrder for order3 should return an 0'd out array as it has been removed"

    test_hashcommit()
    test_saveOrder()
    test_fillOrder()
    test_removeOrder()
    print("data_api/orders.se unit tests completed")

def test_register(contracts, s, t):
    c = contracts.register
    address0 = long(t.a0.encode("hex"), 16)
    with iocapture.capture() as captured:
        retVal = c.register()
        log = parseCapturedLogs(captured.stdout)[-1]
    assert(retVal == 1), "register should return 1"
    assert(log["_event_type"] == "registration"), "eventType should be 'registration' for the log created by register"
    assert(log["timestamp"] == s.block.timestamp), "timestamp should be set to block.timestamp"
    assert(log["sender"] == address0), "sender should be address0"

    print("data_api/register.se unit tests completed")

def test_topics(contracts, s, t):
    c = contracts.topics
    branch1 = 1010101
    # topic0 is the topic added from the markets tests
    topic0 = 'one'
    topic1 = 'augur'
    topic2 = 'predictions'
    longTopic0 = long('one'.encode('hex'), 16)
    longTopic1 = long(topic1.encode('hex'), 16)
    longTopic2 = long(topic2.encode('hex'), 16)
    ONE = 10**18

    def test_defaults():
        assert(c.getNumTopicsInBranch(branch1) == 1), "numTopicsInBranch for branch1 should be 1 at this point"
        assert(c.getTopicsInBranch(branch1, 0, 5) == [longTopic0]), "topicsInBranch for branch1 ranging from topic 0 to 5 should return an array containing only topic0 from the markets tests"
        assert(c.getTopicsInfo(branch1, 0, 5) == [longTopic0, ONE*15]), "topicsInfo for branch1 should ranging from topic 0 to 5 should return only topic0 from the markets tests and its popularity"
        assert(c.getTopicPopularity(branch1, topic1) == 0), "topicPopularity for branch1 and topic1 should be 0 by default as topic1 shouldn't exist yet"

    def test_updateTopicPopularity():
        assert(c.updateTopicPopularity(branch1, topic1, ONE) == 1), "updateTopicPopularity wasn't executed successfully"
        assert(c.getTopicPopularity(branch1, topic1) == ONE), "topicPopularity for branch1, topic1 should be set to ONE"
        assert(c.getNumTopicsInBranch(branch1) == 2), "numTopicsInBranch for branch1 should return 2"
        assert(c.getTopicsInBranch(branch1, 0, 5) == [longTopic0, longTopic1]), "topicsInBranch1 ranging from index 0 to 5 should return an array with topic0 and topic1 inside of it"
        assert(c.getTopicsInfo(branch1, 0, 5) == [longTopic0, ONE*15, longTopic1, ONE]), "getTopicsInfo for branch1, index 0 to 5, should return topic0 and its popularity of ONE*15 and topic1 and it's popularity of ONE in a length 4 array"
        assert(c.getTopicPopularity(branch1, topic2) == 0), "topicPopularity for topic2 should be 0 as topic2 hasn't been added yet"
        assert(c.updateTopicPopularity(branch1, topic2, ONE*4) == 1), "updateTopicPopularity wasn't executed successfully"
        assert(c.getTopicPopularity(branch1, topic2) == ONE*4), "topicPopularity for topic2 should now be set to ONE*4"
        assert(c.getNumTopicsInBranch(branch1) == 3), "numTopicsInBranch should be set to 3"
        assert(c.getTopicsInBranch(branch1, 0, 5) == [longTopic0, longTopic1, longTopic2]), "getTopicsInBranch for branch1, index 0 to 5 should return an array with topic0, topic1, and topic2 contained within"
        assert(c.getTopicsInfo(branch1, 0, 5) == [longTopic0, ONE*15, longTopic1, ONE, longTopic2, ONE*4]), "getTopicsInfo for branch1, index 0 to 5 should return a length 6 array with topic0 and it's popularity, topic1 and it's popularity, and topic2 and it's popularity"
        assert(c.updateTopicPopularity(branch1, topic1, ONE*2) == 1), "updateTopicPopularity wasn't executed successfully"
        assert(c.updateTopicPopularity(branch1, topic2, -ONE) == 1), "updateTopicPopularity wasn't executed successfully"
        assert(c.getTopicPopularity(branch1, topic1) == ONE*3), "topicPopularity for branch1, topic1 should be set to ONE*3"
        assert(c.getTopicPopularity(branch1, topic2) == ONE*3), "topicPopularity for branch1, topic2 should be set to ONE*3"
        assert(c.getTopicsInfo(branch1, 0, 5) == [longTopic0, ONE*15, longTopic1, ONE*3, longTopic2, ONE*3]), "getTopicsInfo for branch1, index 0 to 5, should return topic0 and it's popularity, topic1 and it's updated popularity, and topic2 and it's updated popularity"

    test_defaults()
    test_updateTopicPopularity()
    print("data_api/topics.se unit tests completed")

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
    test_expiringEvents(contracts, state, t)
    test_info(contracts, state, t)
    test_markets(contracts, state, t)
    test_mutex(contracts, state, t)
    test_orders(contracts, state, t)
    test_register(contracts, state, t)
    # data_api/reporting.se
    # data_api/reportingThreshold.se
    test_topics(contracts, state, t)
    print "FINISH TESTING DATA_API"
