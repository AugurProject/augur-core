from ethereum.tools import tester
from utils import fix, longToHexString, bytesToLong

def test_all_the_things(contractsFixture):
    factory = contractsFixture.contracts['IterableMapUint256Factory']
    address = factory.createIterableMapUint256(contractsFixture.controller.address, tester.a0)
    iterableMap = contractsFixture.applySignature('IterableMapUint256', address)
    assert iterableMap.count() == 0
    assert iterableMap.add(5, 10)
    assert iterableMap.getByKey(5) == 10
    assert iterableMap.getByOffset(0) == 5
    assert iterableMap.contains(5)
    assert iterableMap.count() == 1
