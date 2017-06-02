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

def test_expiringEvents(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
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
    WEI_TO_ETH = 10**18
    subsidy1 = 15*WEI_TO_ETH

    def test_addEvent():
        assert(c.getEvents(branch1, period1) == []), "events should be an empty array"
        assert(c.getEventsRange(branch1, period1, 0, 5) == [0, 0, 0, 0, 0]), "events ranged 0 to 5 should have been an array of 0s"
        assert(c.getNumberEvents(branch1, period1) == 0), "number of events should be 0 by default"
        assert(c.getEventIndex(branch1, period1, event1) == 0), "event at event1 position should be 0 since it hasn't been added yet"
        assert(c.getEvent(branch1, period1, 0) == 0), "event 0 should be 0 as no event has been added"
        assert(c.addEvent(branch1, period1, event1, subsidy1, cashAddr, cashWallet, 0) == 1), "addEvent didn't execute successfully"
        assert(contracts.events.initializeEvent(event1, branch1, period1, WEI_TO_ETH, WEI_TO_ETH*2, 2, "https://someresolution.eth", address0, address1, address2) == 1), "events.initializeEvent didn't execute successfully"
        assert(c.addEvent(branch1, period1, event2, subsidy1, cashAddr, cashWallet, 0) == 1), "addEvent didn't execute successfully"
        assert(contracts.events.initializeEvent(event2, branch1, period1, WEI_TO_ETH, WEI_TO_ETH*4, 4, "https://someresolution.eth", address0, address1, address2) == 1), "events.initializeEvent didn't execute successfully"
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
        assert(c.setEthicReport(branch1, period1, event1, WEI_TO_ETH, address0) == 1), "setEthicReport wasn't executed successfully"
        assert(c.getEthicReport(branch1, period1, event1, address0) == WEI_TO_ETH), "ethicReport for event1 address0 should be set to 10**18 (WEI_TO_ETH)"

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
        assert(contracts.events.initializeEvent(event3, branch2, period0, WEI_TO_ETH, WEI_TO_ETH*4, 4, "https://someresolution.eth", address0, address1, address2) == 1), "events.initializeEvent wasn't executed successfully"
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

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_expiringEvents(contracts)
