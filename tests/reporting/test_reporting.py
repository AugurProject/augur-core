from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs
from reporting_utils import proceedToDesignatedReporting, proceedToFirstReporting, proceedToLastReporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

tester.STARTGAS = long(6.7 * 10**6)

def test_reportingFullHappyPath(reportingFixture):
    cash = reportingFixture.cash
    market = reportingFixture.binaryMarket
    universe = reportingFixture.universe
    reputationToken = reportingFixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingTokenNo = reportingFixture.getReportingToken(market, [10**18,0])
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,10**18])
    reportingWindow = reportingFixture.applySignature('ReportingWindow', universe.getNextReportingWindow())
    expectedMarketCreatorFeePayout = reportingFixture.contracts["MarketFeeCalculator"].getValidityBond(universe.address)
    reporterGasCosts = reportingFixture.contracts["MarketFeeCalculator"].getTargetReporterGasCosts(universe.address)

    # We can't yet report on the market as it's in the pre reporting phase
    assert market.getReportingState() == reportingFixture.constants.PRE_REPORTING()
    with raises(TransactionFailed, message="Reporting cannot be done in the PRE REPORTING state"):
        reportingTokenNo.buy(100, sender=tester.k0)

    # Fast forward to one second after the next reporting window
    reportingFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1

    # This will cause us to be in the first reporting phase
    assert market.getReportingState() == reportingFixture.constants.FIRST_REPORTING()

    noShowBondCosts = 3 * reportingFixture.constants.DEFAULT_DESIGNATED_REPORT_NO_SHOW_BOND()
    # Both reporters report on the outcome. Tester 1 reports first, winning the no-show REP bond and and causing the YES outcome to be the tentative winner
    initialFirstReporterETH = reportingFixture.utils.getETHBalance(tester.a1)
    reportingTokenYes.buy(0, sender=tester.k1)
    assert reportingTokenYes.balanceOf(tester.a1) == 2 * 10 ** 18
    assert reputationToken.balanceOf(tester.a1) == 1 * 10**6 * 10 **18
    reportingTokenNo.buy(100, sender=tester.k0)
    assert reportingTokenNo.balanceOf(tester.a0) == 100
    assert reputationToken.balanceOf(tester.a0) == 8 * 10**6 * 10 **18 - 100 - noShowBondCosts
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenYes.getPayoutDistributionHash()

    # The first reporter also recieves reporter gas fees
    assert reportingFixture.utils.getETHBalance(tester.a1) == initialFirstReporterETH + reporterGasCosts

    # Move time forward into the FIRST DISPUTE phase
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.FIRST_DISPUTE()

    # Contest the results with Tester 0
    market.disputeFirstReporters([], 0, sender=tester.k0)
    assert not reportingWindow.isContainerForMarket(market.address)
    assert universe.isContainerForMarket(market.address)
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)

    # We're now in the LAST REPORTING phase
    assert market.getReportingState() == reportingFixture.constants.LAST_REPORTING()

    # Tester 0 has a REP balance less the first bond amount
    assert reputationToken.balanceOf(tester.a0) == 8 * 10**6 * 10 **18 - 100 - 11 * 10**21 - noShowBondCosts

    # Tester 2 reports for the NO outcome
    reportingFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1
    reportingTokenNo.buy(2, sender=tester.k2)
    assert reportingTokenNo.balanceOf(tester.a2) == 2
    assert reputationToken.balanceOf(tester.a2) == 10**6 * 10 **18 - 2
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenNo.getPayoutDistributionHash()

    # Move forward in time to put us in the LAST DISPUTE PHASE
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.LAST_DISPUTE()

    # Tester 1 contests the outcome of the ALL report which will cause a fork
    market.disputeLastReporters(sender=tester.k1)
    assert universe.getForkingMarket() == market.address
    assert not reportingWindow.isContainerForMarket(market.address)
    assert universe.isContainerForMarket(market.address)
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)
    assert market.getReportingState() == reportingFixture.constants.FORKING()

    # The universe forks and there is now a universe where NO and YES are the respective outcomes of each
    noUniverse = reportingFixture.getOrCreateChildUniverse(universe, market, [10**18,0])
    noUniverseReputationToken = reportingFixture.applySignature('ReputationToken', noUniverse.getReputationToken())
    assert noUniverse.address != universe.address
    yesUniverse = reportingFixture.getOrCreateChildUniverse(universe, market, [0,10**18])
    yesUniverseReputationToken = reportingFixture.applySignature('ReputationToken', yesUniverse.getReputationToken())
    assert yesUniverse.address != universe.address
    assert yesUniverse.address != noUniverse.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated
    assert market.tryFinalize() == 0

    # Tester 1 moves their ~1 Million REP to the YES universe
    reputationToken.migrateOut(yesUniverseReputationToken.address, tester.a1, reputationToken.balanceOf(tester.a1), sender = tester.k1)
    assert not reputationToken.balanceOf(tester.a1)
    assert yesUniverseReputationToken.balanceOf(tester.a1) == 10**6 * 10**18 - 110000 * 10**18

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    assert market.tryFinalize() == 0

    # Testers 0 and 2 move their combined ~9 million REP to the NO universe
    reputationToken.migrateOut(noUniverseReputationToken.address, tester.a0, reputationToken.balanceOf(tester.a0), sender = tester.k0)
    assert not reputationToken.balanceOf(tester.a0)
    assert noUniverseReputationToken.balanceOf(tester.a0) == 8 * 10 ** 6 * 10 ** 18 - 100 - 11000 * 10 ** 18 - noShowBondCosts
    reputationToken.migrateOut(noUniverseReputationToken.address, tester.a2, reputationToken.balanceOf(tester.a2), sender = tester.k2)
    assert not reputationToken.balanceOf(tester.a2)
    assert noUniverseReputationToken.balanceOf(tester.a2) == 1 * 10 ** 6 * 10 ** 18  - 2

    # We can finalize the market now since a mjaority of REP has moved. Alternatively we could "reportingFixture.chain.head_state.timestamp = universe.getForkEndTime() + 1" to move
    initialMarketCreatorETHBalance = reportingFixture.utils.getETHBalance(market.getOwner())
    assert market.tryFinalize()

    # The market is now finalized and the NO outcome is the winner
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()
    assert market.getFinalWinningReportingToken() == reportingTokenNo.address

    # Since the designated report was not invalid the market creator gets back the validity bond
    increaseInMarketCreatorBalance = reportingFixture.utils.getETHBalance(market.getOwner()) - initialMarketCreatorETHBalance
    assert increaseInMarketCreatorBalance == expectedMarketCreatorFeePayout

    # We can redeem forked REP on any universe we didn't dispute
    assert reportingTokenNo.redeemForkedTokens(sender = tester.k0)
    assert noUniverseReputationToken.balanceOf(tester.a0) == 8 * 10 ** 6 * 10 ** 18 - 11000 * 10 ** 18 - noShowBondCosts

def test_designatedReportingHappyPath(reportingFixture):
    market = reportingFixture.binaryMarket

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(reportingFixture, market, [0,10**18])

    # To progress into the DESIGNATED DISPUTE phase we do a designated report
    assert reportingFixture.designatedReport(market, [0,10**18], tester.k0)

    # We're now in the DESIGNATED DISPUTE PHASE
    assert market.getReportingState() == reportingFixture.constants.DESIGNATED_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    reportingFixture.chain.head_state.timestamp = market.getEndTime() + reportingFixture.constants.DESIGNATED_REPORTING_DURATION_SECONDS() + reportingFixture.constants.DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == reportingFixture.constants.AWAITING_FINALIZATION()

    # We can finalize it
    assert market.tryFinalize()
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()

@mark.parametrize('makeReport', [
    True,
    False
])
def test_firstReportingHappyPath(makeReport, reportingFixture):
    market = reportingFixture.binaryMarket
    universe = reportingFixture.universe
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = reportingFixture.applySignature('ReputationToken', universe.getReputationToken())

    # Proceed to the FIRST REPORTING phase
    proceedToFirstReporting(reportingFixture, market, makeReport, tester.k1, [0,10**18], [10**18,0])

    # We make one report by Tester 2
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,10**18])
    reportingTokenYes.buy(1, sender=tester.k2)
    # If there ws no designated report he first reporter gets the no-show REP bond auto-staked on the outcome they're purchasing
    expectedReportingTokenBalance = 1
    if (not makeReport):
        expectedReportingTokenBalance += reportingFixture.contracts["MarketFeeCalculator"].getDesignatedReportNoShowBond(universe.address)

    assert reportingTokenYes.balanceOf(tester.a2) == expectedReportingTokenBalance

    assert reputationToken.balanceOf(tester.a2) == 1 * 10 ** 6 * 10 ** 18 - 1
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    if (makeReport):
        # The tentative winner will be the No outcome at first since we disputed Yes and have to stake on an outcome in that case
        reportingTokenNo = reportingFixture.getReportingToken(market, [10**18,0])
        assert tentativeWinner == reportingTokenNo.getPayoutDistributionHash()
        # If we buy the full designated bond amount we will be back to the YES outcome winning
        reportingTokenYes.buy(reportingFixture.constants.DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT(), sender=tester.k2)
        tentativeWinner = market.getTentativeWinningPayoutDistributionHash()

    assert tentativeWinner == reportingTokenYes.getPayoutDistributionHash()

    # To progress into the FIRST DISPUTE phase we move time forward
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.FIRST_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == reportingFixture.constants.AWAITING_FINALIZATION()

    # We can finalize it
    assert market.tryFinalize()
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()


@mark.parametrize('makeReport', [
    True,
    False
])
def test_lastReportingHappyPath(reportingFixture, makeReport):
    market = reportingFixture.binaryMarket
    universe = reportingFixture.universe
    reputationToken = reportingFixture.applySignature('ReputationToken', universe.getReputationToken())

    # Proceed to the LAST REPORTING phase
    proceedToLastReporting(reportingFixture, market, makeReport, tester.k1, tester.k3, [0,10**18], [10**18,0], tester.k2, [10**18,0], [0,10**18])

    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    reportingTokenNo = reportingFixture.getReportingToken(market, [10**18,0])
    reportingTokenYes = reportingFixture.getReportingToken(market, [0,10**18])

    # When disputing the FIRST REPORT outcome enough was staked on the other outcome that it is now the winner
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenYes.getPayoutDistributionHash()

    # If we buy the delta between outcome stakes that will be sufficient to make the outcome win
    marketExtensions = reportingFixture.contracts["MarketExtensions"]
    noStake = marketExtensions.getPayoutDistributionHashStake(market.address, reportingTokenNo.getPayoutDistributionHash())
    yesStake = marketExtensions.getPayoutDistributionHashStake(market.address, reportingTokenYes.getPayoutDistributionHash())
    stakeDelta = yesStake - noStake
    reportingTokenNo.buy(stakeDelta + 1, sender=tester.k3)

    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenNo.getPayoutDistributionHash()

    # To progress into the LAST DISPUTE phase we move time forward
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == reportingFixture.constants.LAST_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == reportingFixture.constants.AWAITING_FINALIZATION()

    # We can finalize it
    assert market.tryFinalize()
    assert market.getReportingState() == reportingFixture.constants.FINALIZED()


@mark.parametrize('makeReport, finalizeByMigration', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_forking(reportingFixture, makeReport, finalizeByMigration):
    market = reportingFixture.binaryMarket
    # Proceed to the FORKING phase
    proceedToForking(reportingFixture, market, makeReport, tester.k1, tester.k3, tester.k3, [0,10**18], [10**18,0], tester.k2, [10**18,0], [0,10**18], [10**18,0])

    # Finalize the market
    finalizeForkingMarket(reportingFixture, market, finalizeByMigration, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,10**18], [10**18,0])


@mark.parametrize('makeReport, finalizeByMigration', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_forkMigration(reportingFixture, makeReport, finalizeByMigration):
    market = reportingFixture.binaryMarket
    cash = reportingFixture.cash
    newMarket = reportingFixture.createReasonableBinaryMarket(reportingFixture.universe, cash)
    completeSets = reportingFixture.contracts['CompleteSets']

    # We'll do some transactions that cause fee collection here so we can test that fees are properly migrated automatically when a market migrates from a fork
    cost = 10 * newMarket.getNumTicks()
    completeSets.publicBuyCompleteSets(newMarket.address, 10, sender = tester.k1, value = cost)
    completeSets.publicSellCompleteSets(newMarket.address, 10, sender=tester.k1)
    oldReportingWindowAddress = newMarket.getReportingWindow()
    fees = cash.balanceOf(oldReportingWindowAddress)
    assert fees > 0
    assert cash.balanceOf(oldReportingWindowAddress) == fees

    # We proceed the standard market to the FORKING state
    proceedToForking(reportingFixture,  market, makeReport, tester.k1, tester.k2, tester.k3, [0,10**18], [10**18,0], tester.k2, [10**18,0], [0,10**18], [10**18,0])

    # The market we created is now awaiting migration
    assert newMarket.getReportingState() == reportingFixture.constants.AWAITING_FORK_MIGRATION()

    # If we attempt to migrate now it will not work since the forking market is not finalized
    with raises(TransactionFailed, message="Migration cannot occur until the forking market is finalized"):
        newMarket.migrateThroughOneFork()

    # We'll finalize the forking market
    finalizeForkingMarket(reportingFixture, market, finalizeByMigration, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,10**18], [10**18,0])

    # Now we can migrate the market to the winning universe
    assert newMarket.migrateThroughOneFork()

    # We observe that the reporting window no longer has the fees collected
    assert cash.balanceOf(oldReportingWindowAddress) == 0

    # Now that we're on the correct universe we are send back to the DESIGNATED REPORTING phase
    assert newMarket.getReportingState() == reportingFixture.constants.DESIGNATED_REPORTING()

    # We can confirm that migrating the market also triggered a migration of its reporting window's ETH fees to the new reporting window
    assert cash.balanceOf(newMarket.getReportingWindow()) == fees

@mark.parametrize('pastDisputePhase', [
    True,
    False
])
def test_noReports(reportingFixture, pastDisputePhase):
    market = reportingFixture.binaryMarket

    # Proceed to the FIRST REPORTING phase
    proceedToFirstReporting(reportingFixture, market, False, tester.k1, [0,10**18], [10**18,0])

    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())

    if (pastDisputePhase):
        reportingFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    else:
        reportingFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    
    # If we receive no reports by the time Limited Reporting is finished we will be in the AWAITING NO REPORT MIGRATION phase
    assert market.getReportingState() == reportingFixture.constants.AWAITING_NO_REPORT_MIGRATION()

    # We can try to report on the market, which will move it to the next reporting window where it will be back in FIRST REPORTING
    reportingToken = reportingFixture.getReportingToken(market, [0,10**18])
    assert reportingToken.buy(1, sender=tester.k2)

    assert market.getReportingState() == reportingFixture.constants.FIRST_REPORTING()
    assert market.getReportingWindow() != reportingWindow.address

def test_invalid_first_report(reportingFixture):
    market = reportingFixture.binaryMarket
    universe = reportingFixture.universe
    cash = reportingFixture.cash
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = reportingFixture.applySignature('ReputationToken', universe.getReputationToken())
    expectedReportingWindowFeePayout = reportingFixture.contracts["MarketFeeCalculator"].getValidityBond(universe.address)

    # Proceed to the FIRST REPORTING phase
    proceedToFirstReporting(reportingFixture, market, False, tester.k1, [0,10**18], [10**18,0])

    # We make an invalid report
    reportingTokenInvalid = reportingFixture.getReportingToken(market, [long(0.5 * 10 ** 18), long(0.5 * 10 ** 18)])
    reportingTokenInvalid.buy(1, sender=tester.k2)
    assert reportingTokenInvalid.balanceOf(tester.a2) == 1 + reportingFixture.contracts["MarketFeeCalculator"].getDesignatedReportNoShowBond(universe.address)
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenInvalid.getPayoutDistributionHash()
    assert not reportingTokenInvalid.isValid()

    # If we finalize the market it will be recorded as an invalid result
    initialReportingWindowCashBalance = cash.balanceOf(reportingWindow.address)
    reportingFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()
    assert not market.isValid()
    assert reportingWindow.getNumInvalidMarkets() == 1

    # Since the market resolved with an invalid outcome the validity bond is paid out to the reporting window in Cash
    increaseInReportingWindowBalance = cash.balanceOf(reportingWindow.address) - initialReportingWindowCashBalance
    assert increaseInReportingWindowBalance == expectedReportingWindowFeePayout

def test_invalid_designated_report(reportingFixture):
    market = reportingFixture.binaryMarket
    cash = reportingFixture.cash
    reportingWindow = reportingFixture.applySignature('ReportingWindow', market.getReportingWindow())
    expectedReportingWindowFeePayout = reportingFixture.contracts["MarketFeeCalculator"].getValidityBond(market.getUniverse())
    expectedMarketCreatorFeePayout = reportingFixture.contracts["MarketFeeCalculator"].getTargetReporterGasCosts(market.getUniverse())

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(reportingFixture, market, [long(0.5 * 10 ** 18), long(0.5 * 10 ** 18)])

    # To progress into the DESIGNATED DISPUTE phase we do a designated report of invalid
    initialMarketCreatorETHBalance = reportingFixture.utils.getETHBalance(market.getOwner())
    assert reportingFixture.designatedReport(market, [long(0.5 * 10 ** 18), long(0.5 * 10 ** 18)], tester.k0)

    # We're now in the DESIGNATED DISPUTE PHASE
    assert market.getReportingState() == reportingFixture.constants.DESIGNATED_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    reportingFixture.chain.head_state.timestamp = market.getEndTime() + reportingFixture.constants.DESIGNATED_REPORTING_DURATION_SECONDS() + reportingFixture.constants.DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == reportingFixture.constants.AWAITING_FINALIZATION()

    # If we finalize the market it will be recorded as an invalid result
    initialReportingWindowCashBalance = cash.balanceOf(reportingWindow.address)
    assert market.tryFinalize()
    assert not market.isValid()
    assert reportingWindow.getNumInvalidMarkets() == 1

    # Since the market resolved with an invalid outcome the validity bond is paid out to the reporting window
    increaseInReportingWindowBalance = cash.balanceOf(reportingWindow.address) - initialReportingWindowCashBalance
    assert increaseInReportingWindowBalance == expectedReportingWindowFeePayout

    # Since the designated reporter showed up the market creator still gets back the reporter gas cost fee
    increaseInMarketCreatorBalance = reportingFixture.utils.getETHBalance(market.getOwner()) - initialMarketCreatorETHBalance
    assert increaseInMarketCreatorBalance == expectedMarketCreatorFeePayout

@fixture(scope="session")
def reportingSnapshot(sessionFixture):
    sessionFixture.resetSnapshot()
    return initializeReportingFixture(sessionFixture, sessionFixture.binaryMarket)

@fixture
def reportingFixture(sessionFixture, reportingSnapshot):
    sessionFixture.resetToSnapshot(reportingSnapshot)
    return sessionFixture
