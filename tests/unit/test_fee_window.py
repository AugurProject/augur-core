from ethereum.tools import tester
from utils import longToHexString, stringToBytes, bytesToHexString, twentyZeros, thirtyTwoZeros, longTo32Bytes
from pytest import fixture, raises
from ethereum.tools.tester import TransactionFailed

numTicks = 10 ** 10
feeWindowId = 1467446882

def test_fee_window_creation(localFixture, initializedFeeWindow, mockReputationToken, mockUniverse, constants, mockFeeToken, mockFeeTokenFactory, Time):
    assert initializedFeeWindow.getTypeName() == stringToBytes("FeeWindow")
    assert initializedFeeWindow.getReputationToken() == mockReputationToken.address
    assert initializedFeeWindow.getStartTime() == feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds()
    assert initializedFeeWindow.getUniverse() == mockUniverse.address
    assert initializedFeeWindow.getEndTime() == feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + constants.DISPUTE_ROUND_DURATION_SECONDS()
    assert initializedFeeWindow.getFeeToken() == mockFeeToken.address
    assert initializedFeeWindow.getNumInvalidMarkets() == 0
    assert initializedFeeWindow.getNumIncorrectDesignatedReportMarkets() == 0
    assert initializedFeeWindow.getNumDesignatedReportNoShows() == 0
    assert initializedFeeWindow.isActive() == False
    assert initializedFeeWindow.isOver() == False
    assert mockFeeTokenFactory.getCreateFeeTokenFeeWindowValue() == initializedFeeWindow.address
    Time.setTimestamp(feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + 1)
    assert initializedFeeWindow.isActive() == True
    Time.setTimestamp(feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + constants.DISPUTE_ROUND_DURATION_SECONDS())
    assert initializedFeeWindow.isActive() == False
    assert initializedFeeWindow.isOver() == True

def test_fee_window_note_initial_reporting_gas_price(localFixture, initializedFeeWindow, mockUniverse):
    mockUniverse.setIsContainerForReportingParticipant(False)
    with raises(TransactionFailed, message="reporting participant needs to be in fee windows universe"):
        initializedFeeWindow.noteInitialReportingGasPrice()
    gasPrice = 100000
    mockUniverse.setIsContainerForReportingParticipant(True)
    gasValue = initializedFeeWindow.getAvgReportingGasPrice()

    assert initializedFeeWindow.noteInitialReportingGasPrice(gasprice=gasPrice) == True
    assert initializedFeeWindow.getAvgReportingGasPrice() == (gasPrice + gasValue) / 2

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

def test_fee_window_buy(localFixture, initializedFeeWindow, Time, mockReputationToken, mockUniverse):
    with raises(TransactionFailed, message="atto token needs to be greater than 0"):
        initializedFeeWindow.buy(0)

    attoToken = 10 ** 10
    assert initializedFeeWindow.isActive() == False
    with raises(TransactionFailed, message="fee window needs to be active to buy"):
        initializedFeeWindow.buy(attoToken)

    Time.setTimestamp(feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + 1)
    assert initializedFeeWindow.isActive() == True
    user_balance = initializedFeeWindow.balanceOf(tester.a0)
    assert initializedFeeWindow.buy(attoToken, sender=tester.k0) == True
    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a0)
    assert mockReputationToken.getTrustedTransferDestinationValue() == initializedFeeWindow.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == attoToken
    assert initializedFeeWindow.balanceOf(tester.a0) == user_balance + attoToken

def test_fee_window_redeem_for_reporting_participant_zero(localFixture, initializedFeeWindow, mockUniverse, Time, mockReputationToken, mockFeeToken, constants, mockCash):
    assert initializedFeeWindow.isOver() == False
    mockUniverse.setIsForking(False)
    with raises(TransactionFailed, message="fee window needs to be over or universe needs to be forking"):
        initializedFeeWindow.redeemForReportingParticipant()

    # no tokens purchased and no fee token balance
    mockUniverse.setIsForking(True)
    assert mockFeeToken.getFeeWindowBurnTargetValue() == longToHexString(0)
    assert mockFeeToken.getFeeWindowBurnAmountValue() == 0
    assert initializedFeeWindow.totalSupply() == 0
    mockFeeToken.setTotalSupply(0)
    assert initializedFeeWindow.redeemForReportingParticipant(sender=tester.k0) == True
    assert mockFeeToken.getFeeWindowBurnTargetValue() == longToHexString(0)
    assert mockFeeToken.getFeeWindowBurnAmountValue() == 0
    assert initializedFeeWindow.totalSupply() == 0
    assert mockReputationToken.getTransferValueFor(tester.a0) == 0

def test_fee_window_redeem_for_reporting_participant_with_balance(localFixture, initializedFeeWindow, mockUniverse, Time, mockReputationToken, mockFeeToken, constants, mockCash):
    attoToken = 10 ** 10
    feeTokenBalance = 10 ** 2
    feeWindowBalance = 10 ** 4

    # buy tokens
    Time.setTimestamp(feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + 1)
    assert initializedFeeWindow.isActive() == True
    assert initializedFeeWindow.buy(attoToken, sender=tester.k0) == True
    assert initializedFeeWindow.balanceOf(tester.a0) == attoToken

    # verify fee window fee stake is updated with buy
    assert initializedFeeWindow.getTotalFeeStake() == attoToken
    # set up feeTokens for user
    mockFeeToken.setBalanceOf(feeTokenBalance)
    # set up fee window cash balance
    mockCash.setBalanceOf(feeWindowBalance)

    Time.setTimestamp(feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + constants.DISPUTE_ROUND_DURATION_SECONDS())
    assert initializedFeeWindow.isOver() == True
    assert mockFeeToken.balanceOf(tester.a0) == feeTokenBalance

    assert initializedFeeWindow.redeemForReportingParticipant(sender=tester.k0) == True
    assert mockReputationToken.getTransferValueFor(tester.a0) == attoToken
    # participation tokens should have been burnt
    assert initializedFeeWindow.balanceOf(tester.a0) == 0
    assert mockFeeToken.getFeeWindowBurnTargetValue() == bytesToHexString(tester.a0)
    assert mockFeeToken.getFeeWindowBurnAmountValue() == feeTokenBalance

    assert mockCash.getTransferValueFor(tester.a0) == feeWindowBalance * (attoToken + feeTokenBalance) / attoToken
    assert mockCash.getwithdrawEtherToAddressValue() == longToHexString(0)
    assert mockCash.getwithdrawEthertoAmountValue() == 0


def test_fee_window_redeem_with_balance(localFixture, initializedFeeWindow, mockUniverse, Time, mockReputationToken, mockFeeToken, constants, mockCash):
    attoToken = 10 ** 10
    feeTokenBalance = 10 ** 2
    feeWindowBalance = 10 ** 4

    # buy tokens
    Time.setTimestamp(feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + 1)
    assert initializedFeeWindow.isActive() == True
    assert initializedFeeWindow.buy(attoToken, sender=tester.k1) == True
    assert initializedFeeWindow.balanceOf(tester.a1) == attoToken

    # verify fee window fee stake is updated with buy
    assert initializedFeeWindow.getTotalFeeStake() == attoToken
    # set up feeTokens for user
    mockFeeToken.setBalanceOf(feeTokenBalance)
    # set up fee window cash balance
    mockCash.setBalanceOf(feeWindowBalance)
    assert mockReputationToken.getTransferValueFor(tester.a1) == 0
    Time.setTimestamp(feeWindowId * mockUniverse.getDisputeRoundDurationInSeconds() + constants.DISPUTE_ROUND_DURATION_SECONDS())
    assert initializedFeeWindow.isOver() == True
    assert mockFeeToken.balanceOf(tester.a1) == feeTokenBalance

    assert initializedFeeWindow.redeem(tester.a1) == True
    assert mockReputationToken.getTransferValueFor(tester.a1) == attoToken

    assert initializedFeeWindow.balanceOf(tester.a1) == 0
    assert mockFeeToken.getFeeWindowBurnTargetValue() == bytesToHexString(tester.a1)
    assert mockFeeToken.getFeeWindowBurnAmountValue() == feeTokenBalance

    assert mockCash.getTransferValueFor(tester.a1) == 0

    assert mockCash.getwithdrawEtherToAddressValue() == bytesToHexString(tester.a1)
    assert mockCash.getwithdrawEthertoAmountValue() == feeWindowBalance * (attoToken + feeTokenBalance) / attoToken

def test_fee_window_mint_fee_tokens(localFixture, initializedFeeWindow, mockUniverse, mockFeeToken, mockInitialReporter):
    amount = 10 ** 3

    with raises(TransactionFailed, message="caller needs to be IReporting Participant"):
        initializedFeeWindow.mintFeeTokens(amount)

    mockUniverse.setIsContainerForReportingParticipant(False)
    with raises(TransactionFailed, message="IReporting Participant needs to be in same Universe"):
        mockInitialReporter.callMintFeeTokens(initializedFeeWindow.address, amount)

    mockUniverse.setIsContainerForReportingParticipant(True)
    assert mockInitialReporter.callMintFeeTokens(initializedFeeWindow.address, amount) == True
    assert mockFeeToken.getMintForReportingParticipantTargetValue() == mockInitialReporter.address
    assert mockFeeToken.getMintForReportingParticipantAmountValue() == amount

@fixture(scope="module")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockCash = fixture.contracts['MockCash']
    mockAugur = fixture.contracts['MockAugur']
    mockFeeToken = fixture.contracts['MockFeeToken']
    mockFeeTokenFactory = fixture.contracts['MockFeeTokenFactory']
    mockFeeTokenFactory.setCreateFeeToken(mockFeeToken.address)
    mockReputationToken = fixture.contracts['MockReputationToken']
    controller.registerContract(stringToBytes('Cash'), mockCash.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('Augur'), mockAugur.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('FeeTokenFactory'), mockFeeTokenFactory.address, twentyZeros, thirtyTwoZeros)
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
def mockFeeToken(localFixture):
    return localFixture.contracts['MockFeeToken']

@fixture
def mockFeeTokenFactory(localFixture):
    return localFixture.contracts['MockFeeTokenFactory']

@fixture
def mockInitialReporter(localFixture):
    return localFixture.contracts['MockInitialReporter']

@fixture
def Time(localFixture):
    return localFixture.contracts["Time"]
