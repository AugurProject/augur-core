from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString, twentyZeros, thirtyTwoZeros
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed
from reporting_utils import proceedToDesignatedReporting, proceedToFirstReporting, proceedToLastReporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture


def test_reputation_token_creation(localFixture, mockUniverse):
    reputationToken = localFixture.upload('../source/contracts/reporting/ReputationToken.sol', 'reputationToken')
    reputationToken.setController(localFixture.contracts['Controller'].address)
    with raises(TransactionFailed, message="universe has to have address"):
        reputationToken.initialize(longToHexString(0))

    assert reputationToken.initialize(mockUniverse.address)
    assert reputationToken.getTypeName() == stringToBytes('ReputationToken')
    assert reputationToken.getUniverse() == mockUniverse.address


def test_reputation_token_migrate_out(localFixture, mockUniverse, initializedReputationToken, mockStakeToken, mockReputationToken, mockMarket, mockDisputeBond, mockLegacyReputationToken):
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
    assert mockStakeToken.callMigrateOutStakeToken(initializedReputationToken.address, mockReputationToken.address, mockStakeToken.address, 54)

    assert initializedReputationToken.totalSupply() == 1011 - 54
    assert mockReputationToken.getMigrateInReporterValue() == stringToBytes(mockStakeToken.address)
    assert mockReputationToken.getMigrateInAttoTokensValue() == 54
    assert mockReputationToken.getMigrateInBonusIfInForkWindowValue() == True
    assert initializedReputationToken.getTopMigrationDestination() == stringToBytes(mockReputationToken.address)

    give_some_rep_to(mockLegacyReputationToken, initializedReputationToken, tester.k1, 35)
    assert initializedReputationToken.totalSupply() == 1011 - 54 + 35

    with raises(TransactionFailed, message="reporter not approve for sender can not sub from zero"):
        mockStakeToken.callMigrateOutStakeToken(initializedReputationToken.address, mockReputationToken.address, tester.a1, 35)

    assert initializedReputationToken.approve(mockStakeToken.address, 35, sender=tester.k1)
    assert initializedReputationToken.allowance(tester.a1, mockStakeToken.address) == 35
    assert initializedReputationToken.balanceOf(tester.a1) == 35
    # sender is not reporter
    assert mockStakeToken.callMigrateOutStakeToken(initializedReputationToken.address, mockReputationToken.address, tester.a1, 35)
    assert initializedReputationToken.allowance(tester.a1, mockStakeToken.address) == 0
    assert initializedReputationToken.balanceOf(tester.a1) == 0

    assert initializedReputationToken.totalSupply() == 1011 - 54 + 35 - 35
    assert initializedReputationToken.getTopMigrationDestination() == stringToBytes(mockReputationToken.address)
    assert mockReputationToken.getMigrateInReporterValue() == bytesToHexString(tester.a1)
    assert mockReputationToken.getMigrateInAttoTokensValue() == 35
    assert mockReputationToken.getMigrateInBonusIfInForkWindowValue() == True

    newReputationToken = localFixture.upload('solidity_test_helpers/MockReputationToken.sol', 'newReputationToken')
    parentUniverse.setReputationToken(newReputationToken.address)
    newReputationToken.setUniverse(parentUniverse.address)
    newReputationToken.setTotalSupply(6005)
    assert mockStakeToken.callMigrateOut(initializedReputationToken.address, newReputationToken.address, mockStakeToken.address, 33)
    # new destination with larger total supply gets migration
    assert initializedReputationToken.totalSupply() == 1011 - 54 - 33
    assert initializedReputationToken.getTopMigrationDestination() == stringToBytes(newReputationToken.address)
    assert newReputationToken.getMigrateInReporterValue() == stringToBytes(mockStakeToken.address)
    assert newReputationToken.getMigrateInAttoTokensValue() == 33
    assert newReputationToken.getMigrateInBonusIfInForkWindowValue() == False

    with raises(TransactionFailed, message="universe needs to contain dispute bond"):
        mockDisputeBond.callMigrateOutDisputeBond(initializedReputationToken.address, mockReputationToken.address, mockDisputeBond.address, 100)

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

    mockReputationToken.callMigrateIn(initializedReputationToken.address, tester.a2, 100, True)
    assert initializedReputationToken.totalSupply() == 200

def test_reputation_token_migrate_from_legacy_reputationToken(localFixture, initializedReputationToken, mockLegacyReputationToken):
    mockLegacyReputationToken.setBalanceOf(100)
    mockLegacyReputationToken.getFaucetAmountValue() == 0
    assert initializedReputationToken.migrateFromLegacyReputationToken(sender=tester.k2)
    assert mockLegacyReputationToken.getFaucetAmountValue() == 0
    assert mockLegacyReputationToken.getTransferFromFromValue() == bytesToHexString(tester.a2)
    assert mockLegacyReputationToken.getTransferFromToValue() == longToHexString(0)
    assert mockLegacyReputationToken.getTransferFromValueValue() == 100
    assert initializedReputationToken.totalSupply() == 100

def test_reputation_token_mint_for_dispute_bond_migration(localFixture, initializedReputationToken, mockDisputeBond, mockUniverse):
    with raises(TransactionFailed, message="caller has to be a IDisputeBond"):
        initializedReputationToken.mintForDisputeBondMigration(1000)

    with raises(TransactionFailed, message="parent universe does not contain dispute bond"):
        mockDisputeBond.callMintForDisputeBondMigration(1000)

    assert initializedReputationToken.balanceOf(mockDisputeBond.address) == 0
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')
    mockUniverse.setParentUniverse(parentUniverse.address)
    parentUniverse.setIsContainerForDisputeBond(True)
    mockUniverse.setIsParentOf(True)
    assert mockDisputeBond.callMintForDisputeBondMigration(initializedReputationToken.address, 100)
    assert initializedReputationToken.balanceOf(mockDisputeBond.address) == 100


def test_reputation_token_trusted_transfer(localFixture, mockUniverse, initializedReputationToken, mockMarket, mockReportingWindow, mockStakeToken, mockParticipationToken, mockLegacyReputationToken):
    with raises(TransactionFailed, message="universe does not contain reporting window and caller has to be a IReportingWindow"):
        initializedReputationToken.trustedReportingWindowTransfer(tester.a1, tester.a2, 100)

    with raises(TransactionFailed, message="universe does not contain reporting window"):
        mockReportingWindow.callTrustedReportingWindowTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)

    with raises(TransactionFailed, message="universe does not contain market"):
        mockMarket.callTrustedMarketTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)

    with raises(TransactionFailed, message="universe does not contain stake token"):
        mockStakeToken.callTrustedStakeTokenTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)

    with raises(TransactionFailed, message="universe does not contain participation token"):
        mockParticipationToken.callTrustedParticipationTokenTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)

    mockUniverse.setIsContainerForReportingWindow(True)
    with raises(TransactionFailed, message="source balance can not be 0"):
        mockReportingWindow.callTrustedReportingWindowTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)


    assert initializedReputationToken.totalSupply() == 0
    assert initializedReputationToken.balanceOf(tester.a1) == 0
    give_some_rep_to(mockLegacyReputationToken, initializedReputationToken, tester.k1, 35)
    assert initializedReputationToken.totalSupply() == 35
    assert initializedReputationToken.balanceOf(tester.a2) == 0
    assert initializedReputationToken.balanceOf(tester.a1) == 35

    with raises(TransactionFailed, message="transfer has to be approved"):
        mockReportingWindow.callTrustedReportingWindowTransfer(initializedReputationToken.address, tester.a1, tester.a2, 100)

    assert initializedReputationToken.approve(mockStakeToken.address, 35, sender=tester.k1)
    assert initializedReputationToken.allowance(tester.a1, mockStakeToken.address) == 35

    assert mockReportingWindow.callTrustedReportingWindowTransfer(initializedReputationToken.address, tester.a1, tester.a2, 35)
    # TODO find out why total supply grows
    assert initializedReputationToken.totalSupply() == 35
    assert initializedReputationToken.balanceOf(tester.a2) == 35
    assert initializedReputationToken.balanceOf(tester.a1) == 0

def give_some_rep_to(mockLegacyReputationToken, targetReputationToken, userAccount, amount):
    mockLegacyReputationToken.setBalanceOf(amount)
    assert targetReputationToken.migrateFromLegacyReputationToken(sender=userAccount)

@fixture(scope="session")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockLegacyReputationToken = fixture.contracts['MockLegacyReputationToken']
    controller.registerContract(stringToBytes('LegacyReputationToken'), mockLegacyReputationToken.address, twentyZeros, thirtyTwoZeros)
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
def mockMarket(localFixture):
    mockMarket = localFixture.contracts['MockMarket']
    return mockMarket

@fixture
def mockDisputeBond(localFixture):
    return localFixture.contracts['MockDisputeBond']

@fixture
def mockReportingWindow(localFixture):
    return localFixture.contracts['MockReportingWindow']

@fixture
def mockParticipationToken(localFixture):
    return localFixture.contracts['MockParticipationToken']

@fixture
def mockLegacyReputationToken(localFixture):
    return localFixture.contracts['MockLegacyReputationToken']

@fixture
def mockAugur(localFixture):
    return localFixture.contracts['MockAugur']

@fixture
def initializedReputationToken(localFixture, mockUniverse):
    reputationToken = localFixture.upload('../source/contracts/reporting/ReputationToken.sol', 'reputationToken')
    reputationToken.setController(localFixture.contracts['Controller'].address)
    assert reputationToken.initialize(mockUniverse.address)
    return reputationToken
