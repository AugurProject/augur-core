from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import stringToBytes, captureFilteredLogs, bytesToHexString

tester.STARTGAS = long(6.7 * 10**6)

def test_markett_creation(contractsFixture, universe, cash, market):
    reportingWindow = contractsFixture.applySignature('ReportingWindow', market.getReportingWindow())

    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(0))
    with raises(TransactionFailed, message="markets can only use Cash as their denomination token"):
       contractsFixture.createReasonableBinaryMarket(universe, shareToken)

    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, universe, logs)
    market = contractsFixture.createReasonableBinaryMarket(universe, cash, extraInfo="so extra")

    assert len(logs) == 1
    assert logs[0]['_event_type'] == 'MarketCreated'
    assert logs[0]['extraInfo'] == 'so extra'
    assert logs[0]['marketCreationFee'] == universe.getMarketCreationCost()
    assert logs[0]['market'] == market.address
    assert logs[0]['marketCreator'] == bytesToHexString(tester.a0)

    shadyStakeToken = contractsFixture.upload('../source/contracts/reporting/StakeToken.sol', 'shadyStakeToken')
    shadyStakeToken.initialize(market.address, [0,10**18])

    assert market.getUniverse() == universe.address
    assert market.getNumberOfOutcomes() == 2
    assert market.getNumTicks() == 10**18
    assert reportingWindow.getReputationToken() == universe.getReputationToken()
    assert market.getFinalPayoutDistributionHash() == stringToBytes("")
    assert market.getReportingState() == contractsFixture.contracts['Constants'].PRE_REPORTING()
    assert market.isContainerForStakeToken(shadyStakeToken.address) == 0
    assert market.getDesignatedReportDueTimestamp() == market.getEndTime() + timedelta(days=3).total_seconds()
