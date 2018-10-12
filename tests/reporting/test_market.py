from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, mark
from utils import stringToBytes, AssertLog, bytesToHexString, EtherDelta, TokenDelta
from reporting_utils import proceedToDesignatedReporting

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

    endTime = 0
    with raises(TransactionFailed, message="Cannot create a market with an end date in the past"):
        contractsFixture.createYesNoMarket(universe, endTime, 1, cash, tester.a0)

    endTime = contractsFixture.contracts["Time"].getTimestamp() + contractsFixture.contracts["Constants"].MAXIMUM_MARKET_DURATION() + 1
    with raises(TransactionFailed, message="Cannot create a market with an end date past the maximum duration"):
        contractsFixture.createYesNoMarket(universe, endTime, 1, cash, tester.a0)

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

@mark.parametrize('invalid', [
    True,
    False
])
def test_variable_validity_bond(invalid, contractsFixture, universe, cash):
    # We can't make a market with less than the minimum required validity bond
    minimumValidityBond = universe.getOrCacheMarketCreationCost()

    with raises(TransactionFailed):
       contractsFixture.createReasonableYesNoMarket(universe, cash, validityBond=minimumValidityBond-1)

    # But we can make one with a greater bond
    higherValidityBond = minimumValidityBond+1
    market = contractsFixture.createReasonableYesNoMarket(universe, cash, validityBond=higherValidityBond)
    assert market.getValidityBondAttoEth() == higherValidityBond

    # If we resolve the market the bond in it's entirety will go to the fee pool or to the market creator if the resolution was not invalid
    proceedToDesignatedReporting(contractsFixture, market)

    if invalid:
        market.doInitialReport([market.getNumTicks() / 2, market.getNumTicks() / 2], True, "")
    else:
        market.doInitialReport([0, market.getNumTicks()], False, "")

    # Move time forward so we can finalize and see the bond move
    feeWindow = contractsFixture.applySignature('FeeWindow', market.getFeeWindow())
    assert contractsFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    if invalid:
        with TokenDelta(cash, higherValidityBond, universe.getAuction(), "Validity bond did not go to the auction"):
            market.finalize()
    else:
        with EtherDelta(higherValidityBond, market.getMarketCreatorMailbox(), contractsFixture.chain, "Validity bond did not go to the market creator"):
            market.finalize()
