from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises
from utils import longToHexString

NULL_ADDRESS = longToHexString(0)

def test_reporting_window_functions(kitchenSinkFixture, universe):
    universe = kitchenSinkFixture.createUniverse(universe.address, "")

    # We have many getters and getOrCreate method on the universe for retreiving and creating reporting windows. We'll confirm first that all the getters simply return 0 when the requested window does not yet exist
    assert universe.getReportingWindowByTimestamp(0) == NULL_ADDRESS
    assert universe.getReportingWindowByMarketEndTime(31) == NULL_ADDRESS
    assert universe.getPreviousReportingWindow() == NULL_ADDRESS
    assert universe.getCurrentReportingWindow() == NULL_ADDRESS
    assert universe.getNextReportingWindow() == NULL_ADDRESS

    # Now lets use the getOrCreate variants to actually generate these windows
    assert universe.getOrCreateReportingWindowByTimestamp(0) != NULL_ADDRESS
    assert universe.getOrCreateReportingWindowByMarketEndTime(31) != NULL_ADDRESS
    assert universe.getOrCreatePreviousReportingWindow() != NULL_ADDRESS
    assert universe.getOrCreateCurrentReportingWindow() != NULL_ADDRESS
    assert universe.getOrCreateNextReportingWindow() != NULL_ADDRESS

    # And now confirm the getters return the correct windows
    assert universe.getReportingWindowByTimestamp(0) != NULL_ADDRESS
    assert universe.getReportingWindowByMarketEndTime(31) != NULL_ADDRESS
    assert universe.getPreviousReportingWindow() != NULL_ADDRESS
    assert universe.getCurrentReportingWindow() != NULL_ADDRESS
    assert universe.getNextReportingWindow() != NULL_ADDRESS

def test_market_creation_fee_getter(kitchenSinkFixture, universe):
    universe = kitchenSinkFixture.createUniverse(universe.address, "")

    # When getting the market creation cost we may use a view function that will throw if the current and previous reporting window do not exist
    with raises(TransactionFailed):
        universe.getMarketCreationCost()

    # Calling the normal function which creates these windows if they do not exist should return correctly
    marketCreationCost = universe.getOrCacheMarketCreationCost()
    assert marketCreationCost > 0

    # Now we should be able to call the view version and get the same value
    assert marketCreationCost == universe.getMarketCreationCost()
