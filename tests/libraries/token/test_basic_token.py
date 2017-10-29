
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longToHexString, stringToBytes
from pytest import fixture, raises


def test_basic_token_transfer(localFixture, mockToken, mockAugur):
    
    assert mockToken.mint(tester.a1, 100)
    assert mockToken.balanceOf(tester.a1) == 100
    assert mockToken.balanceOf(tester.a2) == 0
    with raises(AttributeError, message="can not call internal method"):
        mockToken.internalTransfer(tester.a1, tester.a2, 100)

    assert mockToken.callInternalTransfer(tester.a1, tester.a2, 100)
    assert mockToken.balanceOf(tester.a1) == 0
    assert mockToken.balanceOf(tester.a2) == 100


@fixture
def localSnapshot(fixture, augurInitializedSnapshot):
    fixture.resetToSnapshot(augurInitializedSnapshot)
    controller = fixture.contracts['Controller']
    mockToken = fixture.uploadAndAddToController("solidity_test_helpers/MockToken.sol")
    mockAugur = fixture.uploadAndAddToController("solidity_test_helpers/MockAugur.sol")
    controller.setValue(stringToBytes('Augur'), mockAugur.address)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def mockAugur(localFixture):
    return localFixture.contracts['MockAugur']

@fixture
def mockToken(localFixture):
    return localFixture.contracts['MockToken']