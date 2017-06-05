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

def test_events(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
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
    WEI_TO_ETH = 1000000000000000000
    TWO = 2000000000000000000
    PointTwo = 200000000000000000

    def test_initializeEvent():
        assert(c.getEventInfo(event1) == [0, 0, 0, 0, 0, 0, 0, 0]), "event1 shouldn't exist yet, should return an array of 0's"
        assert(c.initializeEvent(event1, branch1, expirationDate1, WEI_TO_ETH, TWO, 2, "https://someresolution.eth", address2, address3, address4) == 1), "initializeEvent wasn't executed successfully"
        assert(c.getEventInfo(event1) == [branch1, expirationDate1, 0, WEI_TO_ETH, TWO, 2, 0, address2]), "eventInfo wasn't set to the expected values for event1"
        assert(c.getForkResolveAddress(event1) == address4), "forkResolveAddress wasn't the expected address"
        assert(c.getResolveBondPoster(event1) == address3), "resolveBondPoster wasn't the expected address"
        assert(c.getResolutionAddress(event1) == address2), "resolutionAddress wasn't the expected address"
        assert(c.getEventResolution(event1) == 'https://someresolution.eth'), "eventResolution wasn't the expected string"
        assert(c.getResolutionLength(event1) == len('https://someresolution.eth')), "resolutionLength wasn't correctly set to 26"
        assert(c.getMinValue(event1) == WEI_TO_ETH), "minValue wasn't set to WEI_TO_ETH as expected"
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

        assert(c.setOutcome(event1, WEI_TO_ETH) == 1), "setOutcome wasn't executed successfully"
        assert(c.setFirstPreliminaryOutcome(event1, WEI_TO_ETH) == 1), "setFirstPreliminaryOutcome wasn't executed successfully"
        assert(c.setUncaughtOutcome(event1, WEI_TO_ETH) == 1), "setUncaughtOutcome wasn't executed successfully"

        assert(c.getOutcome(event1) == WEI_TO_ETH), "outcome should be set to WEI_TO_ETH"
        assert(c.getFirstPreliminaryOutcome(event1) == WEI_TO_ETH), "firstPreliminaryOutcome should be set to WEI_TO_ETH"
        assert(c.getUncaughtOutcome(event1) == WEI_TO_ETH), "uncaughtOutcome should be set to WEI_TO_ETH"

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
        assert(c.setEthics(event1, WEI_TO_ETH) == WEI_TO_ETH), "setEthics wasn't executed successfully"
        assert(c.getEthics(event1) == WEI_TO_ETH), "ethics should be set to WEI_TO_ETH"

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
        assert(c.setForkEthicality(event1, WEI_TO_ETH) == 1), "setForkEthicality wasn't executed successfully"
        assert(c.setForkOutcome(event1, TWO) == 1), "setForkOutcome wasn't executed successfully"
        assert(c.setForkDone(event1) == 1), "setForkDone wasn't executed successfully"
        # check updated values
        assert(c.getForked(event1) == 1), "forked should be set to 1"
        assert(c.getForkEthicality(event1) == WEI_TO_ETH), "forkEthicality should be set to WEI_TO_ETH"
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

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_events(contracts)
