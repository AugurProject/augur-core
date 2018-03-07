from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import stringToBytes, captureFilteredLogs, bytesToHexString

tester.STARTGAS = long(6.7 * 10**6)

def test_market_creation(contractsFixture, universe, cash, market):
    numTicks = market.getNumTicks()

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
    assert numTicks == 10000
    assert market.getReputationToken() == universe.getReputationToken()
    assert market.getWinningPayoutDistributionHash() == stringToBytes("")

def test_num_ticks_validation(contractsFixture, universe, cash):
    # Require numTicks != 0
    with raises(TransactionFailed):
       market = contractsFixture.createReasonableScalarMarket(universe, 30, -10, 0, cash)
