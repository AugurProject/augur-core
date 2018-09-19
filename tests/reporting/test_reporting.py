from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, bytesToHexString, TokenDelta, AssertLog, EtherDelta, longToHexString
from reporting_utils import proceedToDesignatedReporting, proceedToInitialReporting, proceedToNextRound, proceedToFork, finalizeFork

tester.STARTGAS = long(6.7 * 10**6)

def test_designatedReportHappyPath(localFixture, universe, market):
    # proceed to the designated reporting period
    proceedToDesignatedReporting(localFixture, market)

    # an address that is not the designated reporter cannot report
    with raises(TransactionFailed):
        market.doInitialReport([0, market.getNumTicks()], False, "", sender=tester.k1)

    # Reporting with an invalid number of outcomes should fail
    with raises(TransactionFailed):
        market.doInitialReport([0, 0, market.getNumTicks()], False, "")

    # do an initial report as the designated reporter
    initialReportLog = {
        "universe": universe.address,
        "reporter": bytesToHexString(tester.a0),
        "market": market.address,
        "amountStaked": universe.getInitialReportMinValue(),
        "isDesignatedReporter": True,
        "payoutNumerators": [0, market.getNumTicks()],
        "invalid": False,
        "description": "Obviously I'm right",
    }
    with AssertLog(localFixture, "InitialReportSubmitted", initialReportLog):
        assert market.doInitialReport([0, market.getNumTicks()], False, "Obviously I'm right")

    with raises(TransactionFailed, message="Cannot initial report twice"):
        assert market.doInitialReport([0, market.getNumTicks()], False, "Obviously I'm right")

    # the market is now assigned a fee window
    newFeeWindowAddress = market.getFeeWindow()
    assert newFeeWindowAddress
    feeWindow = localFixture.applySignature('FeeWindow', newFeeWindowAddress)

    # time marches on and the market can be finalized
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    marketFinalizedLog = {
        "universe": universe.address,
        "market": market.address
    }
    with AssertLog(localFixture, "MarketFinalized", marketFinalizedLog):
        assert market.finalize()

    with raises(TransactionFailed, message="Cannot finalize twice"):
        market.finalize()

@mark.parametrize('reportByDesignatedReporter', [
    True,
    False
])
def test_initialReportHappyPath(reportByDesignatedReporter, localFixture, universe, market):
    # proceed to the initial reporting period
    proceedToInitialReporting(localFixture, market)

    # do an initial report as someone other than the designated reporter
    sender = tester.k0 if reportByDesignatedReporter else tester.k1
    assert market.doInitialReport([0, market.getNumTicks()], False, "", sender=sender)

    # the market is now assigned a fee window
    newFeeWindowAddress = market.getFeeWindow()
    assert newFeeWindowAddress
    feeWindow = localFixture.applySignature('FeeWindow', newFeeWindowAddress)

    # time marches on and the market can be finalized
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

def test_initialReport_methods(localFixture, universe, market, cash, constants):
    reputationToken = localFixture.applySignature("ReputationToken", universe.getReputationToken())

    # proceed to the initial reporting period
    proceedToInitialReporting(localFixture, market)

    # do an initial report as someone other than the designated reporter
    assert market.doInitialReport([0, market.getNumTicks()], False, "", sender=tester.k1)

    # the market is now assigned a fee window
    newFeeWindowAddress = market.getFeeWindow()
    assert newFeeWindowAddress
    feeWindow = localFixture.applySignature('FeeWindow', newFeeWindowAddress)

    # time marches on and the market can be finalized
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    # We can see that the market reports the designated reporter did not show
    assert not market.designatedReporterShowed()

    # Let's get a reference to the Initial Reporter bond and transfer it to the original designated reporter account
    initialReporter = localFixture.applySignature("InitialReporter", market.getInitialReporter())
    transferLog = {
        "universe": universe.address,
        "market": market.address,
        "from": bytesToHexString(tester.a1),
        "to": initialReporter.getDesignatedReporter(),
    }
    with AssertLog(localFixture, "InitialReporterTransferred", transferLog):
        assert initialReporter.transferOwnership(initialReporter.getDesignatedReporter(), sender=tester.k1)

    # Transfering to the owner is a noop
    assert initialReporter.transferOwnership(initialReporter.getDesignatedReporter())

    # The market still correctly indicates the designated reporter did not show up
    assert not market.designatedReporterShowed()

    # confirm we cannot call protected methods on the initial reporter which only the market may use
    with raises(TransactionFailed):
        initialReporter.report(tester.a0, "", [], False)

    with raises(TransactionFailed):
        initialReporter.returnRepFromDisavow()

    with raises(TransactionFailed):
        initialReporter.migrateToNewUniverse(tester.a0)

    # When we redeem the initialReporter it goes to the correct party as well
    expectedRep = initialReporter.getStake()
    owner = initialReporter.getOwner()

    with TokenDelta(reputationToken, expectedRep, owner, "Redeeming didn't refund REP"):
        assert initialReporter.redeem(owner)

@mark.parametrize('rounds', [
    2,
    3,
    6,
    16
])
def test_roundsOfReporting(rounds, localFixture, market, universe):
    feeWindow = universe.getOrCreateCurrentFeeWindow()

    # Do the initial report
    proceedToNextRound(localFixture, market, moveTimeForward = False)

    # Do the first round outside of the loop and test logging
    crowdsourcerCreatedLog = {
        "universe": universe.address,
        "market": market.address,
        "size": universe.getInitialReportMinValue() * 2,
        "payoutNumerators": [0, market.getNumTicks()],
        "invalid": False
    }

    crowdsourcerContributionLog = {
        "universe": universe.address,
        "reporter": bytesToHexString(tester.a0),
        "market": market.address,
        "amountStaked": universe.getInitialReportMinValue() * 2,
        "description": "Clearly incorrect",
    }

    crowdsourcerCompletedLog = {
        "universe": universe.address,
        "market": market.address
    }

    with AssertLog(localFixture, "DisputeCrowdsourcerCreated", crowdsourcerCreatedLog):
        with AssertLog(localFixture, "DisputeCrowdsourcerContribution", crowdsourcerContributionLog):
            with AssertLog(localFixture, "DisputeCrowdsourcerCompleted", crowdsourcerCompletedLog):
                proceedToNextRound(localFixture, market, description="Clearly incorrect")

    # proceed through several rounds of disputing
    for i in range(rounds - 2):
        proceedToNextRound(localFixture, market)
        assert feeWindow != market.getFeeWindow()
        feeWindow = market.getFeeWindow()
        assert feeWindow == universe.getCurrentFeeWindow()

@mark.parametrize('finalizeByMigration, manuallyDisavow', [
    #(True, True),
    (False, True),
    #(True, False),
    (False, False),
])
def test_forking(finalizeByMigration, manuallyDisavow, localFixture, universe, cash, market, categoricalMarket, scalarMarket):
    # Let's go into the one dispute round for the categorical market
    proceedToNextRound(localFixture, categoricalMarket)
    proceedToNextRound(localFixture, categoricalMarket)

    # proceed to forking
    proceedToFork(localFixture, market, universe)

    with raises(TransactionFailed):
        universe.fork()

    with raises(TransactionFailed, message="We cannot migrate until the fork is finalized"):
        categoricalMarket.migrateThroughOneFork([0,0,categoricalMarket.getNumTicks()], False, "")

    with raises(TransactionFailed, message="We cannot create markets during a fork"):
        time = localFixture.contracts["Time"].getTimestamp()
        localFixture.createYesNoMarket(universe, time + 1000, 1, cash, tester.a0)

    # confirm that we can manually create a child universe from an outcome no one asserted was true during dispute
    numTicks = market.getNumTicks()
    childUniverse = universe.createChildUniverse([numTicks/ 4, numTicks * 3 / 4], False)

    # confirm that before the fork is finalized we can redeem stake in other markets crowdsourcers, which are disavowable
    categoricalDisputeCrowdsourcer = localFixture.applySignature("DisputeCrowdsourcer", categoricalMarket.getReportingParticipant(1))

    # confirm we cannot migrate it
    with raises(TransactionFailed):
        categoricalDisputeCrowdsourcer.migrate()

    # confirm we cannot liquidate it
    with raises(TransactionFailed):
        categoricalDisputeCrowdsourcer.liquidateLosing()

    # confirm we cannot fork it
    with raises(TransactionFailed):
        categoricalDisputeCrowdsourcer.forkAndRedeem()

    if manuallyDisavow:
        marketParticipantsDisavowedLog = {
            "universe": universe.address,
            "market": categoricalMarket.address,
        }
        with AssertLog(localFixture, "MarketParticipantsDisavowed", marketParticipantsDisavowedLog):
            assert categoricalMarket.disavowCrowdsourcers()
        # We can redeem before the fork finalizes since disavowal has occured
        assert categoricalDisputeCrowdsourcer.redeem(tester.a0)

    # We cannot contribute to a crowdsourcer during a fork
    with raises(TransactionFailed):
        categoricalMarket.contribute([2,2,categoricalMarket.getNumTicks()-4], False, 1, "")

    # We cannot purchase new Participation Tokens during a fork
    feeWindowAddress = universe.getCurrentFeeWindow()
    feeWindow = localFixture.applySignature("FeeWindow", feeWindowAddress)
    with raises(TransactionFailed):
        feeWindow.buy(1)

    # finalize the fork
    marketFinalizedLog = {
        "universe": universe.address,
        "market": market.address,
    }
    with AssertLog(localFixture, "MarketFinalized", marketFinalizedLog):
        finalizeFork(localFixture, market, universe, finalizeByMigration)

    # We cannot contribute to a crowdsourcer in a forked universe
    with raises(TransactionFailed):
        categoricalMarket.contribute([2,2,categoricalMarket.getNumTicks()-4], False, 1, "")

    newUniverseAddress = universe.getWinningChildUniverse()

    # buy some complete sets to change OI
    completeSets = localFixture.contracts['CompleteSets']
    numSets = 10
    cost = categoricalMarket.getNumTicks() * numSets
    assert completeSets.publicBuyCompleteSets(categoricalMarket.address, 10, sender=tester.k1, value=cost)
    assert universe.getOpenInterestInAttoEth() == cost

    marketMigratedLog = {
        "market": categoricalMarket.address,
        "newUniverse": newUniverseAddress,
        "originalUniverse": universe.address,
    }
    with AssertLog(localFixture, "MarketMigrated", marketMigratedLog):
        assert categoricalMarket.migrateThroughOneFork([0,0,categoricalMarket.getNumTicks()], False, "")

    assert universe.getOpenInterestInAttoEth() == 0


    # The dispute crowdsourcer has been disavowed
    newUniverse = localFixture.applySignature("Universe", categoricalMarket.getUniverse())
    assert newUniverse.address != universe.address
    assert categoricalDisputeCrowdsourcer.isDisavowed()
    assert not universe.isContainerForReportingParticipant(categoricalDisputeCrowdsourcer.address)
    assert not newUniverse.isContainerForReportingParticipant(categoricalDisputeCrowdsourcer.address)
    assert newUniverse.getOpenInterestInAttoEth() == cost

    # The initial report is still present however
    categoricalInitialReport = localFixture.applySignature("InitialReporter", categoricalMarket.getReportingParticipant(0))
    assert categoricalMarket.getReportingParticipant(0) == categoricalInitialReport.address
    assert not categoricalInitialReport.isDisavowed()
    assert not universe.isContainerForReportingParticipant(categoricalInitialReport.address)
    assert newUniverse.isContainerForReportingParticipant(categoricalInitialReport.address)

    # The categorical market has a new fee window since it was initially reported on and may be disputed now
    categoricalMarketFeeWindowAddress = categoricalMarket.getFeeWindow()
    categoricalMarketFeeWindow = localFixture.applySignature("FeeWindow", categoricalMarketFeeWindowAddress)

    proceedToNextRound(localFixture, categoricalMarket)

    # We can also purchase Participation Tokens in this fee window
    assert categoricalMarketFeeWindow.buy(1)

    # We will finalize the categorical market in the new universe
    feeWindow = localFixture.applySignature('FeeWindow', categoricalMarket.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    assert categoricalMarket.finalize()

    # We can migrate a market that has not had its initial reporting completed as well, and confirm that the report is now made in the new universe
    reputationToken = localFixture.applySignature("ReputationToken", universe.getReputationToken())
    previousREPBalance = reputationToken.balanceOf(scalarMarket.address)
    assert previousREPBalance > 0
    assert scalarMarket.migrateThroughOneFork([0,scalarMarket.getNumTicks()], False, "")
    newUniverseREP = localFixture.applySignature("ReputationToken", newUniverse.getReputationToken())
    initialReporter = localFixture.applySignature('InitialReporter', scalarMarket.getInitialReporter())
    assert newUniverseREP.balanceOf(initialReporter.address) == newUniverse.getOrCacheDesignatedReportNoShowBond()

    # We can finalize this market as well
    proceedToNextRound(localFixture, scalarMarket)
    feeWindow = localFixture.applySignature('FeeWindow', scalarMarket.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    assert scalarMarket.finalize()

def test_finalized_fork_migration(localFixture, universe, market, categoricalMarket):
    # Make the categorical market finalized
    proceedToNextRound(localFixture, categoricalMarket)
    feeWindow = localFixture.applySignature('FeeWindow', categoricalMarket.getFeeWindow())

    # Time marches on and the market can be finalized
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert categoricalMarket.finalize()

    # Proceed to Forking for the yesNo market and finalize it
    proceedToFork(localFixture, market, universe)
    finalizeFork(localFixture, market, universe)

    # The categorical market is finalized and cannot be migrated to the new universe
    with raises(TransactionFailed):
        categoricalMarket.migrateThroughOneFork([0,0,categoricalMarket.getNumTicks()], False, "")

    # We also can't disavow the crowdsourcers for this market
    with raises(TransactionFailed):
        categoricalMarket.disavowCrowdsourcers()

    # The forking market may not migrate or disavow crowdsourcers either
    with raises(TransactionFailed):
        market.migrateThroughOneFork([0,market.getNumTicks()], False, "")

    with raises(TransactionFailed):
        market.disavowCrowdsourcers()

def test_fork_migration_no_report(localFixture, universe, market, cash):
    # Proceed to Forking for the yesNo market but don't go all the way so that we can create the new market still
    for i in range(10):
        proceedToNextRound(localFixture, market)

    # Create a market before the fork occurs which has an end date past the forking window
    endTime = long(localFixture.contracts["Time"].getTimestamp() + timedelta(days=90).total_seconds())
    longMarket = localFixture.createYesNoMarket(universe, endTime, 1, cash, tester.a0)

    # Go to the forking period
    proceedToFork(localFixture, market, universe)

    # Now finalize the fork so migration can occur
    finalizeFork(localFixture, market, universe)

    # Now when we migrate the market through the fork we'll place a new bond in the winning universe's REP
    oldReputationToken = localFixture.applySignature("ReputationToken", universe.getReputationToken())
    oldBalance = oldReputationToken.balanceOf(longMarket.address)
    newUniverse = localFixture.applySignature("Universe", universe.getChildUniverse(market.getWinningPayoutDistributionHash()))
    newReputationToken = localFixture.applySignature("ReputationToken", newUniverse.getReputationToken())
    with TokenDelta(oldReputationToken, 0, longMarket.address, "Migrating didn't disavow old no show bond"):
        with TokenDelta(newReputationToken, oldBalance, longMarket.address, "Migrating didn't place new no show bond"):
            assert longMarket.migrateThroughOneFork([], False, "")

def test_forking_values(localFixture, universe, market, cash):
    reputationToken = localFixture.applySignature("ReputationToken", universe.getReputationToken())

    # Give some REP to another account
    reputationToken.transfer(tester.a1, 100)

    # proceed to forking
    proceedToFork(localFixture, market, universe)

    # finalize the fork
    finalizeFork(localFixture, market, universe)

    # We can see that the theoretical total REP supply in the winning child universe is equal to the parent supply
    winningPayoutHash = market.getWinningPayoutDistributionHash()
    childUniverse = localFixture.applySignature("Universe", universe.getChildUniverse(winningPayoutHash))
    childUniverseReputationToken = localFixture.applySignature("ReputationToken", childUniverse.getReputationToken())
    childUniverseTheoreticalSupply = childUniverseReputationToken.getTotalTheoreticalSupply()
    assert childUniverseTheoreticalSupply == reputationToken.getTotalTheoreticalSupply()

    # If we nudge the reputation token to update its theoretical balance we can see a lower total to account for sibling migrations
    assert childUniverseReputationToken.updateTotalTheoreticalSupply()
    assert childUniverseReputationToken.getTotalTheoreticalSupply() <= childUniverseTheoreticalSupply
    childUniverseTheoreticalSupply = childUniverseReputationToken.getTotalTheoreticalSupply()

    # If we migrate some REP to another Universe we can recalculate and see that amount deducted from the theoretical supply
    losingPayoutNumerators = [0, market.getNumTicks()]
    losingUniverse =  localFixture.applySignature('Universe', universe.createChildUniverse(losingPayoutNumerators, False))
    losingUniverseReputationToken = localFixture.applySignature('ReputationToken', losingUniverse.getReputationToken())
    assert reputationToken.migrateOut(losingUniverseReputationToken.address, 100, sender=tester.k1)
    assert childUniverseReputationToken.updateTotalTheoreticalSupply()
    lowerChildUniverseTheoreticalSupply = childUniverseReputationToken.getTotalTheoreticalSupply()
    assert lowerChildUniverseTheoreticalSupply == childUniverseTheoreticalSupply - 100

    # If we move past the forking window end time and we update the theoretical supply however we will see that some REP was trapped in the parent and deducted from the supply
    localFixture.contracts["Time"].setTimestamp(universe.getForkEndTime() + 1)
    assert childUniverseReputationToken.updateTotalTheoreticalSupply()
    childUniverseTheoreticalSupply = childUniverseReputationToken.getTotalTheoreticalSupply()
    assert childUniverseTheoreticalSupply < lowerChildUniverseTheoreticalSupply

    # The universe needs to be nudged to actually update values since there are potentially unbounded universes and updating the values derived by this total is not essential as a matter of normal procedure
    # In a forked universe the total supply will be different so its childrens goals will not be the same initially
    if not localFixture.subFork:
        assert childUniverse.getForkReputationGoal() == universe.getForkReputationGoal()
        assert childUniverse.getDisputeThresholdForFork() == universe.getDisputeThresholdForFork()
        assert childUniverse.getInitialReportMinValue() == universe.getInitialReportMinValue()

    # The universe uses this theoretical total to calculate values such as the fork goal, fork dispute threshhold and the initial reporting defaults and floors
    assert childUniverse.updateForkValues()
    assert childUniverse.getForkReputationGoal() == childUniverseTheoreticalSupply / 2
    assert childUniverse.getDisputeThresholdForFork() == long(childUniverseTheoreticalSupply / 40L)
    assert childUniverse.getInitialReportMinValue() == long(childUniverse.getDisputeThresholdForFork() / 3L / 2**18 + 1)

    # Now we'll fork again and confirm it still takes only 20 dispute rounds in the worst case
    newMarket = localFixture.createReasonableYesNoMarket(childUniverse, cash)
    proceedToFork(localFixture, newMarket, childUniverse)
    assert newMarket.getNumParticipants() == 21

    # finalize the fork
    finalizeFork(localFixture, newMarket, childUniverse)

    # The total theoretical supply is again the same as the parents during the fork
    childWinningPayoutHash = newMarket.getWinningPayoutDistributionHash()
    leafUniverse = localFixture.applySignature("Universe", childUniverse.getChildUniverse(childWinningPayoutHash))
    leafUniverseReputationToken = localFixture.applySignature("ReputationToken", leafUniverse.getReputationToken())
    leafUniverseTheoreticalSupply = leafUniverseReputationToken.getTotalTheoreticalSupply()
    assert leafUniverseTheoreticalSupply == childUniverseReputationToken.getTotalTheoreticalSupply()

    # After the fork window ends however we can again recalculate
    localFixture.contracts["Time"].setTimestamp(childUniverse.getForkEndTime() + 1)
    assert leafUniverseReputationToken.updateTotalTheoreticalSupply()
    leafUniverseTheoreticalSupply = leafUniverseReputationToken.getTotalTheoreticalSupply()
    assert leafUniverseTheoreticalSupply < childUniverseReputationToken.getTotalTheoreticalSupply()


def test_fee_window_record_keeping(localFixture, universe, cash, market, categoricalMarket, scalarMarket):
    feeWindow = localFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())

    # First we'll confirm we get the expected default values for the window record keeping
    assert feeWindow.getNumMarkets() == 0
    assert feeWindow.getNumInvalidMarkets() == 0
    assert feeWindow.getNumIncorrectDesignatedReportMarkets() == 0
    assert feeWindow.getNumDesignatedReportNoShows() == 0

    # Go to designated reporting
    proceedToDesignatedReporting(localFixture, market)

    # Do a report that we'll make incorrect
    assert market.doInitialReport([0, market.getNumTicks()], False, "")

    # Do a report for a market we'll say is invalid
    assert categoricalMarket.doInitialReport([0, 0, categoricalMarket.getNumTicks()], False, "")

    # Designated reporter doesn't show up for the third market. Go into initial reporting and do a report by someone else
    reputationToken = localFixture.applySignature('ReputationToken', universe.getReputationToken())
    reputationToken.transfer(tester.a1, 10**6 * 10**18)
    proceedToInitialReporting(localFixture, scalarMarket)
    assert scalarMarket.doInitialReport([0, scalarMarket.getNumTicks()], False, "", sender=tester.k1)

    # proceed to the window start time
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # dispute the first market
    chosenPayoutNumerators = [market.getNumTicks(), 0]
    chosenPayoutHash = market.derivePayoutDistributionHash(chosenPayoutNumerators, False)
    amount = 2 * market.getParticipantStake() - 3 * market.getStakeInOutcome(chosenPayoutHash)
    assert market.contribute(chosenPayoutNumerators, False, amount, "")
    newFeeWindowAddress = market.getFeeWindow()
    assert newFeeWindowAddress != feeWindow

    # dispute the second market with an invalid outcome
    chosenPayoutNumerators = [categoricalMarket.getNumTicks() / 3, categoricalMarket.getNumTicks() / 3, categoricalMarket.getNumTicks() / 3]
    chosenPayoutHash = categoricalMarket.derivePayoutDistributionHash(chosenPayoutNumerators, True)
    amount = 2 * categoricalMarket.getParticipantStake() - 3 * categoricalMarket.getStakeInOutcome(chosenPayoutHash)
    assert categoricalMarket.contribute(chosenPayoutNumerators, True, amount, "")
    assert categoricalMarket.getFeeWindow() != feeWindow

    # progress time forward
    feeWindow = localFixture.applySignature('FeeWindow', newFeeWindowAddress)
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    # finalize the markets
    assert market.finalize()
    assert categoricalMarket.finalize()
    assert scalarMarket.finalize()

    # Now we'll confirm the record keeping was updated
    # Fee Window cadence is different in the subFork Univese tests so we account for that
    assert feeWindow.getNumMarkets() == 3 if localFixture.subFork else 2
    assert feeWindow.getNumInvalidMarkets() == 1
    assert feeWindow.getNumIncorrectDesignatedReportMarkets() == 2

    feeWindow = localFixture.applySignature('FeeWindow', scalarMarket.getFeeWindow())
    assert feeWindow.getNumMarkets() == 3 if localFixture.subFork else 1
    assert feeWindow.getNumDesignatedReportNoShows() == 1

def test_rep_migration_convenience_function(localFixture, universe, market):
    proceedToFork(localFixture, market, universe)

    payoutNumerators = [1, market.getNumTicks()-1]
    payoutDistributionHash = market.derivePayoutDistributionHash(payoutNumerators, False)

    # Initially child universes don't exist
    assert universe.getChildUniverse(payoutDistributionHash) == longToHexString(0)

    # We'll use the convenience function for migrating REP instead of manually creating a child universe
    reputationToken = localFixture.applySignature("ReputationToken", universe.getReputationToken())

    with raises(TransactionFailed):
        reputationToken.migrateOutByPayout(payoutNumerators, False, 0)

    assert reputationToken.migrateOutByPayout(payoutNumerators, False, 10)

    # We can see that the child universe was created
    newUniverse = localFixture.applySignature("Universe", universe.getChildUniverse(payoutDistributionHash))
    newReputationToken = localFixture.applySignature("ReputationToken", newUniverse.getReputationToken())
    assert newReputationToken.balanceOf(tester.a0) == 10

def test_dispute_pacing_threshold(localFixture, universe, market):
    # We'll dispute until we reach the dispute pacing threshold
    while not market.getDisputePacingOn():
        proceedToNextRound(localFixture, market, moveTimeForward = False)

    # Now if we try to immediately dispute without the newly assgiend fee window being active the tx will fail
    with raises(TransactionFailed):
        market.contribute([market.getNumTicks(), 0], False, 1, "")

    # If we move time forward to the fee window start we succeed
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    assert localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    assert market.contribute([market.getNumTicks(), 0], False, 1, "")

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def constants(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['Constants']
