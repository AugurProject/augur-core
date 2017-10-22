from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed
from reporting_utils import proceedToDesignatedReporting, proceedToRound1Reporting, proceedToRound2Reporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture


def test_reporting_window_initialize(localFixture, chain, mockUniverse, mockReportingAttendanceToken):
    timestamp = chain.head_state.timestamp
    mockUniverse.setReportingPeriodDurationInSeconds(timestamp)

    mockReportingAttendanceTokenFactory = localFixture.contracts['MockReportingAttendanceTokenFactory']
    mockReportingAttendanceTokenFactory.setAttendanceTokenValue(mockReportingAttendanceToken.address)

    reportingWindow = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'reportingWindow')
    reportingWindow.setController(localFixture.contracts['Controller'].address)

    start_time = 2 * timestamp
    assert reportingWindow.initialize(mockUniverse.address, 2)
    assert reportingWindow.getStartTime() == start_time     
    assert reportingWindow.getAvgReportingGasPrice() == localFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()
    assert reportingWindow.getReportingAttendanceToken() == mockReportingAttendanceToken.address
    assert reportingWindow.getReportingStartTime() ==    start_time
    reporting_end = start_time + localFixture.contracts['Constants'].REPORTING_DURATION_SECONDS()
    assert reportingWindow.getReportingEndTime() == reporting_end
    assert reportingWindow.getDisputeStartTime() == reporting_end
    assert reportingWindow.getDisputeEndTime() == reporting_end + localFixture.contracts['Constants'].REPORTING_DISPUTE_DURATION_SECONDS()

    nextReportingWindow = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'nextReportingWindow')
    mockUniverse.setReportingWindowByTimestamp(nextReportingWindow.address)
    assert reportingWindow.getNextReportingWindow() == nextReportingWindow.address

    previousReportingWindow = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'previousReportingWindow')
    mockUniverse.setReportingWindowByTimestamp(previousReportingWindow.address)
    assert reportingWindow.getPreviousReportingWindow() == previousReportingWindow.address

def test_reporting_window_create_market(localFixture, chain, mockUniverse, mockMarket, cash, mockReputationToken, mockReportingAttendanceToken):
    mockMarketFactory = localFixture.contracts['MockMarketFactory']
    mockReportingAttendanceTokenFactory = localFixture.contracts['MockReportingAttendanceTokenFactory']
    mockMarketFactory.setMarket(mockMarket.address)
    mockReportingAttendanceTokenFactory.setAttendanceTokenValue(mockReportingAttendanceToken.address)

    timestamp = chain.head_state.timestamp
    endTimeValue = timestamp + 10
    numOutcomesValue = 2
    numTicks = 1 * 10**6 * 10**18
    feePerEthInWeiValue = 10 ** 18
    designatedReporterAddressValue = tester.a2
    
    mockUniverse.setReportingPeriodDurationInSeconds(timestamp - 10)
    reportingWindow1 = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'reportingWindow1')
    reportingWindow1.setController(localFixture.contracts['Controller'].address)

    assert reportingWindow1.initialize(mockUniverse.address, 1)
    with raises(TransactionFailed, message="start time is less than current block time"):
        newMarket = reportingWindow1.createMarket(endTimeValue, numOutcomesValue, numTicks, feePerEthInWeiValue, cash.address, designatedReporterAddressValue)

    mockUniverse.setReportingPeriodDurationInSeconds(timestamp)
    reportingWindow2 = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'reportingWindow2')
    reportingWindow2.setController(localFixture.contracts['Controller'].address)
    assert reportingWindow2.initialize(mockUniverse.address, 2)
    mockUniverse.setReportingWindowByMarketEndTime(tester.a0)
    with raises(TransactionFailed, message="reporting window not associated with universe"):
        newMarket = reportingWindow2.createMarket(endTimeValue, numOutcomesValue, numTicks, feePerEthInWeiValue, cash.address, designatedReporterAddressValue)

    mockUniverse.setReportingPeriodDurationInSeconds(timestamp - 1)
    mockUniverse.setDesignatedReportNoShowBond(10)
    mockUniverse.setReputationToken(mockReputationToken.address)
    reportingWindow3 = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'reportingWindow3')
    reportingWindow3.setController(localFixture.contracts['Controller'].address)

    assert reportingWindow3.initialize(mockUniverse.address, 2)
    assert reportingWindow3.getNumMarkets() == 0
    mockUniverse.setReportingWindowByMarketEndTime(reportingWindow3.address)
    newMarket = reportingWindow3.createMarket(endTimeValue, numOutcomesValue, numTicks, feePerEthInWeiValue, cash.address, designatedReporterAddressValue)

    assert newMarket == mockMarket.address
    assert mockMarketFactory.getCreateMarketReportingWindowValue() == reportingWindow3.address
    assert mockMarketFactory.getCreateMarketEndTimeValue() == endTimeValue
    assert mockMarketFactory.getCreateMarketNumOutcomesValue() == numOutcomesValue
    assert mockMarketFactory.getCreateMarketNumTicksValue() == numTicks
    assert mockMarketFactory.getCreateMarketfeePerEthInWeiValue() == feePerEthInWeiValue
    assert mockMarketFactory.getCreateMarketDenominationTokenValue() == cash.address
    assert mockMarketFactory.getCreateMarketCreatorValue() == bytesToHexString(tester.a0)
    assert mockMarketFactory.getCreateMarketDesignatedReporterAddressValue() == bytesToHexString(designatedReporterAddressValue)
    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a0)
    assert mockReputationToken.getTrustedTransferDestinationValue() == mockMarketFactory.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == 10
    assert reportingWindow3.getNumMarkets() == 1

def test_reporting_window_migrate_market_in_from_sib(localFixture, chain, mockUniverse, mockMarket, mockReputationToken, populatedReportingWindow):
    
    with raises(TransactionFailed, message="method has be called from Market"):
        populatedReportingWindow.migrateMarketInFromSibling()
    
    mockUniverse.setIsContainerForReportingWindow(False)
    with raises(TransactionFailed, message="market is not in universe"):
        mockMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    
    newMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMarket')
    assert populatedReportingWindow.isContainerForMarket(newMarket.address) == False
    
    newWindow = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol', 'newWindow')    
    newWindow.setIsContainerForMarket(False)
    mockUniverse.setIsContainerForReportingWindow(True)
    with raises(TransactionFailed, message="market reporting window doesn't contain market"):
        newMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    
    newMarket.setReportingWindow(newWindow.address)
    newMarket.setUniverse(mockUniverse.address)
    newWindow.setIsContainerForMarket(True)
    newWindow.setMigrateFeesDueToMarketMigration(True)
    assert populatedReportingWindow.isContainerForMarket(mockMarket.address)
    assert newMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    assert populatedReportingWindow.isContainerForMarket(newMarket.address)

#def test_reporting_window_migrate_market_in_from_N_sib(localFixture, chain, mockUniverse, mockMarket, mockReputationToken, populatedReportingWindow):
    
    
@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    controller = fixture.contracts['Controller']
    fixture.uploadAndAddToController('solidity_test_helpers/MockMarket.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockUniverse.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockReportingWindow.sol')    
    fixture.uploadAndAddToController('solidity_test_helpers/MockReputationToken.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockDisputeBondToken.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockReportingAttendanceToken.sol')
    mockReportingAttendanceTokenFactory = fixture.upload('solidity_test_helpers/MockReportingAttendanceTokenFactory.sol')
    mockMarketFactory = fixture.upload('solidity_test_helpers/MockMarketFactory.sol')
    controller.setValue(stringToBytes('MarketFactory'), mockMarketFactory.address)
    controller.setValue(stringToBytes('ReportingAttendanceTokenFactory'), mockReportingAttendanceTokenFactory.address)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)
    return fixture.createSnapshot()

@fixture
def universe(localFixture, chain, kitchenSinkSnapshot):
    universe = ABIContract(chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    return universe

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def chain(localFixture):
    return localFixture.chain

@fixture
def cash(localFixture, chain, kitchenSinkSnapshot):
    cash = ABIContract(chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
    return cash

@fixture
def mockUniverse(localFixture):
    mockUniverse = localFixture.contracts['MockUniverse']
    mockUniverse.setIsContainerForReportingWindow(True)
    mockUniverse.setIsContainerForMarket(True)
    return mockUniverse

@fixture
def mockReputationToken(localFixture):
    mockReputationToken = localFixture.contracts['MockReputationToken']
    mockReputationToken.setTrustedTransfer(True)
    return mockReputationToken

@fixture
def mockReportingAttendanceToken(localFixture):
    mockReportingAttendanceToken = localFixture.contracts['MockReportingAttendanceToken']
    return mockReportingAttendanceToken

@fixture
def mockDisputeBondToken(localFixture):
    mockDisputeBondToken = localFixture.contracts['MockDisputeBondToken']
    return mockDisputeBondToken

@fixture
def mockMarket(localFixture, mockUniverse):
    # wire up mock market
    mockMarket = localFixture.contracts['MockMarket']
    mockMarket.setDesignatedReporter(bytesToHexString(tester.a0))
    mockMarket.setUniverse(mockUniverse.address)
    mockMarket.setIsContainerForStakeToken(True)
    mockMarket.setMigrateDueToNoReports(True)
    mockMarket.setMigrateDueToNoReportsNextState(localFixture.contracts['Constants'].ROUND1_REPORTING())
    mockMarket.setRound1ReporterCompensationCheck(0)
    mockMarket.setDerivePayoutDistributionHash(stringToBytes("1"))
    return mockMarket

@fixture
def populatedReportingWindow(localFixture, chain, mockUniverse, mockMarket, cash, mockReportingAttendanceToken, mockReputationToken):
    mockMarketFactory = localFixture.contracts['MockMarketFactory']
    mockReportingAttendanceTokenFactory = localFixture.contracts['MockReportingAttendanceTokenFactory']
    mockMarketFactory.setMarket(mockMarket.address)
    mockReportingAttendanceTokenFactory.setAttendanceTokenValue(mockReportingAttendanceToken.address)

    timestamp = chain.head_state.timestamp
    endTimeValue = timestamp + 10
    numOutcomesValue = 2
    numTicks = 1 * 10**6 * 10**18
    feePerEthInWeiValue = 10 ** 18
    designatedReporterAddressValue = tester.a2
    
    mockUniverse.setReportingPeriodDurationInSeconds(timestamp - 10)
    reportingWindow = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'reportingWindow')
    reportingWindow.setController(localFixture.contracts['Controller'].address)
    mockUniverse.setReportingPeriodDurationInSeconds(timestamp - 1)
    mockUniverse.setDesignatedReportNoShowBond(10)
    mockUniverse.setReputationToken(mockReputationToken.address)
    assert reportingWindow.initialize(mockUniverse.address, 2)
    mockUniverse.setReportingWindowByMarketEndTime(reportingWindow.address)
    reportingWindow.createMarket(endTimeValue, numOutcomesValue, numTicks, feePerEthInWeiValue, cash.address, designatedReporterAddressValue)
    return reportingWindow