
from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString, twentyZeros, thirtyTwoZeros
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
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, oneEther / 2 + 1, mockCash.address, tester.a1, tester.a1)

    with raises(TransactionFailed, message="creator address can not be 0"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, longToHexString(0), tester.a1)

    with raises(TransactionFailed, message="designated reporter address can not be 0"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, tester.a1, longToHexString(0))

    mockUniverse.setForkingMarket(mockMarket.address)
    with raises(TransactionFailed, message="forking market address has to be 0"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, tester.a1, tester.a1)

    mockUniverse.setForkingMarket(longToHexString(0))
    mockReputationToken.setBalanceOf(0)
    mockUniverse.setDesignatedReportNoShowBond(100)
    with raises(TransactionFailed, message="reporting window reputation token does not have enough balance"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, tester.a1, tester.a1)
    
    mockReputationToken.setBalanceOf(100)
    mockUniverse.setTargetReporterGasCosts(15)
    mockUniverse.setValidityBond(12)
    with raises(TransactionFailed, message="refund is not over 0"):
        market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 5, mockCash.address, tester.a1, tester.a1, value=0)

    mockShareTokenFactory.resetCreateShareToken();
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
    assert mockShareTokenFactory.getCreateShareTokenCounter() == 5;
    assert mockShareTokenFactory.getCreateShareToken(0) == market.getShareToken(0)
    assert mockShareTokenFactory.getCreateShareToken(1) == market.getShareToken(1)
    assert mockShareTokenFactory.getCreateShareToken(2) == market.getShareToken(2)
    assert mockShareTokenFactory.getCreateShareToken(3) == market.getShareToken(3)
    assert mockShareTokenFactory.getCreateShareToken(4) == market.getShareToken(4)
    
def test_market_decrease_market_creator_settlement_fee(localFixture, initializeMarket, mockMarket):
    oneEther = 10 ** 18

    with raises(TransactionFailed, message="method needs to be called from onlyOwner"):
        initializeMarket.decreaseMarketCreatorSettlementFeeInAttoethPerEth(55, sender=tester.k4)

    with raises(TransactionFailed, message="new fee divisor needs to be greater than fee divisor"):
        initializeMarket.decreaseMarketCreatorSettlementFeeInAttoethPerEth(55, sender=tester.k1)

    assert initializeMarket.getMarketCreatorSettlementFeeDivisor() == oneEther / 16
    assert initializeMarket.decreaseMarketCreatorSettlementFeeInAttoethPerEth(15, sender=tester.k1)
    assert initializeMarket.getMarketCreatorSettlementFeeDivisor() == oneEther / 15

def test_market_designated_report(localFixture, constants, mockUniverse, chain, initializeMarket, mockStakeToken, mockStakeTokenFactory, mockReportingWindow, mockReputationToken):
    with raises(TransactionFailed, message="market is not in designated reporting state"):
        initializeMarket.designatedReport()
    
    chain.head_state.timestamp = initializeMarket.getDesignatedReportDueTimestamp() - 1
    with raises(TransactionFailed, message="designated report method needs to be called from StakeToken"):
        initializeMarket.designatedReport()

    with raises(TransactionFailed, message="StakeToken needs to be contained by market"):
        mockStakeToken.callMarketDesignatedReport(initializeMarket.address)
    
    numTicks = 10 ** 10
    payoutDesignatedNumerators = [numTicks, 0, 0, 0, 0]
    push_to_designated_despute_state(localFixture, mockUniverse, chain, initializeMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)

def test_market_dispute_report_with_attoeth(localFixture, constants, initializeMarket, chain, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockStakeToken, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, mockAugur):
    numTicks = 10 ** 10
    payoutDesignatedNumerators = [numTicks, 0, 0, 0, 0]
    payoutSecondNumeratorsDispute = [0, numTicks, 0, 0, 0]
    payoutDesignatedHashValue = initializeMarket.derivePayoutDistributionHash(payoutSecondNumeratorsDispute, False)
    
    with raises(TransactionFailed, message="market needs to be in DESIGNATED_DISPUTE state"):
        initializeMarket.disputeDesignatedReport(payoutDesignatedNumerators, 100, False)
    
    push_to_designated_despute_state(localFixture, mockUniverse, chain, initializeMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    mockReportingWindow.reset()
    mockDisputeBondFactory.setCreateDisputeBond(mockDisputeBond.address)

    disputeStakeToken = set_mock_stake_token_value(localFixture, initializeMarket, payoutSecondNumeratorsDispute, mockStakeTokenFactory, 0)

    bondAmount = constants.DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
    stakeAmount = initializeMarket.getTotalStake()
    beforeAmount = initializeMarket.getExtraDisputeBondRemainingToBePaidOut()
    tentWinningHash = initializeMarket.getTentativeWinningPayoutDistributionHash()
    assert initializeMarket.getReportingState() == constants.DESIGNATED_DISPUTE()    

    with raises(TransactionFailed, message="tentative winning payout distro can not be 0 for stake token"):
        initializeMarket.disputeDesignatedReport(payoutSecondNumeratorsDispute, 0, False, sender=tester.k2)

    # execute disputeDesignatedReport on market
    assert initializeMarket.disputeDesignatedReport(payoutSecondNumeratorsDispute, 100, False, sender=tester.k2)
    assert mockReportingWindow.getUpdateMarketPhaseCalled() == True
    assert mockReportingWindow.getIncreaseTotalStakeCalled() == True
    assert mockAugur.logReportsDisputedCalled() == True

    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a2)
    assert mockReputationToken.getTrustedTransferDestinationValue() == mockDisputeBond.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == bondAmount

    assert initializeMarket.getExtraDisputeBondRemainingToBePaidOut() == beforeAmount + bondAmount
    assert initializeMarket.getTotalStake() == stakeAmount + bondAmount
    assert initializeMarket.getDesignatedReporterDisputeBond() == mockDisputeBond.address

    assert mockDisputeBondFactory.getCreateDisputeBondMarket() == initializeMarket.address
    assert mockDisputeBondFactory.getCreateDisputeBondBondHolder() == bytesToHexString(tester.a2)
    assert mockDisputeBondFactory.getCreateDisputeBondAmountValue() == bondAmount
    assert mockDisputeBondFactory.getCreateDisputeBondPayoutDistributionHash() == tentWinningHash

    assert disputeStakeToken.getTrustedBuyAddressValue() == bytesToHexString(tester.a2)
    assert disputeStakeToken.getTrustedBuyAttoTokensValue() == 100


def test_market_dispute_report_with_no_attoeth(localFixture, constants, initializeMarket, chain, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockStakeToken, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, mockAugur):
    numTicks = 10 ** 10
    payoutDesignatedNumerators = [numTicks, 0, 0, 0, 0]
    payoutdNumeratorsDispute = [0, numTicks, 0, 0, 0]
    payoutFirstDisputeNumeratorsDispute = [0, 0, numTicks, 0, 0]
    with raises(TransactionFailed, message="market needs to be in DESIGNATED_DISPUTE state"):
        initializeMarket.disputeDesignatedReport(payoutDesignatedNumerators, 100, False)
    
    payoutDesignatedHash = initializeMarket.derivePayoutDistributionHash(payoutDesignatedNumerators, False)
    payoutFirstDisputeHash = initializeMarket.derivePayoutDistributionHash(payoutFirstDisputeNumeratorsDispute, False)

    push_to_designated_despute_state(localFixture, mockUniverse, chain, initializeMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHash
    assert initializeMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == stringToBytes("")
    # set value for original designated report so that calcuations for tent. winning token doesn't blow up
    mockStakeToken.setTotalSupply(105)
    mockDisputeStakeToken = set_mock_stake_token_value(localFixture, initializeMarket, payoutdNumeratorsDispute, mockStakeTokenFactory, 100)

    assert initializeMarket.getReportingState() == constants.DESIGNATED_DISPUTE()
    mockDisputeBondFactory.setCreateDisputeBond(mockDisputeBond.address)
    # execute disputeDesignatedReport on market
    assert initializeMarket.disputeDesignatedReport(payoutdNumeratorsDispute, 0, False, sender=tester.k2)
    # execution path is same as with attoeth except no stake token transfer
    assert mockDisputeStakeToken.getTrustedBuyAddressValue() == longToHexString(0)
    assert mockDisputeStakeToken.getTrustedBuyAttoTokensValue() == 0

    bondAmount = constants.FIRST_REPORTERS_DISPUTE_BOND_AMOUNT()
    stakeAmount = initializeMarket.getTotalStake()
    beforeAmount = initializeMarket.getExtraDisputeBondRemainingToBePaidOut()

    # might as well test first dispute
    mockReportingWindow.setEndTime(chain.head_state.timestamp + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    chain.head_state.timestamp = initializeMarket.getDesignatedReportDisputeDueTimestamp() - 1

    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHash
    assert initializeMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == stringToBytes("")

    mockFirstDisputeStakeToken = set_mock_stake_token_value(localFixture, initializeMarket, payoutFirstDisputeNumeratorsDispute, mockStakeTokenFactory, 10)
    mockReportingWindow.setIsDisputeActive(True)
    assert initializeMarket.getReportingState() == constants.FIRST_DISPUTE()

    mockFirstDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockFirstDisputeBond');
    mockDisputeBondFactory.setCreateDisputeBond(mockFirstDisputeBond.address)
    endTime = mockReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockNextReportingWindow = set_mock_reporting_window(localFixture, initializeMarket, mockUniverse, mockReputationToken, endTime)
    mockUniverse.setNextReportingWindow(mockNextReportingWindow.address)

    # execute disputeFirstReporters on market
    assert initializeMarket.disputeFirstReporters(payoutFirstDisputeNumeratorsDispute, 14, False, sender=tester.k3)

    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a3)
    assert mockReputationToken.getTrustedTransferDestinationValue() == mockFirstDisputeBond.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == bondAmount
    
    assert mockNextReportingWindow.getMigrateMarketInFromSiblingCalled() == True
    assert mockReportingWindow.getIncreaseTotalStakeCalled() == True
    assert mockReportingWindow.getRemoveMarketCalled() == True
    assert mockReportingWindow.getUpdateMarketPhaseCalled() == True

    assert initializeMarket.getFirstReportersDisputeBond() == mockFirstDisputeBond.address
 
    assert mockFirstDisputeStakeToken.getTrustedBuyAddressValue() == bytesToHexString(tester.a3)
    assert mockFirstDisputeStakeToken.getTrustedBuyAttoTokensValue() == 14
    payoutFirstDisputeHashDisputeValue = payoutFirstDisputeHash
    # verify that best guess second place is updated correctly
    assert mockFirstDisputeStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializeMarket.address, payoutFirstDisputeHashDisputeValue)
    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHash
    assert initializeMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutFirstDisputeHash

def test_market_update_tentative_winning_payout(localFixture, constants, initializeMarket, chain, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockStakeToken, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, mockAugur):
    numTicks = 10 ** 10
    payoutDesignatedNumerators = [numTicks, 0, 0, 0, 0]
    payoutSecondNumeratorsDispute = [0, numTicks, 0, 0, 0]
    payoutThirdNumerators = [0, 0, numTicks, 0, 0]
    payoutFourthNumerators = [0, 0, 0, numTicks, 0]

    payoutDesignatedHashValue = initializeMarket.derivePayoutDistributionHash(payoutDesignatedNumerators, False)
    payoutSecondHashDisputeValue = initializeMarket.derivePayoutDistributionHash(payoutSecondNumeratorsDispute, False)
    payoutThirdHashValue = initializeMarket.derivePayoutDistributionHash(payoutThirdNumerators, False)
    payoutFourthHashValue = initializeMarket.derivePayoutDistributionHash(payoutFourthNumerators, False)

    push_to_designated_despute_state(localFixture, mockUniverse, chain, initializeMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHashValue
    
    mockReportingWindow.reset()
    # get second token
    mockSecondStakeToken = set_mock_stake_token_value(localFixture, initializeMarket, payoutSecondNumeratorsDispute, mockStakeTokenFactory, 0)
    
    # verify stake tokens are set
    assert initializeMarket.getStakeToken(payoutDesignatedNumerators, False) == mockStakeToken.address
    assert initializeMarket.getStakeToken(payoutSecondNumeratorsDispute, False) == mockSecondStakeToken.address

    with raises(TransactionFailed, message="tentative winning payout distro can not be 0 we need stake token with positive supply"):
        mockSecondStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializeMarket.address, payoutSecondHashDisputeValue)
    
    mockStakeToken.setTotalSupply(105)
    mockSecondStakeToken.setTotalSupply(20)
    assert initializeMarket.getTotalStake() == 0
    assert mockSecondStakeToken.callIncreaseTotalStake(initializeMarket.address, 20)
    assert initializeMarket.getTotalStake() == 20
    assert mockReportingWindow.getIncreaseTotalStakeCalled() == True

    assert mockSecondStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializeMarket.address, payoutSecondHashDisputeValue)
    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHashValue
    assert initializeMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutSecondHashDisputeValue
    # buy a third stake token
    mockThirdStakeToken = set_mock_stake_token_value(localFixture, initializeMarket, payoutThirdNumerators, mockStakeTokenFactory, 200)

    # verify stake tokens have correct value
    assert initializeMarket.getPayoutDistributionHashStake(payoutDesignatedHashValue) == 105
    assert initializeMarket.getPayoutDistributionHashStake(payoutSecondHashDisputeValue) == 20
    assert initializeMarket.getPayoutDistributionHashStake(payoutThirdHashValue) == 200

    assert mockThirdStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializeMarket.address, payoutThirdHashValue)
    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == payoutThirdHashValue
    assert initializeMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutDesignatedHashValue
    # bump up existing stake token supply
    mockSecondStakeToken.setTotalSupply(500)
    
    assert mockSecondStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializeMarket.address, payoutSecondHashDisputeValue)
    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == payoutSecondHashDisputeValue
    assert initializeMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutThirdHashValue

    # stake token to rule them all
    mockFourthStakeToken = set_mock_stake_token_value(localFixture, initializeMarket, payoutFourthNumerators, mockStakeTokenFactory, 800)

    assert mockFourthStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializeMarket.address, payoutFourthHashValue)
    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == payoutFourthHashValue
    assert initializeMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutSecondHashDisputeValue
    
    mockFourthStakeToken.setTotalSupply(0)    
    assert mockFourthStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializeMarket.address, payoutFourthHashValue)
    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == payoutSecondHashDisputeValue
    assert initializeMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == stringToBytes("")

    mockSecondStakeToken.setTotalSupply(0)
    with raises(TransactionFailed, message="can not withdraw stake token supply it leaves no tentative winning payout"):
        mockSecondStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializeMarket.address, payoutSecondHashDisputeValue)

def test_market_get_payout_distr_hash_stake(localFixture, initializeMarket, mockStakeTokenFactory):
    numTicks = 10 ** 10
    mockStakeToken_1 = set_mock_stake_token_value(localFixture, initializeMarket, [numTicks, 0, 0, 0, 0], mockStakeTokenFactory, 80)
    assert initializeMarket.getPayoutDistributionHashStake(mockStakeToken_1.getPayoutDistributionHash()) == 80

    mockStakeToken_2 = set_mock_stake_token_value(localFixture, initializeMarket, [0, numTicks, 0, 0, 0], mockStakeTokenFactory, 30)
    assert initializeMarket.getPayoutDistributionHashStake(mockStakeToken_2.getPayoutDistributionHash()) == 30

    mockStakeToken_3 = set_mock_stake_token_value(localFixture, initializeMarket, [0, 0, numTicks, 0, 0], mockStakeTokenFactory, 100)
    assert initializeMarket.getPayoutDistributionHashStake(mockStakeToken_3.getPayoutDistributionHash()) == 100

def test_market_dispute_last_reporter(localFixture, initializeMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow):
    numTicks = 10 ** 10

    push_to_designated_despute_state(localFixture, mockUniverse, chain, initializeMarket, mockStakeToken, [0,numTicks,0,0,0], mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)

    push_first_dispute_last_reporting(localFixture, chain, mockReputationToken, initializeMarket, mockStakeTokenFactory, mockReportingWindow, mockUniverse, constants, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow)
    
    with raises(TransactionFailed, message="market needs to be in last dispute state"):
        initializeMarket.disputeLastReporters()
    
    chain.head_state.timestamp = mockNextReportingWindow.getEndTime() - 1

    mockLastDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockLastDisputeBond');   
    mockDisputeBondFactory.setCreateDisputeBond(mockLastDisputeBond.address)
    bondAmount = constants.LAST_REPORTERS_DISPUTE_BOND_AMOUNT()
    extraPaidOut = initializeMarket.getExtraDisputeBondRemainingToBePaidOut()
    totalStake = initializeMarket.getTotalStake()
    # set up new reputation tokan for reporting window
    mockReputationToken.reset()
    mockNextReportingWindow.setIsDisputeActive(True)
    endTime = mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockForkReportingWindow = set_mock_reporting_window(localFixture, initializeMarket, mockUniverse, mockReputationToken, endTime)
    mockUniverse.setReportingWindowForForkEndTime(mockForkReportingWindow.address)

    assert initializeMarket.getReportingState() == constants.LAST_DISPUTE()
    assert initializeMarket.getReportingWindow() == mockNextReportingWindow.address

    assert initializeMarket.disputeLastReporters(sender=tester.k0)

    assert mockDisputeBondFactory.getCreateDisputeBondMarket() == initializeMarket.address
    assert mockDisputeBondFactory.getCreateDisputeBondBondHolder() == bytesToHexString(tester.a0)
    assert mockDisputeBondFactory.getCreateDisputeBondAmountValue() == bondAmount
    assert mockDisputeBondFactory.getCreateDisputeBondPayoutDistributionHash() == initializeMarket.getTentativeWinningPayoutDistributionHash()

    assert mockUniverse.getForkCalled() == True
    assert initializeMarket.getLastReportersDisputeBond() == mockLastDisputeBond.address
    assert initializeMarket.getExtraDisputeBondRemainingToBePaidOut() == extraPaidOut + bondAmount
    assert initializeMarket.getTotalStake() == totalStake + bondAmount

    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a0)
    assert mockReputationToken.getTrustedTransferDestinationValue() == mockLastDisputeBond.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == bondAmount

    assert mockAugur.logReportsDisputedCalled() == True
    assert mockNextReportingWindow.getIncreaseTotalStakeCalled() == True
    assert mockNextReportingWindow.getRemoveMarketCalled() == True
    assert mockNextReportingWindow.getUpdateMarketPhaseCalled() == True
    assert mockForkReportingWindow.getMigrateMarketInFromSiblingCalled() == True

    assert initializeMarket.getReportingWindow() == mockForkReportingWindow.address

def test_market_try_finalize_valid(localFixture, chain, initializeMarket, constants, mockReputationToken, mockStakeToken, mockAugur, mockReportingWindow, mockStakeTokenFactory, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow, mockCash):
    numTicks = 10 ** 10
    assert initializeMarket.getReportingState() == constants.PRE_REPORTING()
    assert initializeMarket.tryFinalize() == False   
    endTime = mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockForkReportingWindow = set_mock_reporting_window(localFixture, initializeMarket, mockUniverse, mockReputationToken, endTime)
    push_to_last_dispute(localFixture, initializeMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow, mockForkReportingWindow)
    assert initializeMarket.tryFinalize() == False
    chain.head_state.timestamp = mockForkReportingWindow.getEndTime() + 1
    assert initializeMarket.getReportingState() == constants.AWAITING_FINALIZATION()
    tentativeWinning = initializeMarket.getTentativeWinningPayoutDistributionHash()
    ownerBalance = chain.head_state.get_balance(tester.a1)
    designatedReporterDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', initializeMarket.getDesignatedReporterDisputeBond())
    firstReporterDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', initializeMarket.getFirstReportersDisputeBond())

    mockReputationToken.setBalanceOfValueFor(designatedReporterDisputeBond.address, 34)
    mockReputationToken.setBalanceOfValueFor(firstReporterDisputeBond.address, 55)

    assert initializeMarket.tryFinalize() == True
    finalPayoutStakeToken = localFixture.upload('solidity_test_helpers/MockStakeToken.sol', initializeMarket.getFinalWinningStakeToken())
    finalPayoutStakeToken.setIsValid(True)
    # since market is not the forking market tentative winning hash will be the winner
    assert initializeMarket.getFinalPayoutDistributionHash() == tentativeWinning
    assert mockForkReportingWindow.getUpdateMarketPhaseCalled() == True
    assert mockAugur.logMarketFinalizedCalled() == True
    # market is valid market owner gets validity bond back
    assert chain.head_state.get_balance(tester.a1) == ownerBalance + mockUniverse.getValidityBond()
    mockReputationToken.getTransferValueFor(finalPayoutStakeToken.address) == 34
    mockReputationToken.getTransferValueFor(finalPayoutStakeToken.address) == 55

def test_market_try_finalize_not_valid(localFixture, chain, initializeMarket, constants, mockReputationToken, mockStakeToken, mockAugur, mockReportingWindow, mockStakeTokenFactory, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow, mockCash):
    numTicks = 10 ** 10
    endTime = mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockForkReportingWindow = set_mock_reporting_window(localFixture, initializeMarket, mockUniverse, mockReputationToken, endTime)
    push_to_last_dispute(localFixture, initializeMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow, mockForkReportingWindow)
    chain.head_state.timestamp = mockForkReportingWindow.getEndTime() + 1
    assert initializeMarket.getReportingState() == constants.AWAITING_FINALIZATION()
    mockReputationToken.reset()

    mockStakeToken.setIsValid(False)
    newOwnerBalance = chain.head_state.get_balance(tester.a1)

    assert initializeMarket.tryFinalize() == True

    # verify market owner does not get back validity bond for invalid finalized markets 
    assert mockCash.getDepositEtherForAddressValue() == mockForkReportingWindow.address
    assert chain.head_state.get_balance(tester.a1) == newOwnerBalance


def test_market_try_finalize_forking(localFixture, chain, initializeMarket, constants, mockReputationToken, mockStakeToken, mockAugur, mockReportingWindow, mockStakeTokenFactory, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow, mockCash):
    numTicks = 10 ** 10
    endTime = mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockForkReportingWindow = set_mock_reporting_window(localFixture, initializeMarket, mockUniverse, mockReputationToken, endTime)
    push_to_last_dispute(localFixture, initializeMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow, mockForkReportingWindow)
    chain.head_state.timestamp = mockForkReportingWindow.getEndTime() + 1
    mockReputationToken.reset()

    mockReputationToken.setTopMigrationDestination(longToHexString(0))
    # if no top migration destination then state is FORKING
    #assert initializeMarket.getReportingState() == constants.FORKING()

    mockUniverse.setForkEndTime(chain.head_state.timestamp + 1)
    mockUniverse.setForkReputationGoal(55)
    mockWinningReputationToken = localFixture.upload('solidity_test_helpers/MockReputationToken.sol', 'mockWinningReputationToken');

    mockReputationToken.setTopMigrationDestination(mockWinningReputationToken.address)
    mockWinningReputationToken.setTotalSupply(10)
    mockWinningReputationToken.setUniverse(mockUniverse.address)
    # if winning dest reputation token has less supply thant universe fork reputation token and block time less than universe fork end time
    #assert initializeMarket.getReportingState() == constants.FORKING()
    mockDisputeStakeToken = set_mock_stake_token_value(localFixture, initializeMarket, [0, 0, 0, numTicks/2, numTicks/2], mockStakeTokenFactory, 100)
    payoutStakeTokenHashTarget = mockDisputeStakeToken.getPayoutDistributionHash()

    mockUniverse.setForkEndTime(chain.head_state.timestamp - 1)
    mockUniverse.setForkReputationGoal(5500)
    mockUniverse.setParentPayoutDistributionHash(stringToBytes(payoutStakeTokenHashTarget))
    mockUniverse.setForkingMarket(initializeMarket.address)
    mockWinningReputationToken.setTotalSupply(4000)
    assert initializeMarket.getReportingState() == constants.AWAITING_FINALIZATION()

    mockDisputeStakeToken.setIsValid(True)
    assert initializeMarket.getStakeToken([0, 0, 0, numTicks/2, numTicks/2], False) == mockDisputeStakeToken.address
    assert initializeMarket.tryFinalize() == True
    assert initializeMarket.getFinalPayoutDistributionHash() == payoutStakeTokenHashTarget

def test_market_migrate_due_to_no_reports(localFixture, initializeMarket, chain, mockReportingWindow, mockNextReportingWindow):
    with raises(TransactionFailed, message="reporting state needs to be AWAITING_NO_REPORT_MIGRATION"):
        initializeMarket.migrateDueToNoReports()

    chain.head_state.timestamp = mockNextReportingWindow.getEndTime()
    assert initializeMarket.migrateDueToNoReports()

    mockUniverse.setNextReportingWindow(mockNextReportingWindow.address)
    assert mockReportingWindow.getUpdateMarketPhaseCalled() == True
    assert mockReportingWindow.getRemoveMarketCalled() == True
    assert mockNextReportingWindow.getMigrateMarketInFromSiblingCalled() == True
    assert initializeMarket.getReportingWindow() == mockNextReportingWindow.address

def push_to_last_dispute(localFixture, initializeMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow, mockForkReportingWindow):
    numTicks = 10 ** 10
    push_to_designated_despute_state(localFixture, mockUniverse, chain, initializeMarket, mockStakeToken, [0, numTicks, 0, 0, 0], mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    push_first_dispute_last_reporting(localFixture, chain, mockReputationToken, initializeMarket, mockStakeTokenFactory, mockReportingWindow, mockUniverse, constants, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow)
    chain.head_state.timestamp = mockNextReportingWindow.getEndTime() - 1

    mockLastDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockLastDisputeBond');   
    mockDisputeBondFactory.setCreateDisputeBond(mockLastDisputeBond.address)
    bondAmount = constants.LAST_REPORTERS_DISPUTE_BOND_AMOUNT()
    extraPaidOut = initializeMarket.getExtraDisputeBondRemainingToBePaidOut()
    totalStake = initializeMarket.getTotalStake()
    mockReputationToken.reset()
    mockNextReportingWindow.setIsDisputeActive(True)

    mockForkReportingWindow.setEndTime(mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    mockForkReportingWindow.setReputationToken(mockReputationToken.address)
    mockForkReportingWindow.setUniverse(mockUniverse.address)
    mockUniverse.setReportingWindowForForkEndTime(mockForkReportingWindow.address)
    mockForkReportingWindow.setIsDisputeActive(True)
    
    assert initializeMarket.disputeLastReporters(sender=tester.k0)
    assert initializeMarket.getReportingWindow() == mockForkReportingWindow.address
    assert initializeMarket.getReportingState() == constants.LAST_DISPUTE()

# create stake token and association with market
def set_mock_stake_token_value(localFixture, initializeMarket, payoutDesignatedNumerators, mockStakeTokenFactory, value):
    payoutDesignatedHashValue = initializeMarket.derivePayoutDistributionHash(payoutDesignatedNumerators, False)
    newMockStakeToken = localFixture.upload('solidity_test_helpers/MockStakeToken.sol', str(payoutDesignatedHashValue));
    newMockStakeToken.setPayoutDistributionHash(payoutDesignatedHashValue)
    mockStakeTokenFactory.setStakeToken(payoutDesignatedHashValue, newMockStakeToken.address)
    assert initializeMarket.getStakeToken(payoutDesignatedNumerators, False) == newMockStakeToken.address
    newMockStakeToken.setTotalSupply(value)
    newMockStakeToken.setIsValid(True)
    return newMockStakeToken

def set_mock_reporting_window(localFixture, initializeMarket, mockUniverse, mockReputationToken, endTime):
    mockReportingWindowCreated = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol');
    mockReportingWindowCreated.setReputationToken(mockReputationToken.address)
    mockReportingWindowCreated.setUniverse(mockUniverse.address)
    if endTime:
        mockReportingWindowCreated.setEndTime(endTime)
    return mockReportingWindowCreated

def push_first_dispute_last_reporting(localFixture, chain, mockReputationToken, initializeMarket, mockStakeTokenFactory, mockReportingWindow, mockUniverse, constants, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow):
    numTicks = 10 ** 10
    mockReportingWindow.setEndTime(chain.head_state.timestamp + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    chain.head_state.timestamp = initializeMarket.getDesignatedReportDisputeDueTimestamp() - 1

    mockDisputeStakeToken = set_mock_stake_token_value(localFixture, initializeMarket, [0, 0, 0, numTicks, 0], mockStakeTokenFactory, 10)

    mockReportingWindow.setIsDisputeActive(True)

    mockDesignatedDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockDesignatedDisputeBond');    
    mockDisputeBondFactory.setCreateDisputeBond(mockDesignatedDisputeBond.address)
    assert mockReportingWindow.getReputationToken() == mockReputationToken.address
    assert initializeMarket.getReportingState() == constants.DESIGNATED_DISPUTE()

    assert initializeMarket.disputeDesignatedReport([0, 0, 0, numTicks, 0], 100, False, sender=tester.k2)
    assert initializeMarket.getReportingState() == constants.FIRST_DISPUTE()

    mockFirstDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockFirstDisputeBond');
    mockDisputeBondFactory.setCreateDisputeBond(mockFirstDisputeBond.address)
   
    mockUniverse.setNextReportingWindow(mockNextReportingWindow.address)
    mockDisputeStakeToken = set_mock_stake_token_value(localFixture, initializeMarket, [0, 0, 0, 0, numTicks], mockStakeTokenFactory, 1000)

    # execute disputeFirstReporters on market
    assert initializeMarket.disputeFirstReporters([0, 0, 0, 0, numTicks], 50, False, sender=tester.k4)
    assert initializeMarket.getReportingWindow() == mockNextReportingWindow.address
    chain.head_state.timestamp = mockNextReportingWindow.getEndTime() - 1
    assert initializeMarket.getReportingState() == constants.LAST_REPORTING()

def push_to_designated_despute_state(localFixture, mockUniverse, chain, initializeMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants):
    chain.head_state.timestamp = initializeMarket.getDesignatedReportDueTimestamp() - 1 
    payoutDesignatedHashValue = initializeMarket.derivePayoutDistributionHash(payoutDesignatedNumerators, False)
    mockStakeToken.setPayoutDistributionHash(payoutDesignatedHashValue)
    mockStakeTokenFactory.setStakeToken(payoutDesignatedHashValue, mockStakeToken.address)
    assert initializeMarket.getReportingState() == constants.DESIGNATED_REPORTING()

    assert initializeMarket.getStakeToken(payoutDesignatedNumerators, False)
    assert mockStakeTokenFactory.getCreateDistroHashValue() == payoutDesignatedHashValue
    assert mockStakeTokenFactory.getCreateStakeTokenMarketValue() == initializeMarket.address
    assert mockStakeTokenFactory.getCreateStakeTokenPayoutValue() == payoutDesignatedNumerators
    assert initializeMarket.getStakeToken(payoutDesignatedNumerators, False) == mockStakeToken.address

    mockReputationToken.setBalanceOf(105)
    ownerBalance = chain.head_state.get_balance(tester.a1)

    assert mockStakeToken.callMarketDesignatedReport(initializeMarket.address)
    assert initializeMarket.getDesignatedReportReceivedTime() == chain.head_state.timestamp
    assert initializeMarket.getTentativeWinningPayoutDistributionHash() == mockStakeToken.getPayoutDistributionHash()
    assert mockReportingWindow.getUpdateMarketPhaseCalled() == True
    assert mockReportingWindow.getNoteDesignatedReport() == True
    assert mockReputationToken.getTransferValueFor(tester.a1) == 105
    assert chain.head_state.get_balance(tester.a1) == ownerBalance + mockUniverse.getTargetReporterGasCosts()
    assert initializeMarket.getReportingState() == constants.DESIGNATED_DISPUTE()

@fixture(scope="session")
def localSnapshot(fixture, augurInitializedWithMocksSnapshot):
    fixture.resetToSnapshot(augurInitializedWithMocksSnapshot)
    controller = fixture.contracts['Controller']
    mockReportingParticipationTokenFactory = fixture.contracts['MockParticipationTokenFactory']
    mockDisputeBondFactory = fixture.contracts['MockDisputeBondFactory']
    mockCash = fixture.contracts['MockCash']
    mockAugur = fixture.contracts['MockAugur']
    mockShareTokenFactory = fixture.contracts['MockShareTokenFactory']    
    mockShareToken = fixture.contracts['MockShareToken']
    mockFillOrder = fixture.contracts['MockFillOrder']
    mockStakeTokenFactory = fixture.contracts['MockStakeTokenFactory']

    # pre populate share tokens for max of 8 possible outcomes
    for index in range(8):
        item = fixture.upload('solidity_test_helpers/MockShareToken.sol', 'newMockShareToken' + str(index));
        mockShareTokenFactory.pushCreateShareToken(item.address)
    
    controller.registerContract(stringToBytes('Cash'), mockCash.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('ParticipationTokenFactory'), mockReportingParticipationTokenFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('ShareTokenFactory'), mockShareTokenFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('FillOrder'), mockShareTokenFactory.address, twentyZeros, thirtyTwoZeros)    
    controller.registerContract(stringToBytes('StakeTokenFactory'), mockStakeTokenFactory.address, twentyZeros, thirtyTwoZeros)    
    controller.registerContract(stringToBytes('DisputeBondFactory'), mockDisputeBondFactory.address, twentyZeros, thirtyTwoZeros)    
    mockShareTokenFactory.resetCreateShareToken();
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def mockUniverse(localFixture):
    return localFixture.contracts['MockUniverse']

@fixture
def mockReportingWindow(localFixture, mockReputationToken, mockUniverse):
    mockReportingWindow = localFixture.contracts['MockReportingWindow']
    mockReportingWindow.setReputationToken(mockReputationToken.address)
    mockReportingWindow.setUniverse(mockUniverse.address)
    mockReportingWindow.reset()
    return mockReportingWindow

@fixture
def mockNextReportingWindow(localFixture, mockReputationToken, mockUniverse):
    mockNextReportingWindow = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol', 'mockNextReportingWindow');
    mockNextReportingWindow.setReputationToken(mockReputationToken.address)
    mockNextReportingWindow.setUniverse(mockUniverse.address)
    return mockNextReportingWindow

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
    mockAugur = localFixture.contracts['MockAugur']
    mockAugur.reset()
    return mockAugur

@fixture
def mockReputationToken(localFixture):
    mockReputationToken = localFixture.contracts['MockReputationToken']
    mockReputationToken.reset()
    return mockReputationToken

@fixture
def mockShareToken(localFixture):
    return localFixture.contracts['MockShareToken']

@fixture
def mockStakeTokenFactory(localFixture):
    mockStakeTokenFactory = localFixture.contracts['MockStakeTokenFactory']
    mockStakeTokenFactory.initializeMap(localFixture.contracts['Controller'].address)
    return mockStakeTokenFactory

@fixture
def mockShareTokenFactory(localFixture):
    return localFixture.contracts['MockShareTokenFactory']

@fixture
def mockStakeToken(localFixture):
    mockStakeToken = localFixture.contracts['MockStakeToken']
    mockStakeToken.setIsValid(True)
    return mockStakeToken

@fixture
def mockDisputeBond(localFixture):
    return localFixture.contracts['MockDisputeBond']

@fixture
def mockDisputeBondFactory(localFixture):
    return localFixture.contracts['MockDisputeBondFactory']

@fixture
def initializeMarket(localFixture, mockReportingWindow, mockUniverse, mockReputationToken, chain, constants, mockCash, mockNextReportingWindow):
    market = localFixture.upload('../source/contracts/reporting/Market.sol', 'market')
    contractMap = localFixture.upload('../source/contracts/libraries/collections/Map.sol', 'Map')
    numTicks = 10 ** 10
    endTime = chain.head_state.timestamp + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    market.setController(localFixture.contracts["Controller"].address)

    mockUniverse.setForkingMarket(longToHexString(0))
    mockUniverse.setDesignatedReportNoShowBond(100)
    mockReputationToken.setBalanceOf(100)
    mockUniverse.setTargetReporterGasCosts(15)
    mockUniverse.setValidityBond(12)
    mockUniverse.setNextReportingWindow(mockNextReportingWindow.address)
    mockReportingWindow.setEndTime(chain.head_state.timestamp + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    mockNextReportingWindow.setEndTime(mockReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    assert market.initialize(mockReportingWindow.address, endTime, 5, numTicks, 16, mockCash.address, tester.a1, tester.a2, value=100)
    return market