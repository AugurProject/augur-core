#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises

# These should match the macros in marketFetcher.se
NUM_GET_MARKET_FIELDS = 2

MARKET_ADDRESS = 0
MARKET_CREATION_BLOCK = 1

NUM_GET_MARKET_INFO_FIELDS = 5

# MARKET_ADDRESS = 0
MARKET_FINALIZATION_TIME = 1
MARKET_CREATOR_FEE = 2
MARKET_VOLUME = 3
MARKET_NUM_OUTCOMES = 4

@fixture(scope="session")
def marketFetcherSnapshot(sessionFixture):
    marketFetcher = sessionFixture.upload('../src/extensions/marketFetcher.se')
    marketFetcher.initialize(sessionFixture.controller.address)
    sessionFixture.chain.mine(1)
    return sessionFixture.chain.snapshot()

@fixture
def marketFetcherContractsFixture(sessionFixture, marketFetcherSnapshot):
    sessionFixture.chain.revert(marketFetcherSnapshot)
    return sessionFixture

def test_marketFetcherGetMarketDataHappyPath(marketFetcherContractsFixture):

    market = marketFetcherContractsFixture.binaryMarket
    marketFetcher = marketFetcherContractsFixture.contracts['marketFetcher']

    # We can use the getMarketData function to return a market address and market creation block
    marketData = marketFetcher.getMarketData(market.address)
    assert marketData[MARKET_ADDRESS] == market.address
    # TODO: assert market[MARKET_CREATION_BLOCK] == market.getCreationBlock()

def test_marketFetcherGetMarketsHappyPath(marketFetcherContractsFixture):

    branch = marketFetcherContractsFixture.branch
    market = marketFetcherContractsFixture.binaryMarket
    marketFetcher = marketFetcherContractsFixture.contracts['marketFetcher']

    # We can request markets from the market fetcher and get back market address and creation block for each market returned
    markets = marketFetcher.getMarkets(branch.address)
    assert len(markets) == 3 * NUM_GET_MARKET_FIELDS
    assert markets[MARKET_ADDRESS] == market.address
    # TODO: assert markets[MARKET_CREATION_BLOCK] == market.getCreationBlock()

    # We can limit the markets returned by total number
    markets = marketFetcher.getMarkets(branch.address, 0, 2)
    assert len(markets) == 2 * NUM_GET_MARKET_FIELDS
    assert markets[MARKET_ADDRESS] == market.address

    # We can also begin the markets returned from an existing market (exclusive of the provided market)
    markets = marketFetcher.getMarkets(branch.address, market.address)
    assert len(markets) == 2 * NUM_GET_MARKET_FIELDS
    assert markets[MARKET_ADDRESS] != market.address
    assert markets[NUM_GET_MARKET_FIELDS + MARKET_ADDRESS] != market.address

    # We can also begin the markets returned from an existing market (exclusive of the provided market) and limit the number returned
    markets = marketFetcher.getMarkets(branch.address, market.address, 1)
    assert len(markets) == 1 * NUM_GET_MARKET_FIELDS
    assert markets[MARKET_ADDRESS] != market.address

def test_marketFetcherGetMarketsNoResults(marketFetcherContractsFixture):

    branch = marketFetcherContractsFixture.branch
    marketFetcher = marketFetcherContractsFixture.contracts['marketFetcher']

    # If we provide a starting market that doesn't exist we'll get back no results
    markets = marketFetcher.getMarkets(branch.address, 42)
    assert len(markets) == 0

def test_marketFetcherGetMarketInfoHappyPath(marketFetcherContractsFixture):

    orders = marketFetcherContractsFixture.contracts['orders']
    market = marketFetcherContractsFixture.binaryMarket
    categoricalMarket = marketFetcherContractsFixture.categoricalMarket
    marketFetcher = marketFetcherContractsFixture.contracts['marketFetcher']

    # We can request market info for a market address and get back relevant metadata for that market
    numOutcomes = market.getNumberOfOutcomes()
    expectedLength = NUM_GET_MARKET_INFO_FIELDS + numOutcomes
    marketInfo = marketFetcher.getMarketInfo(market.address, expectedLength)
    AssertMarketInfoCorrect(market, marketInfo, orders)

    # The fields returned are variable in length since we include outcome data and for categorical markets this is variable
    numOutcomes = categoricalMarket.getNumberOfOutcomes()
    expectedLength = NUM_GET_MARKET_INFO_FIELDS + numOutcomes
    marketInfo = marketFetcher.getMarketInfo(categoricalMarket.address, expectedLength)
    AssertMarketInfoCorrect(categoricalMarket, marketInfo, orders)

def test_marketFetcherGetMarketsInfoHappyPath(marketFetcherContractsFixture):

    orders = marketFetcherContractsFixture.contracts['orders']
    market = marketFetcherContractsFixture.binaryMarket
    categoricalMarket = marketFetcherContractsFixture.categoricalMarket
    scalarMarket = marketFetcherContractsFixture.scalarMarket

    marketFetcher = marketFetcherContractsFixture.contracts['marketFetcher']

    # We can request market info by providing a list of market addresses and get back relevant metadata for each market
    requestData = [market.address, categoricalMarket.address, scalarMarket.address]
    markets = marketFetcher.getMarketsInfo(requestData)

    # Since the categorical market has variable outcomes the total expected length has to be custom calculated
    expectedLength = NUM_GET_MARKET_INFO_FIELDS * 3 + market.getNumberOfOutcomes() + categoricalMarket.getNumberOfOutcomes() + scalarMarket.getNumberOfOutcomes()
    assert len(markets) == expectedLength

    # Lets confirm all the returned data is correct
    # First the binary market
    marketInfoLength = NUM_GET_MARKET_INFO_FIELDS + market.getNumberOfOutcomes()
    start = 0
    end = marketInfoLength
    AssertMarketInfoCorrect(market, markets[start:end], orders)

    # Then the categorical market
    categoricalMarketInfoLength = NUM_GET_MARKET_INFO_FIELDS + categoricalMarket.getNumberOfOutcomes()
    start = end
    end = start + categoricalMarketInfoLength
    AssertMarketInfoCorrect(categoricalMarket, markets[start:end], orders)

    # Finally the scalar market
    scalarMarketInfoLength = NUM_GET_MARKET_INFO_FIELDS + scalarMarket.getNumberOfOutcomes()
    start = end
    end = start + scalarMarketInfoLength
    AssertMarketInfoCorrect(scalarMarket, markets[start:end], orders)

def AssertMarketInfoCorrect(market, marketInfo, orders):
    numOutcomes = market.getNumberOfOutcomes()
    expectedLength = NUM_GET_MARKET_INFO_FIELDS + numOutcomes

    assert len(marketInfo) == expectedLength
    assert marketInfo[MARKET_ADDRESS] == market.address
    assert marketInfo[MARKET_FINALIZATION_TIME] == market.getFinalizationTime()
    assert marketInfo[MARKET_CREATOR_FEE] == market.getMarketCreatorSettlementFeeInAttoethPerEth()
    assert marketInfo[MARKET_VOLUME] == orders.getVolume(market.address)
    assert marketInfo[MARKET_NUM_OUTCOMES] == numOutcomes
    outcomeIndex = 0
    while outcomeIndex < numOutcomes:
        assert marketInfo[NUM_GET_MARKET_INFO_FIELDS + outcomeIndex] == orders.getLastOutcomePrice(market.address, outcomeIndex)
        outcomeIndex += 1