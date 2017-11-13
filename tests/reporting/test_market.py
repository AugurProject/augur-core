from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import stringToBytes, captureFilteredLogs, bytesToHexString

tester.STARTGAS = long(6.7 * 10**6)

def test_market_creation(contractsFixture, universe, cash, market):
    reportingWindow = contractsFixture.applySignature('ReportingWindow', market.getReportingWindow())
    shadyStakeToken = contractsFixture.upload('../source/contracts/reporting/StakeToken.sol', 'shadyStakeToken')
    shadyStakeToken.setController(contractsFixture.contracts["Controller"].address)
    shadyStakeToken.initialize(market.address, [0,10**18])

    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    market = contractsFixture.createReasonableBinaryMarket(universe, cash, extraInfo="so extra")

    assert len(logs) == 3
    assert logs[2]['_event_type'] == 'MarketCreated'
    assert logs[2]['extraInfo'] == 'so extra'
    assert logs[2]['marketCreationFee'] == universe.getOrCacheMarketCreationCost()
    assert logs[2]['market'] == market.address
    assert logs[2]['marketCreator'] == bytesToHexString(tester.a0)

    assert market.getUniverse() == universe.address
    assert market.getNumberOfOutcomes() == 2
    assert market.getNumTicks() == 10**18
    assert reportingWindow.getReputationToken() == universe.getReputationToken()
    assert market.getFinalPayoutDistributionHash() == stringToBytes("")
    assert market.getReportingState() == contractsFixture.contracts['Constants'].PRE_REPORTING()
    assert market.isContainerForStakeToken(shadyStakeToken.address) == 0
    assert market.getDesignatedReportDueTimestamp() == market.getEndTime() + timedelta(days=3).total_seconds()

def test_extraction(contractsFixture, market, universe, cash, scalarMarket):
    controller = contractsFixture.contracts["Controller"]
    reputationToken = contractsFixture.applySignature("ReputationToken", universe.getReputationToken())

    # ETH, REP, and Cash extraction are not allowed
    with raises(TransactionFailed, message="markets should not be allowed to extract ETH"):
       controller.extractEther(market.address, tester.a0)

    with raises(TransactionFailed, message="markets should not be allowed to extract REP"):
       controller.extractTokens(market.address, tester.a0, reputationToken.address)

    assert cash.depositEtherFor(market.address, value=10)
    assert cash.balanceOf(market.address) == 10

    with raises(TransactionFailed, message="markets should not be allowed to extract Cash"):
       controller.extractTokens(market.address, tester.a0, cash.address)


    # We also do not allow extraction of the Share tokens a market may hold in escrow
    shareToken = contractsFixture.getShareToken(market, 0)
    assert shareToken.createShares(tester.a0, 10)

    assert shareToken.transfer(market.address, 10)
    assert shareToken.balanceOf(tester.a0) == 0
    assert shareToken.balanceOf(market.address) == 10

    with raises(TransactionFailed, message="markets should not be allowed to extract their own Share tokens"):
        controller.extractTokens(market.address, tester.a0, shareToken.address)

    # If we send some other markets share token however we should be allowed to extract it
    shareToken = contractsFixture.getShareToken(scalarMarket, 0)
    assert shareToken.createShares(tester.a0, 11)

    assert shareToken.transfer(market.address, 11)
    assert shareToken.balanceOf(tester.a0) == 0
    assert shareToken.balanceOf(market.address) == 11

    assert controller.extractTokens(market.address, tester.a0, shareToken.address)

    # now we should have the original balance
    assert shareToken.balanceOf(tester.a0) == 11
