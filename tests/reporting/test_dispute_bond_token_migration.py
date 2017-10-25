from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed, ABIContract
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString
from reporting_utils import proceedToForking, finalizeForkingMarket, initializeReportingFixture


# Migration data is expressed as [beforeFinalization, targetUniverse]
@mark.parametrize('invalidRep,yesRep,noRep,designatedMigration,firstMigration,lastMigration,finalizeByMigration', [
    (0, 0, 0, [False, 0], [False, 0], [False, 0], False),
    (100000, 0, 0, [True, 0], [False, 0], [True, 0], True),
    (10 ** 23, 0, 0, [True, 0], [False, 0], [True, 0], False),
    (100000, 100000, 0, [True, 0], [True, 2], [True, 2], True),
    (100000, 0, 100000, [True, 1], [True, 2], [False, 2], False),
    (0, 100000, 100000, [True, 1], [True, 2], [False, 2], True),
    (0, 10**23, 10**23, [True, 1], [True, 2], [False, 2], False),
    (10**23, 10**23, 10**23, [False, 1], [True, 2], [True, 2], True),
])
def test_dispute_bond_token_migration(invalidRep, yesRep, noRep, designatedMigration, firstMigration, lastMigration, finalizeByMigration, localFixture, universe, cash, market):
    reputationToken = localFixture.applySignature("ReputationToken", universe.getReputationToken())
    completeSets = localFixture.contracts['CompleteSets']
    YES_OUTCOME = [10**18,0]
    NO_OUTCOME = [0,10**18]
    INVALID_OUTCOME = [10**18 / 2,10**18 / 2]
    YES_DISTRIBUTION_HASH = market.derivePayoutDistributionHash(YES_OUTCOME, False)
    NO_DISTRIBUTION_HASH = market.derivePayoutDistributionHash(NO_OUTCOME, False)
    INVALID_DISTRIBUTION_HASH = market.derivePayoutDistributionHash(INVALID_OUTCOME, True)

    # We proceed the standard market to the FORKING state
    proceedToForking(localFixture, universe, market, True, 1, 2, 3, NO_OUTCOME, YES_OUTCOME, 2, YES_OUTCOME, NO_OUTCOME, YES_OUTCOME)

    # We have 3 dispute bonds for the market
    designatedDisputeBond = localFixture.applySignature('DisputeBondToken', market.getDesignatedReporterDisputeBondToken())
    firstDisputeBond = localFixture.applySignature('DisputeBondToken', market.getFirstReportersDisputeBondToken())
    lastDisputeBond = localFixture.applySignature('DisputeBondToken', market.getLastReportersDisputeBondToken())

    # Validate the owners
    assert designatedDisputeBond.getBondHolder() == bytesToHexString(tester.a1)
    assert firstDisputeBond.getBondHolder() == bytesToHexString(tester.a2)
    assert lastDisputeBond.getBondHolder() == bytesToHexString(tester.a0)

    # Validate the disputes outcomes
    assert designatedDisputeBond.getDisputedPayoutDistributionHash() == NO_DISTRIBUTION_HASH
    assert firstDisputeBond.getDisputedPayoutDistributionHash() == YES_DISTRIBUTION_HASH
    assert lastDisputeBond.getDisputedPayoutDistributionHash() == YES_DISTRIBUTION_HASH

    # Get 3 Universe's that may be used as migration targets
    yesUniverse = localFixture.applySignature("Universe", universe.getOrCreateChildUniverse(YES_DISTRIBUTION_HASH))
    noUniverse = localFixture.applySignature("Universe", universe.getOrCreateChildUniverse(NO_DISTRIBUTION_HASH))
    invalidUniverse = localFixture.applySignature("Universe", universe.getOrCreateChildUniverse(INVALID_DISTRIBUTION_HASH))
    universeMap = {0: invalidUniverse, 1:yesUniverse, 2:noUniverse}

    if (invalidRep > 0):
        reputationToken.migrateOut(invalidUniverse.getReputationToken(), tester.a3, invalidRep, sender=tester.k3)
    if (yesRep > 0):
        reputationToken.migrateOut(yesUniverse.getReputationToken(), tester.a3, invalidRep, sender=tester.k3)
    if (noRep > 0):
        reputationToken.migrateOut(noUniverse.getReputationToken(), tester.a3, invalidRep, sender=tester.k3)

    if (designatedMigration[0]):
        destinationUniverse = universeMap[designatedMigration[1]]
        doBondWithdraw(localFixture, designatedDisputeBond, True, universe, reputationToken, destinationUniverse, tester.a1, tester.k1)
    if (firstMigration[0]):
        destinationUniverse = universeMap[firstMigration[1]]
        doBondWithdraw(localFixture, firstDisputeBond, True, universe, reputationToken, destinationUniverse, tester.a2, tester.k2)
    if (lastMigration[0]):
        destinationUniverse = universeMap[lastMigration[1]]
        doBondWithdraw(localFixture, lastDisputeBond, True, universe, reputationToken, destinationUniverse, tester.a0, tester.k0)

    # We'll finalize the forking market. If we finalize by migrating REP we'll get the bonus since dispute bonds have that perk. If we wait till the window is over to finalize though we get no such benefit
    finalizeForkingMarket(localFixture, universe, market, finalizeByMigration, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, NO_OUTCOME, YES_OUTCOME)

    if (not designatedMigration[0]):
        destinationUniverse = universeMap[designatedMigration[1]]
        doBondWithdraw(localFixture, designatedDisputeBond, finalizeByMigration, universe, reputationToken, destinationUniverse, tester.a1, tester.k1)
    if (not firstMigration[0]):
        destinationUniverse = universeMap[firstMigration[1]]
        doBondWithdraw(localFixture, firstDisputeBond, finalizeByMigration, universe, reputationToken, destinationUniverse, tester.a2, tester.k2)
    if (not lastMigration[0]):
        destinationUniverse = universeMap[lastMigration[1]]
        doBondWithdraw(localFixture, lastDisputeBond, finalizeByMigration, universe, reputationToken, destinationUniverse, tester.a0, tester.k0)

def doBondWithdraw(fixture, bond, bonus, universe, reputationToken, destinationUniverse, testerAddress, testerKey):
    disputeUniverse = fixture.applySignature("Universe", universe.getOrCreateChildUniverse(bond.getDisputedPayoutDistributionHash()))
    destinationReputationToken = fixture.applySignature("ReputationToken", destinationUniverse.getReputationToken())
    bondRemainingToBePaid = bond.getBondRemainingToBePaidOut()
    bondAmount = bondRemainingToBePaid / 2
    amountRequiredForBondPayouts = universe.getExtraDisputeBondRemainingToBePaidOut()
    amountInMigrationPool = disputeUniverse.getRepAvailableForExtraBondPayouts()
    bonusDivisor = fixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()

    amountDirectlyMigrated = reputationToken.balanceOf(bond.address)
    if (bonus):
        amountDirectlyMigrated = amountDirectlyMigrated + (amountDirectlyMigrated / bonusDivisor)

    amountNeededForExtraPayout = bondRemainingToBePaid - amountDirectlyMigrated
    expectedAmountPulledFromDestinationPool = amountInMigrationPool * amountNeededForExtraPayout / amountRequiredForBondPayouts
    expectedAmountPulledFromDestinationPool = min(amountNeededForExtraPayout, expectedAmountPulledFromDestinationPool)

    assert bond.withdrawToUniverse(destinationUniverse.address, sender=testerKey)
    balanceInDestinationUniverse = destinationReputationToken.balanceOf(testerAddress)
    assert balanceInDestinationUniverse == amountDirectlyMigrated + expectedAmountPulledFromDestinationPool

    newBondRemainingToBePaid = bond.getBondRemainingToBePaidOut()
    assert newBondRemainingToBePaid == bondRemainingToBePaid - balanceInDestinationUniverse
    assert universe.getExtraDisputeBondRemainingToBePaidOut() == amountRequiredForBondPayouts - (bondAmount - newBondRemainingToBePaid)
    assert disputeUniverse.getRepAvailableForExtraBondPayouts() == amountInMigrationPool - expectedAmountPulledFromDestinationPool

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    return initializeReportingFixture(fixture, universe, market)

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def universe(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)

@fixture
def market(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)

@fixture
def cash(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
