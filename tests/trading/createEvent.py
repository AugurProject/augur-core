#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

# TODO update create event tests pending final review of contract
def test_CreateEvent(contracts):
    t = contracts._ContractLoader__tester
    def test_checkEventCreationPreconditions():
        contracts._ContractLoader__state.mine(1)
        branch = 1010101
        periodLength = 9000
        description = "test binary event"
        expDate = 3000000000
        fxpMinValue = utils.fix(1)
        fxpMaxValue = utils.fix(2)
        numOutcomes = 2
        resolution = "http://lmgtfy.com"
        resolutionAddress = t.a2
        currency = contracts.cash.address
        forkResolveAddress = contracts.forkResolution.address
        try:
            contracts.createEvent.checkEventCreationPreconditions(branch, periodLength, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)
        except Exception as exc:
            assert(isinstance(exc, ethereum.tester.TransactionFailed)), "checkEventCreationPreconditions should throw when createEvent contract is not the caller"
    def test_publicCreateEvent():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.publicDepositEther(value=utils.fix(10000), sender=t.k1) == 1), "Convert ether to cash"
        assert(contracts.cash.approve(contracts.createEvent.address, utils.fix(10000), sender=t.k1) == 1), "Approve createEvent contract to spend cash (for validity bond)"
        branch = 1010101
        assert(contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1) == 1), "Hit Reputation faucet"
        description = "test binary event"
        expDate = 3000000000
        fxpMinValue = utils.fix(1)
        fxpMaxValue = utils.fix(2)
        numOutcomes = 2
        resolution = "http://lmgtfy.com"
        resolutionAddress = t.a2
        currency = contracts.cash.address
        forkResolveAddress = contracts.forkResolution.address
        eventID = contracts.createEvent.publicCreateEvent(branch, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)
        assert(eventID != 0), "Event created"
        assert(contracts.info.getDescription(eventID) == description), "Description matches input"
        assert(contracts.events.getExpiration(eventID) == expDate), "Expiration date matches input"
        assert(contracts.events.getMinValue(eventID) == fxpMinValue), "Min value matches input"
        assert(contracts.events.getMaxValue(eventID) == fxpMaxValue), "Max value matches input"
        assert(contracts.events.getNumOutcomes(eventID) == numOutcomes), "Number of outcomes matches input"
        assert(contracts.events.getEventResolution(eventID) == resolution), "Resolution matches input"
        assert(utils.hex2str(contracts.events.getEventType(eventID)) == "62696e6172790000000000000000000000000000000000000000000000000000"), "Event type is binary"
    test_checkEventCreationPreconditions()
    test_publicCreateEvent()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_CreateEvent(contracts)
