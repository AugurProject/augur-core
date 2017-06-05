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

def test_markets(contracts):
    t = contracts._ContractLoader__tester
    s = contracts._ContractLoader__state
    c = contracts.markets
    branch1 = 1010101
    market1 = 1111111111
    event1 = 12345678901
    period1 = contracts.branches.getVotePeriod(branch1)
    gasSubsidy1 = 10**14*234
    creationFee1 = 10**14*340
    twoPercent = 10**16*2
    WEI_TO_ETH = 10**18
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

    def test_initializeMarket():
        assert(c.getMarketsHash(branch1) == 0), "getMarketsHash for branch1 should be defaulted to 0"
        assert(c.initializeMarket(market1, event1, period1, twoPercent, branch1, tag1, tag2, tag3, WEI_TO_ETH, 2, 'this is extra information', gasSubsidy1, creationFee1, expirationDate1, shareContracts, walletContracts, value=gasSubsidy1) == 1), "initializeMarket wasn't executed successfully"
        assert(c.getMarketsHash(branch1) != 0), "marketsHash should no longer be set to 0"
        assert(c.getBranch(market1) == branch1), "branch for market1 should be set to branch1"
        assert(c.getMarketEvent(market1) == event1), "marketEvent for market1 shoudl be event1"
        assert(c.getLastExpDate(market1) == expirationDate1), "lastExpDate for market1 should be set to expirationDate1"
        assert(c.getTags(market1) == [longTag1, longTag2, longTag3]), "tags for market1 should return an array with 3 tags"
        assert(c.getTopic(market1) == longTag1), "topic for market1 should be set to topic1"
        assert(c.getFees(market1) == creationFee1), "fees for market1 should be set to creationFee1"
        assert(c.getTradingFee(market1) == twoPercent), "tradingFee for market1 should be set to twoPercent"
        # assert(c.getVolume(market1) == 0), "volumne for market1 should be set to 0 by default"
        assert(c.getExtraInfo(market1) == 'this is extra information'), "extraInfo for market1 should be set to 'this is extra information'"
        assert(c.getExtraInfoLength(market1) == 25), "extraInfoLength for market1 should be 25"
        assert(c.getGasSubsidy(market1) == gasSubsidy1), "gasSubsidy for market1 should be set to gasSubsidy1"
        assert(c.getMarketNumOutcomes(market1) == 2), "marketNumOutcomes for market1 should be 2"
        assert(c.getCumulativeScale(market1) == WEI_TO_ETH), "cumulativeScale for market1 should be set to WEI_TO_ETH"

    # def test_marketOrders():
    #     assert(c.getOrderIDs(market1) == []), "orderIds for market1 should be an empty array"
    #     assert(c.getTotalOrders(market1) == 0), "totalOrders for market1 should be 0"
    #     assert(c.getLastOrder(market1) == 0), "lastOrder for market1 should be set to 0"
    #
    #     assert(c.addOrderToMarket(market1, orderID1) == 1), "addOrderToMarket wasn't executed successfully"
    #     assert(c.addOrderToMarket(market1, orderID2) == 1), "addOrderToMarket wasn't executed successfully"
    #     assert(c.addOrderToMarket(market1, orderID3) == 1), "addOrderToMarket wasn't executed successfully"
    #     assert(c.addOrderToMarket(market1, orderID4) == 1), "addOrderToMarket wasn't executed successfully"
    #
    #     assert(c.getOrderIDs(market1) == [orderID4, orderID3, orderID2, orderID1]), "orderIds for market1 should return an array of length four containing the orderIds ordered by addition to the array, with most recent addition in the 0 position for the array"
    #     assert(c.getTotalOrders(market1) == 4), "totalOrders for market1 should be 4"
    #     assert(c.getLastOrder(market1) == orderID4), "getLastOrder for market1 should return orderID4"
    #     assert(c.getPrevID(market1, orderID4) == orderID3), "getPrevID for orderID4 should return orderID3"
    #     assert(c.getPrevID(market1, orderID3) == orderID2), "getPrevID for orderID3 should return orderID2"
    #     assert(c.getPrevID(market1, orderID2) == orderID1), "getPrevID for orderID2 should return orderID1"
    #     assert(c.getPrevID(market1, orderID1) == 0), "getPrevId for orderID1 should return 0"
    #
    #     assert(c.removeOrderFromMarket(market1, orderID2) == 1), "removeOrderFromMarket wasn't executed successfully"
    #
    #     assert(c.getOrderIDs(market1) == [orderID4, orderID3, orderID1]), "getOrderIDs should now return only 3 topics in the array, ordered 4, 3, 1 after removing order 2"
    #     assert(c.getPrevID(market1, orderID3) == orderID1), "getPrevID for orderID3 should return orderID1 instead of orderID2 as orderID2 has been removed"
    #     assert(c.getPrevID(market1, orderID2) == 0), "getPrevID for orderID2 should return 0 as orderID2 was removed and not part of the orderbook"
    #     assert(c.getLastOrder(market1) == orderID4), "lastOrder for market1 should be orderID4"
    #
    #     assert(c.removeOrderFromMarket(market1, orderID4) == 1), "removeOrderFromMarket wasn't executed successfully"
    #
    #     assert(c.getOrderIDs(market1) == [orderID3, orderID1]), "getOrderIDs should now return an array with only 2 topics, 3 and 1 as both 4 and 2 have been removed"
    #     assert(c.getPrevID(market1, orderID4) == 0), "getPrevID for orderID4 should be set to 0 as it has been removed and is not part of the orderbook"
    #     assert(c.getLastOrder(market1) == orderID3), "lastOrder for market1 should now be set to orderID3 since orderID4 was removed"
    #     assert(c.getTotalOrders(market1) == 2), "totalOrders for market1 should be 2"

    def test_marketShares():
        assert(c.getSharesValue(market1) == 0), "shareValue for market1 should be set to 0 by default"
        assert(c.getMarketShareContracts(market1) == [shareAddr1, shareAddr2]), "marketShareContracts should be an array of length 2 with shareAddr1 and shareAddr2 contained within"
        assert(c.getTotalSharesPurchased(market1) == 0), "totalSharesPurchased for market1 should be set to 0"
        assert(c.getSharesPurchased(market1, 1) == 0), "sharesPurchased for market1, outcome 1 should be set to 0"
        assert(c.getSharesPurchased(market1, 2) == 0), "sharesPurchased for market1, outcome 2 should be set to 0"
        assert(c.getParticipantSharesPurchased(market1, address1, 1) == 0), "participantSharesPurchased for address1 on market1 for outcome 1 should be set to 0"
        assert(c.getParticipantSharesPurchased(market1, address1, 2) == 0), "participantSharesPurchased for address1 on market1 for outcome 2 should be set to 0"
        assert(c.modifySharesValue(market1, WEI_TO_ETH) == 1), "modifySharesValue wasn't executed successfully"
        assert(c.getSharesValue(market1) == WEI_TO_ETH), "getSharesValue for market1 should be set to WEI_TO_ETH"
        # assert(c.getVolume(market1) == 0), "volume for market1 should be set to 0"
        # assert(c.modifyMarketVolume(market1, WEI_TO_ETH*15) == 1), "modifyMarketVolume wasn't executed successfully"
        # assert(c.getVolume(market1) == WEI_TO_ETH*15), "volume for market1 should be set to WEI_TO_ETH*15"
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

        # assert(c.getLastOutcomePrice(market1, 1) == 0), "lastOutcomePrice for market1, outcome 1 should be 0"
        # assert(c.getLastOutcomePrice(market1, 2) == 0), "lastOutcomePrice for market1, outcome 2 should be 0"
        # assert(c.setPrice(market1, 1, 123) == 1), "setPrice wasn't executed successfully"
        # assert(c.setPrice(market1, 2, 456) == 1), "setPrice wasn't executed successfully"
        # assert(c.getLastOutcomePrice(market1, 1) == 123), "lastOutcomePrice for market1, outcome 1 should be set to 123"
        # assert(c.getLastOutcomePrice(market1, 2) == 456), "lastOutcomePrice for market1, outcome 2 should be set to 456"

        assert(c.getMarketResolved(market1) == 0), "marketResolved for market1 shoudl be set to 0"
        assert(c.setMarketResolved(market1) == 1), "setMarketResolved wasn't executed successfully"
        assert(c.getMarketResolved(market1) == 1), "marketResolved for market1 shoudl be set to 1"

        addr1Bal = s.block.get_balance(t.a1)
        assert(s.block.get_balance(c.address) == gasSubsidy1), "the market contract balance was expected to be set to gasSubsidy1"
        assert(c.refundClosing(market1, address1) == 1), "refundClosing wasn't executed successfully"
        assert(s.block.get_balance(t.a1) == addr1Bal + gasSubsidy1), "the balance of address1 should now be it's previous balance + the gasSubsidy1 from market1"

    test_initializeMarket()
    # test_marketOrders()
    test_marketShares()
    test_marketSettings()

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(ROOT, "upload_contracts"))
    from upload_contracts import ContractLoader
    contracts = ContractLoader(os.path.join(ROOT, "src"), "controller.se", ["mutex.se", "cash.se", "repContract.se"])
    test_markets(contracts)
