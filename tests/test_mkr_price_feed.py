from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, raises
from utils import longTo32Bytes, PrintGasUsed, fix, bytesToLong, bytesToHexString
from datetime import timedelta
from ethereum.utils import ecsign, sha3, normalize_key, int_to_32bytearray, bytearray_to_bytestr, zpad

def test_rep_price_bridge(localFixture, medianizer, feedFactory, repPriceOracle, controller):
    priceFeed1Addr = feedFactory.create()
    priceFeed2Addr = feedFactory.create()

    medianizer.set(priceFeed1Addr)
    medianizer.set(priceFeed2Addr)

    priceFeed1 = localFixture.applySignature('PriceFeed', priceFeed1Addr)
    priceFeed2 = localFixture.applySignature('PriceFeed', priceFeed2Addr)

    expirationTime = controller.getTimestamp() + 10**9

    priceFeed1.post(1, expirationTime, medianizer.address)
    priceFeed2.post(2, expirationTime, medianizer.address)

    assert bytesToLong(medianizer.read()) == 2

    assert repPriceOracle.setRepPriceInAttoEth(3)

    assert repPriceOracle.getRepPriceInAttoEth() == 3

    repPriceBridge = localFixture.upload('../source/contracts/external/RepPriceBridge.sol', "RepPriceBridge", constructorArgs=[repPriceOracle.address, medianizer.address])

    assert repPriceOracle.transferOwnership(repPriceBridge.address)

    priceFeed1.post(10, expirationTime, medianizer.address)
    priceFeed2.post(20, expirationTime, medianizer.address)

    assert bytesToLong(medianizer.read()) == 15

    assert repPriceBridge.poke()

    assert repPriceOracle.getRepPriceInAttoEth() == 15


def test_price_feed_wrapper(localFixture, medianizer, feedFactory, repPriceOracle, controller):
    priceFeed1Addr = feedFactory.create()
    priceFeed2Addr = feedFactory.create()

    medianizer.set(priceFeed1Addr)
    medianizer.set(priceFeed2Addr)

    priceFeed1 = localFixture.applySignature('PriceFeed', priceFeed1Addr)
    priceFeed2 = localFixture.applySignature('PriceFeed', priceFeed2Addr)

    expirationTime = controller.getTimestamp() + 10**9

    priceFeed1.post(1, expirationTime, medianizer.address)
    priceFeed2.post(2, expirationTime, medianizer.address)

    assert bytesToLong(medianizer.read()) == 2

    assert repPriceOracle.setRepPriceInAttoEth(3)

    assert repPriceOracle.getRepPriceInAttoEth() == 3

    repPriceBridge = localFixture.upload('../source/contracts/external/RepPriceBridge.sol', "RepPriceBridge", constructorArgs=[repPriceOracle.address, medianizer.address])

    assert repPriceOracle.transferOwnership(repPriceBridge.address)

    priceFeedWrapper1 = localFixture.upload('../source/contracts/external/PriceFeedWrapper.sol', "PriceFeedWrapper", constructorArgs=[priceFeed1.address, repPriceBridge.address])
    priceFeedWrapper2 = localFixture.upload('../source/contracts/external/PriceFeedWrapper.sol', "PriceFeedWrapper", constructorArgs=[priceFeed2.address, repPriceBridge.address])

    # Upload Authority contract
    # Set Authority on the price feeds to Authority
    # Authorize the priceFeedWrappers to be able to call "post(uint128 val, uint32 zzz, address med)"

    priceFeedWrapper1.post(10, expirationTime, medianizer.address)
    priceFeedWrapper2.post(20, expirationTime, medianizer.address)

    assert repPriceOracle.getRepPriceInAttoEth() == 15


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    augur = fixture.contracts["Augur"]
    kitchenSinkSnapshot['Medianizer'] = fixture.upload('../source/contracts/external/MkrPriceFeed/Medianizer.sol', "Medianizer")
    kitchenSinkSnapshot['FeedFactory'] = fixture.upload('../source/contracts/external/MkrPriceFeed/FeedFactory.sol', "FeedFactory")
    kitchenSinkSnapshot['PriceFeed'] = fixture.upload('../source/contracts/external/MkrPriceFeed/PriceFeed.sol', "PriceFeed")

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
