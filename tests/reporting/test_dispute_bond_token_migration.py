from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString
from reporting_utils import proceedToDesignatedReporting, proceedToRound1Reporting, proceedToRound2Reporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

# Migration data is expressed as [beforeFinalization, targetUniverse]
@mark.parametrize('invalidRep,yesRep,noRep,designatedMigration,round1Migration,round2Migration', [
    (0, 0, 0, [False, 0], [False, 0], [False, 0]),
    (100000, 0, 0, [True, 0], [False, 0], [True, 0]),
    (10 ** 23, 0, 0, [True, 0], [False, 0], [True, 0]),
    (100000, 100000, 0, [True, 0], [True, 2], [True, 2]),
    (100000, 0, 100000, [True, 1], [True, 2], [False, 2]),
    (0, 100000, 100000, [True, 1], [True, 2], [False, 2]),
    (0, 10**23, 10**23, [True, 1], [True, 2], [False, 2]),
    (10**23, 10**23, 10**23, [False, 1], [True, 2], [True, 2]),
])
def test_dispute_bond_token_migration(invalidRep, yesRep, noRep, designatedMigration, round1Migration, round2Migration, reportingFixture):
    market = reportingFixture.binaryMarket
    universe = reportingFixture.universe
    reputationToken = reportingFixture.applySignature("ReputationToken", universe.getReputationToken())
    cash = reportingFixture.cash
    completeSets = reportingFixture.contracts['CompleteSets']
    YES_OUTCOME = [10**18,0]
    NO_OUTCOME = [0,10**18]
    INVALID_OUTCOME = [10**18 / 2,10**18 / 2]
    YES_DISTRIBUTION_HASH = market.derivePayoutDistributionHash(YES_OUTCOME, False)
    NO_DISTRIBUTION_HASH = market.derivePayoutDistributionHash(NO_OUTCOME, False)
    INVALID_DISTRIBUTION_HASH = market.derivePayoutDistributionHash(INVALID_OUTCOME, True)

    # We proceed the standard market to the FORKING state
    proceedToForking(reportingFixture,  market, True, tester.k1, tester.k2, tester.k3, NO_OUTCOME, YES_OUTCOME, tester.k2, YES_OUTCOME, NO_OUTCOME, YES_OUTCOME)

    # We have 3 dispute bonds for the market
    designatedDisputeBond = reportingFixture.applySignature('DisputeBondToken', market.getDesignatedReporterDisputeBondToken())
    round1DisputeBond = reportingFixture.applySignature('DisputeBondToken', market.getRound1ReportersDisputeBondToken())
    round2DisputeBond = reportingFixture.applySignature('DisputeBondToken', market.getRound2ReportersDisputeBondToken())

    # Validate the owners
    assert designatedDisputeBond.getBondHolder() == bytesToHexString(tester.a1)
    assert round1DisputeBond.getBondHolder() == bytesToHexString(tester.a2)
    assert round2DisputeBond.getBondHolder() == bytesToHexString(tester.a0)

    # Validate the disputes outcomes
    assert designatedDisputeBond.getDisputedPayoutDistributionHash() == NO_DISTRIBUTION_HASH
    assert round1DisputeBond.getDisputedPayoutDistributionHash() == YES_DISTRIBUTION_HASH
    assert round2DisputeBond.getDisputedPayoutDistributionHash() == YES_DISTRIBUTION_HASH

    # Get 3 Universe's that may be used as migration targets
    yesUniverse = reportingFixture.applySignature("Universe", universe.getOrCreateChildUniverse(YES_DISTRIBUTION_HASH))
    noUniverse = reportingFixture.applySignature("Universe", universe.getOrCreateChildUniverse(NO_DISTRIBUTION_HASH))
    invalidUniverse = reportingFixture.applySignature("Universe", universe.getOrCreateChildUniverse(INVALID_DISTRIBUTION_HASH))
    universeMap = {0: invalidUniverse, 1:yesUniverse, 2:noUniverse}

    if (invalidRep > 0):
        reputationToken.migrateOut(invalidUniverse.getReputationToken(), tester.a3, invalidRep, sender=tester.k3)
    if (yesRep > 0):
        reputationToken.migrateOut(yesUniverse.getReputationToken(), tester.a3, invalidRep, sender=tester.k3)
    if (noRep > 0):
        reputationToken.migrateOut(noUniverse.getReputationToken(), tester.a3, invalidRep, sender=tester.k3)

    if (designatedMigration[0]):
        destinationUniverse = universeMap[designatedMigration[1]]
        doBondWithdraw(reportingFixture, designatedDisputeBond, True, universe, reputationToken, destinationUniverse, tester.a1, tester.k1)
    if (round1Migration[0]):
        destinationUniverse = universeMap[round1Migration[1]]
        doBondWithdraw(reportingFixture, round1DisputeBond, True, universe, reputationToken, destinationUniverse, tester.a2, tester.k2)
    if (round2Migration[0]):
        destinationUniverse = universeMap[round2Migration[1]]
        doBondWithdraw(reportingFixture, round2DisputeBond, True, universe, reputationToken, destinationUniverse, tester.a0, tester.k0)

    # We'll finalize the forking market
    finalizeForkingMarket(reportingFixture, market, False, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, NO_OUTCOME, YES_OUTCOME)

    if (not designatedMigration[0]):
        destinationUniverse = universeMap[designatedMigration[1]]
        doBondWithdraw(reportingFixture, designatedDisputeBond, False, universe, reputationToken, destinationUniverse, tester.a1, tester.k1)
    if (not round1Migration[0]):
        destinationUniverse = universeMap[round1Migration[1]]
        doBondWithdraw(reportingFixture, round1DisputeBond, False, universe, reputationToken, destinationUniverse, tester.a2, tester.k2)
    if (not round2Migration[0]):
        destinationUniverse = universeMap[round2Migration[1]]
        doBondWithdraw(reportingFixture, round2DisputeBond, False, universe, reputationToken, destinationUniverse, tester.a0, tester.k0)

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
def reportingSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    return initializeReportingFixture(sessionFixture, sessionFixture.binaryMarket)

@fixture
def reportingFixture(sessionFixture, reportingSnapshot):
    sessionFixture.resetToSnapshot(reportingSnapshot)
    return sessionFixture
