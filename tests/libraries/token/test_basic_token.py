
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longToHexString, stringToBytes
from pytest import fixture, raises


def test_basic_token_transfer(localFixture, mockToken, mockAugur):
    
    mockToken.mint(tester.a1, 100)
    assert mockToken.getBalanceForUser(tester.a1) == 100





@fixture
def localSnapshot(fixture, augurInitializedSnapshot):
    fixture.resetToSnapshot(augurInitializedSnapshot)
    controller = fixture.contracts['Controller']
    mockToken = fixture.uploadAndAddToController("solidity_test_helpers/MockToken.sol")
    assert fixture.contracts['MockToken']
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