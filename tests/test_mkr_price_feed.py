from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, raises
from utils import longTo32Bytes, PrintGasUsed, fix, bytesToLong, bytesToHexString, stringToBytes, longToHexString
from datetime import timedelta
from os import path
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
    assert repPriceBridge.poke()

    assert bytesToLong(medianizer.read()) == 6
    assert repPriceOracle.getRepPriceInAttoEth() == 6

    priceFeed2.post(20, expirationTime, medianizer.address)
    assert repPriceBridge.poke()

    assert bytesToLong(medianizer.read()) == 15
    assert repPriceOracle.getRepPriceInAttoEth() == 15


def test_price_feed_wrapper(localFixture, medianizer, feedFactory, guardFactory, repPriceOracle, controller):
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

    priceFeedWrapper1 = localFixture.upload('../source/contracts/external/PriceFeedWrapper.sol', "PriceFeedWrapper1", constructorArgs=[priceFeed1.address, repPriceBridge.address])
    priceFeedWrapper2 = localFixture.upload('../source/contracts/external/PriceFeedWrapper.sol', "PriceFeedWrapper2", constructorArgs=[priceFeed2.address, repPriceBridge.address])

    guardAddress = guardFactory.newGuard()
    localFixture.signatures["DSGuard"] = localFixture.generateSignature(resolveRelativePath("../source/contracts/external/MkrPriceFeed/DSGuard.sol"))
    guard = localFixture.applySignature("DSGuard", guardAddress)

    priceFeed1.setAuthority(guardAddress)
    priceFeed2.setAuthority(guardAddress)

    funcSig = sha3("post(uint128,uint32,address)")[0:4]

    guard.permit(priceFeedWrapper1.address, priceFeed1Addr, funcSig)
    guard.permit(priceFeedWrapper2.address, priceFeed2Addr, funcSig)

    priceFeedWrapper1.post(10, expirationTime, medianizer.address)

    assert bytesToLong(medianizer.read()) == 6
    assert repPriceOracle.getRepPriceInAttoEth() == 6

    priceFeedWrapper2.post(20, expirationTime, medianizer.address)

    assert bytesToLong(medianizer.read()) == 15
    assert repPriceOracle.getRepPriceInAttoEth() == 15


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    augur = fixture.contracts["Augur"]
    kitchenSinkSnapshot['Medianizer'] = fixture.upload('../source/contracts/external/MkrPriceFeed/Medianizer.sol', "Medianizer")
    kitchenSinkSnapshot['FeedFactory'] = fixture.upload('../source/contracts/external/MkrPriceFeed/FeedFactory.sol', "FeedFactory")
    kitchenSinkSnapshot['DSGuardFactory'] = fixture.upload('../source/contracts/external/MkrPriceFeed/DSGuardFactory.sol', "DSGuardFactory")
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
def guardFactory(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['DSGuardFactory'].translator, kitchenSinkSnapshot['DSGuardFactory'].address)

@fixture
def repPriceOracle(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['RepPriceOracle']

@fixture
def controller(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['Controller']

BASE_PATH = path.dirname(path.abspath(__file__))
def resolveRelativePath(relativeFilePath):
    return path.abspath(path.join(BASE_PATH, relativeFilePath))
