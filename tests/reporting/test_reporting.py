from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, bytesToHexString, TokenDelta
from reporting_utils import proceedToDesignatedReporting, proceedToFirstReporting, proceedToLastReporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

tester.STARTGAS = long(6.7 * 10**6)

@mark.parametrize('getStakeBonus', [
    True,
    False
])
def test_reportingFullHappyPath(getStakeBonus, localFixture, universe, cash, market):
    reputationToken = localFixture.applySignature('ReputationToken', universe.getReputationToken())
    stakeTokenNo = localFixture.getOrCreateStakeToken(market, [10**18,0])
    stakeTokenYes = localFixture.getOrCreateStakeToken(market, [0,10**18])
    reportingWindow = localFixture.applySignature('ReportingWindow', universe.getOrCreateNextReportingWindow())
    expectedMarketCreatorFeePayout = universe.getValidityBond()
    reporterGasCosts = universe.getTargetReporterGasCosts()

    # We can't yet report on the market as it's in the pre reporting phase
    assert market.getReportingState() == localFixture.contracts['Constants'].PRE_REPORTING()
    with raises(TransactionFailed, message="Reporting cannot be done in the PRE REPORTING state"):
        stakeTokenNo.buy(100, sender=tester.k0)

    # Fast forward to one second after the next reporting window
    localFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1

    # This will cause us to be in the first reporting phase
    assert market.getReportingState() == localFixture.contracts['Constants'].FIRST_REPORTING()

    noShowBondCosts = 3 * localFixture.contracts['Constants'].DEFAULT_DESIGNATED_REPORT_NO_SHOW_BOND()
    # Both reporters report on the outcome. Tester 1 reports first, winning the no-show REP bond and and causing the YES outcome to be the tentative winner
    initialFirstReporterETH = localFixture.chain.head_state.get_balance(tester.a1)
    stakeTokenYes.buy(0, sender=tester.k1)
    assert stakeTokenYes.balanceOf(tester.a1) == 2 * 10 ** 18
    assert reputationToken.balanceOf(tester.a1) == 1 * 10**6 * 10 **18
    stakeTokenNo.buy(100, sender=tester.k0)
    assert stakeTokenNo.balanceOf(tester.a0) == 100
    assert reputationToken.balanceOf(tester.a0) == 8 * 10**6 * 10 **18 - 100 - noShowBondCosts
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == stakeTokenYes.getPayoutDistributionHash()

    # The first reporter also recieves reporter gas fees
    assert localFixture.chain.head_state.get_balance(tester.a1) == initialFirstReporterETH + reporterGasCosts

    # Move time forward into the FIRST DISPUTE phase
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == localFixture.contracts['Constants'].FIRST_DISPUTE()

    # Contest the results with Tester 0
    market.disputeFirstReporters([], 0, False, sender=tester.k0)
    assert not reportingWindow.isContainerForMarket(market.address)
    assert universe.isContainerForMarket(market.address)
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)

    # We're now in the LAST REPORTING phase
    assert market.getReportingState() == localFixture.contracts['Constants'].LAST_REPORTING()

    # Tester 0 has a REP balance less the first bond amount
    assert reputationToken.balanceOf(tester.a0) == 8 * 10**6 * 10 **18 - 100 - 11 * 10**21 - noShowBondCosts

    # Tester 2 reports for the NO outcome
    localFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1
    stakeTokenNo.buy(2, sender=tester.k2)
    assert stakeTokenNo.balanceOf(tester.a2) == 2
    assert reputationToken.balanceOf(tester.a2) == 10**6 * 10 **18 - 2
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == stakeTokenNo.getPayoutDistributionHash()

    # Move forward in time to put us in the LAST DISPUTE PHASE
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == localFixture.contracts['Constants'].LAST_DISPUTE()

    # Tester 1 contests the outcome of the ALL report which will cause a fork
    market.disputeLastReporters(sender=tester.k1)
    assert universe.getForkingMarket() == market.address
    assert not reportingWindow.isContainerForMarket(market.address)
    assert universe.isContainerForMarket(market.address)
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)
    assert market.getReportingState() == localFixture.contracts['Constants'].FORKING()

    # The universe forks and there is now a universe where NO and YES are the respective outcomes of each
    noUniverse = localFixture.getOrCreateChildUniverse(universe, market, [10**18,0])
    noUniverseReputationToken = localFixture.applySignature('ReputationToken', noUniverse.getReputationToken())
    assert noUniverse.address != universe.address
    yesUniverse = localFixture.getOrCreateChildUniverse(universe, market, [0,10**18])
    yesUniverseReputationToken = localFixture.applySignature('ReputationToken', yesUniverse.getReputationToken())
    assert yesUniverse.address != universe.address
    assert yesUniverse.address != noUniverse.address

    # Attempting to finalize the fork now will not succeed as no REP has been migrated
    assert market.tryFinalize() == 0

    logs = []
    captureFilteredLogs(localFixture.chain.head_state, localFixture.contracts['Augur'], logs)

    # Tester 1 moves their ~1 Million REP to the YES universe and gets a fixed percentage bonus for doing so within the FORKING period
    expectedAmount = reputationToken.balanceOf(tester.a1)
    bonus = expectedAmount / localFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
    reputationToken.migrateOut(yesUniverseReputationToken.address, tester.a1, reputationToken.balanceOf(tester.a1), sender = tester.k1)
    assert not reputationToken.balanceOf(tester.a1)
    assert yesUniverseReputationToken.balanceOf(tester.a1) == expectedAmount + bonus

    # Confirm the token logs were generated correctly

    assert len(logs) == 3

    burnLog = logs[0]
    mintLog = logs[1]
    bonusMintLog = logs[2]

    assert burnLog['_event_type'] == 'TokensBurned'
    assert burnLog['amount'] == expectedAmount
    assert burnLog['token'] == reputationToken.address
    assert burnLog['universe'] == universe.address

    assert mintLog['_event_type'] == 'TokensMinted'
    assert mintLog['amount'] == expectedAmount
    assert mintLog['token'] == yesUniverseReputationToken.address
    assert mintLog['universe'] == yesUniverse.address

    assert bonusMintLog['_event_type'] == 'TokensMinted'
    assert bonusMintLog['amount'] == bonus
    assert bonusMintLog['token'] == yesUniverseReputationToken.address
    assert bonusMintLog['universe'] == yesUniverse.address

    # Attempting to finalize the fork now will not succeed as a majority or REP has not yet migrated and fork end time has not been reached
    assert market.tryFinalize() == 0

    # Testers 0 and 2 move their combined ~9 million REP to the NO universe and receive a bonus since they are within the FORKING period
    expectedAmount = reputationToken.balanceOf(tester.a0)
    bonus = expectedAmount / localFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
    reputationToken.migrateOut(noUniverseReputationToken.address, tester.a0, reputationToken.balanceOf(tester.a0), sender = tester.k0)
    assert not reputationToken.balanceOf(tester.a0)
    tester0REPBalance = noUniverseReputationToken.balanceOf(tester.a0)
    assert tester0REPBalance == expectedAmount + bonus
    expectedAmount = reputationToken.balanceOf(tester.a2)
    bonus = expectedAmount / localFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
    reputationToken.migrateOut(noUniverseReputationToken.address, tester.a2, reputationToken.balanceOf(tester.a2), sender = tester.k2)
    assert not reputationToken.balanceOf(tester.a2)
    assert noUniverseReputationToken.balanceOf(tester.a2) == expectedAmount + bonus

    logs = []
    captureFilteredLogs(localFixture.chain.head_state, localFixture.contracts['Augur'], logs)

    # We can finalize the market now since a mjaority of REP has moved. Alternatively we could "localFixture.chain.head_state.timestamp = universe.getForkEndTime() + 1" to move
    initialMarketCreatorETHBalance = localFixture.chain.head_state.get_balance(market.getOwner())
    assert market.tryFinalize()

    # Confirm market finalization logging works
    assert len(logs) == 1
    assert logs[0]['_event_type'] == 'MarketFinalized'
    assert logs[0]['market'] == market.address

    # The market is now finalized and the NO outcome is the winner
    assert market.getReportingState() == localFixture.contracts['Constants'].FINALIZED()
    assert market.getFinalWinningStakeToken() == stakeTokenNo.address

    # Since the designated report was not invalid the market creator gets back the validity bond
    increaseInMarketCreatorBalance = localFixture.chain.head_state.get_balance(market.getOwner()) - initialMarketCreatorETHBalance
    assert increaseInMarketCreatorBalance == expectedMarketCreatorFeePayout

    # We can redeem forked REP on any universe we didn't dispute
    stakeTokenBalance = stakeTokenNo.balanceOf(tester.a0)

    # If we wait until after the fork window we won't get the bonus when migrating stake tokens
    bonus = stakeTokenBalance / localFixture.contracts["Constants"].FORK_MIGRATION_PERCENTAGE_BONUS_DIVISOR()
    expectedrepBalanceInNewUniverse = noUniverseReputationToken.balanceOf(tester.a0) + stakeTokenBalance
    if (not getStakeBonus):
        localFixture.chain.head_state.timestamp = universe.getForkEndTime() + 1
    else:
        expectedrepBalanceInNewUniverse += bonus

    assert stakeTokenNo.redeemForkedTokens(sender = tester.k0)
    assert noUniverseReputationToken.balanceOf(tester.a0) == expectedrepBalanceInNewUniverse

    # We can also see that a tester who now migrates their REP will also not get the bonus
    expectedAmount = reputationToken.balanceOf(tester.a3)
    reputationToken.migrateOut(noUniverseReputationToken.address, tester.a3, reputationToken.balanceOf(tester.a3), sender = tester.k3)
    assert not reputationToken.balanceOf(tester.a3)
    assert noUniverseReputationToken.balanceOf(tester.a3) == expectedAmount

def test_designatedReportingHappyPath(localFixture, universe, market):
    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(localFixture, universe, market, [0,10**18])

    reportingWindow = localFixture.applySignature("ReportingWindow", market.getReportingWindow())

    originalNumDesignatedReportNoShows = reportingWindow.getNumDesignatedReportNoShows()

    # To progress into the DESIGNATED DISPUTE phase we do a designated report
    logs = []
    captureFilteredLogs(localFixture.chain.head_state, localFixture.contracts['Augur'], logs)
    assert localFixture.designatedReport(market, [0,10**18], tester.k0)

    # Confirm the designated report logging works
    assert len(logs) == 4
    assert logs[3]['_event_type'] == 'DesignatedReportSubmitted'
    assert logs[3]['amountStaked'] == localFixture.contracts["Constants"].DEFAULT_DESIGNATED_REPORT_STAKE()
    assert logs[3]['reporter'] == bytesToHexString(tester.a0)
    assert logs[3]['stakeToken'] == localFixture.getOrCreateStakeToken(market, [0,10**18]).address
    assert logs[3]['market'] == market.address
    assert logs[3]['payoutNumerators'] == [0,10**18]

    # making a designated report also decremented the no show accounting on the reporting window
    assert reportingWindow.getNumDesignatedReportNoShows() == originalNumDesignatedReportNoShows - 1

    # We're now in the DESIGNATED DISPUTE PHASE
    assert market.getReportingState() == localFixture.contracts['Constants'].DESIGNATED_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    localFixture.chain.head_state.timestamp = market.getEndTime() + localFixture.contracts['Constants'].DESIGNATED_REPORTING_DURATION_SECONDS() + localFixture.contracts['Constants'].DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == localFixture.contracts['Constants'].AWAITING_FINALIZATION()

    # We can finalize it
    assert market.tryFinalize()
    assert market.getReportingState() == localFixture.contracts['Constants'].FINALIZED()

@mark.parametrize('makeReport', [
    True,
    False
])
def test_firstReportingHappyPath(makeReport, localFixture, universe, market):
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = localFixture.applySignature('ReputationToken', universe.getReputationToken())

    # Proceed to the FIRST REPORTING phase
    proceedToFirstReporting(localFixture, universe, market, makeReport, 1, [0,10**18], [10**18,0])

    logs = []
    captureFilteredLogs(localFixture.chain.head_state, localFixture.contracts['Augur'], logs)

    # We make one report by Tester 2
    stakeTokenYes = localFixture.getOrCreateStakeToken(market, [0,10**18])
    stakeTokenYes.buy(1, sender=tester.k2)
    # If there ws no designated report he first reporter gets the no-show REP bond auto-staked on the outcome they're purchasing
    expectedStakeTokenBalance = 1
    if (not makeReport):
        expectedStakeTokenBalance += universe.getDesignatedReportNoShowBond()

    assert stakeTokenYes.balanceOf(tester.a2) == expectedStakeTokenBalance

    # Confirm the report logging works
    log = logs[2]
    if not makeReport:
        log = logs[3]
        assert len(logs) == 4
    else:
        assert len(logs) == 3

    assert log['_event_type'] == 'ReportSubmitted'
    assert log['amountStaked'] == expectedStakeTokenBalance
    assert log['reporter'] == bytesToHexString(tester.a2)
    assert log['stakeToken'] == localFixture.getOrCreateStakeToken(market, [0,10**18]).address
    assert log['market'] == market.address
    assert log['payoutNumerators'] == [0,10**18]

    assert reputationToken.balanceOf(tester.a2) == 1 * 10 ** 6 * 10 ** 18 - 1
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    if (makeReport):
        # The tentative winner will be the No outcome at first since we disputed Yes and have to stake on an outcome in that case
        stakeTokenNo = localFixture.getOrCreateStakeToken(market, [10**18,0])
        assert tentativeWinner == stakeTokenNo.getPayoutDistributionHash()
        # If we buy the full designated bond amount we will be back to the YES outcome winning
        stakeTokenYes.buy(localFixture.contracts['Constants'].DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT(), sender=tester.k2)
        tentativeWinner = market.getTentativeWinningPayoutDistributionHash()

    assert tentativeWinner == stakeTokenYes.getPayoutDistributionHash()

    # To progress into the FIRST DISPUTE phase we move time forward
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == localFixture.contracts['Constants'].FIRST_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == localFixture.contracts['Constants'].AWAITING_FINALIZATION()

    # We can finalize it
    assert market.tryFinalize()
    assert market.getReportingState() == localFixture.contracts['Constants'].FINALIZED()

@mark.parametrize('makeReport', [
    True,
    False
])
def test_lastReportingHappyPath(localFixture, makeReport, universe, market, cash):
    newMarket = localFixture.createReasonableBinaryMarket(universe, cash)
    completeSets = localFixture.contracts['CompleteSets']
    reputationToken = localFixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())

    # Generate some fees to confirm the market migration also migrates proportional fees
    cost = 10 * market.getNumTicks()
    assert completeSets.publicBuyCompleteSets(market.address, 10, sender=tester.k1, value=cost)
    assert completeSets.publicSellCompleteSets(market.address, 10, sender=tester.k1)
    fees = cash.balanceOf(newMarket.getReportingWindow())
    assert fees > 0

    # We'll proceed to the designated reporting phase so that there is also stake from a market that does not migrate
    proceedToFirstReporting(localFixture, universe, newMarket, makeReport, 1, [0,10**18], [10**18,0])
    newMarketStakeToken = localFixture.getOrCreateStakeToken(newMarket, [0,10**18])
    firstDisputeStake = localFixture.contracts["Constants"].FIRST_REPORTERS_DISPUTE_BOND_AMOUNT()
    assert newMarketStakeToken.buy(firstDisputeStake)

    # Proceed to the LAST REPORTING phase for the main market
    originalReportingWindowStake = reportingWindow.getTotalStake()
    assert originalReportingWindowStake > 0
    proceedToLastReporting(localFixture, universe, market, makeReport, 1, 3, [0,10**18], [10**18,0], 2, [10**18,0], [0,10**18])

    # Confirm that fees have moved proportionally when the market migrated from the first dispute
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    expectedMigratedFees = fees / 2
    assert cash.balanceOf(market.getReportingWindow()) == expectedMigratedFees

    stakeTokenNo = localFixture.getOrCreateStakeToken(market, [10**18,0])
    stakeTokenYes = localFixture.getOrCreateStakeToken(market, [0,10**18])

    # When disputing the FIRST REPORT outcome enough was staked on the other outcome that it is now the winner
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == stakeTokenYes.getPayoutDistributionHash()

    # If we buy the delta between outcome stakes that will be sufficient to make the outcome win
    noStake = market.getPayoutDistributionHashStake(stakeTokenNo.getPayoutDistributionHash())
    yesStake = market.getPayoutDistributionHashStake(stakeTokenYes.getPayoutDistributionHash())
    stakeDelta = yesStake - noStake
    stakeTokenNo.buy(stakeDelta + 1, sender=tester.k3)

    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == stakeTokenNo.getPayoutDistributionHash()

    # To progress into the LAST DISPUTE phase we move time forward
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == localFixture.contracts['Constants'].LAST_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == localFixture.contracts['Constants'].AWAITING_FINALIZATION()

    # We can finalize it
    assert market.tryFinalize()
    assert market.getReportingState() == localFixture.contracts['Constants'].FINALIZED()

@mark.parametrize('makeReport, finalizeByMigration', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_forking(localFixture, makeReport, finalizeByMigration, universe, market):
    # Proceed to the FORKING phase
    proceedToForking(localFixture, universe, market, makeReport, 1, 3, 3, [0,10**18], [10**18,0], 2, [10**18,0], [0,10**18], [10**18,0])

    # Finalize the market
    finalizeForkingMarket(localFixture, universe, market, finalizeByMigration, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,10**18], [10**18,0])

@mark.parametrize('makeReport, finalizeByMigration', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_forkMigration(localFixture, makeReport, finalizeByMigration, universe, cash, market):
    newMarket = localFixture.createReasonableBinaryMarket(universe, cash)
    completeSets = localFixture.contracts['CompleteSets']

    # Generate some fees to confirm the market migration also migrates fees
    cost = 10 * newMarket.getNumTicks()
    assert completeSets.publicBuyCompleteSets(newMarket.address, 10, sender=tester.k1, value=cost)
    assert completeSets.publicSellCompleteSets(newMarket.address, 10, sender=tester.k1)
    assert cash.balanceOf(newMarket.getReportingWindow()) > 0

    # We'll do a designated report in the new market based on the makeReport param used for the forking market
    proceedToDesignatedReporting(localFixture, universe, newMarket, [0,10**18])
    if (makeReport):
        localFixture.designatedReport(newMarket, [0,10**18], tester.k0)

    # We proceed the standard market to the FORKING state
    proceedToForking(localFixture, universe, market, makeReport, 1, 2, 3, [0,10**18], [10**18,0], 2, [10**18,0], [0,10**18], [10**18,0])

    # The market we created is now awaiting migration
    assert newMarket.getReportingState() == localFixture.contracts['Constants'].AWAITING_FORK_MIGRATION()

    # If we attempt to migrate now it will not work since the forking market is not finalized
    with raises(TransactionFailed, message="Migration cannot occur until the forking market is finalized"):
        newMarket.migrateThroughOneFork()

    # We'll finalize the forking market
    finalizeForkingMarket(localFixture, universe, market, finalizeByMigration, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,10**18], [10**18,0])

    # Now we can migrate the market to the winning universe. We also confirm that migration will move fees
    windowCashBalance = cash.balanceOf(newMarket.getReportingWindow())
    with TokenDelta(cash, -windowCashBalance, newMarket.getReportingWindow(), "Fork migration did not trigger window fee migratgion"):
        assert newMarket.migrateThroughOneFork()

    assert cash.balanceOf(newMarket.getReportingWindow()) == windowCashBalance

    # Now that we're on the correct universe we are send back to the DESIGNATED DISPUTE phase, which in the case of no designated reporter means the FIRST Reporting phase
    if (makeReport):
        assert newMarket.getReportingState() == localFixture.contracts['Constants'].DESIGNATED_DISPUTE()
    else:
        assert newMarket.getReportingState() == localFixture.contracts['Constants'].FIRST_REPORTING()

@mark.parametrize('pastDisputePhase', [
    True,
    False
])
def test_noReports(localFixture, pastDisputePhase, universe, market):
    # Proceed to the FIRST REPORTING phase
    proceedToFirstReporting(localFixture, universe, market, False, 1, [0,10**18], [10**18,0])

    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())

    if (pastDisputePhase):
        localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    else:
        localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    # If we receive no reports by the time Limited Reporting is finished we will be in the AWAITING NO REPORT MIGRATION phase
    assert market.getReportingState() == localFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()

    # We can try to report on the market, which will move it to the next reporting window where it will be back in FIRST REPORTING
    stakeToken = localFixture.getOrCreateStakeToken(market, [0,10**18])
    assert stakeToken.buy(1, sender=tester.k2)

    assert market.getReportingState() == localFixture.contracts['Constants'].FIRST_REPORTING()
    assert market.getReportingWindow() != reportingWindow.address

def test_invalid_first_report(localFixture, universe, cash, market):
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reputationToken = localFixture.applySignature('ReputationToken', universe.getReputationToken())
    expectedReportingWindowFeePayout = universe.getValidityBond()

    # Proceed to the FIRST REPORTING phase
    proceedToFirstReporting(localFixture, universe, market, False, 1, [0,10**18], [10**18,0])

    # We make an invalid report
    stakeTokenInvalid = localFixture.getOrCreateStakeToken(market, [long(0.5 * 10 ** 18), long(0.5 * 10 ** 18)], True)
    stakeTokenInvalid.buy(1, sender=tester.k2)
    assert stakeTokenInvalid.balanceOf(tester.a2) == 1 + universe.getDesignatedReportNoShowBond()
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == stakeTokenInvalid.getPayoutDistributionHash()
    assert not stakeTokenInvalid.isValid()

    # If we finalize the market it will be recorded as an invalid result
    initialReportingWindowCashBalance = cash.balanceOf(reportingWindow.address)
    localFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1
    assert market.tryFinalize()
    assert not market.isValid()
    assert reportingWindow.getNumInvalidMarkets() == 1

    # Since the market resolved with an invalid outcome the validity bond is paid out to the reporting window in Cash
    increaseInReportingWindowBalance = cash.balanceOf(reportingWindow.address) - initialReportingWindowCashBalance
    assert increaseInReportingWindowBalance == expectedReportingWindowFeePayout

def test_invalid_designated_report(localFixture, universe, cash, market):
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    expectedReportingWindowFeePayout = universe.getValidityBond()
    expectedMarketCreatorFeePayout = universe.getTargetReporterGasCosts()

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(localFixture, universe, market, [long(0.5 * 10 ** 18), long(0.5 * 10 ** 18)])

    # To progress into the DESIGNATED DISPUTE phase we do a designated report of invalid
    initialMarketCreatorETHBalance = localFixture.chain.head_state.get_balance(market.getOwner())
    assert localFixture.designatedReport(market, [long(0.5 * 10 ** 18), long(0.5 * 10 ** 18)], tester.k0, True)

    # We're now in the DESIGNATED DISPUTE PHASE
    assert market.getReportingState() == localFixture.contracts['Constants'].DESIGNATED_DISPUTE()

    # If time passes and no dispute bond is placed the market can be finalized
    localFixture.chain.head_state.timestamp = market.getEndTime() + localFixture.contracts['Constants'].DESIGNATED_REPORTING_DURATION_SECONDS() + localFixture.contracts['Constants'].DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS() + 1

    # The market is awaiting finalization now
    assert market.getReportingState() == localFixture.contracts['Constants'].AWAITING_FINALIZATION()

    # If we finalize the market it will be recorded as an invalid result
    initialReportingWindowCashBalance = cash.balanceOf(reportingWindow.address)
    assert market.tryFinalize()
    assert not market.isValid()
    assert reportingWindow.getNumInvalidMarkets() == 1

    # Since the market resolved with an invalid outcome the validity bond is paid out to the reporting window
    increaseInReportingWindowBalance = cash.balanceOf(reportingWindow.address) - initialReportingWindowCashBalance
    assert increaseInReportingWindowBalance == expectedReportingWindowFeePayout

    # Since the designated reporter showed up the market creator still gets back the reporter gas cost fee
    increaseInMarketCreatorBalance = localFixture.chain.head_state.get_balance(market.getOwner()) - initialMarketCreatorETHBalance
    assert increaseInMarketCreatorBalance == expectedMarketCreatorFeePayout

def test_cannot_fork_twice(localFixture, universe, cash, market):
    newMarket = localFixture.createReasonableBinaryMarket(universe, cash)

    proceedToLastReporting(localFixture, universe, market, True, 1, 3, [0,10**18], [10**18,0], 2, [10**18,0], [0,10**18])
    proceedToLastReporting(localFixture, universe, newMarket, True, 1, 3, [0,10**18], [10**18,0], 2, [10**18,0], [0,10**18])

    # Both markets are in last reporting
    assert market.getReportingState() == localFixture.contracts["Constants"].LAST_REPORTING()
    assert newMarket.getReportingState() == localFixture.contracts["Constants"].LAST_REPORTING()

    # We'll progress to the dispute phase for both
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())
    localFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

    # Both markets are in last dispute
    assert market.getReportingState() == localFixture.contracts["Constants"].LAST_DISPUTE()
    assert newMarket.getReportingState() == localFixture.contracts["Constants"].LAST_DISPUTE()

    # One can fork by having a dispute made
    assert market.disputeLastReporters()

    # The other market however cannot fork without error since the current fork is not finalized
    with raises(TransactionFailed):
        newMarket.disputeLastReporters()


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
