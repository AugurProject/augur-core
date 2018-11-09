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
    assert market.doInitialReport([0, market.getNumTicks(), 0], "")

    # The size of the initial report should only be the required reporting stake
    designatedReportCost = universe.getOrCacheDesignatedReportStake()
    initialReporter = contractsFixture.applySignature('InitialReporter', initialReporterAddress)
    assert initialReporter.getSize() == designatedReportCost
