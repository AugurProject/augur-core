from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed
from reporting_utils import proceedToDesignatedReporting, proceedToFirstReporting, proceedToLastReporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture


def test_reputation_token_creation(localFixture, mockUniverse):
    reputationToken = localFixture.upload('../source/contracts/reporting/ReputationToken.sol', 'reputationToken')
    reputationToken.setController(localFixture.contracts['Controller'].address)
    with raises(TransactionFailed, message="universe has to have address"):
        reputationToken.initialize(longToHexString(0))

    assert reputationToken.initialize(mockUniverse.address)


def test_reputation_token_migrate_out_stake_token(localFixture, mockUniverse, initializedReputationToken, mockStakeToken, mockReputationToken, mockMarket):
    with raises(TransactionFailed, message="universe has to contain stake token && called from stake token"):
        initializedReputationToken.migrateOutStakeToken(mockUniverse.address)
    
    mockUniverse.setIsContainerForStakeToken(True)
    with raises(TransactionFailed, message="destination reputation tokens universe needs to be parent of local universe"):
        mockStakeToken.callMigrateOutStakeToken(initializedReputationToken.address, mockReputationToken.address, tester.a1, 100)

    mockReputationToken.setUniverse(mockUniverse.address)
    with raises(TransactionFailed, message="destination reputation tokens needs to be its universes reputation token"):
        mockStakeToken.callMigrateOutStakeToken(initializedReputationToken.address, mockReputationToken.address, tester.a1, 100)

    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')    
    parentUniverse.setForkingMarket(mockMarket.address)
    parentUniverse.setReputationToken(mockReputationToken.address)
    mockReputationToken.setUniverse(parentUniverse.address)
    mockUniverse.setParentUniverse(parentUniverse.address)
    mockUniverse.setIsParentOf(True)
    assert mockReputationToken.callMigrateIn(initializedReputationToken.address, mockStakeToken.address, 1011, False)
    assert initializedReputationToken.totalSupply() == 1011
    mockReputationToken.setTotalSupply(1005)
    # sender and reporter is the same
    mockStakeToken.callMigrateOutStakeToken(initializedReputationToken.address, mockReputationToken.address, mockStakeToken.address, 54)
    # total repu token supply 1000
    # 110 - 54, 1000 - 54
    assert initializedReputationToken.totalSupply() == 1011 - 54
    assert mockReputationToken.getMigrateInReporterValue() == stringToBytes(mockStakeToken.address)
    assert mockReputationToken.getMigrateInAttoTokensValue() == 54
    assert mockReputationToken.getMigrateInBonusIfInForkWindowValue() == True
    assert initializedReputationToken.getTopMigrationDestination() == stringToBytes(mockReputationToken.address)

def test_reputation_token_migrate_in(localFixture, mockUniverse, initializedReputationToken, mockReputationToken, mockMarket):
    with raises(TransactionFailed, message="caller needs to be reputation token"):
        initializedReputationToken.migrateIn(tester.a1, 100, False)
    
    mockUniverse.setIsContainerForStakeToken(True)
    with raises(TransactionFailed, message="calling reputation token has to be parent universe's reputation token"):
        mockReputationToken.callMigrateIn(initializedReputationToken.address, tester.a1, 1000, False)
    
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')    
    parentUniverse.setReputationToken(mockReputationToken.address)
    mockUniverse.setParentUniverse(parentUniverse.address)
    mockReputationToken.setUniverse(mockUniverse.address)
    with raises(TransactionFailed, message="parent universe needs to have a forking market"):
        mockReputationToken.callMigrateIn(initializedReputationToken.address, tester.a1, 100, False)
    
    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    parentUniverse.setForkingMarket(mockMarket.address)

    assert initializedReputationToken.totalSupply() == 0
    mockReputationToken.callMigrateIn(initializedReputationToken.address, tester.a1, 100, False)
    assert initializedReputationToken.totalSupply() == 100

def migrate_reputation_for_sender(localFixture, initializedReputationToken, sender, amount, mockReputationToken, mockMarket, mockUniverse):
    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')    
    parentUniverse.setForkingMarket(mockMarket.address)
    parentUniverse.setReputationToken(mockReputationToken.address)
    mockUniverse.setParentUniverse(parentUniverse.address)
    assert mockReputationToken.callMigrateIn(initializedReputationToken.address, sender, amount, False)

@fixture(scope="session")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockLegacyReputationToken = fixture.contracts['MockLegacyReputationToken']
    controller.setValue(stringToBytes('LegacyReputationToken'), mockLegacyReputationToken.address)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def mockStakeToken(localFixture):
    mockStakeToken = localFixture.contracts['MockStakeToken']
    return mockStakeToken

@fixture
def mockUniverse(localFixture):
    mockUniverse = localFixture.contracts['MockUniverse']
    return mockUniverse

@fixture
def mockReputationToken(localFixture):
    mockReputationToken = localFixture.contracts['MockReputationToken']
    return mockReputationToken

@fixture
def mockMarket(localFixture, mockUniverse):
    # wire up mock market
    mockMarket = localFixture.contracts['MockMarket']
    return mockMarket

@fixture
def initializedReputationToken(localFixture, mockUniverse):
    reputationToken = localFixture.upload('../source/contracts/reporting/ReputationToken.sol', 'reputationToken')
    reputationToken.setController(localFixture.contracts['Controller'].address)
    assert reputationToken.initialize(mockUniverse.address)
    return reputationToken