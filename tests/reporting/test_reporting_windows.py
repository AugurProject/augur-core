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

    assert reportingWindow.initialize(mockUniverse.address, 2)
    assert reportingWindow.getStartTime() == 2 * timestamp     
    assert reportingWindow.getAvgReportingGasPrice() == localFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()
    assert reportingWindow.getReportingAttendanceToken() == mockReportingAttendanceToken.address

def test_reporting_window_create_market(localFixture, chain, mockUniverse, mockMarket, cash, mockReputationToken, mockReportingAttendanceToken):
    mockMarketFactory = localFixture.contracts['MockMarketFactory']
    mockReportingAttendanceTokenFactory = localFixture.contracts['MockReportingAttendanceTokenFactory']
    mockMarketFactory.setMarket(mockMarket.address)
    mockReportingAttendanceTokenFactory.setAttendanceTokenValue(mockReportingAttendanceToken.address)

    controller = localFixture.contracts['Controller']
    assert controller.lookup("MarketFactory") == mockMarketFactory.address
    assert controller.lookup("ReportingAttendanceTokenFactory") == mockReportingAttendanceTokenFactory.address

    timestamp = chain.head_state.timestamp
    endTimeValue = timestamp + 10
    numOutcomesValue = 2
    numTicks = 1 * 10**6 * 10**18
    feePerEthInWeiValue = 10 ** 18
    designatedReporterAddressValue = tester.a2
    
    mockUniverse.setReportingPeriodDurationInSeconds(timestamp - 10)
    reportingWindow1 = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'reportingWindow1')
    assert reportingWindow1.initialize(mockUniverse.address, 1)
    with raises(TransactionFailed, message="start time is less than current block time"):
        newMarket = reportingWindow1.createMarket(endTimeValue, numOutcomesValue, numTicks, feePerEthInWeiValue, cash.address, designatedReporterAddressValue)

    mockUniverse.setReportingPeriodDurationInSeconds(timestamp)
    reportingWindow2 = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'reportingWindow2')
    assert reportingWindow2.initialize(mockUniverse.address, 2)
    mockUniverse.setReportingWindowByMarketEndTime(tester.a0)
    with raises(TransactionFailed, message="reporting window not associated with universe"):
        newMarket = reportingWindow2.createMarket(endTimeValue, numOutcomesValue, numTicks, feePerEthInWeiValue, cash.address, designatedReporterAddressValue)

    mockUniverse.setReportingPeriodDurationInSeconds(timestamp - 1)
    mockUniverse.setDesignatedReportNoShowBond(10)
    mockUniverse.setReputationToken(mockReputationToken.address)
    reportingWindow3 = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'reportingWindow3')
    assert reportingWindow3.initialize(mockUniverse.address, 2)
    mockUniverse.setReportingWindowByMarketEndTime(reportingWindow3.address)
    newMarket = reportingWindow3.createMarket(endTimeValue, numOutcomesValue, numTicks, feePerEthInWeiValue, cash.address, designatedReporterAddressValue)

    assert newMarket == mockMarket
    assert mockMarketFactory.getCreateMarketReportingWindowValue() == reportingWindow
    assert mockMarketFactory.getCreateMarketEndTimeValue() == endTimeValue
    assert mockMarketFactory.getCreateMarketNumOutcomesValue() == numOutcomesValue
    assert mockMarketFactory.getCreateMarketNumTicksValue() == numTicks
    assert mockMarketFactory.getCreateMarketfeePerEthInWeiValue() == feePerEthInWeiValue
    assert mockMarketFactory.getCreateMarketDenominationTokenValue() == cash
    assert mockMarketFactory.getCreateMarketCreatorValue() == tester.a0
    assert mockMarketFactory.getCreateMarketDesignatedReporterAddressValue() == designatedReporterAddressValue
    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a0)
    assert mockReputationToken.getTrustedTransferDestinationValue() == mockMarketFactory.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == 10


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    controller = fixture.contracts['Controller']
    fixture.uploadAndAddToController('solidity_test_helpers/MockMarket.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockUniverse.sol')
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