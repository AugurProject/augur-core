from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import longToHexString

tester.STARTGAS = long(6.7 * 10**6)

def test_market_creation(contractsFixture):
    branch = contractsFixture.branch
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    reportingWindow = contractsFixture.applySignature('reportingWindow', market.getReportingWindow())
    shadyReportingToken = contractsFixture.upload('../src/reporting/ReportingToken.sol', 'shadyReportingToken')
    shadyReportingToken.initialize(market.address, [0,2])

    shadyBranch = contractsFixture.createBranch(0, 0)
    regularMarket = contractsFixture.createReasonableBinaryMarket(branch, cash)
    shadyDenominationToken = contractsFixture.applySignature('shareToken', regularMarket.getShareToken(0))
    with raises(TransactionFailed, message="Shady share token should be failing since it is in a separate branch"):
        contractsFixture.createReasonableBinaryMarket(shadyBranch, shadyDenominationToken)

    assert market.getBranch() == branch.address
    assert market.getNumberOfOutcomes() == 2
    assert market.getPayoutDenominator() == 2
    assert market.getReputationToken() == branch.getReputationToken()
    assert market.getFinalPayoutDistributionHash() == 0
    assert market.isDoneWithAutomatedReporters() == 0
    assert market.isDoneWithAllReporters() == 0
    assert market.isDoneWithLimitedReporters() == 0
    assert market.isFinalized() == 0
    assert market.isInAutomatedReportingPhase() == 0
    assert market.isInAutomatedDisputePhase() == 0
    assert market.isInLimitedReportingPhase() == 0
    assert market.isInLimitedDisputePhase() == 0
    assert market.isInAllReportingPhase() == 0
    assert market.isInAllDisputePhase() == 0
    assert market.isContainerForReportingToken(shadyReportingToken.address) == 0
    assert market.canBeReportedOn() == 0
    assert market.needsMigration() == 0
    assert market.getAutomatedReportDueTimestamp() == market.getEndTime() + timedelta(days=3).total_seconds()
