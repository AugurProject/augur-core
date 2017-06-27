from ContractsFixture import ContractsFixture
from datetime import timedelta
from ethereum import tester
from ethereum.tester import TransactionFailed
from pytest import raises

tester.gas_limit = long(4.2 * 10**6)

def test_market_creation():
    fixture = ContractsFixture()

    branch = fixture.createBranch(3, 5)
    cash = fixture.getSeededCash()
    market = fixture.createReasonableBinaryMarket(branch, cash)
    reportingWindow = fixture.applySignature('reportingWindow', market.getReportingWindow())
    shadyReportingToken = fixture.upload('../src/reporting/reportingToken.se', 'shadyReportingToken')
    shadyReportingToken.initialize(market.address, [0,2])

    shadyBranch = fixture.createBranch(0, 0)
    regularMarket = fixture.createReasonableBinaryMarket(branch, cash)
    shadyDenominationToken = fixture.applySignature('shareToken', regularMarket.getShareToken(0))
    with raises(TransactionFailed, message="Shady share token should be failing since it is in a separate branch"):
        fixture.createReasonableBinaryMarket(shadyBranch, shadyDenominationToken)

    assert(market.getBranch() == branch.address)
    assert(market.getNumberOfOutcomes() == 2)
    assert(market.getPayoutDenominator() == 2)
    assert(market.getReputationToken() == branch.getReputationToken())
    assert(market.getFinalPayoutDistributionHash() == 0)
    assert(market.isDoneWithAutomatedReporters() == 0)
    assert(market.isDoneWithAllReporters() == 0)
    assert(market.isDoneWithLimitedReporters() == 0)
    assert(market.isFinalized() == 0)
    assert(market.isInAutomatedReportingPhase() == 0)
    assert(market.isInAutomatedDisputePhase() == 0)
    assert(market.isInLimitedReportingPhase() == 0)
    assert(market.isInLimitedDisutePhase() == 0)
    assert(market.isInAllReportingPhase() == 0)
    assert(market.isInAllDisputePhase() == 0)
    assert(market.isContainerForReportingToken(shadyReportingToken.address) == 0)
    assert(market.canBeReportedOn() == 0)
    assert(market.needsMigration() == 0)
    assert(market.getAutomatedReportDueTimestamp() == market.getEndTime() + timedelta(days=3).total_seconds())
