from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import stringToBytes, AssertLog, bytesToHexString

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
        market = contractsFixture.createReasonableYesNoMarket(universe, cash, extraInfo="so extra")

    assert market.getUniverse() == universe.address
    assert market.getNumberOfOutcomes() == 2
    assert numTicks == 10000
    assert market.getReputationToken() == universe.getReputationToken()
    assert market.getWinningPayoutDistributionHash() == stringToBytes("")
    assert market.getInitialized()

    with raises(TransactionFailed, message="Cannot create a market with an end date in the past"):
        contractsFixture.createYesNoMarket(universe, 0, 1, cash, tester.a0)

def test_description_requirement(contractsFixture, universe, cash):
    endTime = contractsFixture.contracts["Time"].getTimestamp() + 1

    with raises(TransactionFailed):
        contractsFixture.createYesNoMarket(universe, endTime, 1, cash, tester.a0, description="")

    with raises(TransactionFailed):
        contractsFixture.createCategoricalMarket(universe, 2, endTime, 1, cash, tester.a0, description="")

    with raises(TransactionFailed):
        contractsFixture.createScalarMarket(universe, endTime, 1, cash, 0, 1, 10000, tester.a0, description="")

def test_categorical_market_creation(contractsFixture, universe, cash):
    endTime = contractsFixture.contracts["Time"].getTimestamp() + 1

    with raises(TransactionFailed):
        contractsFixture.createCategoricalMarket(universe, 1, endTime, 1, cash, tester.a0)

    assert contractsFixture.createCategoricalMarket(universe, 3, endTime, 1, cash, tester.a0)
    assert contractsFixture.createCategoricalMarket(universe, 4, endTime, 1, cash, tester.a0)
    assert contractsFixture.createCategoricalMarket(universe, 5, endTime, 1, cash, tester.a0)
    assert contractsFixture.createCategoricalMarket(universe, 6, endTime, 1, cash, tester.a0)
    assert contractsFixture.createCategoricalMarket(universe, 7, endTime, 1, cash, tester.a0)
    assert contractsFixture.createCategoricalMarket(universe, 8, endTime, 1, cash, tester.a0)

def test_num_ticks_validation(contractsFixture, universe, cash):
    # Require numTicks != 0
    with raises(TransactionFailed):
       market = contractsFixture.createReasonableScalarMarket(universe, 30, -10, 0, cash)

def test_transfering_ownership(contractsFixture, universe, market):

    transferLog = {
        "universe": universe.address,
        "market": market.address,
        "from": bytesToHexString(tester.a0),
        "to": bytesToHexString(tester.a1),
    }
    with AssertLog(contractsFixture, "MarketTransferred", transferLog):
        assert market.transferOwnership(tester.a1)

    mailbox = contractsFixture.applySignature('Mailbox', market.getMarketCreatorMailbox())

    transferLog = {
        "universe": universe.address,
        "market": market.address,
        "from": bytesToHexString(tester.a0),
        "to": bytesToHexString(tester.a1),
    }
    with AssertLog(contractsFixture, "MarketMailboxTransferred", transferLog):
        assert mailbox.transferOwnership(tester.a1)