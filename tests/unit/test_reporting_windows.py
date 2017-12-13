from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString, twentyZeros, thirtyTwoZeros
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed


def test_reporting_window_initialize(localFixture, chain, mockUniverse, mockFeeWindow, mockReputationToken):
    timestamp = localFixture.contracts["Time"].getTimestamp()
    duration_in_sec = localFixture.contracts['Constants'].REPORTING_DURATION_SECONDS() + localFixture.contracts['Constants'].DESIGNATED_REPORTING_DURATION_SECONDS()
    mockUniverse.setReportingPeriodDurationInSeconds(duration_in_sec)
    mockUniverse.setReputationToken(mockReputationToken.address)

    mockReportingFeeWindowFactory = localFixture.contracts['MockFeeWindowFactory']
    mockReportingFeeWindowFactory.setFeeWindowValue(mockFeeWindow.address)

    feeWindow = localFixture.upload('../source/contracts/reporting/FeeWindow.sol', 'newFeeWindow')
    feeWindow.setController(localFixture.contracts['Controller'].address)

    start_time = timestamp * mockUniverse.getDisputeRoundDurationInSeconds()
    assert feeWindow.initialize(mockUniverse.address, timestamp)
    assert feeWindow.getUniverse() == mockUniverse.address
    assert feeWindow.getReputationToken() == mockReputationToken.address
    assert feeWindow.getTypeName() == stringToBytes("FeeWindow")
    assert feeWindow.getStartTime() == start_time
    assert feeWindow.getAvgReportingGasPrice() == localFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()
    assert feeWindow.getFeeWindow() == mockFeeWindow.address
    assert feeWindow.getReportingStartTime() ==    start_time
    reporting_end = start_time + localFixture.contracts['Constants'].REPORTING_DURATION_SECONDS()
    assert feeWindow.getReportingEndTime() == reporting_end
    assert feeWindow.getDisputeStartTime() == reporting_end
    dispute_end_time = reporting_end + localFixture.contracts['Constants'].REPORTING_DISPUTE_DURATION_SECONDS()
    assert feeWindow.getDisputeEndTime() == dispute_end_time
    assert feeWindow.getEndTime() == dispute_end_time
    assert feeWindow.isOver() == False

    nextFeeWindow = localFixture.upload('../source/contracts/reporting/FeeWindow.sol', 'nextFeeWindow')
    mockUniverse.setFeeWindowByTimestamp(nextFeeWindow.address)
    assert feeWindow.getOrCreateNextFeeWindow() == nextFeeWindow.address

    previousFeeWindow = localFixture.upload('../source/contracts/reporting/FeeWindow.sol', 'previousFeeWindow')
    mockUniverse.setFeeWindowByTimestamp(previousFeeWindow.address)
    assert feeWindow.getOrCreatePreviousFeeWindow() == previousFeeWindow.address

    time = localFixture.contracts["Time"]

    time.setTimestamp(feeWindow.getStartTime() - 1)
    assert feeWindow.isOver() == False
    assert feeWindow.isActive() == False
    assert feeWindow.isReportingActive() == False
    assert feeWindow.isDisputeActive() == False

    time.setTimestamp(feeWindow.getStartTime())
    assert feeWindow.isActive() == False
    assert feeWindow.isReportingActive() == False
    assert feeWindow.isDisputeActive() == False

    time.setTimestamp(feeWindow.getStartTime() + 1)
    assert feeWindow.isActive() == True
    assert feeWindow.isReportingActive() == True
    assert feeWindow.isDisputeActive() == False

    time.setTimestamp(feeWindow.getReportingEndTime())
    assert feeWindow.isActive() == True
    assert feeWindow.isReportingActive() == False
    assert feeWindow.isDisputeActive() == False

    time.setTimestamp(feeWindow.getReportingEndTime() + 1)
    assert feeWindow.isActive() == True
    assert feeWindow.isReportingActive() == False
    assert feeWindow.isDisputeActive() == True

    time.setTimestamp(feeWindow.getDisputeStartTime())
    assert feeWindow.isActive() == True
    assert feeWindow.isReportingActive() == False
    assert feeWindow.isDisputeActive() == False
    assert feeWindow.isOver() == False

    time.setTimestamp(feeWindow.getDisputeStartTime() + 1)
    assert feeWindow.isActive() == True
    assert feeWindow.isReportingActive() == False
    assert feeWindow.isDisputeActive() == True
    assert feeWindow.isOver() == False

    time.setTimestamp(feeWindow.getEndTime())
    assert feeWindow.isActive() == False
    assert feeWindow.isReportingActive() == False
    assert feeWindow.isDisputeActive() == False
    assert feeWindow.isOver() == True

    time.setTimestamp(feeWindow.getEndTime() + 1)
    assert feeWindow.isActive() == False
    assert feeWindow.isReportingActive() == False
    assert feeWindow.isDisputeActive() == False
    assert feeWindow.isOver() == True

def test_reporting_window_migrate_market_in_from_N_sib(localFixture, mockUniverse, populatedFeeWindow):
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')
    with raises(TransactionFailed, message="method has to be called from Market"):
        populatedFeeWindow.migrateMarketInFromNibling()

    newMockMarket.setFeeWindow(populatedFeeWindow.address)
    newMockMarket.setUniverse(mockUniverse.address)
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')
    mockUniverse.setParentUniverse(parentUniverse.address)
    with raises(TransactionFailed, message="market's universe is not the fee window universe's parent"):
        newMockMarket.callFeeWindowMigrateMarketInFromSibling(populatedFeeWindow.address)

    newMockMarket.setUniverse(parentUniverse.address)
    newWindow = localFixture.upload('solidity_test_helpers/MockFeeWindow.sol', 'newWindow')
    newMockMarket.setFeeWindow(newWindow.address)
    parentUniverse.setIsContainerForFeeWindow(False)
    with raises(TransactionFailed, message="parent universe doesn't contain migrating market's fee window"):
        newMockMarket.callFeeWindowMigrateMarketInFromSibling(populatedFeeWindow.address)

    parentUniverse.setIsContainerForFeeWindow(True)
    newWindow.setIsContainerForMarket(False)
    with raises(TransactionFailed, message="market's fee window doesn't contain migrating market"):
        newMockMarket.callFeeWindowMigrateMarketInFromSibling(populatedFeeWindow.address)

    assert populatedFeeWindow.isContainerForMarket(newMockMarket.address) == False
    newWindow.setIsContainerForMarket(True)
    newMockMarket.callFeeWindowMigrateMarketInFromSibling(populatedFeeWindow.address)
    assert populatedFeeWindow.isContainerForMarket(newMockMarket.address)

def test_reporting_window_remove_market(localFixture, mockUniverse, mockMarket, populatedFeeWindow):
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')
    with raises(TransactionFailed, message="method has to be called from Market"):
        populatedFeeWindow.removeMarket()

    with raises(TransactionFailed, message="market has to be in internal market collection"):
        newMockMarket.callFeeWindowRemoveMarket()

    assert populatedFeeWindow.getFirstReporterMarketsCount() == 1
    assert populatedFeeWindow.getLastReporterMarketsCount() == 0

    # migrate new market to test removing from round 1 market collection
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')
    parentUniverse.setIsContainerForFeeWindow(True)
    newMockMarket.setUniverse(parentUniverse.address)
    newWindow = localFixture.upload('solidity_test_helpers/MockFeeWindow.sol', 'newWindow')
    newWindow.setIsContainerForMarket(True)
    newMockMarket.setFeeWindow(newWindow.address)
    newMockMarket.setUniverse(mockUniverse.address)
    newMockMarket.setReportingState(localFixture.contracts['Constants'].FIRST_REPORTING())
    newMockMarket.callFeeWindowMigrateMarketInFromSibling(populatedFeeWindow.address)
    assert newMockMarket.callFeeWindowUpdateMarketPhase(populatedFeeWindow.address)
    assert populatedFeeWindow.isContainerForMarket(newMockMarket.address)
    assert populatedFeeWindow.isContainerForMarket(mockMarket.address)

    assert populatedFeeWindow.getFirstReporterMarketsCount() == 2
    assert populatedFeeWindow.getLastReporterMarketsCount() == 0

    # update mockMarket to round 2 reporting
    mockMarket.setReportingState(localFixture.contracts['Constants'].LAST_REPORTING())
    assert mockMarket.callFeeWindowUpdateMarketPhase(populatedFeeWindow.address)
    assert populatedFeeWindow.getFirstReporterMarketsCount() == 1
    assert populatedFeeWindow.getLastReporterMarketsCount() == 1

    # remove new market from round 2
    assert newMockMarket.callFeeWindowRemoveMarket(populatedFeeWindow.address)
    # remove market from round 1
    assert mockMarket.callFeeWindowRemoveMarket(populatedFeeWindow.address)

    assert populatedFeeWindow.getLastReporterMarketsCount() == 0
    assert populatedFeeWindow.getFirstReporterMarketsCount() == 0
    assert populatedFeeWindow.isContainerForMarket(mockMarket.address) == False
    assert populatedFeeWindow.isContainerForMarket(newMockMarket.address) == False

def test_reporting_window_update_market_phase(localFixture, mockUniverse, mockMarket, populatedFeeWindow):

    with raises(TransactionFailed, message="method has to be called from Market"):
        populatedFeeWindow.updateMarketPhase()

    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')
    with raises(TransactionFailed, message="market has to be in internal market collection"):
        newMockMarket.callFeeWindowRemoveMarket()

    # mock market is in round 1 by default
    assert populatedFeeWindow.isContainerForMarket(mockMarket.address)
    assert populatedFeeWindow.getFirstReporterMarketsCount() == 1
    assert populatedFeeWindow.getLastReporterMarketsCount() == 0

    # reomve existing market from round 1 and round 2
    mockMarket.setReportingState(localFixture.contracts['Constants'].DESIGNATED_REPORTING())
    assert mockMarket.callFeeWindowUpdateMarketPhase(populatedFeeWindow.address)
    assert populatedFeeWindow.isContainerForMarket(mockMarket.address)
    assert populatedFeeWindow.getFirstReporterMarketsCount() == 0
    assert populatedFeeWindow.getLastReporterMarketsCount() == 0

    mockMarket.setReportingState(localFixture.contracts['Constants'].FIRST_REPORTING())
    assert mockMarket.callFeeWindowUpdateMarketPhase(populatedFeeWindow.address)
    assert populatedFeeWindow.getFirstReporterMarketsCount() == 1
    assert populatedFeeWindow.getLastReporterMarketsCount() == 0

    mockMarket.setReportingState(localFixture.contracts['Constants'].LAST_REPORTING())
    assert mockMarket.callFeeWindowUpdateMarketPhase(populatedFeeWindow.address)
    assert populatedFeeWindow.getFirstReporterMarketsCount() == 0
    assert populatedFeeWindow.getLastReporterMarketsCount() == 1
    assert populatedFeeWindow.allMarketsFinalized() == False

    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED())
    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockStakeToken.setTotalSupply(100)
    mockMarket.setFinalWinningStakeToken(mockStakeToken.address)
    mockMarket.setIsValid(True)
    assert mockMarket.callFeeWindowUpdateMarketPhase(populatedFeeWindow.address)
    assert populatedFeeWindow.getFirstReporterMarketsCount() == 0
    assert populatedFeeWindow.getLastReporterMarketsCount() == 0
    assert populatedFeeWindow.isContainerForMarket(mockMarket.address)
    assert populatedFeeWindow.allMarketsFinalized()
    assert populatedFeeWindow.getNumInvalidMarkets() == 0

def test_reporting_window_update_note_reporting_gas_price(localFixture, mockUniverse, mockMarket, populatedFeeWindow):
    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockMarket.setIsContainerForStakeToken(False)
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')

    with raises(TransactionFailed, message="method has to be called from Stake Token"):
        populatedFeeWindow.noteReportingGasPrice(mockMarket.address)

    with raises(TransactionFailed, message="market has to be in internal market collection"):
        mockStakeToken.callNoteReportingGasPrice(newMockMarket.address, populatedFeeWindow.address)

    mockMarket.setIsContainerForStakeToken(False)
    with raises(TransactionFailed, message="market has to contain Stake Token"):
        mockStakeToken.callNoteReportingGasPrice(mockMarket.address, populatedFeeWindow.address)

    assert populatedFeeWindow.getAvgReportingGasPrice() == localFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()
    mockMarket.setIsContainerForStakeToken(True)
    gasPrice = 7
    avgGas = (gasPrice + localFixture.contracts['Constants'].DEFAULT_REPORTING_GAS_PRICE()) / 2
    assert mockStakeToken.callNoteReportingGasPrice(mockMarket.address, populatedFeeWindow.address, gasprice=gasPrice)
    assert populatedFeeWindow.getAvgReportingGasPrice() == avgGas

def test_reporting_window_invalid_markets(localFixture, mockMarket, populatedFeeWindow):
    assert populatedFeeWindow.getNumInvalidMarkets() == 0
    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED())
    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockStakeToken.setTotalSupply(100)
    mockMarket.setFinalWinningStakeToken(mockStakeToken.address)
    mockMarket.setIsValid(False)
    assert mockMarket.callFeeWindowUpdateMarketPhase(populatedFeeWindow.address)
    assert populatedFeeWindow.getNumInvalidMarkets() == 1

    with raises(TransactionFailed, message="market has already been finialized"):
        mockMarket.callFeeWindowUpdateMarketPhase(populatedFeeWindow.address)

def test_reporting_window_update_fin_market_calculations(localFixture, mockMarket, populatedFeeWindow):
    mockMarket.setFinalPayoutDistributionHash(stringToBytes("101"))
    mockMarket.setDesignatedReportPayoutHash(stringToBytes("10"))
    mockMarket.setIsValid(True)
    finializeMarket(localFixture, mockMarket, populatedFeeWindow, 99, 15)
    # 99 + 15
    assert populatedFeeWindow.getTotalWinningStake() == 114
    assert populatedFeeWindow.getNumIncorrectDesignatedReportMarkets() == 1

    # add new market to finialize
    parentUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'parentUniverse')
    parentUniverse.setIsContainerForFeeWindow(True)
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')
    newMockMarket.setUniverse(parentUniverse.address)
    newWindow = localFixture.upload('solidity_test_helpers/MockFeeWindow.sol', 'newWindow')
    newWindow.setIsContainerForMarket(True)
    newMockMarket.setFinalPayoutDistributionHash(stringToBytes("101"))
    newMockMarket.setDesignatedReportPayoutHash(stringToBytes("10"))
    newMockMarket.setFeeWindow(newWindow.address)
    assert newMockMarket.callFeeWindowMigrateMarketInFromSibling(populatedFeeWindow.address)
    finializeMarket(localFixture, newMockMarket, populatedFeeWindow, 19, 12)
    # 19 + 12 + existing 114  = 114 + 31 = 145
    assert populatedFeeWindow.getTotalWinningStake() == 145
    assert populatedFeeWindow.getNumIncorrectDesignatedReportMarkets() == 2

def test_reporting_window_collect_reporting_fees(localFixture, chain, mockMarket, populatedFeeWindow, mockFeeWindow, mockCash):
    timestamp = localFixture.contracts["Time"].getTimestamp()
    start_time = 2 * timestamp
    reporting_end = start_time + localFixture.contracts['Constants'].REPORTING_DURATION_SECONDS()
    dispute_end_time = reporting_end + localFixture.contracts['Constants'].REPORTING_DISPUTE_DURATION_SECONDS()

    with raises(TransactionFailed, message="method has to be called from Stake Token"):
        populatedFeeWindow.collectStakeTokenReportingFees(tester.a0, 1, False)

    with raises(TransactionFailed, message="method has to be called from Dispute Bond"):
        populatedFeeWindow.collectDisputeBondReportingFees(tester.a0, 1, False)

    with raises(TransactionFailed, message="method has to be called from Participation token"):
        populatedFeeWindow.collectFeeWindowReportingFees(tester.a0, 1, False)

    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockMarket.setIsContainerForStakeToken(True)
    mockStakeToken.setMarket(mockMarket.address)
    reporterAddress = tester.a1
    attoStake = 2
    forgoFees = False
    feeWindow = populatedFeeWindow

    assert feeWindow.allMarketsFinalized() == False
    assert feeWindow.isOver() == False
    # stake calling and fee window not over
    with raises(TransactionFailed, message="can not forgo fees and fee window not finished or markets not finalized"):
        mockStakeToken.callCollectReportingFees(reporterAddress, attoStake, forgoFees, feeWindow.address)

    localFixture.contracts["Time"].setTimestamp(dispute_end_time + 1)
    assert feeWindow.isOver()
    assert feeWindow.allMarketsFinalized() == False
    with raises(TransactionFailed, message="can not forgo fees and all markets not finalized"):
        mockStakeToken.callCollectReportingFees(reporterAddress, attoStake, forgoFees, feeWindow.address)

    mockMarket.setFinalPayoutDistributionHash(stringToBytes("101"))
    mockMarket.setDesignatedReportPayoutHash(stringToBytes("10"))
    mockMarket.callIncreaseTotalStake(feeWindow.address, 1000)
    mockCash.setBalanceOf(134)
    feeWindow.getFeeWindow() == mockFeeWindow.address
    mockFeeWindow.callIncreaseTotalWinningStake(feeWindow.address, 100)

    assert feeWindow.getTotalWinningStake() == 100
    assert feeWindow.getTotalStake() == 1100
    assert mockCash.getwithdrawEthertoAmountValue() == 0

    mockStakeToken.callCollectReportingFees(reporterAddress, 20, True, feeWindow.address)

    assert feeWindow.getTotalWinningStake() == 100 - 20
    assert feeWindow.getTotalStake() == 1100 - 20
    # no fees transfered
    assert mockCash.getwithdrawEthertoAmountValue() == 0

    mockCash.resetWithdrawEtherToValues()
    finializeMarket(localFixture, mockMarket, feeWindow, 77, 23)
    assert feeWindow.allMarketsFinalized()

    with raises(TransactionFailed, message="can not forgo fees and all markets finalized and fee window end time"):
        mockStakeToken.callCollectReportingFees(reporterAddress, attoStake, True, feeWindow.address)

    assert feeWindow.getTotalWinningStake() == 80 + 100
    assert feeWindow.getTotalStake() == 1080
    assert mockCash.getwithdrawEthertoAmountValue() == 0

    mockStakeToken.callCollectReportingFees(reporterAddress, 5, False, feeWindow.address)

    assert feeWindow.getTotalWinningStake() == 100 + 80 - 5
    assert feeWindow.getTotalStake() == 1000 + 80 - 5
    # attoStake fees transfered to reporter address
    assert mockCash.getwithdrawEtherToAddressValue() == bytesToHexString(reporterAddress)
    # cash balance 134 * 5 / total winnings 175
    assert mockCash.getwithdrawEthertoAmountValue() == 3

def test_reporting_window_containers_stake_token(localFixture, mockMarket, populatedFeeWindow):
    newMockStakeToken = localFixture.upload('solidity_test_helpers/MockStakeToken.sol', 'newMockStakeToken')
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')

    newMockStakeToken.setMarket(newMockMarket.address)
    with raises(TransactionFailed, message="stake token not associated with this fee window market collection"):
        populatedFeeWindow.isContainerForStakeToken(newMockStakeToken.address)

    newMockStakeToken.setMarket(mockMarket.address)
    mockMarket.setIsContainerForStakeToken(False)

    assert populatedFeeWindow.isContainerForStakeToken(newMockStakeToken.address) == False

    mockMarket.setIsContainerForStakeToken(True)
    assert populatedFeeWindow.isContainerForStakeToken(newMockStakeToken.address)

def test_reporting_window_containers_dispute_token_market_participation(localFixture, mockMarket, populatedFeeWindow, mockFeeWindow):
    newMockDisputeToken = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'newMockDisputeToken')
    newMockMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'newMockMarket')

    newMockDisputeToken.setMarket(newMockMarket.address)
    with raises(TransactionFailed, message="dispute token not associated with this fee window market collection"):
        populatedFeeWindow.isContainerForDisputeBond(newMockDisputeToken.address)

    newMockDisputeToken.setMarket(mockMarket.address)
    mockMarket.setIsContainerForDisputeBond(False)

    assert populatedFeeWindow.isContainerForDisputeBond(newMockDisputeToken.address) == False

    mockMarket.setIsContainerForDisputeBond(True)
    assert populatedFeeWindow.isContainerForDisputeBond(newMockDisputeToken.address)

    assert populatedFeeWindow.isContainerForMarket(newMockMarket.address) == False
    assert populatedFeeWindow.isContainerForMarket(mockMarket.address)

    newFeeWindow = localFixture.upload('solidity_test_helpers/MockFeeWindow.sol', 'newFeeWindow')
    assert populatedFeeWindow.isContainerForFeeWindow(newFeeWindow.address) == False
    assert populatedFeeWindow.isContainerForFeeWindow(mockFeeWindow.address)

def finializeMarket(localFixture, mockMarket, feeWindow, totalSupply, disputeBondStake):
    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED())
    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockMarket.setFinalWinningStakeToken(mockStakeToken.address)
    mockStakeToken.setTotalSupply(totalSupply)
    mockMarket.setTotalWinningDisputeBondStake(disputeBondStake)
    mockMarket.setIsValid(True)
    assert mockMarket.callFeeWindowUpdateMarketPhase(feeWindow.address)

@fixture(scope="module")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockReportingFeeWindowFactory = fixture.contracts['MockFeeWindowFactory']
    mockCash = fixture.contracts['MockCash']
    mockMarketFactory = fixture.contracts['MockMarketFactory']
    controller.registerContract(stringToBytes('MarketFactory'), mockMarketFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('Cash'), mockCash.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('FeeWindowFactory'), mockReportingFeeWindowFactory.address, twentyZeros, thirtyTwoZeros)

    mockFeeWindow = fixture.contracts['MockFeeWindow']

    mockUniverse = fixture.contracts['MockUniverse']
    mockUniverse.setIsContainerForFeeWindow(True)
    mockUniverse.setIsContainerForMarket(True)

    mockReputationToken = fixture.contracts['MockReputationToken']
    mockReputationToken.setTrustedTransfer(True)

    mockMarket = fixture.contracts['MockMarket']
    mockMarket.setDesignatedReporter(bytesToHexString(tester.a0))
    mockMarket.setUniverse(mockUniverse.address)
    mockMarket.setIsContainerForStakeToken(True)
    mockMarket.setMigrateDueToNoReports(True)
    mockMarket.setMigrateDueToNoReportsNextState(fixture.contracts['Constants'].FIRST_REPORTING())
    mockMarket.setFirstReporterCompensationCheck(0)
    mockMarket.setDerivePayoutDistributionHash(stringToBytes("1"))
    mockMarket.setTotalWinningDisputeBondStake(100)

    mockMarketFactory.setMarket(mockMarket.address)
    mockReportingFeeWindowFactory.setFeeWindowValue(mockFeeWindow.address)

    timestamp = fixture.contracts["Time"].getTimestamp()
    endTimeValue = timestamp + 10
    numTicks = 1 * 10**6 * 10**18
    feePerEthInWeiValue = 10 ** 18
    designatedReporterAddressValue = tester.a2

    mockUniverse.setReportingPeriodDurationInSeconds(timestamp - 10)
    feeWindow = fixture.upload('../source/contracts/reporting/FeeWindow.sol', 'feeWindow')
    feeWindow.setController(fixture.contracts['Controller'].address)
    fixture.contracts['populatedFeeWindow'] = feeWindow
    mockUniverse.setReportingPeriodDurationInSeconds(timestamp - 1)
    mockUniverse.setDesignatedReportNoShowBond(10)
    mockUniverse.setReputationToken(mockReputationToken.address)
    assert feeWindow.initialize(mockUniverse.address, 2)
    mockUniverse.setFeeWindowByMarketEndTime(feeWindow.address)
    mockUniverse.createBinaryMarket(endTimeValue, feePerEthInWeiValue, mockCash.address, designatedReporterAddressValue, "", "description", "")

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def chain(localFixture):
    return localFixture.chain

@fixture
def mockCash(localFixture):
    return localFixture.contracts['MockCash']

@fixture
def mockUniverse(localFixture):
    return localFixture.contracts['MockUniverse']

@fixture
def mockReputationToken(localFixture):
    return localFixture.contracts['MockReputationToken']

@fixture
def mockFeeWindow(localFixture):
    return localFixture.contracts['MockFeeWindow']

@fixture
def mockDisputeBond(localFixture):
    return localFixture.contracts['MockDisputeBond']

@fixture
def mockAugur(localFixture):
    return localFixture.contracts['MockAugur']

@fixture
def mockMarket(localFixture):
    return localFixture.contracts['MockMarket']

@fixture
def populatedFeeWindow(localFixture):
    return localFixture.contracts['populatedFeeWindow']
