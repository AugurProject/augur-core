from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longToHexString, stringToBytes
from pytest import fixture, raises

def test_universe_creation(localFixture):
    universe = localFixture.createUniverse(3, "5")
    reputationToken = localFixture.applySignature('ReputationToken', universe.getReputationToken())
    assert universe.getParentUniverse() == longToHexString(3)
    assert universe.getParentPayoutDistributionHash() == stringToBytes("5")
    assert universe.getForkingMarket() == longToHexString(0)
    assert universe.getForkEndTime() == 0
    assert reputationToken.getUniverse() == universe.address
    assert reputationToken.getTopMigrationDestination() == longToHexString(0)
    assert universe.getTypeName() == stringToBytes('Universe')
    assert universe.getForkEndTime() == 0
    assert universe.getChildUniverse("5") == longToHexString(0)

def test_get_reporting_window(localFixture):
    universe = localFixture.createUniverse(1, "10")
    timestamp = localFixture.chain.head_state.timestamp
    duration =  localFixture.contracts['Constants'].REPORTING_DURATION_SECONDS()
    dispute_duration = localFixture.contracts['Constants'].REPORTING_DISPUTE_DURATION_SECONDS()
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
    end_timestamp = localFixture.chain.head_state.timestamp + 1
    end_report_window_des = universe.getReportingWindowByMarketEndTime(end_timestamp)

    # Test getting same calculated end reporting window
    end_timestamp_des_test = end_timestamp + localFixture.contracts['Constants'].DESIGNATED_REPORTING_DURATION_SECONDS() + localFixture.contracts['Constants'].DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS() + 1 + total_dispute_duration
    assert universe.getReportingWindowByTimestamp(end_timestamp_des_test) == end_report_window_des

    assert universe.getPreviousReportingWindow() == universe.getReportingWindowByTimestamp(localFixture.chain.head_state.timestamp - total_dispute_duration)
    assert universe.getCurrentReportingWindow() == universe.getReportingWindowByTimestamp(localFixture.chain.head_state.timestamp)
    assert universe.getNextReportingWindow() == universe.getReportingWindowByTimestamp(localFixture.chain.head_state.timestamp + total_dispute_duration)

def test_create_child_universe(localFixture, universe):
    assert universe.getChildUniverse("20") == longToHexString(0)
    assert universe.getOrCreateChildUniverse("20") == universe.getChildUniverse("20")
    assert universe.getChildUniverse("20") != longToHexString(0)
    child = universe.getChildUniverse("20")
    assert universe.isParentOf(child)

    other_universe = localFixture.createUniverse(3, "1")
    other_child = other_universe.getOrCreateChildUniverse("21")
    assert universe.isParentOf(other_child) == False

def test_universe_contains_reporting_win(localFixture, universe):
    other_universe = localFixture.createUniverse(1, "15")
    other_curr_reporting_win = other_universe.getCurrentReportingWindow()
    reportingWindow = localFixture.applySignature('ReportingWindow', universe.getCurrentReportingWindow())

    curr_reporting_window = universe.getCurrentReportingWindow()
    assert universe.isContainerForReportingWindow(curr_reporting_window)
    # Reporting window is in different universe
    assert universe.isContainerForReportingWindow(other_curr_reporting_win) == False

    # Pass in non ReportingWindow object address
    nonReportingWindow = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'nonReportingWindow')
    with raises(TransactionFailed):
        assert universe.isContainerForReportingWindow(nonReportingWindow.address)

    # create reporting windo with startTime of 0
    reporting_window_factory = localFixture.upload('../source/contracts/factories/ReportingWindowFactory.sol', 'reporting_window_factory')
    zero_window = reporting_window_factory.createReportingWindow(localFixture.contracts['Controller'].address, universe.address, 0)
    assert universe.isContainerForReportingWindow(zero_window) == False

def test_universe_contains_dispute_bond_token(localFixture, universe, market):
    # Pass in non Dispute Bond Token object address
    nonDisputeBondToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'nonReportingWindow')
    assert universe.isContainerForDisputeBondToken(nonDisputeBondToken.address) == False

    # Create bond for market not in this universe
    dispute_bond_token_factory = localFixture.upload('../source/contracts/factories/DisputeBondTokenFactory.sol', 'dispute_bond_token_factory')
    bond = dispute_bond_token_factory.createDisputeBondToken(localFixture.contracts['Controller'].address, market.address, tester.a0, 10, "15")
    assert universe.isContainerForDisputeBondToken(bond) == False

    # Pass in bond with market address of 0
    zero_market_bond = dispute_bond_token_factory.createDisputeBondToken(localFixture.contracts['Controller'].address, 0, tester.a0, 10, "15")
    assert universe.isContainerForDisputeBondToken(zero_market_bond) == False

    # TODO Get correct dispute bond token from active market in correct state

    # Since we have non Market/StakeToken/ShareToken lets test the getTypeName() tests
    with raises(TransactionFailed):
        universe.isContainerForMarket(nonDisputeBondToken.address)
    assert universe.isContainerForStakeToken(nonDisputeBondToken.address) == False
    assert universe.isContainerForShareToken(nonDisputeBondToken.address) == False

def test_universe_contains_market(localFixture, cash, market):
    universe = localFixture.createUniverse(1, "25")
    # market in different universe
    assert universe.isContainerForMarket(market.address) == False

    # Give some REP in this universe to tester0 to pay market creation fee
    legacyReputationToken = localFixture.contracts['LegacyReputationToken']
    legacyReputationToken.faucet(11 * 10**6 * 10**18)

    # Get the reputation token for this universe and migrate legacy REP to it
    reputationToken = localFixture.applySignature('ReputationToken', universe.getReputationToken())
    legacyReputationToken.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyReputationToken()

    uni_market = localFixture.createReasonableBinaryMarket(universe, cash)
    assert universe.isContainerForMarket(uni_market.address)

def test_universe_stake_token(localFixture, universe, cash, market):
    stake_token_factory = localFixture.upload('../source/contracts/factories/StakeTokenFactory.sol', 'stake_token_factory')

    # Stake token not associated with this universe market
    different_stake_token = stake_token_factory.createStakeToken(localFixture.contracts['Controller'].address, market.address, [0, 10**18])
    assert universe.isContainerForStakeToken(different_stake_token) == False

    # TODO add test for Stake token associated market address of 0

    # Create market and test it's stake token
    uni_market = localFixture.createReasonableBinaryMarket(universe, cash)
    good_stake_token = localFixture.getStakeToken(uni_market, [0,10**18])
    assert universe.isContainerForMarket(uni_market.address)
    assert universe.isContainerForStakeToken(good_stake_token.address)

def test_universe_contains_share_token(localFixture, universe, cash, market):
    share_token_factory = localFixture.upload('../source/contracts/factories/ShareTokenFactory.sol', 'share_token_factory')

    # Share token not associated with this universe market
    different_share_token = share_token_factory.createShareToken(localFixture.contracts['Controller'].address, market.address, 1)
    assert universe.isContainerForShareToken(different_share_token) == False

    # TODO add test for Share token associated market address of 0

    # Create market and test it's stake token
    uni_market = localFixture.createReasonableBinaryMarket(universe, cash)
    good_share_token = localFixture.getShareToken(uni_market, 1)
    assert universe.isContainerForShareToken(good_share_token.address)

def test_open_interest(universe):
    assert universe.getOpenInterestInAttoEth() == 0
    universe.incrementOpenInterest(10)
    assert universe.getOpenInterestInAttoEth() == 10
    universe.decrementOpenInterest(5)
    assert universe.getOpenInterestInAttoEth() == 5

@fixture
def localFixture(fixture, augurInitializedSnapshot):
    fixture.resetToSnapshot(augurInitializedSnapshot)
    fixture.uploadAndAddToController("solidity_test_helpers/Constants.sol")
    universe = fixture.createUniverse(0, "")
    cash = fixture.getSeededCash()
    augur = fixture.contracts['Augur']
    fixture.distributeRep(universe)
    binaryMarket = fixture.createReasonableBinaryMarket(universe, cash)
    return fixture
