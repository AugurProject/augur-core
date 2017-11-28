from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longToHexString, stringToBytes, twentyZeros, thirtyTwoZeros
from pytest import fixture, raises

def test_universe_creation(localFixture, mockReputationToken, mockReputationTokenFactory, mockUniverse, mockUniverseFactory, mockAugur):
    universe = localFixture.upload('../source/contracts/reporting/Universe.sol', 'universe')

    with raises(TransactionFailed, message="reputation token can not be address 0"):
        universe.initialize(mockUniverse.address, stringToBytes("5"))

    mockReputationTokenFactory.setCreateReputationTokenValue(mockReputationToken.address)

    universe.setController(localFixture.contracts['Controller'].address)
    assert universe.initialize(mockUniverse.address, stringToBytes("5"))
    assert universe.getReputationToken() == mockReputationToken.address
    assert universe.getParentUniverse() == mockUniverse.address
    assert universe.getParentPayoutDistributionHash() == stringToBytes("5")
    assert universe.getForkingMarket() == longToHexString(0)
    assert universe.getForkEndTime() == 0
    assert universe.getTypeName() == stringToBytes('Universe')
    assert universe.getForkEndTime() == 0
    assert universe.getChildUniverse("5") == longToHexString(0)

def test_universe_fork_market(localFixture, populatedUniverse, mockUniverse, mockUniverseFactory, mockMarket, mockReportingWindow, chain, mockReportingWindowFactory, mockAugur):
    with raises(TransactionFailed, message="must be called from market"):
        populatedUniverse.fork()

    with raises(TransactionFailed, message="forking market has to be in universe"):
        mockMarket.callForkOnUniverse(populatedUniverse.address)

    timestamp = chain.head_state.timestamp
    mockReportingWindowFactory.setCreateReportingWindowValue(mockReportingWindow.address)
    reportingWindowId = populatedUniverse.getOrCreateReportingWindowByTimestamp(timestamp)
    mockReportingWindow.setStartTime(timestamp)

    mockReportingWindow.setIsContainerForMarket(True)
    mockMarket.setReportingWindow(mockReportingWindow.address)
    assert populatedUniverse.getForkingMarket() == longToHexString(0)
    assert populatedUniverse.isContainerForMarket(mockMarket.address)

    assert mockMarket.callForkOnUniverse(populatedUniverse.address)
    assert mockAugur.logUniverseForkedCalled() == True
    assert populatedUniverse.getForkingMarket() == mockMarket.address
    assert populatedUniverse.getForkEndTime() == timestamp + localFixture.contracts['Constants'].FORK_DURATION_SECONDS()

    # child universe
    mockUniverseFactory.setCreateUniverseUniverseValue(mockUniverse.address)
    mockUniverse.setParentPayoutDistributionHash(stringToBytes("101"))
    assert populatedUniverse.getOrCreateChildUniverse(stringToBytes("101")) == mockUniverse.address
    assert mockAugur.logUniverseCreatedCalled() == True
    assert mockUniverseFactory.getCreateUniverseParentUniverseValue() == populatedUniverse.address
    assert mockUniverseFactory.getCreateUniverseParentPayoutDistributionHashValue() == stringToBytes("101")
    assert populatedUniverse.getChildUniverse(stringToBytes("101")) == mockUniverse.address
    assert populatedUniverse.isParentOf(mockUniverse.address)
    strangerUniverse = localFixture.upload('../source/contracts/reporting/Universe.sol', 'strangerUniverse')
    assert populatedUniverse.isParentOf(strangerUniverse.address) == False

    assert populatedUniverse.getOrCreateReportingWindowForForkEndTime() == mockReportingWindow.address

    with raises(TransactionFailed, message="forking market is already set"):
        mockMarket.callForkOnUniverse()


def test_get_reporting_window(localFixture, populatedUniverse, chain):
    constants = localFixture.contracts['Constants']
    timestamp = chain.head_state.timestamp
    duration =  constants.REPORTING_DURATION_SECONDS()
    dispute_duration = constants.REPORTING_DISPUTE_DURATION_SECONDS()
    total_dispute_duration = duration + dispute_duration
    reportingPeriodDurationForTimestamp = timestamp / total_dispute_duration

    assert populatedUniverse.getReportingWindowId(timestamp) == reportingPeriodDurationForTimestamp
    assert populatedUniverse.getReportingPeriodDurationInSeconds() == total_dispute_duration

    # reporting window not stored internally, only read-only method
    assert populatedUniverse.getReportingWindow(reportingPeriodDurationForTimestamp) == longToHexString(0)
    report_window = populatedUniverse.getOrCreateReportingWindowByTimestamp(timestamp)

    # Now reporting window is in internal collection
    assert populatedUniverse.getReportingWindow(reportingPeriodDurationForTimestamp) == report_window

    # Make up end timestamp for testing internal calculations
    end_timestamp = chain.head_state.timestamp + 1
    end_report_window_des = populatedUniverse.getOrCreateReportingWindowByMarketEndTime(end_timestamp)

    # Test getting same calculated end reporting window
    end_timestamp_des_test = end_timestamp + constants.DESIGNATED_REPORTING_DURATION_SECONDS() + constants.DESIGNATED_REPORTING_DISPUTE_DURATION_SECONDS() + 1 + total_dispute_duration
    assert populatedUniverse.getOrCreateReportingWindowByTimestamp(end_timestamp_des_test) == end_report_window_des
    assert populatedUniverse.getOrCreatePreviousReportingWindow() == populatedUniverse.getOrCreateReportingWindowByTimestamp(chain.head_state.timestamp - total_dispute_duration)
    assert populatedUniverse.getOrCreateCurrentReportingWindow() == populatedUniverse.getOrCreateReportingWindowByTimestamp(chain.head_state.timestamp)
    assert populatedUniverse.getOrCreateNextReportingWindow() == populatedUniverse.getOrCreateReportingWindowByTimestamp(chain.head_state.timestamp + total_dispute_duration)

def test_universe_contains(localFixture, populatedUniverse, mockMarket, mockStakeToken, chain, mockReportingWindow, mockDisputeBond, mockShareToken, mockReportingWindowFactory):
    mockReportingWindow.setStartTime(0)
    assert populatedUniverse.isContainerForReportingWindow(mockReportingWindow.address) == False
    assert populatedUniverse.isContainerForStakeToken(mockStakeToken.address) == False
    assert populatedUniverse.isContainerForMarket(mockMarket.address) == False
    assert populatedUniverse.isContainerForShareToken(mockShareToken.address) == False
    assert populatedUniverse.isContainerForDisputeBond(mockDisputeBond.address) == False

    timestamp = chain.head_state.timestamp
    mockReportingWindowFactory.setCreateReportingWindowValue(mockReportingWindow.address)
    reportingWindowId = populatedUniverse.getOrCreateReportingWindowByTimestamp(timestamp)
    mockReportingWindow.setStartTime(timestamp)

    mockReportingWindow.setIsContainerForMarket(False)
    mockMarket.setIsContainerForStakeToken(False)
    mockMarket.setIsContainerForShareToken(False)
    mockMarket.setIsContainerForDisputeBond(False)

    assert populatedUniverse.isContainerForStakeToken(mockStakeToken.address) == False
    assert populatedUniverse.isContainerForMarket(mockMarket.address) == False
    assert populatedUniverse.isContainerForShareToken(mockShareToken.address) == False
    assert populatedUniverse.isContainerForDisputeBond(mockDisputeBond.address) == False

    mockReportingWindow.setIsContainerForMarket(True)
    mockMarket.setIsContainerForStakeToken(True)
    mockMarket.setIsContainerForShareToken(True)
    mockMarket.setIsContainerForDisputeBond(True)
    mockMarket.setReportingWindow(mockReportingWindow.address)
    mockStakeToken.setMarket(mockMarket.address)
    mockShareToken.setMarket(mockMarket.address)
    mockDisputeBond.setMarket(mockMarket.address)

    assert populatedUniverse.isContainerForReportingWindow(mockReportingWindow.address) == True
    assert populatedUniverse.isContainerForMarket(mockMarket.address) == True
    assert populatedUniverse.isContainerForStakeToken(mockStakeToken.address) == True
    assert populatedUniverse.isContainerForShareToken(mockShareToken.address) == True
    assert populatedUniverse.isContainerForDisputeBond(mockDisputeBond.address) == True

def test_open_interest(localFixture, populatedUniverse):
    multiplier = localFixture.contracts['Constants'].TARGET_REP_MARKET_CAP_MULTIPLIER()
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getOpenInterestInAttoEth() == 0
    populatedUniverse.incrementOpenInterest(10)
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 10 * multiplier
    assert populatedUniverse.getOpenInterestInAttoEth() == 10
    populatedUniverse.decrementOpenInterest(5)
    assert populatedUniverse.getOpenInterestInAttoEth() == 5
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 5 * multiplier

def test_universe_rep_price_oracle(localFixture, populatedUniverse, mockReputationToken, mockShareToken, mockStakeToken):
    controller = localFixture.contracts['Controller']
    repPriceOracle = localFixture.uploadAndAddToController("../source/contracts/reporting/RepPriceOracle.sol", 'repPriceOracle')
    controller.registerContract(stringToBytes('RepPriceOracle'), repPriceOracle.address, twentyZeros, thirtyTwoZeros)
    mockReputationToken.setTotalSupply(0)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 0
    mockReputationToken.setTotalSupply(1)
    repPriceOracle.setRepPriceInAttoEth(100)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 100
    mockReputationToken.setTotalSupply(12)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 1200

def test_universe_calculate_bonds_stakes(localFixture, chain, populatedUniverse, mockReportingWindow, mockReportingWindowFactory):
    timestamp = chain.head_state.timestamp
    constants = localFixture.contracts['Constants']
    currentReportingWindow = mockReportingWindow
    nextReportingWindow = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol', 'nextReportingWindow')
    newCurrentReportingWindow = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol', 'newCurrentReportingWindow')
    # set current reporting window
    mockReportingWindowFactory.setCreateReportingWindowValue(mockReportingWindow.address)
    assert populatedUniverse.getOrCreateCurrentReportingWindow() == mockReportingWindow.address

    # set next reporting window
    mockReportingWindowFactory.setCreateReportingWindowValue(nextReportingWindow.address)
    assert populatedUniverse.getOrCreateNextReportingWindow() == nextReportingWindow.address

    designated_divisor = constants.TARGET_INCORRECT_DESIGNATED_REPORT_MARKETS_DIVISOR()
    designated_default = constants.DEFAULT_DESIGNATED_REPORT_STAKE()
    designated_floor = constants.DESIGNATED_REPORT_STAKE_FLOOR()

    validity_divisor = constants.TARGET_INVALID_MARKETS_DIVISOR()
    validity_default = constants.DEFAULT_VALIDITY_BOND()
    validity_floor = constants.DEFAULT_VALIDITY_BOND_FLOOR()

    noshow_divisor = constants.TARGET_DESIGNATED_REPORT_NO_SHOWS_DIVISOR()
    noshow_default = constants.DEFAULT_DESIGNATED_REPORT_NO_SHOW_BOND()
    noshow_floor = constants.DESIGNATED_REPORT_NO_SHOW_BOND_FLOOR()

    getGasToReport = constants.GAS_TO_REPORT()

    # current reporting window
    designatedStakeValue = populatedUniverse.calculateFloatingValue(0, 0, designated_divisor, 0, designated_default, designated_floor)
    validityBondValue = populatedUniverse.calculateFloatingValue(0, 0, validity_divisor, 0, validity_default, validity_floor)
    noshowBondValue = populatedUniverse.calculateFloatingValue(0, 0, noshow_divisor, 0, noshow_default, noshow_floor)
    # validity bond is the same if window hasn't changed
    assert populatedUniverse.getOrCacheDesignatedReportStake() == designatedStakeValue
    assert populatedUniverse.getOrCacheDesignatedReportStake() == designatedStakeValue
    assert populatedUniverse.getOrCacheValidityBond() == validityBondValue
    assert populatedUniverse.getOrCacheValidityBond() == validityBondValue
    assert populatedUniverse.getOrCacheDesignatedReportNoShowBond() == noshowBondValue
    assert populatedUniverse.getOrCacheDesignatedReportNoShowBond() == noshowBondValue

    # push reporting window forward
    chain.head_state.timestamp = chain.head_state.timestamp + populatedUniverse.getReportingPeriodDurationInSeconds()
    assert populatedUniverse.getOrCreatePreviousReportingWindow() == currentReportingWindow.address

    numMarket = 6
    currentReportingWindow.setNumMarkets(numMarket)
    currentReportingWindow.setNumIncorrectDesignatedReportMarkets(5)
    currentReportingWindow.setNumInvalidMarkets(2)
    currentReportingWindow.setNumDesignatedReportNoShows(3)
    newDesignatedStakeValue = populatedUniverse.calculateFloatingValue(5, numMarket, designated_divisor, designatedStakeValue, designated_default, designated_floor)
    newValidityBondValue = populatedUniverse.calculateFloatingValue(2, numMarket, validity_divisor, validityBondValue, validity_default, validity_floor)
    newNoshowBondValue = populatedUniverse.calculateFloatingValue(3, numMarket, noshow_divisor, noshowBondValue, noshow_default, noshow_floor)

    assert populatedUniverse.getOrCacheDesignatedReportStake() == newDesignatedStakeValue
    assert populatedUniverse.getOrCacheValidityBond() == newValidityBondValue
    assert populatedUniverse.getOrCacheDesignatedReportNoShowBond() == newNoshowBondValue

    currentReportingWindow.setAvgReportingGasPrice(14)
    targetGasCost = getGasToReport * 14 * 2;
    assert populatedUniverse.getOrCacheTargetReporterGasCosts() == targetGasCost
    assert populatedUniverse.getOrCacheMarketCreationCost() == targetGasCost + newValidityBondValue

def test_universe_calculate_floating_value_defaults(populatedUniverse):
    defaultValue = 12
    totalMarkets = 0
    assert populatedUniverse.calculateFloatingValue(11, totalMarkets, 4, 22, defaultValue, 6) == defaultValue

def test_universe_reporting_fee_divisor(localFixture, chain, populatedUniverse, mockReputationToken, mockReportingWindow, mockReportingWindowFactory):
    timestamp = chain.head_state.timestamp
    controller = localFixture.contracts['Controller']
    constants = localFixture.contracts['Constants']
    repPriceOracle = localFixture.uploadAndAddToController("../source/contracts/reporting/RepPriceOracle.sol", 'repPriceOracle')
    controller.registerContract(stringToBytes('RepPriceOracle'), repPriceOracle.address, twentyZeros, thirtyTwoZeros)

    previousReportingWindow = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol', 'previousReportingWindow')

    # set current reporting window
    mockReportingWindowFactory.setCreateReportingWindowValue(mockReportingWindow.address)
    assert populatedUniverse.getOrCreateCurrentReportingWindow() == mockReportingWindow.address

    # set previous reporting window
    mockReportingWindowFactory.setCreateReportingWindowValue(previousReportingWindow.address)
    assert populatedUniverse.getOrCreatePreviousReportingWindow() == previousReportingWindow.address

    multiplier = localFixture.contracts['Constants'].TARGET_REP_MARKET_CAP_MULTIPLIER()
    # default value
    defaultValue = 10000
    assert populatedUniverse.getRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue

    # push reporting window forward
    chain.head_state.timestamp = chain.head_state.timestamp + populatedUniverse.getReportingPeriodDurationInSeconds()

    # check getRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue

    # push reporting window forward
    chain.head_state.timestamp = chain.head_state.timestamp + populatedUniverse.getReportingPeriodDurationInSeconds()

    # _currentFeeDivisor > 0
    mockReputationToken.setTotalSupply(0)
    repPriceOracle.setRepPriceInAttoEth(0)
    populatedUniverse.incrementOpenInterest(10)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 10 * multiplier
    assert populatedUniverse.getOpenInterestInAttoEth() == 10
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue
    # value is cached for reach reporting window
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue

    # push reporting window forward
    chain.head_state.timestamp = chain.head_state.timestamp + populatedUniverse.getReportingPeriodDurationInSeconds()

    mockReputationToken.setTotalSupply(105)
    repPriceOracle.setRepPriceInAttoEth(10)
    populatedUniverse.incrementOpenInterest(10)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 105 * 10
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 20 * multiplier
    assert populatedUniverse.getOpenInterestInAttoEth() == 20
    # default because calculation is greater than 10000
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue

    # push reporting window forward
    chain.head_state.timestamp = chain.head_state.timestamp + populatedUniverse.getReportingPeriodDurationInSeconds()

    mockReputationToken.setTotalSupply(1)
    repPriceOracle.setRepPriceInAttoEth(1)
    populatedUniverse.decrementOpenInterest(15)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 1
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 5 * multiplier
    assert populatedUniverse.getOpenInterestInAttoEth() == 5

    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue / 5 * multiplier

def test_universe_create_market(localFixture, chain, populatedUniverse, mockMarket, mockCash, mockReputationToken, mockParticipationToken, mockAugur, mockReportingWindowFactory, mockReportingWindow):
    timestamp = chain.head_state.timestamp
    endTimeValue = timestamp + 10
    numOutcomesValue = 2
    numTicks = 1 * 10**6 * 10**18
    feePerEthInWeiValue = 10 ** 18
    designatedReporterAddressValue = tester.a2
    mockReportingWindow.setCreateMarket(mockMarket.address)

    # set current reporting window
    mockReportingWindowFactory.setCreateReportingWindowValue(mockReportingWindow.address)
    assert populatedUniverse.getOrCreateCurrentReportingWindow() == mockReportingWindow.address

    # set previous reporting window
    mockReportingWindowFactory.setCreateReportingWindowValue(mockReportingWindow.address)
    assert populatedUniverse.getOrCreatePreviousReportingWindow() == mockReportingWindow.address

    assert mockAugur.logMarketCreatedCalled() == False
    newMarket = populatedUniverse.createMarket(endTimeValue, numOutcomesValue, numTicks, feePerEthInWeiValue, mockCash.address, designatedReporterAddressValue, "topic", "info")
    assert mockAugur.logMarketCreatedCalled() == True
    assert newMarket == mockMarket.address

@fixture
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockReputationTokenFactory = fixture.contracts['MockReputationTokenFactory']
    mockReportingWindowFactory = fixture.contracts['MockReportingWindowFactory']
    mockUniverseFactory = fixture.contracts['MockUniverseFactory']
    controller.registerContract(stringToBytes('ReputationTokenFactory'), mockReputationTokenFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('ReportingWindowFactory'), mockReportingWindowFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('UniverseFactory'), mockUniverseFactory.address, twentyZeros, thirtyTwoZeros)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def chain(localFixture):
    return localFixture.chain

@fixture
def mockReportingWindow(localFixture):
    return localFixture.contracts['MockReportingWindow']

@fixture
def mockReputationToken(localFixture):
    return localFixture.contracts['MockReputationToken']

@fixture
def mockReputationTokenFactory(localFixture):
    return localFixture.contracts['MockReputationTokenFactory']

@fixture
def mockReportingWindowFactory(localFixture):
    return localFixture.contracts['MockReportingWindowFactory']

@fixture
def mockUniverseFactory(localFixture):
    return localFixture.contracts['MockUniverseFactory']

@fixture
def mockUniverse(localFixture):
    return localFixture.contracts['MockUniverse']

@fixture
def mockMarket(localFixture):
    return localFixture.contracts['MockMarket']

@fixture
def mockAugur(localFixture):
    return localFixture.contracts['MockAugur']

@fixture
def mockDisputeBond(localFixture):
    return localFixture.contracts['MockDisputeBond']

@fixture
def mockStakeToken(localFixture):
    return localFixture.contracts['MockStakeToken']

@fixture
def mockShareToken(localFixture):
    return localFixture.contracts['MockShareToken']

@fixture
def mockCash(localFixture):
    return localFixture.contracts['MockCash']

@fixture
def mockParticipationToken(localFixture):
    return localFixture.contracts['MockParticipationToken']

@fixture
def populatedUniverse(localFixture, mockReputationTokenFactory, mockReputationToken, mockUniverse):
    universe = localFixture.upload('../source/contracts/reporting/Universe.sol', 'universe')
    mockReputationTokenFactory.setCreateReputationTokenValue(mockReputationToken.address)
    universe.setController(localFixture.contracts['Controller'].address)
    assert universe.initialize(mockUniverse.address, stringToBytes("5"))
    return universe
