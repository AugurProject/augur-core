from ethereum.tools import tester
from utils import longToHexString, stringToBytes
from pytest import fixture

def test_universe_creation(universeFixture):
    universe = universeFixture.createUniverse(3, "5")
    reputationToken = universeFixture.applySignature('ReputationToken', universe.getReputationToken())

    assert universe.getParentUniverse() == longToHexString(3)
    assert universe.getParentPayoutDistributionHash() == stringToBytes("5")
    assert universe.getForkingMarket() == longToHexString(0)
    assert universe.getForkEndTime() == 0
    assert reputationToken.getUniverse() == universe.address
    assert reputationToken.getTopMigrationDestination() == longToHexString(0)
    assert universe.getTypeName() == stringToBytes('Universe')
    assert universe.getForkEndTime() == 0
    assert universe.getChildUniverse("5") == longToHexString(0)

def test_get_reporting_window(universeFixture):
    universe = universeFixture.createUniverse(1, "10")
    timestamp = universeFixture.chain.head_state.timestamp
    duration =  universeFixture.constants.REPORTING_DURATION_SECONDS()
    dispute_duration = universeFixture.constants.REPORTING_DISPUTE_DURATION_SECONDS()
    total_dispute_duration = duration + dispute_duration
    reportingPeriodDurationForTimestamp = timestamp / total_dispute_duration

    assert universe.getReportingWindowId(timestamp) == reportingPeriodDurationForTimestamp
    assert universe.getReportingPeriodDurationInSeconds() == total_dispute_duration

    # reporting window not stored internally, only read-only method
    assert universe.getReportingWindow(reportingPeriodDurationForTimestamp) == longToHexString(0)
    report_window = universe.getReportingWindowByTimestamp(timestamp)

    # Now reporting window is in internal collection
    assert universe.getReportingWindow(reportingPeriodDurationForTimestamp) == report_window

    # Make up end timestamp for testing internal calculations
    end_timestamp = universeFixture.chain.head_state.timestamp + 1
    end_report_window_des = universe.getReportingWindowByMarketEndTime(end_timestamp, True)

    # Test getting same calculated end reporting window 
    end_timestamp_des_test = end_timestamp + universeFixture.constants.DESIGNATED_REPORTING_DURATION_SECONDS() + universeFixture.constants.DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS() + 1 + total_dispute_duration
    assert universe.getReportingWindowByTimestamp(end_timestamp_des_test) == end_report_window_des

    # Test getting same calculation for non designated reporter
    end_report_window_without_des = universe.getReportingWindowByMarketEndTime(end_timestamp, False)

    # Test getting same calculated end reporting window without des
    end_timestamp_without_des_test = end_timestamp + total_dispute_duration
    assert universe.getReportingWindowByTimestamp(end_timestamp_without_des_test) == end_report_window_without_des

    assert universe.getPreviousReportingWindow() == universe.getReportingWindowByTimestamp(universeFixture.chain.head_state.timestamp - total_dispute_duration)
    assert universe.getCurrentReportingWindow() == universe.getReportingWindowByTimestamp(universeFixture.chain.head_state.timestamp)
    assert universe.getNextReportingWindow() == universe.getReportingWindowByTimestamp(universeFixture.chain.head_state.timestamp + total_dispute_duration)
    
def test_create_child_universe(universeFixture):
    universe = universeFixture.createUniverse(2, "15")
    assert universe.getChildUniverse("20") == longToHexString(0)
    assert universe.getOrCreateChildUniverse("20") == universe.getChildUniverse("20")
    assert universe.getChildUniverse("20") != longToHexString(0)
    child = universe.getChildUniverse("20")
    assert universe.isParentOf(child)

    other_universe = universeFixture.createUniverse(3, "1")
    other_child = other_universe.getOrCreateChildUniverse("21")
    assert universe.isParentOf(other_child) == False

def test_universe_contains_reporting_win(universeFixture):
    universe = universeFixture.createUniverse(0, "5")
    other_universe = universeFixture.createUniverse(1, "15")
    other_curr_reporting_win = other_universe.getCurrentReportingWindow()
    reportingWindow = universeFixture.applySignature('ReportingWindow', universe.getCurrentReportingWindow())

    curr_reporting_window = universe.getCurrentReportingWindow()
    assert universe.isContainerForReportingWindow(curr_reporting_window)
    # Reporting window is in different universe
    assert universe.isContainerForReportingWindow(other_curr_reporting_win) == False

    # Pass in non ReportingWindow object address
    nonReportingWindow = universeFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'nonReportingWindow')
    assert universe.isContainerForReportingWindow(nonReportingWindow.address) == False

    # create reporting windo with startTime of 0
    reporting_window_factory = universeFixture.upload('../source/contracts/factories/ReportingWindowFactory.sol', 'reporting_window_factory')
    zero_window = reporting_window_factory.createReportingWindow(universeFixture.controller.address, universe.address, 0)
    assert universe.isContainerForReportingWindow(zero_window) == False
    
def test_universe_contains_dispute_bond_token(universeFixture):
    universe = universeFixture.createUniverse(0, "55")
    # Pass in non Dispute Bond Token object address
    nonDisputeBondToken = universeFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'nonReportingWindow')
    assert universe.isContainerForDisputeBondToken(nonDisputeBondToken.address) == False
    
    # Create bond for market not in this universe
    market = universeFixture.binaryMarket
    dispute_bond_token_factory = universeFixture.upload('../source/contracts/factories/DisputeBondTokenFactory.sol', 'dispute_bond_token_factory')
    bond = dispute_bond_token_factory.createDisputeBondToken(universeFixture.controller.address, market.address, tester.a0, 10, "15")
    assert universe.isContainerForDisputeBondToken(bond) == False

    # Pass in bond with market address of 0
    zero_market_bond = dispute_bond_token_factory.createDisputeBondToken(universeFixture.controller.address, 0, tester.a0, 10, "15")
    assert universe.isContainerForDisputeBondToken(zero_market_bond) == False
 
    # TODO Get correct dispute bond token from active market in correct state

    # Since we have non Market/ReportingToken/ShareToken lets test the getTypeName() tests
    assert universe.isContainerForMarket(nonDisputeBondToken.address) == False
    assert universe.isContainerForReportingToken(nonDisputeBondToken.address) == False
    assert universe.isContainerForShareToken(nonDisputeBondToken.address) == False

def test_universe_contains_market(universeFixture):
    universe = universeFixture.createUniverse(1, "25")
    # market in different universe
    market = universeFixture.binaryMarket
    assert universe.isContainerForMarket(market.address) == False
        
    uni_market = universeFixture.createReasonableBinaryMarket(universe, universeFixture.cash)
    assert universe.isContainerForMarket(uni_market.address)

def test_universe_reporting_token(universeFixture):
    universe = universeFixture.createUniverse(1, "25")
    reporting_token_factory = universeFixture.upload('../source/contracts/factories/ReportingTokenFactory.sol', 'reporting_token_factory')

    # Reporting token not associated with this universe market
    different_reporting_token = reporting_token_factory.createReportingToken(universeFixture.controller.address, universeFixture.binaryMarket.address, [0, 10**18])
    assert universe.isContainerForReportingToken(different_reporting_token) == False

    # TODO add test for Reporting token associated market address of 0

    # Create market and test it's reporting token
    uni_market = universeFixture.createReasonableBinaryMarket(universe, universeFixture.cash)
    good_reporting_token = universeFixture.getReportingToken(uni_market, [0,10**18])
    assert universe.isContainerForMarket(uni_market.address)
    assert universe.isContainerForReportingToken(good_reporting_token.address)

def test_universe_contains_share_token(universeFixture):
    universe = universeFixture.createUniverse(1, "25")
    share_token_factory = universeFixture.upload('../source/contracts/factories/ShareTokenFactory.sol', 'share_token_factory')

    # Share token not associated with this universe market
    different_share_token = share_token_factory.createShareToken(universeFixture.controller.address, universeFixture.binaryMarket.address, 1)
    assert universe.isContainerForShareToken(different_share_token) == False

    # TODO add test for Share token associated market address of 0

    # Create market and test it's reporting token
    uni_market = universeFixture.createReasonableBinaryMarket(universe, universeFixture.cash)
    good_share_token = universeFixture.getShareToken(uni_market, 1)
    assert universe.isContainerForShareToken(good_share_token.address)
    
@fixture
def sessionSnapshot(contractsFixture):
    contractsFixture.resetSnapshot()
    return contractsFixture.createSnapshot()

@fixture
def universeFixture(contractsFixture, sessionSnapshot):
    contractsFixture.resetToSnapshot(sessionSnapshot)
    return contractsFixture
