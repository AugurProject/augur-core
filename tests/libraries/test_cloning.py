#!/usr/bin/env python

from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises
from utils import stringToBytes

def test_cloneFactory(localFixture):
    clone = localFixture.contracts['Clone']
    assert clone.getTypeName().startswith("DelegatorHelper")

def test_cloneTargetInitialMemberValues(localFixture):
    clone = localFixture.contracts['Clone']
    cloneTarget = localFixture.contracts['DelegatorHelper']

    # Members set at declaration time on the delegation target are not set/retreivable on the delegator unless declared constant
    assert cloneTarget.intValue() == -42
    assert clone.intValue() == 0
    assert cloneTarget.name() == stringToBytes("Name")
    assert clone.name() == stringToBytes("")
    assert clone.constantName() == stringToBytes("ConstantName")
    assert clone.constantName() == cloneTarget.constantName()

    # String values are retrievable, but like ints are not set at declaration time.
    assert cloneTarget.stringMember() == "StringMember"
    assert cloneTarget.stringConstant() == "StringConstant"
    assert clone.stringMember() == ""
    assert clone.stringConstant() == ""
    assert clone.setStringMember("StringValue")
    assert clone.stringMember() == "StringValue"
    assert clone.getStringMember() == "StringValue"

    # Once a non-string member is explicitly set on the delegator it will have the newly provided value
    assert clone.setName("NewName")
    assert clone.getName() == stringToBytes("NewName")
    assert clone.name() == stringToBytes("NewName")
    assert clone.name() != cloneTarget.name()

    assert clone.setIntValue(1)
    assert clone.getIntValue() == 1
    assert clone.intValue() == 1
    assert clone.intValue() != cloneTarget.intValue()


def test_delegationMapStorage(localFixture):
    clone = localFixture.contracts['Clone']
    cloneTarget = localFixture.contracts['DelegatorHelper']

    # We can store maps and access them in a delegator
    assert clone.getMapValue(1) == 0
    assert clone.addToMap(1, 42)
    assert clone.getMapValue(1) == 42


def test_delegationArrayStorage(localFixture):
    clone = localFixture.contracts['Clone']
    cloneTarget = localFixture.contracts['DelegatorHelper']

    # We can store arrays and access them in a delegator
    assert clone.getArraySize() == 0

    with raises(TransactionFailed):
        clone.getArrayValue(0)

    assert clone.pushArrayValue(42)
    assert clone.getArraySize() == 1
    assert clone.getArrayValue(0) == 42


def test_delegationExternalContractCalls(localFixture):
    clone = localFixture.contracts['Clone']
    cloneTarget = localFixture.contracts['DelegatorHelper']

    # We can make external calls in a function of a delegated contract and recieve back values correctly
    assert clone.setOtherContract(cloneTarget.address)
    assert clone.getOtherName() == stringToBytes("Name")

    assert clone.addToOtherMap(1, 2)
    assert clone.getOtherMapValue(1) == 2


def test_delegationInputsAndOutputs(localFixture):
    clone = localFixture.contracts['Clone']
    cloneTarget = localFixture.contracts['DelegatorHelper']

    # The size of our input data and output data are constrained only in the same way as all other functions by the evm.
    assert clone.noInputReturn() == 1

    clone.manyInputsNoReturn(1, 2, 3, 4)

    # We can return dynamic arrays or arrays of fixed size.
    assert clone.returnDynamic() == [1L, 0L, 0L, 0L, 0L]
    assert clone.returnFixed() == [1L, 0L, 0L, 0L, 0L]

@fixture(scope="session")
def localSnapshot(fixture, controllerSnapshot):
    fixture.resetToSnapshot(controllerSnapshot)
    fixture.uploadAugur()
    fixture.uploadAndAddToController("solidity_test_helpers/DelegatorHelper.sol")
    delegatorHelperFactory = fixture.uploadAndAddToController("solidity_test_helpers/DelegatorHelperFactory.sol")
    delegatorHelperAddress = delegatorHelperFactory.createDelegatorHelper(fixture.contracts['Controller'].address)
    fixture.contracts["Clone"] = fixture.applySignature("DelegatorHelper", delegatorHelperAddress)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture
