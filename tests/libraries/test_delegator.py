#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, lazy_fixture, raises
from utils import stringToBytes

@fixture(scope="session")
def delegatorSnapshot(sessionFixture):
    name = "DelegatorHelper"
    targetName = "DelegatorHelperTarget"
    sessionFixture.uploadAndAddToController("solidity_test_helpers/DelegatorHelper.sol", targetName, name)
    sessionFixture.uploadAndAddToController("../src/libraries/Delegator.sol", name, "delegator", constructorArgs=[sessionFixture.controller.address, targetName.ljust(32, '\x00')])
    sessionFixture.contracts[name] = sessionFixture.applySignature(name, sessionFixture.contracts[name].address)
    return sessionFixture.chain.snapshot()

@fixture
def delegatorContractsFixture(sessionFixture, delegatorSnapshot):
    sessionFixture.chain.revert(delegatorSnapshot)
    return sessionFixture


def test_delegationTargetInitialMemberValues(delegatorContractsFixture):

    delegatorHelperTarget = delegatorContractsFixture.contracts['DelegatorHelperTarget']
    delegatorHelper = delegatorContractsFixture.contracts['DelegatorHelper']

    # Members set at declaration time on the delegation target are not set/retreivable on the delegator unless declared constant
    assert delegatorHelperTarget.intValue() == -42
    assert delegatorHelper.intValue() == 0
    assert delegatorHelperTarget.name() == stringToBytes("Name")
    assert delegatorHelper.name() == stringToBytes("")
    assert delegatorHelper.constantName() == stringToBytes("ConstantName")
    assert delegatorHelper.constantName() == delegatorHelperTarget.constantName()

    # Constant string values however are not retrievable. In fact, string values will not work at all with delegated contract storage. See: https://github.com/ethereum/solidity/issues/164#issuecomment-149846605
    assert delegatorHelperTarget.stringMember() == "StringMember"
    assert delegatorHelperTarget.stringConstant() == "StringConstant"
    assert delegatorHelper.stringMember() == ""
    assert delegatorHelper.stringConstant() == ""
    assert delegatorHelper.setStringMember("StringValue")
    assert delegatorHelper.stringMember() == ""
    assert delegatorHelper.getStringMember() == ""

    # Note that even if we do not attempt to pass in the string value and let the contract set the value itself we will not be able to retrieve the value
    assert delegatorHelper.populateStringMember()
    assert delegatorHelper.getStringMember() == ""

    # Once a non-string member is explicitly set on the delegator it will have the newly provided value
    assert delegatorHelper.setName("NewName")
    assert delegatorHelper.getName() == stringToBytes("NewName")
    assert delegatorHelper.name() == stringToBytes("NewName")
    assert delegatorHelper.name() != delegatorHelperTarget.name()

    assert delegatorHelper.setIntValue(1)
    assert delegatorHelper.getIntValue() == 1
    assert delegatorHelper.intValue() == 1
    assert delegatorHelper.intValue() != delegatorHelperTarget.intValue()


def test_delegationMapStorage(delegatorContractsFixture):

    delegatorHelper = delegatorContractsFixture.contracts['DelegatorHelper']

    # We can store maps and access them in a delegator
    assert delegatorHelper.getMapValue(1) == 0
    assert delegatorHelper.addToMap(1, 42)
    assert delegatorHelper.getMapValue(1) == 42


def test_delegationArrayStorage(delegatorContractsFixture):

    delegatorHelper = delegatorContractsFixture.contracts['DelegatorHelper']

    # We can store arrays and access them in a delegator
    assert delegatorHelper.getArraySize() == 0

    with raises(TransactionFailed):
        delegatorHelper.getArrayValue(0)

    assert delegatorHelper.pushArrayValue(42)
    assert delegatorHelper.getArraySize() == 1
    assert delegatorHelper.getArrayValue(0) == 42


def test_delegationExternalContractCalls(delegatorContractsFixture):

    delegatorHelperTarget = delegatorContractsFixture.contracts['DelegatorHelperTarget']
    delegatorHelper = delegatorContractsFixture.contracts['DelegatorHelper']

    # We can make external calls in a function of a delegated contract and recieve back values correctly
    assert delegatorHelper.setOtherContract(delegatorHelperTarget.address)
    assert delegatorHelper.getOtherName() == stringToBytes("Name")

    assert delegatorHelper.addToOtherMap(1, 2)
    assert delegatorHelper.getOtherMapValue(1) == 2


def test_delegationInputsAndOutputs(delegatorContractsFixture):

    delegatorHelper = delegatorContractsFixture.contracts['DelegatorHelper']

    # The size of our input data and output data are constrained only in the same way as all other functions by the evm.
    assert delegatorHelper.noInputReturn() == 1

    delegatorHelper.manyInputsNoReturn(1, 2, 3, 4)

    # We cannot return dynamic arrays or arrays of fixed size.
    # In the dynamic case we recieve an empty array
    assert delegatorHelper.returnDynamic() == []
    # Trying this with a fixed size results in an error (within our testing framework)
    with raises(AssertionError):
        delegatorHelper.returnFixed()
