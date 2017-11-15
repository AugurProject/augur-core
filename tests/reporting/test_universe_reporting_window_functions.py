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

    # When getting the market creation cost we may use a view function that will return 0 if the current or previous reporting window do not exist
    assert universe.getMarketCreationCost() == 0

    # Calling the normal function which creates these windows if they do not exist should return correctly
    marketCreationCost = universe.getOrCacheMarketCreationCost()
    assert marketCreationCost > 0

    # Now we should be able to call the view version and get the same value
    assert marketCreationCost == universe.getMarketCreationCost()

def test_validity_bond_getter(kitchenSinkFixture, universe):
    universe = kitchenSinkFixture.createUniverse(universe.address, "")

    # When getting the validity bond we may use a view function that will return 0 if the current or previous reporting window do not exist
    assert universe.getValidityBond() == 0

    # Calling the normal function which creates these windows if they do not exist should return correctly
    bond = universe.getOrCacheValidityBond()
    assert bond > 0

    # Now we should be able to call the view version and get the same value
    assert bond == universe.getValidityBond()

def test_designated_report_stake_getter(kitchenSinkFixture, universe):
    universe = kitchenSinkFixture.createUniverse(universe.address, "")

    # When getting the designated report stake we may use a view function that will return 0 if the current or previous reporting window do not exist
    assert universe.getDesignatedReportStake() == 0

    # Calling the normal function which creates these windows if they do not exist should return correctly
    stake = universe.getOrCacheDesignatedReportStake()
    assert stake > 0

    # Now we should be able to call the view version and get the same value
    assert stake == universe.getDesignatedReportStake()

def test_designated_report_no_show_bond_getter(kitchenSinkFixture, universe):
    universe = kitchenSinkFixture.createUniverse(universe.address, "")

    # When getting the no show bond we may use a view function that will return 0 if the current or previous reporting window do not exist
    assert universe.getDesignatedReportNoShowBond() == 0

    # Calling the normal function which creates these windows if they do not exist should return correctly
    bond = universe.getOrCacheDesignatedReportNoShowBond()
    assert bond > 0

    # Now we should be able to call the view version and get the same value
    assert bond == universe.getDesignatedReportNoShowBond()

def test_reporting_fee_divisor_getter(kitchenSinkFixture, universe):
    universe = kitchenSinkFixture.createUniverse(universe.address, "")

    # When getting the reporting fee divisor we may use a view function that will return 0 if the current or previous reporting window do not exist
    assert universe.getReportingFeeDivisor() == 0

    # Calling the normal function which creates these windows if they do not exist should return correctly
    feeDivisor = universe.getOrCacheReportingFeeDivisor()
    assert feeDivisor > 0

    # Now we should be able to call the view version and get the same value
    assert feeDivisor == universe.getReportingFeeDivisor()
