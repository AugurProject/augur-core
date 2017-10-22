from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed
from reporting_utils import proceedToDesignatedReporting, proceedToRound1Reporting, proceedToRound2Reporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture


def test_reporting_window_initialize(localFixture, chain, mockUniverse, mockReportingAttendanceToken, mockReputationToken):
    timestamp = chain.head_state.timestamp
    mockUniverse.setReportingPeriodDurationInSeconds(timestamp)
    mockUniverse.setReputationToken(mockReputationToken.address)

    mockReportingAttendanceTokenFactory = localFixture.contracts['MockReportingAttendanceTokenFactory']
    mockReportingAttendanceTokenFactory.setAttendanceTokenValue(mockReportingAttendanceToken.address)

    reportingWindow = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'reportingWindow')
    reportingWindow.setController(localFixture.contracts['Controller'].address)

    start_time = 2 * timestamp
    assert reportingWindow.initialize(mockUniverse.address, 2)
    assert reportingWindow.getUniverse() == mockUniverse.address
    assert reportingWindow.getReputationToken() == mockReputationToken.address
    assert reportingWindow.getTypeName() == stringToBytes("ReportingWindow")
    assert reportingWindow.getStartTime() == start_time     
    assert reportingWindow.getAvgReportingGasPrice() == localFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()
    assert reportingWindow.getReportingAttendanceToken() == mockReportingAttendanceToken.address
    assert reportingWindow.getReportingStartTime() ==    start_time
    reporting_end = start_time + localFixture.contracts['Constants'].REPORTING_DURATION_SECONDS()
    assert reportingWindow.getReportingEndTime() == reporting_end
    assert reportingWindow.getDisputeStartTime() == reporting_end
    dispute_end_time = reporting_end + localFixture.contracts['Constants'].REPORTING_DISPUTE_DURATION_SECONDS()
    assert reportingWindow.getDisputeEndTime() == dispute_end_time
    assert reportingWindow.getEndTime() == dispute_end_time
    assert reportingWindow.isOver() == False

    nextReportingWindow = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'nextReportingWindow')
    mockUniverse.setReportingWindowByTimestamp(nextReportingWindow.address)
    assert reportingWindow.getNextReportingWindow() == nextReportingWindow.address

    previousReportingWindow = localFixture.upload('../source/contracts/reporting/ReportingWindow.sol', 'previousReportingWindow')
    mockUniverse.setReportingWindowByTimestamp(previousReportingWindow.address)
    assert reportingWindow.getPreviousReportingWindow() == previousReportingWindow.address
    chain.head_state.timestamp = dispute_end_time + 1
    assert reportingWindow.isOver()

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

def test_reporting_window_migrate_market_in_from_sib(localFixture, mockUniverse, populatedReportingWindow):
    with raises(TransactionFailed, message="method has be called from Market"):
        populatedReportingWindow.migrateMarketInFromSibling()
    
    newMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMarket')
    mockUniverse.setIsContainerForReportingWindow(False)
    with raises(TransactionFailed, message="market is not in universe"):
        newMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    
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
    assert newMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    assert populatedReportingWindow.isContainerForMarket(newMarket.address)

def test_reporting_window_migrate_market_in_from_N_sib(localFixture, mockUniverse, populatedReportingWindow):
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')
    with raises(TransactionFailed, message="method has to be called from Market"):
        populatedReportingWindow.migrateMarketInFromNibling()

    newMockMarket.setReportingWindow(populatedReportingWindow.address)
    newMockMarket.setUniverse(mockUniverse.address)
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')    
    mockUniverse.setParentUniverse(parentUniverse.address)
    with raises(TransactionFailed, message="market's universe is not the reporting window universe's parent"):
        newMockMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    
    newMockMarket.setUniverse(parentUniverse.address)
    newWindow = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol', 'newWindow')    
    newMockMarket.setReportingWindow(newWindow.address)
    parentUniverse.setIsContainerForReportingWindow(False)
    with raises(TransactionFailed, message="parent universe doesn't contain migrating market's reporting window"):
        newMockMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)

    parentUniverse.setIsContainerForReportingWindow(True)
    newWindow.setIsContainerForMarket(False)
    with raises(TransactionFailed, message="market's reporting window doesn't contain migrating market"):
        newMockMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    
    assert populatedReportingWindow.isContainerForMarket(newMockMarket.address) == False
    newWindow.setIsContainerForMarket(True)
    newMockMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    assert populatedReportingWindow.isContainerForMarket(newMockMarket.address)
    
def test_reporting_window_remove_market(localFixture, mockUniverse, mockMarket, populatedReportingWindow):
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')
    with raises(TransactionFailed, message="method has to be called from Market"):
        populatedReportingWindow.removeMarket()

    with raises(TransactionFailed, message="market has to be in internal market collection"):
        newMockMarket.callReportingWindowRemoveMarket()

    assert populatedReportingWindow.getRound1ReporterMarketsCount() == 1
    assert populatedReportingWindow.getRound2ReporterMarketsCount() == 0

    # migrate new market to test removing from round 1 market collection
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')    
    parentUniverse.setIsContainerForReportingWindow(True)
    newMockMarket.setUniverse(parentUniverse.address)
    newWindow = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol', 'newWindow')    
    newWindow.setIsContainerForMarket(True)
    newMockMarket.setReportingWindow(newWindow.address)
    newMockMarket.setUniverse(mockUniverse.address)
    newMockMarket.setReportingState(localFixture.contracts['Constants'].ROUND1_REPORTING()) 
    newMockMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    assert newMockMarket.callReportingWindowUpdateMarketPhase(populatedReportingWindow.address)
    assert populatedReportingWindow.isContainerForMarket(newMockMarket.address)
    assert populatedReportingWindow.isContainerForMarket(mockMarket.address)

    assert populatedReportingWindow.getRound1ReporterMarketsCount() == 2
    assert populatedReportingWindow.getRound2ReporterMarketsCount() == 0

    # update mockMarket to round 2 reporting
    mockMarket.setReportingState(localFixture.contracts['Constants'].ROUND2_REPORTING()) 
    assert mockMarket.callReportingWindowUpdateMarketPhase(populatedReportingWindow.address)
    assert populatedReportingWindow.getRound1ReporterMarketsCount() == 1
    assert populatedReportingWindow.getRound2ReporterMarketsCount() == 1

    # remove new market from round 2
    assert newMockMarket.callReportingWindowRemoveMarket(populatedReportingWindow.address)    
    # remove market from round 1
    assert mockMarket.callReportingWindowRemoveMarket(populatedReportingWindow.address)
    
    assert populatedReportingWindow.getRound2ReporterMarketsCount() == 0
    assert populatedReportingWindow.getRound1ReporterMarketsCount() == 0    
    assert populatedReportingWindow.isContainerForMarket(mockMarket.address) == False
    assert populatedReportingWindow.isContainerForMarket(newMockMarket.address) == False

def test_reporting_window_update_market_phase(localFixture, mockUniverse, mockMarket, populatedReportingWindow):
    
    with raises(TransactionFailed, message="method has to be called from Market"):
        populatedReportingWindow.updateMarketPhase()

    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')
    with raises(TransactionFailed, message="market has to be in internal market collection"):
        newMockMarket.callReportingWindowRemoveMarket()

    # mock market is in round 1 by default
    assert populatedReportingWindow.isContainerForMarket(mockMarket.address)
    assert populatedReportingWindow.getRound1ReporterMarketsCount() == 1
    assert populatedReportingWindow.getRound2ReporterMarketsCount() == 0

    # reomve existing market from round 1 and round 2
    mockMarket.setReportingState(localFixture.contracts['Constants'].DESIGNATED_REPORTING()) 
    assert mockMarket.callReportingWindowUpdateMarketPhase(populatedReportingWindow.address)
    assert populatedReportingWindow.isContainerForMarket(mockMarket.address)
    assert populatedReportingWindow.getRound1ReporterMarketsCount() == 0
    assert populatedReportingWindow.getRound2ReporterMarketsCount() == 0

    mockMarket.setReportingState(localFixture.contracts['Constants'].ROUND1_REPORTING()) 
    assert mockMarket.callReportingWindowUpdateMarketPhase(populatedReportingWindow.address)
    assert populatedReportingWindow.getRound1ReporterMarketsCount() == 1
    assert populatedReportingWindow.getRound2ReporterMarketsCount() == 0

    mockMarket.setReportingState(localFixture.contracts['Constants'].ROUND2_REPORTING()) 
    assert mockMarket.callReportingWindowUpdateMarketPhase(populatedReportingWindow.address)
    assert populatedReportingWindow.getRound1ReporterMarketsCount() == 0
    assert populatedReportingWindow.getRound2ReporterMarketsCount() == 1
    assert populatedReportingWindow.allMarketsFinalized() == False

    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockStakeToken.setTotalSupply(100)
    mockMarket.setFinalWinningStakeToken(mockStakeToken.address)
    mockMarket.setIsValid(True)
    assert mockMarket.callReportingWindowUpdateMarketPhase(populatedReportingWindow.address)
    assert populatedReportingWindow.getRound1ReporterMarketsCount() == 0
    assert populatedReportingWindow.getRound2ReporterMarketsCount() == 0
    assert populatedReportingWindow.isContainerForMarket(mockMarket.address)
    assert populatedReportingWindow.allMarketsFinalized()
    assert populatedReportingWindow.getNumInvalidMarkets() == 0

def test_reporting_window_update_note_reporting_gas_price(localFixture, mockUniverse, mockMarket, populatedReportingWindow):
    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockMarket.setIsContainerForStakeToken(False)
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')

    with raises(TransactionFailed, message="method has to be called from Stake Token"):
        populatedReportingWindow.noteReportingGasPrice(mockMarket.address)

    with raises(TransactionFailed, message="market has to be in internal market collection"):
        mockStakeToken.callNoteReportingGasPrice(newMockMarket.address, populatedReportingWindow.address)
    
    mockMarket.setIsContainerForStakeToken(False)
    with raises(TransactionFailed, message="market has to contain Stake Token"):
        mockStakeToken.callNoteReportingGasPrice(mockMarket.address, populatedReportingWindow.address)

    assert populatedReportingWindow.getAvgReportingGasPrice() == localFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()
    mockMarket.setIsContainerForStakeToken(True)
    gasPrice = 7
    avgGas = (gasPrice + localFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()) / 2
    assert mockStakeToken.callNoteReportingGasPrice(mockMarket.address, populatedReportingWindow.address, gasprice=gasPrice)
    assert populatedReportingWindow.getAvgReportingGasPrice() == avgGas

def test_reporting_window_invalid_markets(localFixture, mockMarket, populatedReportingWindow):
    assert populatedReportingWindow.getNumInvalidMarkets() == 0
    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockStakeToken.setTotalSupply(100)
    mockMarket.setFinalWinningStakeToken(mockStakeToken.address)
    mockMarket.setIsValid(False)
    assert mockMarket.callReportingWindowUpdateMarketPhase(populatedReportingWindow.address)
    assert populatedReportingWindow.getNumInvalidMarkets() == 1

    with raises(TransactionFailed, message="market has already been finialized"):
        mockMarket.callReportingWindowUpdateMarketPhase(populatedReportingWindow.address)

def test_reporting_window_update_fin_market_calculations(localFixture, mockMarket, populatedReportingWindow):
    mockMarket.setFinalPayoutDistributionHash(stringToBytes("101"))
    mockMarket.setDesignatedReportPayoutHash(stringToBytes("10"))
    mockMarket.setIsValid(True)
    finializMarket(localFixture, mockMarket, populatedReportingWindow, 99, 15)
    # 99 + 15 
    assert populatedReportingWindow.getTotalWinningStake() == 114
    assert populatedReportingWindow.getNumIncorrectDesignatedReportMarkets() == 1

    # add new market to finialize 
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')    
    parentUniverse.setIsContainerForReportingWindow(True)
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')
    newMockMarket.setUniverse(parentUniverse.address)
    newWindow = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol', 'newWindow')    
    newWindow.setIsContainerForMarket(True)
    newMockMarket.setFinalPayoutDistributionHash(stringToBytes("101"))
    newMockMarket.setDesignatedReportPayoutHash(stringToBytes("10"))
    newMockMarket.setReportingWindow(newWindow.address)
    assert newMockMarket.callReportingWindowMigrateMarketInFromSibling(populatedReportingWindow.address)
    finializMarket(localFixture, newMockMarket, populatedReportingWindow, 19, 12)
    # 19 + 12 + existing 114  = 114 + 31 = 145
    assert populatedReportingWindow.getTotalWinningStake() == 145
    assert populatedReportingWindow.getNumIncorrectDesignatedReportMarkets() == 2

def test_reporting_window_collect_reporting_fees(localFixture, chain, mockMarket, populatedReportingWindow, mockReportingAttendanceToken, mockCash):
    timestamp = chain.head_state.timestamp
    start_time = 2 * timestamp
    reporting_end = start_time + localFixture.contracts['Constants'].REPORTING_DURATION_SECONDS()
    dispute_end_time = reporting_end + localFixture.contracts['Constants'].REPORTING_DISPUTE_DURATION_SECONDS()

    with raises(TransactionFailed, message="method has to be called from Stake Token or Dispute Bond or reporting attendance token"):
        populatedReportingWindow.collectReportingFees(tester.a0, 1, False)

    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockMarket.setIsContainerForStakeToken(True)
    mockStakeToken.setMarket(mockMarket.address)
    reporterAddress = tester.a1
    attoStake = 2
    forgoFees = False
    reportingWindow = populatedReportingWindow

    assert reportingWindow.allMarketsFinalized() == False
    assert reportingWindow.isOver() == False
    # stake calling and reporting window not over
    with raises(TransactionFailed, message="can not forgo fees and reporting window not finished or markets not finalized"):
        mockStakeToken.callCollectReportingFees(reporterAddress, attoStake, forgoFees, reportingWindow.address)

    chain.head_state.timestamp = dispute_end_time + 1
    assert reportingWindow.isOver()
    assert reportingWindow.allMarketsFinalized() == False
    with raises(TransactionFailed, message="can not forgo fees and all markets not finalized"):
        mockStakeToken.callCollectReportingFees(reporterAddress, attoStake, forgoFees, reportingWindow.address)

    mockMarket.setFinalPayoutDistributionHash(stringToBytes("101"))
    mockMarket.setDesignatedReportPayoutHash(stringToBytes("10"))
    mockMarket.callIncreaseTotalStake(reportingWindow.address, 1000)
    mockCash.setBalanceOf(134)
    reportingWindow.getReportingAttendanceToken() == mockReportingAttendanceToken.address
    mockReportingAttendanceToken.callIncreaseTotalWinningStake(reportingWindow.address, 100)

    assert reportingWindow.getTotalWinningStake() == 100
    assert reportingWindow.getTotalStake() == 1100
    assert mockCash.getwithdrawEthertoAmountValue() == 0

    mockStakeToken.callCollectReportingFees(reporterAddress, 20, True, reportingWindow.address)

    assert reportingWindow.getTotalWinningStake() == 100 - 20
    assert reportingWindow.getTotalStake() == 1100 - 20
    # no fees transfered
    assert mockCash.getwithdrawEthertoAmountValue() == 0

    mockCash.resetWithdrawEtherToValues()
    finializMarket(localFixture, mockMarket, reportingWindow, 77, 23)
    assert reportingWindow.allMarketsFinalized()

    with raises(TransactionFailed, message="can not forgo fees and all markets finalized and reporting window end time"):
        mockStakeToken.callCollectReportingFees(reporterAddress, attoStake, True, reportingWindow.address)

    assert reportingWindow.getTotalWinningStake() == 80 + 100
    assert reportingWindow.getTotalStake() == 1080
    assert mockCash.getwithdrawEthertoAmountValue() == 0

    mockStakeToken.callCollectReportingFees(reporterAddress, 5, False, reportingWindow.address)

    assert reportingWindow.getTotalWinningStake() == 100 + 80 - 5
    assert reportingWindow.getTotalStake() == 1000 + 80 - 5
    # attoStake fees transfered to reporter address
    assert mockCash.getwithdrawEtherToAddressValue() == bytesToHexString(reporterAddress)
    # cash balance 134 * 5 / total winnings 175
    assert mockCash.getwithdrawEthertoAmountValue() == 3
    
def finializMarket(localFixture, mockMarket, reportingWindow, totalSupply, disputeBondStake):
    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockMarket.setFinalWinningStakeToken(mockStakeToken.address)
    mockStakeToken.setTotalSupply(totalSupply)
    mockMarket.setTotalWinningDisputeBondStake(disputeBondStake)
    mockMarket.setIsValid(True)
    assert mockMarket.callReportingWindowUpdateMarketPhase(reportingWindow.address)

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    controller = fixture.contracts['Controller']
    fixture.uploadAndAddToController('solidity_test_helpers/MockStakeToken.sol', 'MockStakeToken')
    fixture.uploadAndAddToController('solidity_test_helpers/MockMarket.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockUniverse.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockReportingWindow.sol')    
    fixture.uploadAndAddToController('solidity_test_helpers/MockReputationToken.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockDisputeBondToken.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockReportingAttendanceToken.sol')
    mockReportingAttendanceTokenFactory = fixture.upload('solidity_test_helpers/MockReportingAttendanceTokenFactory.sol')
    mockCash = fixture.upload('solidity_test_helpers/MockCash.sol')
    mockMarketFactory = fixture.upload('solidity_test_helpers/MockMarketFactory.sol')
    controller.setValue(stringToBytes('MarketFactory'), mockMarketFactory.address)
    controller.setValue(stringToBytes('Cash'), mockCash.address)
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
def mockCash(localFixture):
    mockCash = localFixture.contracts['MockCash']
    return mockCash;

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
    mockMarket.setTotalWinningDisputeBondStake(100)
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