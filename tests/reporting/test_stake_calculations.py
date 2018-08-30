from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import captureFilteredLogs, bytesToHexString, AssertLog, TokenDelta, longToHexString
from pytest import raises
from reporting_utils import proceedToNextRound

def test_initial_report_bond_size(contractsFixture, market, universe):
    reputationToken = contractsFixture.applySignature('ReputationToken', universe.getReputationToken())

    # Skip to Designated Reporting
    contractsFixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)

    # Before the initial report we'll transfer REP manually to the InitialReport contract
    initialReporterAddress = market.getInitialReporter()
    assert reputationToken.transfer(initialReporterAddress, 1)

    # Now we do the initial report
    assert market.doInitialReport([market.getNumTicks(), 0], False, "")

    # The size of the initial report should only be the required reporting stake
    designatedReportCost = universe.getOrCacheDesignatedReportStake()
    initialReporter = contractsFixture.applySignature('InitialReporter', initialReporterAddress)
    assert initialReporter.getSize() == designatedReportCost

def test_fork_bonus(contractsFixture, market, universe):
    # proceed to forking
    while (market.getForkingMarket() == longToHexString(0)):
        proceedToNextRound(contractsFixture, market)

    reputationToken = contractsFixture.applySignature('ReputationToken', universe.getReputationToken())
    payoutHash = market.derivePayoutDistributionHash([market.getNumTicks(), 0], False)
    childUniverse = contractsFixture.applySignature("Universe", universe.createChildUniverse([market.getNumTicks(), 0], False))
    childReputationToken = contractsFixture.applySignature("ReputationToken", childUniverse.getReputationToken())

    # We'll transfer some additional REP to the initial reporter contract to try and get a larger bonus
    initialReporterAddress = market.getInitialReporter()
    extraAmount = 10000
    assert reputationToken.transfer(initialReporterAddress, extraAmount)

    # When we redeem the bonus we will only be given a bonus relative to the legitimate stake in the bond
    designatedReportCost = universe.getOrCacheDesignatedReportStake()
    initialReporter = contractsFixture.applySignature('InitialReporter', initialReporterAddress)

    # Skip to after the fork end to not deal with 5% bonus math
    contractsFixture.contracts["Time"].setTimestamp(universe.getForkEndTime() + 1)

    expectedPayout = designatedReportCost + (designatedReportCost / 2) + extraAmount
    with TokenDelta(childReputationToken, expectedPayout, tester.a0, "Redeeming forked bond didn't result in the expected amount"):
        assert initialReporter.forkAndRedeem()
