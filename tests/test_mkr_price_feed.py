from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, raises
from utils import longTo32Bytes, PrintGasUsed, fix
from datetime import timedelta
from ethereum.utils import ecsign, sha3, normalize_key, int_to_32bytearray, bytearray_to_bytestr, zpad

def test_rep_price_bridge(localFixture, medianizer, feedFactory, repPriceOracle, controller):
    # Add 2 price feeds
    # Change price
    # confirm on medianizer
    # set price manually
    # ask price
    # create the bridge
    # transfer ownership to the bridge
    # Change price
    # poke bridge
    # ask price
    pass

def test_price_feed_wrapper(localFixture, medianizer, feedFactory, repPriceOracle, controller):
    # Add 2 price feeds
    # create the bridge
    # transfer ownership to the bridge
    # wrap price feeds
    # Change price
    # ask price
    pass

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    augur = fixture.contracts["Augur"]
    kitchenSinkSnapshot['Medianizer'] = fixture.upload('solidity_test_helpers/MkrPriceFeed/Medianizer.sol', "Medianizer")
    kitchenSinkSnapshot['FeedFactory'] = fixture.upload('solidity_test_helpers/MkrPriceFeed/FeedFactory.sol', "FeedFactory")
    kitchenSinkSnapshot['PriceFeed'] = fixture.upload('solidity_test_helpers/MkrPriceFeed/PriceFeed.sol', "PriceFeed")

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def medianizer(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['Medianizer'].translator, kitchenSinkSnapshot['Medianizer'].address)

@fixture
def feedFactory(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['FeedFactory'].translator, kitchenSinkSnapshot['FeedFactory'].address)

@fixture
def repPriceOracle(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['RepPriceOracle']

@fixture
def controller(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['Controller']

