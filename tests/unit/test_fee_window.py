from ethereum.tools import tester
from utils import longToHexString, stringToBytes, bytesToHexString, twentyZeros, thirtyTwoZeros, longTo32Bytes
from pytest import fixture, raises
from ethereum.tools.tester import TransactionFailed

numTicks = 10 ** 10
feeWindowId = 1467446882

def test_fee_window_creation(localFixture, initializedFeeWindow, mockReputationToken, mockUniverse, constants, Time):
    assert initializedFeeWindow.getTypeName() == stringToBytes("FeeWindow")
    assert initializedFeeWindow.getReputationToken() == mockReputationToken.address
    assert initializedFeeWindow.getStartTime() == feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds()
    assert initializedFeeWindow.getUniverse() == mockUniverse.address
    assert initializedFeeWindow.getEndTime() == feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + constants.DISPUTE_ROUND_DURATION_SECONDS()
    assert initializedFeeWindow.getNumInvalidMarkets() == 0
    assert initializedFeeWindow.getNumIncorrectDesignatedReportMarkets() == 0
    assert initializedFeeWindow.getNumDesignatedReportNoShows() == 0
    assert initializedFeeWindow.isActive() == False
    assert initializedFeeWindow.isOver() == False
    Time.setTimestamp(feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + 1)
    assert initializedFeeWindow.isActive() == True
    Time.setTimestamp(feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + constants.DISPUTE_ROUND_DURATION_SECONDS())
    assert initializedFeeWindow.isActive() == False
    assert initializedFeeWindow.isOver() == True

def test_fee_window_on_market_finalization(localFixture, initializedFeeWindow, mockUniverse, mockMarket):
    with raises(TransactionFailed, message="on market finalized needs to be called from market"):
        initializedFeeWindow.onMarketFinalized()

    with raises(TransactionFailed, message="market needs to be in same universe"):
        mockMarket.callOnMarketFinalized()

    mockUniverse.setIsContainerForMarket(True)
    mockMarket.setIsInvalid(False)
    mockMarket.setDesignatedReporterWasCorrect(True)
    mockMarket.setDesignatedReporterShowed(True)

    numMarkets = initializedFeeWindow.getNumMarkets()
    invalidMarkets = initializedFeeWindow.getNumInvalidMarkets()
    incorrectDRMarkets = initializedFeeWindow.getNumIncorrectDesignatedReportMarkets()

    assert mockMarket.callOnMarketFinalized(initializedFeeWindow.address) == True
    assert initializedFeeWindow.getNumMarkets() == numMarkets + 1
    assert initializedFeeWindow.getNumInvalidMarkets() == invalidMarkets
    assert initializedFeeWindow.getNumIncorrectDesignatedReportMarkets() == incorrectDRMarkets

    mockMarket.setIsInvalid(True)
    mockMarket.setDesignatedReporterWasCorrect(False)
    mockMarket.setDesignatedReporterShowed(False)

    numMarkets = initializedFeeWindow.getNumMarkets()
    invalidMarkets = initializedFeeWindow.getNumInvalidMarkets()
    incorrectDRMarkets = initializedFeeWindow.getNumIncorrectDesignatedReportMarkets()

    assert mockMarket.callOnMarketFinalized(initializedFeeWindow.address) == True
    assert initializedFeeWindow.getNumMarkets() == numMarkets + 1
    assert initializedFeeWindow.getNumInvalidMarkets() == invalidMarkets + 1
    assert initializedFeeWindow.getNumIncorrectDesignatedReportMarkets() == incorrectDRMarkets + 1

@fixture(scope="module")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockCash = fixture.contracts['MockCash']
    mockAugur = fixture.contracts['MockAugur']
    mockReputationToken = fixture.contracts['MockReputationToken']
    controller.registerContract(stringToBytes('Cash'), mockCash.address)
    controller.registerContract(stringToBytes('Augur'), mockAugur.address)
    feeWindow = fixture.upload('../source/contracts/reporting/FeeWindow.sol', 'feeWindow')
    fixture.contracts["initializedFeeWindow"] = feeWindow
    feeWindow.setController(fixture.contracts["Controller"].address)

    mockUniverse = fixture.contracts['MockUniverse']
    mockUniverse.setReputationToken(mockReputationToken.address)
    mockUniverse.setDisputeRoundDurationInSeconds(5040)
    mockUniverse.setForkingMarket(5040)
    mockUniverse.setForkingMarket(longToHexString(0))
    mockUniverse.setIsForking(False)
    fixture.contracts["Time"].setTimestamp(feeWindowId)
    feeWindow.initialize(mockUniverse.address, feeWindowId)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def mockUniverse(localFixture):
    return localFixture.contracts['MockUniverse']

@fixture
def mockMarket(localFixture):
    return localFixture.contracts['MockMarket']

@fixture
def mockCash(localFixture):
    return localFixture.contracts['MockCash']

@fixture
def mockReputationToken(localFixture):
    return localFixture.contracts['MockReputationToken']

@fixture
def initializedFeeWindow(localFixture):
    return localFixture.contracts["initializedFeeWindow"]

@fixture
def constants(localFixture):
    return localFixture.contracts['Constants']

@fixture
def mockInitialReporter(localFixture):
    return localFixture.contracts['MockInitialReporter']

@fixture
def Time(localFixture):
    return localFixture.contracts["Time"]
