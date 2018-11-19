from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString, twentyZeros, thirtyTwoZeros
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed

def test_reputation_token_creation(localFixture, mockUniverse):
    reputationToken = localFixture.upload('../source/contracts/reporting/ReputationToken.sol', 'reputationToken', constructorArgs=[localFixture.contracts['Controller'].address, mockUniverse.address, mockUniverse.address])

    assert reputationToken.getTypeName() == stringToBytes('ReputationToken')
    assert reputationToken.getUniverse() == mockUniverse.address

def test_reputation_token_migrate_in(localFixture, mockUniverse, initializedReputationToken, mockReputationToken, mockMarket):
    with raises(TransactionFailed, message="caller needs to be reputation token"):
        initializedReputationToken.migrateIn(tester.a1, 100)

    with raises(TransactionFailed, message="calling reputation token has to be parent universe's reputation token"):
        mockReputationToken.callMigrateIn(initializedReputationToken.address, tester.a1, 1000)

    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')
    parentUniverse.setReputationToken(mockReputationToken.address)
    mockUniverse.setParentUniverse(parentUniverse.address)
    parentUniverse.setForkEndTime(1000000000000000)
    mockReputationToken.setUniverse(mockUniverse.address)
    with raises(TransactionFailed, message="parent universe needs to have a forking market"):
        mockReputationToken.callMigrateIn(initializedReputationToken.address, tester.a1, 100)

    parentUniverse.setForkingMarket(mockMarket.address)

    assert initializedReputationToken.totalSupply() == 100
    mockReputationToken.callMigrateIn(initializedReputationToken.address, tester.a1, 100)
    assert initializedReputationToken.totalSupply() == 200

    mockReputationToken.callMigrateIn(initializedReputationToken.address, tester.a2, 100)
    assert initializedReputationToken.totalSupply() == 300

def test_reputation_token_trusted_transfer(localFixture, mockUniverse, initializedReputationToken, mockMarket, mockDisputeWindow, mockLegacyReputationToken):
    with raises(TransactionFailed, message="universe does not contain dispute window and caller has to be a IDisputeWindow"):
        initializedReputationToken.trustedDisputeWindowTransfer(tester.a1, tester.a2, 100)

    with raises(TransactionFailed, message="universe does not contain dispute window"):
        mockDisputeWindow.callTrustedDisputeWindowTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)

    with raises(TransactionFailed, message="universe does not contain market"):
        mockMarket.callTrustedMarketTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)

    with raises(TransactionFailed, message="universe does not contain participation token"):
        mockDisputeWindow.callTrustedDisputeWindowTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)

    mockUniverse.setIsContainerForDisputeWindow(True)
    with raises(TransactionFailed, message="source balance can not be 0"):
        mockDisputeWindow.callTrustedDisputeWindowTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)


    assert initializedReputationToken.totalSupply() == 100
    assert initializedReputationToken.balanceOf(tester.a1) == 0
    assert initializedReputationToken.transfer(tester.a1, 35)
    assert initializedReputationToken.totalSupply() == 100
    assert initializedReputationToken.balanceOf(tester.a2) == 0
    assert initializedReputationToken.balanceOf(tester.a1) == 35

    with raises(TransactionFailed, message="transfer has to be approved"):
        mockDisputeWindow.callTrustedDisputeWindowTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)

    assert mockDisputeWindow.callTrustedDisputeWindowTransfer(initializedReputationToken.address, tester.a1, tester.a2, 35)
    # TODO find out why total supply grows
    assert initializedReputationToken.totalSupply() == 100
    assert initializedReputationToken.balanceOf(tester.a2) == 35
    assert initializedReputationToken.balanceOf(tester.a1) == 0

@fixture(scope="session")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockLegacyReputationToken = fixture.contracts['MockLegacyReputationToken']
    controller.registerContract(stringToBytes('LegacyReputationToken'), mockLegacyReputationToken.address)
    mockLegacyReputationToken.setTotalSupply(100)
    mockLegacyReputationToken.setBalanceOfValueFor(tester.a0, 100)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def mockUniverse(localFixture):
    mockUniverse = localFixture.contracts['MockUniverse']
    return mockUniverse

@fixture
def mockReputationToken(localFixture):
    mockReputationToken = localFixture.contracts['MockReputationToken']
    return mockReputationToken

@fixture
def mockMarket(localFixture):
    mockMarket = localFixture.contracts['MockMarket']
    return mockMarket

@fixture
def mockDisputeWindow(localFixture):
    return localFixture.contracts['MockDisputeWindow']

@fixture
def mockDisputeWindow(localFixture):
    return localFixture.contracts['MockDisputeWindow']

@fixture
def mockLegacyReputationToken(localFixture):
    return localFixture.contracts['MockLegacyReputationToken']

@fixture
def mockAugur(localFixture):
    return localFixture.contracts['MockAugur']

@fixture
def initializedReputationToken(localFixture, mockUniverse, mockLegacyReputationToken):
    reputationToken = localFixture.upload('../source/contracts/reporting/ReputationToken.sol', 'reputationToken', constructorArgs=[localFixture.contracts['Controller'].address, mockUniverse.address, mockUniverse.address])
    totalSupply = 11 * 10**6 * 10**18
    assert mockLegacyReputationToken.faucet(totalSupply)
    assert mockLegacyReputationToken.approve(reputationToken.address, totalSupply)
    assert reputationToken.migrateFromLegacyReputationToken()
    return reputationToken
