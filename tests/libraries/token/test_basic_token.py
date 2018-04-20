
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longToHexString, stringToBytes, twentyZeros, thirtyTwoZeros, AssertLog
from pytest import fixture, raises


def test_basic_token_transfer(localFixture, chain, mockToken):
    assert mockToken.mint(tester.a1, 100)
    assert mockToken.balanceOf(tester.a1) == 100
    assert mockToken.balanceOf(tester.a2) == 0
    with raises(AttributeError, message="can not call internal method"):
        mockToken.internalTransfer(tester.a1, tester.a2, 100)

    with raises(TransactionFailed, message="can not cause negative balance"):
        mockToken.callInternalTransfer(tester.a1, tester.a2, 150)

    assert mockToken.callInternalTransfer(tester.a1, tester.a2, 100)
    assert mockToken.balanceOf(tester.a1) == 0
    assert mockToken.balanceOf(tester.a2) == 100

    value =  2**256-1
    assert mockToken.mint(tester.a1, value)

    with raises(TransactionFailed, message="can not cause user to overflow balance"):
        mockToken.callInternalTransfer(tester.a1, tester.a2, value)

def test_basic_token_emit(localFixture, mockToken):
    assert mockToken.mint(tester.a1, 101)
    transferLog = {
        'value': 101L
    }
    with AssertLog(localFixture, "Transfer", transferLog, contract=mockToken):
        assert mockToken.callInternalTransfer(tester.a1, tester.a2, 101)

    assert mockToken.balanceOf(tester.a2) == 101


@fixture
def localSnapshot(fixture, augurInitializedSnapshot):
    fixture.resetToSnapshot(augurInitializedSnapshot)
    controller = fixture.contracts['Controller']
    mockAugur = fixture.uploadAndAddToController("solidity_test_helpers/MockAugur.sol", "Augur")
    mockToken = fixture.uploadAndAddToController("solidity_test_helpers/MockToken.sol")
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def mockAugur(localFixture):
    return localFixture.contracts['MockAugur']

@fixture
def chain(localFixture):
    return localFixture.chain

@fixture
def mockToken(localFixture):
    return localFixture.contracts['MockToken']
