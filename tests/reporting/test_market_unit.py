
from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed

def test_market_creation(localFixture, mockUniverse, mockReportingWindow, mockCash, chain, constants, mockMarket, mockReputationToken, mockShareToken, mockShareTokenFactory):
    numTicks = 10 ** 10
    fee = 1
    oneEther = 10 ** 18
    endTime = chain.head_state.timestamp + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    market = localFixture.upload('../source/contracts/reporting/Market.sol', 'market')
    market.setController(localFixture.contracts["Controller"].address)
    with raises(TransactionFailed, message="outcomes has to be greater than 1"):
        market.initialize(mockReportingWindow.address, endTime, 1, numTicks, fee, mockCash.address, tester.a1, tester.a1)

    with raises(TransactionFailed, message="outcomes has to be less than 9"):
        market.initialize(mockReportingWindow.address, endTime, 9, numTicks, fee, mockCash.address, tester.a1, tester.a1)

    with raises(TransactionFailed, message="numTicks needs to be divisable by outcomes"):
        market.initialize(mockReportingWindow.address, endTime, 7, numTicks, fee, mockCash.address, tester.a1, tester.a1)

    with raises(TransactionFailed, message="fee per eth can not be greater than max fee per eth in attoEth"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, tester.a1, tester.a1)

    with raises(TransactionFailed, message="creator address can not be 0"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, longToHexString(0), tester.a1)

    with raises(TransactionFailed, message="designated reporter address can not be 0"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, tester.a1, longToHexString(0))

    mockUniverse.setForkingMarket(mockMarket.address)
    mockReportingWindow.setUniverse(mockUniverse.address)
    with raises(TransactionFailed, message="forking market address has to be 0"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, tester.a1, tester.a1)

    mockUniverse.setForkingMarket(longToHexString(0))
    mockReputationToken.setBalanceOf(0)
    mockUniverse.setDesignatedReportNoShowBond(100)
    mockReportingWindow.setReputationToken(mockReputationToken.address)
    with raises(TransactionFailed, message="reporting window reputation token does not have enough balance"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, tester.a1, tester.a1)
    
    mockReputationToken.setBalanceOf(100)
    mockUniverse.setTargetReporterGasCosts(15)
    mockUniverse.setValidityBond(12)
    with raises(TransactionFailed, message="refund is not over 0"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, tester.a1, tester.a1, value=0)

    assert market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 16, mockCash.address, tester.a1, tester.a2, value=100)
    assert mockShareTokenFactory.getCreateShareTokenMarketValue() == market.address
    assert mockShareTokenFactory.getCreateShareTokenOutcomeValue() == 5 - 1 # mock logs the last outcome
    assert market.getTypeName() == stringToBytes("Market")
    assert market.getUniverse() == mockUniverse.address
    assert market.getReportingWindow() == mockReportingWindow.address
    assert market.getDesignatedReporter() == bytesToHexString(tester.a2)
    assert market.getNumberOfOutcomes() == 5
    assert market.getEndTime() == endTime
    assert market.getNumTicks() == numTicks
    assert market.getDenominationToken() == mockCash.address
    assert market.getMarketCreatorSettlementFeeDivisor() == oneEther / 16
    
def test_market_decrease_market_creator_settlement_fee(localFixture, initializeMarket, mockMarket):
    oneEther = 10 ** 18

    with raises(TransactionFailed, message="method needs to be called from onlyOwner"):
        initializeMarket.decreaseMarketCreatorSettlementFeeInAttoethPerEth(55, sender=tester.k4)

    with raises(TransactionFailed, message="new fee divisor needs to be greater than fee divisor"):
        initializeMarket.decreaseMarketCreatorSettlementFeeInAttoethPerEth(55, sender=tester.k1)

    assert initializeMarket.getMarketCreatorSettlementFeeDivisor() == oneEther / 16
    assert initializeMarket.decreaseMarketCreatorSettlementFeeInAttoethPerEth(15, sender=tester.k1)
    assert initializeMarket.getMarketCreatorSettlementFeeDivisor() == oneEther / 15


@fixture(scope="session")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockReportingParticipationTokenFactory = fixture.contracts['MockParticipationTokenFactory']
    mockCash = fixture.contracts['MockCash']
    mockShareTokenFactory = fixture.contracts['MockShareTokenFactory']
    mockShareToken = fixture.contracts['MockShareToken']
    mockFillOrder = fixture.contracts['MockFillOrder']
    mockShareTokenFactory.setCreateShareToken(mockShareToken.address)
    mockMapFactory = fixture.contracts['MockMapFactory']
    controller.setValue(stringToBytes('MapFactory'), mockMapFactory.address)
    controller.setValue(stringToBytes('Cash'), mockCash.address)
    controller.setValue(stringToBytes('ParticipationTokenFactory'), mockReportingParticipationTokenFactory.address)
    controller.setValue(stringToBytes('ShareTokenFactory'), mockShareTokenFactory.address)
    controller.setValue(stringToBytes('FillOrder'), mockShareTokenFactory.address)    
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def mockUniverse(localFixture):
    return localFixture.contracts['MockUniverse']

@fixture
def mockReportingWindow(localFixture):
    return localFixture.contracts['MockReportingWindow']

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
def mockReputationToken(localFixture):
    return localFixture.contracts['MockReputationToken']

@fixture
def mockShareToken(localFixture):
    return localFixture.contracts['MockShareToken']

@fixture
def mockShareTokenFactory(localFixture):
    return localFixture.contracts['MockShareTokenFactory']

@fixture
def initializeMarket(localFixture, mockReportingWindow, mockUniverse, mockReputationToken, chain, constants, mockCash):
    market = localFixture.upload('../source/contracts/reporting/Market.sol', 'market')
    numTicks = 10 ** 10
    fee = 1
    endTime = chain.head_state.timestamp + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    market.setController(localFixture.contracts["Controller"].address)

    mockUniverse.setForkingMarket(longToHexString(0))
    mockUniverse.setDesignatedReportNoShowBond(100)
    mockReportingWindow.setReputationToken(mockReputationToken.address)
    mockReputationToken.setBalanceOf(100)
    mockUniverse.setTargetReporterGasCosts(15)
    mockUniverse.setValidityBond(12)
    mockReportingWindow.setUniverse(mockUniverse.address)
    assert market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 16, mockCash.address, tester.a1, tester.a2, value=100)
    return market