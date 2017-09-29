from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import stringToBytes

tester.STARTGAS = long(6.7 * 10**6)

def test_market_creation(contractsFixture):
    universe = contractsFixture.universe
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    reportingWindow = contractsFixture.applySignature('ReportingWindow', market.getReportingWindow())
    shadyReportingToken = contractsFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'shadyReportingToken')
    shadyReportingToken.initialize(market.address, [0,10**18])

    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(0))
    with raises(TransactionFailed, message="Markets can only use Cash as their denomination token"):
        contractsFixture.createReasonableBinaryMarket(universe, shareToken)

    assert market.getUniverse() == universe.address
    assert market.getNumberOfOutcomes() == 2
    assert market.getNumTicks() == 10**18
    assert reportingWindow.getReputationToken() == universe.getReputationToken()
    assert market.getFinalPayoutDistributionHash() == stringToBytes("")
    assert market.getReportingState() == contractsFixture.constants.PRE_REPORTING()
    assert market.isContainerForReportingToken(shadyReportingToken.address) == 0
    assert market.getDesignatedReportDueTimestamp() == market.getEndTime() + timedelta(days=3).total_seconds()
