from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import stringToBytes, AssertLog, bytesToHexString, AssertLog

tester.STARTGAS = long(6.7 * 10**6)

def test_market_creation(contractsFixture, universe, cash, market):
    numTicks = market.getNumTicks()

    market = None

    marketCreatedLog = {
        "extraInfo": 'so extra',
        "marketCreationFee": universe.getOrCacheMarketCreationCost(),
        "marketCreator": bytesToHexString(tester.a0),
    }
    with AssertLog(contractsFixture, "MarketCreated", marketCreatedLog):
        market = contractsFixture.createReasonableBinaryMarket(universe, cash, extraInfo="so extra")

    assert market.getUniverse() == universe.address
    assert market.getNumberOfOutcomes() == 2
    assert numTicks == 10000
    assert market.getReputationToken() == universe.getReputationToken()
    assert market.getWinningPayoutDistributionHash() == stringToBytes("")

def test_num_ticks_validation(contractsFixture, universe, cash):
    # Require numTicks != 0
    with raises(TransactionFailed):
       market = contractsFixture.createReasonableScalarMarket(universe, 30, -10, 0, cash)
