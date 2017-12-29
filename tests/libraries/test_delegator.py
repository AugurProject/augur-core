#!/usr/bin/env python

from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises
from utils import stringToBytes

def test_delegationTargetInitialMemberValues(localFixture):

    delegatorHelperTarget = localFixture.contracts['DelegatorHelperTarget']
    delegatorHelper = localFixture.contracts['DelegatorHelper']

    # Members set at declaration time on the delegation target are not set/retreivable on the delegator unless declared constant
    assert delegatorHelperTarget.intValue() == -42
    assert delegatorHelper.intValue() == 0
    assert delegatorHelperTarget.name() == stringToBytes("Name")
    assert delegatorHelper.name() == stringToBytes("")
    assert delegatorHelper.constantName() == stringToBytes("ConstantName")
    assert delegatorHelper.constantName() == delegatorHelperTarget.constantName()

    # String values are retrievable, but like ints are not set at declaration time.
    assert delegatorHelperTarget.stringMember() == "StringMember"
    assert delegatorHelperTarget.stringConstant() == "StringConstant"
    assert delegatorHelper.stringMember() == ""
    assert delegatorHelper.stringConstant() == ""
    assert delegatorHelper.setStringMember("StringValue")
    assert delegatorHelper.stringMember() == "StringValue"
    assert delegatorHelper.getStringMember() == "StringValue"

    # Once a non-string member is explicitly set on the delegator it will have the newly provided value
    assert delegatorHelper.setName("NewName")
    assert delegatorHelper.getName() == stringToBytes("NewName")
    assert delegatorHelper.name() == stringToBytes("NewName")
    assert delegatorHelper.name() != delegatorHelperTarget.name()

    assert delegatorHelper.setIntValue(1)
    assert delegatorHelper.getIntValue() == 1
    assert delegatorHelper.intValue() == 1
    assert delegatorHelper.intValue() != delegatorHelperTarget.intValue()


def test_delegationMapStorage(localFixture):

    delegatorHelper = localFixture.contracts['DelegatorHelper']

    # We can store maps and access them in a delegator
    assert delegatorHelper.getMapValue(1) == 0
    assert delegatorHelper.addToMap(1, 42)
    assert delegatorHelper.getMapValue(1) == 42


def test_delegationArrayStorage(localFixture):

    delegatorHelper = localFixture.contracts['DelegatorHelper']

    # We can store arrays and access them in a delegator
    assert delegatorHelper.getArraySize() == 0

    with raises(TransactionFailed):
        delegatorHelper.getArrayValue(0)

    assert delegatorHelper.pushArrayValue(42)
    assert delegatorHelper.getArraySize() == 1
    assert delegatorHelper.getArrayValue(0) == 42


def test_delegationExternalContractCalls(localFixture):

    delegatorHelperTarget = localFixture.contracts['DelegatorHelperTarget']
    delegatorHelper = localFixture.contracts['DelegatorHelper']

    # We can make external calls in a function of a delegated contract and recieve back values correctly
    assert delegatorHelper.setOtherContract(delegatorHelperTarget.address)
    assert delegatorHelper.getOtherName() == stringToBytes("Name")

    assert delegatorHelper.addToOtherMap(1, 2)
    assert delegatorHelper.getOtherMapValue(1) == 2


def test_delegationInputsAndOutputs(localFixture):

    delegatorHelper = localFixture.contracts['DelegatorHelper']

    # The size of our input data and output data are constrained only in the same way as all other functions by the evm.
    assert delegatorHelper.noInputReturn() == 1

    delegatorHelper.manyInputsNoReturn(1, 2, 3, 4)

    # We can return dynamic arrays or arrays of fixed size.
    assert delegatorHelper.returnDynamic() == [1L, 0L, 0L, 0L, 0L]
    assert delegatorHelper.returnFixed() == [1L, 0L, 0L, 0L, 0L]

@fixture(scope="session")
def localSnapshot(fixture, controllerSnapshot):
    fixture.resetToSnapshot(controllerSnapshot)
    fixture.uploadAugur()
    name = "DelegatorHelper"
    targetName = "DelegatorHelperTarget"
    fixture.uploadAndAddToController("solidity_test_helpers/DelegatorHelper.sol", targetName, name)
    fixture.uploadAndAddToController("../source/contracts/libraries/Delegator.sol", name, "delegator", constructorArgs=[fixture.contracts['Controller'].address, stringToBytes(targetName)])
    fixture.contracts[name] = fixture.applySignature(name, fixture.contracts[name].address)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture
