from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import longToHexString, stringToBytes

tester.STARTGAS = long(6.7 * 10**6)

def test_market_creation(contractsFixture):
    branch = contractsFixture.branch
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    reportingWindow = contractsFixture.applySignature('ReportingWindow', market.getReportingWindow())
    shadyReportingToken = contractsFixture.upload('../src/reporting/ReportingToken.sol', 'shadyReportingToken')
    shadyReportingToken.initialize(market.address, [0,10**18])

    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(0))
    with raises(TransactionFailed, message="Markets can only use Cash as their denomination token"):
        contractsFixture.createReasonableBinaryMarket(branch, shareToken)

    assert market.getBranch() == branch.address
    assert market.getNumberOfOutcomes() == 2
    assert market.getMarketDenominator() == 10**18
    assert reportingWindow.getReputationToken() == branch.getReputationToken()
    assert market.getFinalPayoutDistributionHash() == stringToBytes("")
    assert market.getReportingState() == contractsFixture.constants.PRE_REPORTING()
    assert market.isContainerForReportingToken(shadyReportingToken.address) == 0
    assert market.getAutomatedReportDueTimestamp() == market.getEndTime() + timedelta(days=3).total_seconds()
