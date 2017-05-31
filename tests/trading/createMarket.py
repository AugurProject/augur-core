#!/usr/bin/env python

from __future__ import division
import os
import sys
import iocapture
import ethereum.tester
from decimal import *
import utils

# TODO update create market tests pending final review of contract
def test_CreateMarket(contracts):
    t = contracts._ContractLoader__tester
    def test_publicCreateMarket():
        contracts._ContractLoader__state.mine(1)
        assert(contracts.cash.publicDepositEther(value=utils.fix(10000), sender=t.k1) == 1), "Convert ether to cash"
        assert(contracts.cash.approve(contracts.createEvent.address, utils.fix(10000), sender=t.k1) == 1), "Approve createEvent contract to spend cash (for validity bond)"
        assert(contracts.cash.approve(contracts.createMarket.address, utils.fix(10000), sender=t.k1) == 1), "Approve createMarket contract to spend cash"
        branch = 1010101
        assert(contracts.reputationFaucet.reputationFaucet(branch, sender=t.k1) == 1), "Hit Reputation faucet"
        description = "test binary event"
        expDate = 3000000001
        fxpMinValue = utils.fix(1)
        fxpMaxValue = utils.fix(2)
        numOutcomes = 2
        resolution = "http://lmgtfy.com"
        resolutionAddress = t.a2
        currency = contracts.cash.address
        forkResolveAddress = contracts.forkResolution.address
        eventID = contracts.createEvent.publicCreateEvent(branch, description, expDate, fxpMinValue, fxpMaxValue, numOutcomes, resolution, resolutionAddress, currency, forkResolveAddress, sender=t.k1)
        fxpTradingFee = 20000000000000001
        tag1 = 123
        tag2 = 456
        tag3 = 789
        extraInfo = "rabble rabble rabble"
        marketID = contracts.createMarket.publicCreateMarket(branch, fxpTradingFee, eventID, tag1, tag2, tag3, extraInfo, currency, 0, 0, sender=t.k1, value=utils.fix(10000))
        assert(marketID != 0)
        assert(contracts.markets.getTradingFee(marketID) == fxpTradingFee), "Trading fee matches input"
        assert(contracts.markets.getMarketEvent(marketID) == eventID), "Market event matches input"
        assert(contracts.markets.getTags(marketID) == [tag1, tag2, tag3]), "Tags array matches input"
        assert(contracts.markets.getTopic(marketID)), "Topic matches input tag1"
        assert(contracts.markets.getExtraInfo(marketID) == extraInfo), "Extra info matches input"
        assert(contracts.cash.publicDepositEther(value=utils.fix(10000), sender=t.k1) == 1), "Convert ether to cash"
        assert(contracts.cash.approve(contracts.createEvent.address, utils.fix(10000), sender=t.k1) == 1), "Approve createEvent contract to spend cash (for validity bond)"
        assert(contracts.cash.approve(contracts.createMarket.address, utils.fix(10000), sender=t.k1) == 1), "Approve createMarket contract to spend cash"
        marketID2 = contracts.createMarket.publicCreateMarket(branch, 0, eventID, tag1, tag2, tag3, extraInfo, contracts.markets.getOutcomeShareContract(marketID, 1), marketID, 1, sender=t.k1, value=utils.fix(10000))
    test_publicCreateMarket()

if __name__ == '__main__':
    ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_CreateMarket(contracts)
