from ethereum.tools import tester
from utils import longToHexString, stringToBytes, bytesToHexString, twentyZeros, thirtyTwoZeros, longTo32Bytes
from pytest import fixture, raises
from ethereum.tools.tester import TransactionFailed

numTicks = 10 ** 10
def test_market_creation(localFixture, mockUniverse, mockFeeWindow, mockCash, chain, constants, mockMarket, mockReputationToken, mockShareToken, mockShareTokenFactory):
    fee = 16
    oneEther = 10 ** 18
    endTime = localFixture.contracts["Time"].getTimestamp() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    market = localFixture.upload('../source/contracts/reporting/Market.sol', 'newMarket')
    market.setController(localFixture.contracts["Controller"].address)

    with raises(TransactionFailed, message="outcomes has to be greater than 1"):
        market.initialize(mockUniverse.address, endTime, fee, mockCash.address, tester.a1, tester.a1, 1, numTicks)

    with raises(TransactionFailed, message="outcomes has to be less than 9"):
        market.initialize(mockUniverse.address, endTime, fee, mockCash.address, tester.a1, tester.a1, 9, numTicks)

    with raises(TransactionFailed, message="numTicks needs to be divisable by outcomes"):
        market.initialize(mockUniverse.address, endTime, fee, mockCash.address, tester.a1, tester.a1, 7, numTicks)

    with raises(TransactionFailed, message="fee per eth can not be greater than max fee per eth in attoEth"):
        market.initialize(mockUniverse.address, endTime, oneEther / 2 + 1, mockCash.address, tester.a1, tester.a1, 5, numTicks)

    with raises(TransactionFailed, message="creator address can not be 0"):
        market.initialize(mockUniverse.address, endTime, fee, mockCash.address, longToHexString(0), tester.a1, 5, numTicks)

    with raises(TransactionFailed, message="designated reporter address can not be 0"):
        market.initialize(mockUniverse.address, endTime, fee, mockCash.address, tester.a1, longToHexString(0), 5, numTicks)

    mockUniverse.setForkingMarket(mockMarket.address)
    with raises(TransactionFailed, message="forking market address has to be 0"):
        market.initialize(mockUniverse.address, endTime, fee, mockCash.address, tester.a1, tester.a1, 5, numTicks)

    mockUniverse.setForkingMarket(longToHexString(0))
    mockReputationToken.setBalanceOf(0)
    mockUniverse.setOrCacheDesignatedReportNoShowBond(100)
    with raises(TransactionFailed, message="reporting window reputation token does not have enough balance"):
        market.initialize(mockUniverse.address, endTime, fee, mockCash.address, tester.a1, tester.a1, 5, numTicks)

    badCash = localFixture.upload('../source/contracts/trading/Cash.sol', 'uncontrolledCash')
    with raises(TransactionFailed, message="the denomination token must be a valid cash implementation"):
        market.initialize(mockUniverse.address, endTime, fee, badCash.address, tester.a1, tester.a1, 5, numTicks, value=100)

    mockReputationToken.setBalanceOf(100)
    mockUniverse.setOrCacheTargetReporterGasCosts(15)
    mockUniverse.setOrCacheValidityBond(12)
    with raises(TransactionFailed, message="refund is not over 0"):
        market.initialize(mockUniverse.address, endTime, fee, mockCash.address, tester.a1, tester.a1, 5, numTicks, value=0)

    mockShareTokenFactory.resetCreateShareToken()
    assert market.initialize(mockUniverse.address, endTime, fee, mockCash.address, tester.a1, tester.a1, 5, numTicks, value=100)
    assert mockShareTokenFactory.getCreateShareTokenMarketValue() == market.address
    assert mockShareTokenFactory.getCreateShareTokenOutcomeValue() == 5 - 1 # mock logs the last outcome
    assert market.getTypeName() == stringToBytes("Market")
    assert market.getUniverse() == mockUniverse.address
    assert market.getUniverse() == mockUniverse.address
    assert market.getDesignatedReporter() == bytesToHexString(tester.a1)
    assert market.getNumberOfOutcomes() == 5
    assert market.getEndTime() == endTime
    assert market.getNumTicks() == numTicks
    assert market.getDenominationToken() == mockCash.address
    assert market.getMarketCreatorSettlementFeeDivisor() == oneEther / 16
    assert mockShareTokenFactory.getCreateShareTokenCounter() == 5
    assert mockShareTokenFactory.getCreateShareToken(0) == market.getShareToken(0)
    assert mockShareTokenFactory.getCreateShareToken(1) == market.getShareToken(1)
    assert mockShareTokenFactory.getCreateShareToken(2) == market.getShareToken(2)
    assert mockShareTokenFactory.getCreateShareToken(3) == market.getShareToken(3)
    assert mockShareTokenFactory.getCreateShareToken(4) == market.getShareToken(4)
    assert mockUniverse.getOrCacheTargetReporterGasCostsWasCalled() == True
    assert mockUniverse.getOrCacheValidityBondWallCalled() == True

def test_initial_report(localFixture, initializedMarket, mockReputationToken, mockUniverse, mockInitialReporter):
    # We can't do the initial report till the market has ended
    with raises(TransactionFailed, message="initial report allowed before market end time"):
        initializedMarket.doInitialReport([initializedMarket.getNumTicks(), 0, 0, 0, 0], False, sender=tester.k1)

    localFixture.contracts["Time"].setTimestamp(initializedMarket.getEndTime() + 1)

    # Only the designated reporter can report at this time
    with raises(TransactionFailed, message="only the designated reporter can report at this time"):
        assert initializedMarket.doInitialReport([initializedMarket.getNumTicks(), 0, 0, 0, 0], False)
    repBalance = 10 ** 4
    initBond = 10 ** 8
    mockUniverse.setOrCacheDesignatedReportStake(initBond)
    mockReputationToken.setBalanceOf(repBalance)
    assert initializedMarket.doInitialReport([initializedMarket.getNumTicks(), 0, 0, 0, 0], False, sender=tester.k1)
    # verify creator gets back rep bond
    assert mockReputationToken.getTransferValueFor(tester.a2) == repBalance
    # verify init reporter pays init rep bond
    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a1)
    assert mockReputationToken.getTrustedTransferAttotokensValue() == initBond
    initialReporter = localFixture.applySignature("InitialReporter", initializedMarket.getInitialReporter())
    assert mockReputationToken.getTrustedTransferDestinationValue() == initialReporter.address
    assert mockInitialReporter.reportWasCalled() == True

def test_contribute(localFixture, initializedMarket, mockNextFeeWindow, mockInitialReporter, mockDisputeCrowdsourcer, mockDisputeCrowdsourcerFactory):
    # We can't contribute until there is an initial report to dispute
    with raises(TransactionFailed, message="can't contribute until there is an initial report to dispute"):
        initializedMarket.contribute([0, 0, 0, 0, initializedMarket.getNumTicks()], False, 1)

    localFixture.contracts["Time"].setTimestamp(initializedMarket.getEndTime() + 1)

    assert initializedMarket.doInitialReport([initializedMarket.getNumTicks(), 0, 0, 0, 0], False, sender=tester.k1)

    # We can't contribute till the window begins
    with raises(TransactionFailed, message="can't contribute until the window begins"):
        initializedMarket.contribute([0, 0, 0, 0, initializedMarket.getNumTicks()], False, 1)

    mockNextFeeWindow.setIsActive(True)
    winningPayoutHash = initializedMarket.derivePayoutDistributionHash([initializedMarket.getNumTicks(), 0, 0, 0, 0], False)
    mockInitialReporter.setPayoutDistributionHash(winningPayoutHash)

    # We can't contribute to the current winning outcome
    with raises(TransactionFailed, message="can't contribute to current winning outcome"):
        initializedMarket.contribute([initializedMarket.getNumTicks(), 0, 0, 0, 0], False, 1)

    assert initializedMarket.contribute([0, 0, 0, 0, initializedMarket.getNumTicks()], False, 1)
    assert mockDisputeCrowdsourcer.contributeWasCalled() == True
    assert mockDisputeCrowdsourcer.getContributeParticipant() == bytesToHexString(tester.a0)
    assert mockDisputeCrowdsourcer.getContributeAmount() == 1


def test_market_finish_crowdsourcing_dispute_bond_fork(localFixture, initializedMarket, mockDisputeCrowdsourcer, mockNextFeeWindow, mockUniverse):
    localFixture.contracts["Time"].setTimestamp(initializedMarket.getEndTime() + 1)
    assert initializedMarket.doInitialReport([initializedMarket.getNumTicks(), 0, 0, 0, 0], False, sender=tester.k1)
    mockNextFeeWindow.setIsActive(True)

    mockUniverse.setDisputeThresholdForFork(200)
    mockDisputeCrowdsourcer.setTotalSupply(1)
    mockDisputeCrowdsourcer.setSize(200)

    assert initializedMarket.contribute([0, 0, 0, 0, initializedMarket.getNumTicks()], False, 1)

    assert mockUniverse.getForkCalled() == False

    mockDisputeCrowdsourcer.setTotalSupply(200)

    assert initializedMarket.contribute([0, 0, 0, 0, initializedMarket.getNumTicks()], False, 1)

    assert mockUniverse.getForkCalled() == True

    assert mockUniverse.getOrCreateNextFeeWindowWasCalled() == True

def test_market_finalize_fork(localFixture, initializedMarket, mockUniverse):
    with raises(TransactionFailed, message="current market needs to be forking market"):
        initializedMarket.finalizeFork()

    mockUniverse.setForkingMarket(initializedMarket.address)
    winningUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'winningUniverse')
    mockUniverse.setWinningChildUniverse(winningUniverse.address)
    winningUniverse.setParentPayoutDistributionHash(stringToBytes("111"))

    assert initializedMarket.finalizeFork() == True
    assert initializedMarket.getWinningPayoutDistributionHash() == stringToBytes("111")

def test_migrate_through_one_fork(localFixture, initializedMarket, mockUniverse):
    with raises(TransactionFailed, message="universe forking market needs to be finialized"):
        initializedMarket.migrateThroughOneFork()

    forkingMarket = localFixture.upload('solidity_test_helpers/MockMarket.sol', 'forkingMarket')
    winningUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'winningUniverse')
    mockUniverse.setForkingMarket(forkingMarket.address)
    mockUniverse.setChildUniverse(winningUniverse.address)

    initializedMarket.migrateThroughOneFork()
    assert initializedMarket.getUniverse() == winningUniverse.address
    assert winningUniverse.addMarketToWasCalled() == True
    assert mockUniverse.removeMarketFromWasCalled() == True


def test_finalize(localFixture, chain, initializedMarket, mockInitialReporter, mockNextFeeWindow, mockUniverse):
    with raises(TransactionFailed, message="can't finalize without an initial report"):
        initializedMarket.finalize()

    localFixture.contracts["Time"].setTimestamp(initializedMarket.getEndTime() + 1)
    assert initializedMarket.doInitialReport([initializedMarket.getNumTicks(), 0, 0, 0, 0], False, sender=tester.k1)
    mockInitialReporter.setReportTimestamp(1)

    with raises(TransactionFailed, message="can't finalize before the fee window is over"):
        initializedMarket.finalize()

    mockNextFeeWindow.setIsOver(True)

    mockUniverse.setForkingMarket(longToHexString(1))

    with raises(TransactionFailed, message="can't finalize if there is a forking market"):
        initializedMarket.finalize()

    mockUniverse.setForkingMarket(longToHexString(0))

    mockInitialReporter.setPayoutDistributionHash(longTo32Bytes(2))

    assert initializedMarket.finalize()
    # since market is not the forking market tentative winning hash will be the winner
    assert initializedMarket.getWinningPayoutDistributionHash() == longTo32Bytes(2)

def test_approve_spenders(localFixture, initializedMarket, mockCash, mockShareTokenFactory):
    approvalAmount = 2**256-1
    # approveSpender was called as part of market initialization
    initializedMarket.approveSpenders()
    cancelOrder = localFixture.contracts['CancelOrder']
    assert mockCash.getApproveValueFor(cancelOrder.address) == approvalAmount
    CompleteSets = localFixture.contracts['CompleteSets']
    assert mockCash.getApproveValueFor(CompleteSets.address) == approvalAmount
    TradingEscapeHatch = localFixture.contracts['TradingEscapeHatch']
    assert mockCash.getApproveValueFor(TradingEscapeHatch.address) == approvalAmount
    ClaimTradingProceeds = localFixture.contracts['ClaimTradingProceeds']
    assert mockCash.getApproveValueFor(ClaimTradingProceeds.address) == approvalAmount

    FillOrder = localFixture.contracts['FillOrder']
    assert mockCash.getApproveValueFor(FillOrder.address) == approvalAmount

    # verify all shared tokens have approved amount for fill order contract
    # this market only has 5 outcomes
    for index in range(5):
        shareToken = localFixture.applySignature('MockShareToken', mockShareTokenFactory.getCreateShareToken(index));
        assert shareToken.getApproveValueFor(FillOrder.address) == approvalAmount

@fixture(scope="module")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockCash = fixture.contracts['MockCash']
    mockAugur = fixture.contracts['MockAugur']
    mockInitialReporter = fixture.contracts['MockInitialReporter']
    mockDisputeCrowdsourcer = fixture.contracts['MockDisputeCrowdsourcer']
    mockShareTokenFactory = fixture.contracts['MockShareTokenFactory']
    mockInitialReporterFactory = fixture.contracts['MockInitialReporterFactory']
    mockDisputeCrowdsourcerFactory = fixture.contracts['MockDisputeCrowdsourcerFactory']
    mockShareToken = fixture.contracts['MockShareToken']

    # pre populate share tokens for max of 8 possible outcomes
    for index in range(8):
        item = fixture.uploadAndAddToController('solidity_test_helpers/MockShareToken.sol', 'newMockShareToken' + str(index));
        mockShareTokenFactory.pushCreateShareToken(item.address)

    controller.registerContract(stringToBytes('Cash'), mockCash.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('ShareTokenFactory'), mockShareTokenFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('InitialReporterFactory'), mockInitialReporterFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('DisputeCrowdsourcerFactory'), mockDisputeCrowdsourcerFactory.address, twentyZeros, thirtyTwoZeros)
    mockShareTokenFactory.resetCreateShareToken()

    mockReputationToken = fixture.contracts['MockReputationToken']
    mockUniverse = fixture.contracts['MockUniverse']
    mockUniverse.setReputationToken(mockReputationToken.address)

    mockFeeWindow = fixture.contracts['MockFeeWindow']
    mockFeeWindow.setReputationToken(mockReputationToken.address)
    mockFeeWindow.setUniverse(mockUniverse.address)

    mockNextFeeWindow = fixture.upload('solidity_test_helpers/MockFeeWindow.sol', 'mockNextFeeWindow')
    mockNextFeeWindow.setReputationToken(mockReputationToken.address)
    mockNextFeeWindow.setUniverse(mockUniverse.address)

    mockInitialReporterFactory.setInitialReporter(mockInitialReporter.address)
    mockDisputeCrowdsourcerFactory.setDisputeCrowdsourcer(mockDisputeCrowdsourcer.address)

    constants = fixture.contracts['Constants']

    market = fixture.upload('../source/contracts/reporting/Market.sol', 'market')
    fixture.contracts["initializedMarket"] = market
    contractMap = fixture.upload('../source/contracts/libraries/collections/Map.sol', 'Map')
    endTime = fixture.contracts["Time"].getTimestamp() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    market.setController(fixture.contracts["Controller"].address)

    mockUniverse.setForkingMarket(longToHexString(0))
    mockUniverse.setOrCacheDesignatedReportNoShowBond(100)
    mockReputationToken.setBalanceOf(100)
    mockUniverse.setOrCacheTargetReporterGasCosts(15)
    mockUniverse.setOrCacheValidityBond(12)
    mockUniverse.setNextFeeWindow(mockNextFeeWindow.address)
    mockFeeWindow.setEndTime(fixture.contracts["Time"].getTimestamp() + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    mockNextFeeWindow.setEndTime(mockFeeWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    assert market.initialize(mockUniverse.address, endTime, 16, mockCash.address, tester.a1, tester.a2, 5, numTicks, value=100)

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def mockUniverse(localFixture):
    return localFixture.contracts['MockUniverse']

@fixture
def mockFeeWindow(localFixture):
    return localFixture.contracts['MockFeeWindow']

@fixture
def mockNextFeeWindow(localFixture):
    return localFixture.contracts['mockNextFeeWindow']

@fixture
def constants(localFixture):
    return localFixture.contracts['Constants']

@fixture
def mockCash(localFixture):
    return localFixture.contracts['MockCash']

@fixture
def chain(localFixture):
    return localFixture.chain

@fixture
def mockMarket(localFixture):
    return localFixture.contracts['MockMarket']

@fixture
def mockAugur(localFixture):
    return localFixture.contracts['MockAugur']

@fixture
def mockReputationToken(localFixture):
    return localFixture.contracts['MockReputationToken']

@fixture
def mockShareToken(localFixture):
    return localFixture.contracts['MockShareToken']

@fixture
def mockShareTokenFactory(localFixture):
    return localFixture.contracts['MockShareTokenFactory']

@fixture
def mockInitialReporter(localFixture):
    return localFixture.contracts['MockInitialReporter']

@fixture
def initializedMarket(localFixture):
    return localFixture.contracts["initializedMarket"]

@fixture
def mockDisputeCrowdsourcer(localFixture):
    return localFixture.contracts["MockDisputeCrowdsourcer"]

@fixture
def mockDisputeCrowdsourcerFactory(localFixture):
    return localFixture.contracts["MockDisputeCrowdsourcerFactory"]
