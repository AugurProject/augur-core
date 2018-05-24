from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import longToHexString, stringToBytes, twentyZeros, thirtyTwoZeros, bytesToHexString
from pytest import fixture, raises

def test_universe_creation(localFixture, mockReputationToken, mockReputationTokenFactory, mockUniverse, mockUniverseFactory, mockAugur):
    universe = localFixture.upload('../source/contracts/reporting/Universe.sol', 'newUniverse')

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

def test_universe_fork_market(localFixture, populatedUniverse, mockUniverse, mockCash, mockFeeWindow, mockUniverseFactory, mockFeeWindowFactory, mockMarket, chain, mockMarketFactory, mockAugur):
    with raises(TransactionFailed, message="must be called from market"):
        populatedUniverse.fork()

    timestamp = localFixture.contracts["Time"].getTimestamp()

    mockFeeWindowFactory.setCreateFeeWindowValue(mockFeeWindow.address)
    mockMarketFactory.setMarket(mockMarket.address)
    endTime = localFixture.contracts["Time"].getTimestamp() + 30 * 24 * 60 * 60 # 30 days

    with raises(TransactionFailed, message="forking market has to be in universe"):
        mockMarket.callForkOnUniverse(populatedUniverse.address)

    assert populatedUniverse.createBinaryMarket(endTime, 1000, mockCash.address, tester.a0, "topic", "description", "info")
    assert mockMarketFactory.getCreateMarketUniverseValue() == populatedUniverse.address

    assert populatedUniverse.isContainerForMarket(mockMarket.address)

    assert populatedUniverse.getForkingMarket() == longToHexString(0)

    assert mockMarket.callForkOnUniverse(populatedUniverse.address)
    assert mockAugur.logUniverseForkedCalled() == True
    assert populatedUniverse.getForkingMarket() == mockMarket.address
    assert populatedUniverse.getForkEndTime() == timestamp + localFixture.contracts['Constants'].FORK_DURATION_SECONDS()

def test_get_reporting_window(localFixture, populatedUniverse, chain):
    constants = localFixture.contracts['Constants']
    timestamp = localFixture.contracts["Time"].getTimestamp()
    duration =  constants.DISPUTE_ROUND_DURATION_SECONDS()
    reportingPeriodDurationForTimestamp = timestamp / duration

    assert populatedUniverse.getFeeWindowId(timestamp) == reportingPeriodDurationForTimestamp
    assert populatedUniverse.getDisputeRoundDurationInSeconds() == duration

    # fee window not stored internally, only read-only method
    assert populatedUniverse.getFeeWindow(reportingPeriodDurationForTimestamp) == longToHexString(0)
    report_window = populatedUniverse.getOrCreateFeeWindowByTimestamp(timestamp)

    # Now fee window is in internal collection
    assert populatedUniverse.getFeeWindow(reportingPeriodDurationForTimestamp) == report_window

    # Make up end timestamp for testing internal calculations
    end_timestamp = localFixture.contracts["Time"].getTimestamp() + 1

    # Test getting same calculated end fee window
    assert populatedUniverse.getOrCreatePreviousFeeWindow() == populatedUniverse.getOrCreateFeeWindowByTimestamp(chain.head_state.timestamp - duration)
    assert populatedUniverse.getOrCreateCurrentFeeWindow() == populatedUniverse.getOrCreateFeeWindowByTimestamp(chain.head_state.timestamp)
    assert populatedUniverse.getOrCreateNextFeeWindow() == populatedUniverse.getOrCreateFeeWindowByTimestamp(chain.head_state.timestamp + duration)

def test_universe_contains(localFixture, populatedUniverse, mockMarket, chain, mockCash, mockMarketFactory, mockFeeWindow, mockShareToken, mockFeeWindowFactory):
    mockFeeWindow.setStartTime(0)
    assert populatedUniverse.isContainerForFeeWindow(mockFeeWindow.address) == False
    assert populatedUniverse.isContainerForMarket(mockMarket.address) == False
    assert populatedUniverse.isContainerForShareToken(mockShareToken.address) == False

    timestamp = localFixture.contracts["Time"].getTimestamp()
    mockFeeWindowFactory.setCreateFeeWindowValue(mockFeeWindow.address)
    feeWindowId = populatedUniverse.getOrCreateFeeWindowByTimestamp(timestamp)
    mockFeeWindow.setStartTime(timestamp)

    mockMarket.setIsContainerForShareToken(False)

    assert populatedUniverse.isContainerForMarket(mockMarket.address) == False
    assert populatedUniverse.isContainerForShareToken(mockShareToken.address) == False

    mockMarket.setIsContainerForShareToken(True)
    mockMarket.setFeeWindow(mockFeeWindow.address)
    mockShareToken.setMarket(mockMarket.address)

    mockMarketFactory.setMarket(mockMarket.address)
    endTime = localFixture.contracts["Time"].getTimestamp() + 30 * 24 * 60 * 60 # 30 days

    assert populatedUniverse.createBinaryMarket(endTime, 1000, mockCash.address, tester.a0, "topic", "description", "info")
    assert mockMarketFactory.getCreateMarketUniverseValue() == populatedUniverse.address

    assert populatedUniverse.isContainerForFeeWindow(mockFeeWindow.address) == True
    assert populatedUniverse.isContainerForMarket(mockMarket.address) == True
    assert populatedUniverse.isContainerForShareToken(mockShareToken.address) == True

def test_open_interest(localFixture, populatedUniverse):
    multiplier = localFixture.contracts['Constants'].TARGET_REP_MARKET_CAP_MULTIPLIER() / float(localFixture.contracts['Constants'].TARGET_REP_MARKET_CAP_DIVISOR())
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getOpenInterestInAttoEth() == 0
    populatedUniverse.incrementOpenInterest(20)
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 20 * multiplier
    assert populatedUniverse.getOpenInterestInAttoEth() == 20

def test_universe_rep_price_oracle(localFixture, populatedUniverse, mockReputationToken, mockShareToken):
    controller = localFixture.contracts['Controller']
    repPriceOracle = localFixture.uploadAndAddToController("../source/contracts/reporting/RepPriceOracle.sol", 'repPriceOracle')
    controller.registerContract(stringToBytes('RepPriceOracle'), repPriceOracle.address, twentyZeros, thirtyTwoZeros)
    mockReputationToken.setTotalSupply(0)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 0
    mockReputationToken.setTotalSupply(1)
    assert repPriceOracle.setRepPriceInAttoEth(100)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 100
    mockReputationToken.setTotalSupply(12)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 1200
    assert repPriceOracle.transferOwnership(tester.a1)
    assert repPriceOracle.getOwner() == bytesToHexString(tester.a1)

def test_universe_calculate_bonds_stakes(localFixture, chain, populatedUniverse, mockFeeWindow, mockFeeWindowFactory):
    timestamp = localFixture.contracts["Time"].getTimestamp()
    constants = localFixture.contracts['Constants']
    currentFeeWindow = mockFeeWindow
    nextFeeWindow = localFixture.upload('solidity_test_helpers/MockFeeWindow.sol', 'nextFeeWindow')
    newCurrentFeeWindow = localFixture.upload('solidity_test_helpers/MockFeeWindow.sol', 'newCurrentFeeWindow')
    # set current fee window
    mockFeeWindowFactory.setCreateFeeWindowValue(mockFeeWindow.address)
    assert populatedUniverse.getOrCreateCurrentFeeWindow() == mockFeeWindow.address

    # set next fee window
    mockFeeWindowFactory.setCreateFeeWindowValue(nextFeeWindow.address)
    assert populatedUniverse.getOrCreateNextFeeWindow() == nextFeeWindow.address

    initial_report_min = populatedUniverse.getInitialReportMinValue()
    designated_divisor = constants.TARGET_INCORRECT_DESIGNATED_REPORT_MARKETS_DIVISOR()
    designated_default = initial_report_min
    designated_floor = initial_report_min

    validity_divisor = constants.TARGET_INVALID_MARKETS_DIVISOR()
    validity_default = constants.DEFAULT_VALIDITY_BOND()
    validity_floor = constants.VALIDITY_BOND_FLOOR()

    noshow_divisor = constants.TARGET_DESIGNATED_REPORT_NO_SHOWS_DIVISOR()
    noshow_default = initial_report_min
    noshow_floor = initial_report_min

    getGasToReport = constants.GAS_TO_REPORT()

    # current fee window
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

    # push fee window forward
    localFixture.contracts["Time"].incrementTimestamp(populatedUniverse.getDisputeRoundDurationInSeconds())
    assert populatedUniverse.getOrCreatePreviousFeeWindow() == currentFeeWindow.address

    numMarket = 6
    currentFeeWindow.setNumMarkets(numMarket)
    currentFeeWindow.setNumIncorrectDesignatedReportMarkets(5)
    currentFeeWindow.setNumInvalidMarkets(2)
    currentFeeWindow.setNumDesignatedReportNoShows(3)
    newDesignatedStakeValue = populatedUniverse.calculateFloatingValue(5, numMarket, designated_divisor, designatedStakeValue, designated_default, designated_floor)
    newValidityBondValue = populatedUniverse.calculateFloatingValue(2, numMarket, validity_divisor, validityBondValue, validity_default, validity_floor)
    newNoshowBondValue = populatedUniverse.calculateFloatingValue(3, numMarket, noshow_divisor, noshowBondValue, noshow_default, noshow_floor)

    assert populatedUniverse.getOrCacheDesignatedReportStake() == newDesignatedStakeValue
    assert populatedUniverse.getOrCacheValidityBond() == newValidityBondValue
    assert populatedUniverse.getOrCacheDesignatedReportNoShowBond() == newNoshowBondValue

    currentFeeWindow.setAvgReportingGasPrice(14)
    targetGasCost = getGasToReport * 14 * 2
    assert populatedUniverse.getOrCacheTargetReporterGasCosts() == targetGasCost
    assert populatedUniverse.getOrCacheMarketCreationCost() == targetGasCost + newValidityBondValue

def test_universe_calculate_floating_value_defaults(populatedUniverse):
    defaultValue = 12
    totalMarkets = 0
    assert populatedUniverse.calculateFloatingValue(11, totalMarkets, 4, 22, defaultValue, 6) == defaultValue

def test_universe_reporting_fee_divisor(localFixture, chain, populatedUniverse, mockReputationToken, mockFeeWindow, mockFeeWindowFactory):
    timestamp = localFixture.contracts["Time"].getTimestamp()
    controller = localFixture.contracts['Controller']
    constants = localFixture.contracts['Constants']
    repPriceOracle = localFixture.uploadAndAddToController("../source/contracts/reporting/RepPriceOracle.sol", 'repPriceOracle')
    controller.registerContract(stringToBytes('RepPriceOracle'), repPriceOracle.address, twentyZeros, thirtyTwoZeros)

    previousFeeWindow = localFixture.upload('solidity_test_helpers/MockFeeWindow.sol', 'previousFeeWindow')

    # set current fee window
    mockFeeWindowFactory.setCreateFeeWindowValue(mockFeeWindow.address)
    assert populatedUniverse.getOrCreateCurrentFeeWindow() == mockFeeWindow.address

    # set previous fee window
    mockFeeWindowFactory.setCreateFeeWindowValue(previousFeeWindow.address)
    assert populatedUniverse.getOrCreatePreviousFeeWindow() == previousFeeWindow.address

    multiplier = localFixture.contracts['Constants'].TARGET_REP_MARKET_CAP_MULTIPLIER() / float(localFixture.contracts['Constants'].TARGET_REP_MARKET_CAP_DIVISOR())
    # default value
    defaultValue = 100
    assert populatedUniverse.getRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue

    # push fee window forward
    localFixture.contracts["Time"].incrementTimestamp(populatedUniverse.getDisputeRoundDurationInSeconds())

    # check getRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue

    # push fee window forward
    localFixture.contracts["Time"].incrementTimestamp(populatedUniverse.getDisputeRoundDurationInSeconds())

    # check previousDivisor > 0 and getRepMarketCapInAttoeth == 0
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue

    # _currentFeeDivisor > 0
    mockReputationToken.setTotalSupply(0)
    assert repPriceOracle.setRepPriceInAttoEth(0)
    populatedUniverse.incrementOpenInterest(10)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 0
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 10 * multiplier
    assert populatedUniverse.getOpenInterestInAttoEth() == 10
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue
    # value is cached for reach fee window
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue

    # push fee window forward
    localFixture.contracts["Time"].incrementTimestamp(populatedUniverse.getDisputeRoundDurationInSeconds())

    mockReputationToken.setTotalSupply(105)
    assert repPriceOracle.setRepPriceInAttoEth(10)
    populatedUniverse.incrementOpenInterest(10)
    assert populatedUniverse.getRepMarketCapInAttoeth() == 105 * 10
    assert populatedUniverse.getTargetRepMarketCapInAttoeth() == 20 * multiplier
    assert populatedUniverse.getOpenInterestInAttoEth() == 20
    # default because calculation is greater than 10000
    assert populatedUniverse.getOrCacheReportingFeeDivisor() == defaultValue

def test_universe_create_market(localFixture, chain, populatedUniverse, mockMarket, mockMarketFactory, mockCash, mockReputationToken, mockAugur, mockFeeWindowFactory, mockFeeWindow):
    timestamp = localFixture.contracts["Time"].getTimestamp()
    endTimeValue = timestamp + 10
    feePerEthInWeiValue = 10 ** 18
    designatedReporterAddressValue = tester.a2
    mockFeeWindow.setCreateMarket(mockMarket.address)

    # set current fee window
    mockFeeWindowFactory.setCreateFeeWindowValue(mockFeeWindow.address)
    assert populatedUniverse.getOrCreateCurrentFeeWindow() == mockFeeWindow.address

    # set previous fee window
    mockFeeWindowFactory.setCreateFeeWindowValue(mockFeeWindow.address)
    assert populatedUniverse.getOrCreatePreviousFeeWindow() == mockFeeWindow.address

    assert mockAugur.logMarketCreatedCalled() == False
    mockMarketFactory.setMarket(mockMarket.address)

    newMarket = populatedUniverse.createBinaryMarket(endTimeValue, feePerEthInWeiValue, mockCash.address, designatedReporterAddressValue, "topic", "description", "info")

    assert mockMarketFactory.getCreateMarketUniverseValue() == populatedUniverse.address
    assert populatedUniverse.isContainerForMarket(mockMarket.address)
    assert mockAugur.logMarketCreatedCalled() == True
    assert newMarket == mockMarket.address

@fixture(scope="module")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockReputationTokenFactory = fixture.contracts['MockReputationTokenFactory']
    mockFeeWindowFactory = fixture.contracts['MockFeeWindowFactory']
    mockMarketFactory = fixture.contracts['MockMarketFactory']
    mockUniverseFactory = fixture.contracts['MockUniverseFactory']
    controller.registerContract(stringToBytes('MarketFactory'), mockMarketFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('ReputationTokenFactory'), mockReputationTokenFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('FeeWindowFactory'), mockFeeWindowFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('UniverseFactory'), mockUniverseFactory.address, twentyZeros, thirtyTwoZeros)

    mockReputationToken = fixture.contracts['MockReputationToken']
    mockUniverse = fixture.contracts['MockUniverse']

    universe = fixture.upload('../source/contracts/reporting/Universe.sol', 'universe')
    fixture.contracts['populatedUniverse'] = universe
    mockReputationTokenFactory.setCreateReputationTokenValue(mockReputationToken.address)
    universe.setController(fixture.contracts['Controller'].address)
    assert universe.initialize(mockUniverse.address, stringToBytes("5"))

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def chain(localFixture):
    return localFixture.chain

@fixture
def mockFeeWindow(localFixture):
    return localFixture.contracts['MockFeeWindow']

@fixture
def mockReputationToken(localFixture):
    return localFixture.contracts['MockReputationToken']

@fixture
def mockReputationTokenFactory(localFixture):
    return localFixture.contracts['MockReputationTokenFactory']

@fixture
def mockFeeWindowFactory(localFixture):
    return localFixture.contracts['MockFeeWindowFactory']

@fixture
def mockUniverseFactory(localFixture):
    return localFixture.contracts['MockUniverseFactory']

@fixture
def mockMarketFactory(localFixture):
    return localFixture.contracts['MockMarketFactory']

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
def mockShareToken(localFixture):
    return localFixture.contracts['MockShareToken']

@fixture
def mockCash(localFixture):
    return localFixture.contracts['MockCash']

@fixture
def populatedUniverse(localFixture, mockReputationTokenFactory, mockReputationToken, mockUniverse):
    return localFixture.contracts['populatedUniverse']
