from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises
from utils import longToHexString

NULL_ADDRESS = longToHexString(0)

def test_reporting_window_functions(kitchenSinkFixture):
    universe = kitchenSinkFixture.createUniverse()

    # We have many getters and getOrCreate method on the universe for retreiving and creating fee windows. We'll confirm first that all the getters simply return 0 when the requested window does not yet exist
    assert universe.getFeeWindowByTimestamp(0) == NULL_ADDRESS
    assert universe.getPreviousFeeWindow() == NULL_ADDRESS
    assert universe.getCurrentFeeWindow() == NULL_ADDRESS
    assert universe.getNextFeeWindow() == NULL_ADDRESS

    # Now lets use the getOrCreate variants to actually generate these windows
    assert universe.getOrCreateFeeWindowByTimestamp(0) != NULL_ADDRESS
    assert universe.getOrCreatePreviousFeeWindow() != NULL_ADDRESS
    assert universe.getOrCreateCurrentFeeWindow() != NULL_ADDRESS
    assert universe.getOrCreateNextFeeWindow() != NULL_ADDRESS

    # And now confirm the getters return the correct windows
    assert universe.getFeeWindowByTimestamp(0) != NULL_ADDRESS
    assert universe.getPreviousFeeWindow() != NULL_ADDRESS
    assert universe.getCurrentFeeWindow() != NULL_ADDRESS
    assert universe.getNextFeeWindow() != NULL_ADDRESS

def test_market_creation_fee(kitchenSinkFixture):
    universe = kitchenSinkFixture.createUniverse()

    # Calling the normal function which creates these windows if they do not exist should return correctly
    marketCreationCost = universe.getOrCacheMarketCreationCost()
    assert marketCreationCost > 0

def test_validity_bond(kitchenSinkFixture):
    universe = kitchenSinkFixture.createUniverse()

    # Calling the normal function which creates these windows if they do not exist should return correctly
    bond = universe.getOrCacheValidityBond()
    assert bond > 0

def test_designated_report_stake(kitchenSinkFixture):
    universe = kitchenSinkFixture.createUniverse()

    # Calling the normal function which creates these windows if they do not exist should return correctly
    stake = universe.getOrCacheDesignatedReportStake()
    assert stake > 0

    assert universe.getInitialReportStakeSize() == stake

def test_designated_report_no_show_bond(kitchenSinkFixture):
    universe = kitchenSinkFixture.createUniverse()

    # Calling the normal function which creates these windows if they do not exist should return correctly
    bond = universe.getOrCacheDesignatedReportNoShowBond()
    assert bond > 0

def test_reporting_fee_divisor(kitchenSinkFixture):
    universe = kitchenSinkFixture.createUniverse()

    # Calling the normal function which creates these windows if they do not exist should return correctly
    feeDivisor = universe.getOrCacheReportingFeeDivisor()
    assert feeDivisor > 0
