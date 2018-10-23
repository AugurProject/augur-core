from ethereum.tools import tester
from utils import longToHexString, stringToBytes, bytesToHexString, twentyZeros, thirtyTwoZeros, longTo32Bytes
from pytest import fixture, raises
from ethereum.tools.tester import TransactionFailed

numTicks = 10 ** 10
disputeWindowId = 1467446882

def test_fee_window_creation(localFixture, initializedDisputeWindow, mockReputationToken, mockUniverse, constants, Time):
    assert initializedDisputeWindow.getTypeName() == stringToBytes("DisputeWindow")
    assert initializedDisputeWindow.getReputationToken() == mockReputationToken.address
    assert initializedDisputeWindow.getStartTime() == disputeWindowId * mockUniverse.getDisputeRoundDurationInSeconds()
    assert initializedDisputeWindow.getUniverse() == mockUniverse.address
    assert initializedDisputeWindow.getEndTime() == disputeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + constants.DISPUTE_ROUND_DURATION_SECONDS()
    assert initializedDisputeWindow.getNumInvalidMarkets() == 0
    assert initializedDisputeWindow.getNumIncorrectDesignatedReportMarkets() == 0
    assert initializedDisputeWindow.getNumDesignatedReportNoShows() == 0
    assert initializedDisputeWindow.isActive() == False
    assert initializedDisputeWindow.isOver() == False
    Time.setTimestamp(disputeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + 1)
    assert initializedDisputeWindow.isActive() == True
    Time.setTimestamp(disputeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + constants.DISPUTE_ROUND_DURATION_SECONDS())
    assert initializedDisputeWindow.isActive() == False
    assert initializedDisputeWindow.isOver() == True

def test_fee_window_on_market_finalization(localFixture, initializedDisputeWindow, mockUniverse, mockMarket):
    with raises(TransactionFailed, message="on market finalized needs to be called from market"):
        initializedDisputeWindow.onMarketFinalized()

    with raises(TransactionFailed, message="market needs to be in same universe"):
        mockMarket.callOnMarketFinalized()

    mockUniverse.setIsContainerForMarket(True)
    mockMarket.setIsInvalid(False)
    mockMarket.setDesignatedReporterWasCorrect(True)
    mockMarket.setDesignatedReporterShowed(True)

    numMarkets = initializedDisputeWindow.getNumMarkets()
    invalidMarkets = initializedDisputeWindow.getNumInvalidMarkets()
    incorrectDRMarkets = initializedDisputeWindow.getNumIncorrectDesignatedReportMarkets()

    assert mockMarket.callOnMarketFinalized(initializedDisputeWindow.address) == True
    assert initializedDisputeWindow.getNumMarkets() == numMarkets + 1
    assert initializedDisputeWindow.getNumInvalidMarkets() == invalidMarkets
    assert initializedDisputeWindow.getNumIncorrectDesignatedReportMarkets() == incorrectDRMarkets

    mockMarket.setIsInvalid(True)
    mockMarket.setDesignatedReporterWasCorrect(False)
    mockMarket.setDesignatedReporterShowed(False)

    numMarkets = initializedDisputeWindow.getNumMarkets()
    invalidMarkets = initializedDisputeWindow.getNumInvalidMarkets()
    incorrectDRMarkets = initializedDisputeWindow.getNumIncorrectDesignatedReportMarkets()

    assert mockMarket.callOnMarketFinalized(initializedDisputeWindow.address) == True
    assert initializedDisputeWindow.getNumMarkets() == numMarkets + 1
    assert initializedDisputeWindow.getNumInvalidMarkets() == invalidMarkets + 1
    assert initializedDisputeWindow.getNumIncorrectDesignatedReportMarkets() == incorrectDRMarkets + 1

@fixture(scope="module")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockCash = fixture.contracts['MockCash']
    mockAugur = fixture.contracts['MockAugur']
    mockReputationToken = fixture.contracts['MockReputationToken']
    controller.registerContract(stringToBytes('Cash'), mockCash.address)
    controller.registerContract(stringToBytes('Augur'), mockAugur.address)
    disputeWindow = fixture.upload('../source/contracts/reporting/DisputeWindow.sol', 'disputeWindow')
    fixture.contracts["initializedDisputeWindow"] = disputeWindow
    disputeWindow.setController(fixture.contracts["Controller"].address)

    mockUniverse = fixture.contracts['MockUniverse']
    mockUniverse.setReputationToken(mockReputationToken.address)
    mockUniverse.setDisputeRoundDurationInSeconds(5040)
    mockUniverse.setForkingMarket(5040)
    mockUniverse.setForkingMarket(longToHexString(0))
    mockUniverse.setIsForking(False)
    fixture.contracts["Time"].setTimestamp(disputeWindowId)
    disputeWindow.initialize(mockUniverse.address, disputeWindowId)
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
def initializedDisputeWindow(localFixture):
    return localFixture.contracts["initializedDisputeWindow"]

@fixture
def constants(localFixture):
    return localFixture.contracts['Constants']

@fixture
def mockInitialReporter(localFixture):
    return localFixture.contracts['MockInitialReporter']

@fixture
def Time(localFixture):
    return localFixture.contracts["Time"]
