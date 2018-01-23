from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString, TokenDelta, AssertLog, EtherDelta
from reporting_utils import proceedToDesignatedReporting, proceedToInitialReporting, proceedToNextRound, proceedToFork, finalizeFork

tester.STARTGAS = long(6.7 * 10**6)

def test_designatedReportHappyPath(localFixture, universe, market):
    # proceed to the designated reporting period
    proceedToDesignatedReporting(localFixture, market)

    # an address that is not the designated reporter cannot report
    with raises(TransactionFailed):
        market.doInitialReport([0, market.getNumTicks()], False, sender=tester.k1)

    # Reporting with an invalid number of outcomes should fail
    with raises(TransactionFailed):
        market.doInitialReport([0, 0, market.getNumTicks()], False)

    # do an initial report as the designated reporter
    initialReportLog = {
        "universe": universe.address,
        "reporter": bytesToHexString(tester.a0),
        "market": market.address,
        "amountStaked": universe.getInitialReportMinValue(),
        "isDesignatedReporter": True,
        "payoutNumerators": [0, market.getNumTicks()],
        "invalid": False
    }
    with AssertLog(localFixture, "InitialReportSubmitted", initialReportLog):
        assert market.doInitialReport([0, market.getNumTicks()], False)

    with raises(TransactionFailed, message="Cannot initial report twice"):
        assert market.doInitialReport([0, market.getNumTicks()], False)

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
    assert market.doInitialReport([0, market.getNumTicks()], False, sender=sender)

    # the market is now assigned a fee window
    newFeeWindowAddress = market.getFeeWindow()
    assert newFeeWindowAddress
    feeWindow = localFixture.applySignature('FeeWindow', newFeeWindowAddress)

    # time marches on and the market can be finalized
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

def test_initialReport_transfer_ownership(localFixture, universe, market, cash, constants):
    reputationToken = localFixture.applySignature("ReputationToken", universe.getReputationToken())

    # proceed to the initial reporting period
    proceedToInitialReporting(localFixture, market)

    # do an initial report as someone other than the designated reporter
    assert market.doInitialReport([0, market.getNumTicks()], False, sender=tester.k1)

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
    assert initialReporter.transferOwnership(initialReporter.getDesignatedReporter(), sender=tester.k1)

    # The market still correctly indicates the designated reporter did not show up
    assert not market.designatedReporterShowed()

    # When we redeem the initialReporter it goes to the correct party as well
    expectedRep = initialReporter.getStake()
    owner = initialReporter.getOwner()

    expectedGasBond = 2 * constants.GAS_TO_REPORT() * constants.DEFAULT_REPORTING_GAS_PRICE()
    with EtherDelta(expectedGasBond, owner, localFixture.chain, "Initial reporter did not get the reporting gas cost bond"):
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

    # We can't contribute to a crowdsourcer now since the new fee window is not yet active
    with raises(TransactionFailed):
        market.contribute([0, market.getNumTicks()], False)

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
        "amountStaked": universe.getInitialReportMinValue() * 2
    }

    crowdsourcerCompletedLog = {
        "universe": universe.address,
        "market": market.address
    }

    with AssertLog(localFixture, "DisputeCrowdsourcerCreated", crowdsourcerCreatedLog):
        with AssertLog(localFixture, "DisputeCrowdsourcerContribution", crowdsourcerContributionLog):
            with AssertLog(localFixture, "DisputeCrowdsourcerCompleted", crowdsourcerCompletedLog):
                proceedToNextRound(localFixture, market)

    # proceed through several rounds of disputing
    for i in range(rounds - 2):
        proceedToNextRound(localFixture, market)
        assert feeWindow != market.getFeeWindow()
        feeWindow = market.getFeeWindow()
        assert feeWindow == universe.getCurrentFeeWindow()

@mark.parametrize('finalizeByMigration, manuallyDisavow', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_forking(finalizeByMigration, manuallyDisavow, localFixture, universe, market, categoricalMarket, scalarMarket):
    # Let's go into the one dispute round for the categorical market
    proceedToNextRound(localFixture, categoricalMarket)
    proceedToNextRound(localFixture, categoricalMarket)

    # proceed to forking
    proceedToFork(localFixture, market, universe)

    with raises(TransactionFailed, message="We cannot migrate until the fork is finalized"):
        categoricalMarket.migrateThroughOneFork()

    # confirm that we can manually create a child universe from an outcome no one asserted was true during dispute
    numTicks = market.getNumTicks()
    childUniverse = universe.createChildUniverse([numTicks/ 4, numTicks * 3 / 4], False)

    # confirm that before the fork is finalized we can redeem stake in other markets crowdsourcers, which are disavowable
    categoricalDisputeCrowdsourcer = localFixture.applySignature("DisputeCrowdsourcer", categoricalMarket.getReportingParticipant(1))

    if manuallyDisavow:
        assert categoricalMarket.disavowCrowdsourcers()
        # We can redeem before the fork finalizes since disavowal has occured
        assert categoricalDisputeCrowdsourcer.redeem(tester.a0)

    # We cannot contribute to a crowdsourcer during a fork
    with raises(TransactionFailed):
        categoricalMarket.contribute([2,2,categoricalMarket.getNumTicks()-4], False, 1)

    # We cannot purchase new Participation Tokens during a fork
    feeWindowAddress = universe.getCurrentFeeWindow()
    feeWindow = localFixture.applySignature("FeeWindow", feeWindowAddress)
    with raises(TransactionFailed):
        feeWindow.buy(1)

    # finalize the fork
    finalizeFork(localFixture, market, universe, finalizeByMigration)

    # We cannot contribute to a crowdsourcer in a forked universe
    with raises(TransactionFailed):
        categoricalMarket.contribute([2,2,categoricalMarket.getNumTicks()-4], False, 1)

    # The categorical market can be migrated to the winning universe
    assert categoricalMarket.migrateThroughOneFork()

    # The dispute crowdsourcer has been disavowed
    newUniverse = localFixture.applySignature("Universe", categoricalMarket.getUniverse())
    assert newUniverse.address != universe.address
    assert categoricalDisputeCrowdsourcer.isDisavowed()
    assert not universe.isContainerForReportingParticipant(categoricalDisputeCrowdsourcer.address)
    assert not newUniverse.isContainerForReportingParticipant(categoricalDisputeCrowdsourcer.address)

    # The initial report is still present however
    categoricalInitialReport = localFixture.applySignature("InitialReporter", categoricalMarket.getReportingParticipant(0))
    assert categoricalMarket.getReportingParticipant(0) == categoricalInitialReport.address
    assert not categoricalInitialReport.isDisavowed()
    assert not universe.isContainerForReportingParticipant(categoricalInitialReport.address)
    assert newUniverse.isContainerForReportingParticipant(categoricalInitialReport.address)

    # The categorical market has a new fee window since it was initially reported on and may be disputed now
    categoricalMarketFeeWindowAddress = categoricalMarket.getFeeWindow()
    categoricalMarketFeeWindow = localFixture.applySignature("FeeWindow", categoricalMarketFeeWindowAddress)

    proceedToNextRound(localFixture, categoricalMarket, moveTimeForward = False)

    # We can also purchase Participation Tokens in this fee window
    assert categoricalMarketFeeWindow.buy(1)

    # We can migrate a market that has not had its initial reporting completed as well
    assert scalarMarket.migrateThroughOneFork()

def test_forking_values(localFixture, universe, market, cash):
    reputationToken = localFixture.applySignature("ReputationToken", universe.getReputationToken())

    # proceed to forking
    proceedToFork(localFixture, market, universe)

    # finalize the fork
    finalizeFork(localFixture, market, universe)

    # We can see that the theoretical total REP supply in the winning child universe is higher than the initial REP supply
    winningPayoutHash = market.getWinningPayoutDistributionHash()
    childUniverse = localFixture.applySignature("Universe", universe.getChildUniverse(winningPayoutHash))
    childUniverseReputationToken = localFixture.applySignature("ReputationToken", childUniverse.getReputationToken())
    childUniverseTheoreticalSupply = childUniverseReputationToken.getTotalTheoreticalSupply()
    assert childUniverseTheoreticalSupply > reputationToken.getTotalTheoreticalSupply()

    # In fact it will be approximately the bonus REP migrated into the new universe more.
    delta = childUniverseTheoreticalSupply - reputationToken.getTotalTheoreticalSupply()
    migrationBonus = long(childUniverseReputationToken.getTotalMigrated() / 20L)
    participantIndex = 0
    while True:
        try:
            reportingParticipant = localFixture.applySignature("DisputeCrowdsourcer", market.getReportingParticipant(participantIndex))
            participantIndex += 1
            if reportingParticipant.getPayoutDistributionHash() != winningPayoutHash:
                continue
            migrationBonus += long(reportingParticipant.getSize() / 2L)
        except TransactionFailed:
            break
    assert delta == migrationBonus - 5 # rounding error dust buildup

    # The universe needs to be nudged to actually update values since there are potentially unbounded universes and updating the values derived by this total is not essential as a matter of normal procedure
    assert childUniverse.getForkReputationGoal() == universe.getForkReputationGoal()
    assert childUniverse.getDisputeThresholdForFork() == universe.getDisputeThresholdForFork()
    assert childUniverse.getInitialReportMinValue() == universe.getInitialReportMinValue()

    # The universe uses this theoretical total to calculate values such as the fork goal, fork dispute threshhold and the initial reporting defaults and floors
    assert childUniverse.updateForkValues()
    assert childUniverse.getForkReputationGoal() == childUniverseTheoreticalSupply / 2
    assert childUniverse.getDisputeThresholdForFork() == long(childUniverseTheoreticalSupply / 40L)
    assert childUniverse.getInitialReportMinValue() == long(childUniverse.getDisputeThresholdForFork() / 3L / 2**18 + 1)

    # Now we'll fork again and confirm it still takes only 20 dispute rounds in the worst case
    newMarket = localFixture.createReasonableBinaryMarket(childUniverse, cash)
    proceedToFork(localFixture, newMarket, childUniverse)
    assert newMarket.getNumParticipants() == 21

    # finalize the fork
    finalizeFork(localFixture, newMarket, childUniverse)

    # The total theoretical supply is again larger.
    childWinningPayoutHash = newMarket.getWinningPayoutDistributionHash()
    leafUniverse = localFixture.applySignature("Universe", childUniverse.getChildUniverse(childWinningPayoutHash))
    leafUniverseReputationToken = localFixture.applySignature("ReputationToken", leafUniverse.getReputationToken())
    leafUniverseTheoreticalSupply = leafUniverseReputationToken.getTotalTheoreticalSupply()
    assert leafUniverseTheoreticalSupply > childUniverseReputationToken.getTotalTheoreticalSupply()

    # We can make the child universe theoretical total more accurate by asking for a recomputation given a specific sibling universe to deduct from
    losingPayoutHash = market.derivePayoutDistributionHash([0, market.getNumTicks()], False)
    siblingUniverse = localFixture.applySignature("Universe", universe.getChildUniverse(losingPayoutHash))
    siblingReputationToken = localFixture.applySignature("ReputationToken", siblingUniverse.getReputationToken())
    assert childUniverseReputationToken.updateSiblingMigrationTotal(siblingReputationToken.address)
    newChildTheoreticalSupply = childUniverseReputationToken.getTotalTheoreticalSupply()
    siblingMigrationAmount = siblingReputationToken.getTotalMigrated()
    assert childUniverseTheoreticalSupply - newChildTheoreticalSupply == siblingMigrationAmount

    # Now that the child universe has been updated we can ask the leaf universe to recompute based on its parent's new theoretical total supply
    assert leafUniverseReputationToken.updateParentTotalTheoreticalSupply()
    newLeafTheoreticalSupply = leafUniverseReputationToken.getTotalTheoreticalSupply()
    assert leafUniverseTheoreticalSupply - newLeafTheoreticalSupply == siblingMigrationAmount

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
    assert market.doInitialReport([0, market.getNumTicks()], False)

    # Do a report for a market we'll say is invalid
    assert categoricalMarket.doInitialReport([0, 0, categoricalMarket.getNumTicks()], False)

    # Designated reporter doesn't show up for the third market. Go into initial reporting and do a report by someone else
    reputationToken = localFixture.applySignature('ReputationToken', universe.getReputationToken())
    reputationToken.transfer(tester.a1, 10**6 * 10**18)
    proceedToInitialReporting(localFixture, scalarMarket)
    assert scalarMarket.doInitialReport([0, scalarMarket.getNumTicks()], False, sender=tester.k1)

    # proceed to the window start time
    feeWindow = localFixture.applySignature('FeeWindow', market.getFeeWindow())
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # dispute the first market
    chosenPayoutNumerators = [market.getNumTicks(), 0]
    chosenPayoutHash = market.derivePayoutDistributionHash(chosenPayoutNumerators, False)
    amount = 2 * market.getTotalStake() - 3 * market.getStakeInOutcome(chosenPayoutHash)
    assert market.contribute(chosenPayoutNumerators, False, amount)
    newFeeWindowAddress = market.getFeeWindow()
    assert newFeeWindowAddress != feeWindow

    # dispute the second market with an invalid outcome
    chosenPayoutNumerators = [categoricalMarket.getNumTicks() / 3, categoricalMarket.getNumTicks() / 3, categoricalMarket.getNumTicks() / 3]
    chosenPayoutHash = categoricalMarket.derivePayoutDistributionHash(chosenPayoutNumerators, True)
    amount = 2 * categoricalMarket.getTotalStake() - 3 * categoricalMarket.getStakeInOutcome(chosenPayoutHash)
    assert categoricalMarket.contribute(chosenPayoutNumerators, True, amount)
    assert categoricalMarket.getFeeWindow() != feeWindow

    # progress time forward
    feeWindow = localFixture.applySignature('FeeWindow', newFeeWindowAddress)
    localFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    # finalize the markets
    assert market.finalize()
    assert categoricalMarket.finalize()
    assert scalarMarket.finalize()

    # Now we'll confirm the record keeping was updated
    assert feeWindow.getNumMarkets() == 2
    assert feeWindow.getNumInvalidMarkets() == 1
    assert feeWindow.getNumIncorrectDesignatedReportMarkets() == 2

    feeWindow = localFixture.applySignature('FeeWindow', scalarMarket.getFeeWindow())
    assert feeWindow.getNumMarkets() == 1
    assert feeWindow.getNumDesignatedReportNoShows() == 1


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