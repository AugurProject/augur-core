
from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString, twentyZeros, thirtyTwoZeros
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed

numTicks = 10 ** 10
def test_market_creation(localFixture, mockUniverse, mockReportingWindow, mockCash, chain, constants, mockMarket, mockReputationToken, mockShareToken, mockShareTokenFactory):
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
    assert mockShareTokenFactory.getCreateShareTokenCounter() == 5
    assert mockShareTokenFactory.getCreateShareToken(0) == market.getShareToken(0)
    assert mockShareTokenFactory.getCreateShareToken(1) == market.getShareToken(1)
    assert mockShareTokenFactory.getCreateShareToken(2) == market.getShareToken(2)
    assert mockShareTokenFactory.getCreateShareToken(3) == market.getShareToken(3)
    assert mockShareTokenFactory.getCreateShareToken(4) == market.getShareToken(4)

def test_market_designated_report(localFixture, constants, mockUniverse, chain, initializedMarket, mockStakeToken, mockStakeTokenFactory, mockReportingWindow, mockReputationToken):
    with raises(TransactionFailed, message="market is not in designated reporting state"):
        initializedMarket.designatedReport()

    chain.head_state.timestamp = initializedMarket.getDesignatedReportDueTimestamp() - 1
    with raises(TransactionFailed, message="designated report method needs to be called from StakeToken"):
        initializedMarket.designatedReport()

    with raises(TransactionFailed, message="StakeToken needs to be contained by market"):
        mockStakeToken.callMarketDesignatedReport(initializedMarket.address)
    
    payoutDesignatedNumerators = [numTicks, 0, 0, 0, 0]
    push_to_designated_dispute_state(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)

def test_market_dispute_report_with_attoeth(localFixture, constants, initializedMarket, chain, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockStakeToken, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, mockAugur):
    payoutDesignatedNumerators = [numTicks, 0, 0, 0, 0]
    payoutSecondNumeratorsDispute = [0, numTicks, 0, 0, 0]
    payoutDesignatedHashValue = initializedMarket.derivePayoutDistributionHash(payoutSecondNumeratorsDispute, False)

    with raises(TransactionFailed, message="market needs to be in DESIGNATED_DISPUTE state"):
        initializedMarket.disputeDesignatedReport(payoutDesignatedNumerators, 100, False)

    push_to_designated_dispute_state(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    mockReportingWindow.reset()
    mockDisputeBondFactory.setCreateDisputeBond(mockDisputeBond.address)

    disputeStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, payoutSecondNumeratorsDispute, mockStakeTokenFactory, 0)

    bondAmount = constants.DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
    stakeAmount = initializedMarket.getTotalStake()
    beforeAmount = initializedMarket.getExtraDisputeBondRemainingToBePaidOut()
    tentWinningHash = initializedMarket.getTentativeWinningPayoutDistributionHash()
    assert initializedMarket.getReportingState() == constants.DESIGNATED_DISPUTE()

    with raises(TransactionFailed, message="tentative winning payout distro can not be 0 for stake token"):
        initializedMarket.disputeDesignatedReport(payoutSecondNumeratorsDispute, 0, False, sender=tester.k2)

    # execute disputeDesignatedReport on market
    assert initializedMarket.disputeDesignatedReport(payoutSecondNumeratorsDispute, 100, False, sender=tester.k2)
    assert mockReportingWindow.getUpdateMarketPhaseCalled() == True
    assert mockReportingWindow.getIncreaseTotalStakeCalled() == True
    assert mockAugur.logReportsDisputedCalled() == True

    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a2)
    assert mockReputationToken.getTrustedTransferDestinationValue() == mockDisputeBond.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == bondAmount

    assert initializedMarket.getExtraDisputeBondRemainingToBePaidOut() == beforeAmount + bondAmount
    assert initializedMarket.getTotalStake() == stakeAmount + bondAmount
    assert initializedMarket.getDesignatedReporterDisputeBond() == mockDisputeBond.address

    assert mockDisputeBondFactory.getCreateDisputeBondMarket() == initializedMarket.address
    assert mockDisputeBondFactory.getCreateDisputeBondBondHolder() == bytesToHexString(tester.a2)
    assert mockDisputeBondFactory.getCreateDisputeBondAmountValue() == bondAmount
    assert mockDisputeBondFactory.getCreateDisputeBondPayoutDistributionHash() == tentWinningHash

    assert disputeStakeToken.getTrustedBuyAddressValue() == bytesToHexString(tester.a2)
    assert disputeStakeToken.getTrustedBuyAttoTokensValue() == 100


def test_market_dispute_report_with_no_attoeth(localFixture, constants, initializedMarket, chain, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockStakeToken, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, mockAugur):
    payoutDesignatedNumerators = [numTicks, 0, 0, 0, 0]
    payoutdNumeratorsDispute = [0, numTicks, 0, 0, 0]
    payoutFirstDisputeNumeratorsDispute = [0, 0, numTicks, 0, 0]
    with raises(TransactionFailed, message="market needs to be in DESIGNATED_DISPUTE state"):
        initializedMarket.disputeDesignatedReport(payoutDesignatedNumerators, 100, False)

    payoutDesignatedHash = initializedMarket.derivePayoutDistributionHash(payoutDesignatedNumerators, False)
    payoutFirstDisputeHash = initializedMarket.derivePayoutDistributionHash(payoutFirstDisputeNumeratorsDispute, False)

    push_to_designated_dispute_state(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHash
    assert initializedMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == stringToBytes("")
    # set value for original designated report so that calcuations for tent. winning token doesn't blow up
    mockStakeToken.setTotalSupply(105)
    mockDisputeStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, payoutdNumeratorsDispute, mockStakeTokenFactory, 100)

    assert initializedMarket.getReportingState() == constants.DESIGNATED_DISPUTE()
    mockDisputeBondFactory.setCreateDisputeBond(mockDisputeBond.address)
    # execute disputeDesignatedReport on market
    assert initializedMarket.disputeDesignatedReport(payoutdNumeratorsDispute, 0, False, sender=tester.k2)
    # execution path is same as with attoeth except no stake token transfer
    assert mockDisputeStakeToken.getTrustedBuyAddressValue() == longToHexString(0)
    assert mockDisputeStakeToken.getTrustedBuyAttoTokensValue() == 0

    bondAmount = constants.FIRST_REPORTERS_DISPUTE_BOND_AMOUNT()
    stakeAmount = initializedMarket.getTotalStake()
    beforeAmount = initializedMarket.getExtraDisputeBondRemainingToBePaidOut()

    # might as well test first dispute
    mockReportingWindow.setEndTime(chain.head_state.timestamp + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    chain.head_state.timestamp = initializedMarket.getDesignatedReportDisputeDueTimestamp() - 1

    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHash
    assert initializedMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == stringToBytes("")

    mockFirstDisputeStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, payoutFirstDisputeNumeratorsDispute, mockStakeTokenFactory, 10)
    mockReportingWindow.setIsDisputeActive(True)
    assert initializedMarket.getReportingState() == constants.FIRST_DISPUTE()

    mockFirstDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockFirstDisputeBond');
    mockDisputeBondFactory.setCreateDisputeBond(mockFirstDisputeBond.address)
    endTime = mockReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockNextReportingWindow = set_mock_reporting_window(localFixture, initializedMarket, mockUniverse, mockReputationToken, endTime)
    mockUniverse.setNextReportingWindow(mockNextReportingWindow.address)

    # execute disputeFirstReporters on market
    assert initializedMarket.disputeFirstReporters(payoutFirstDisputeNumeratorsDispute, 14, False, sender=tester.k3)

    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a3)
    assert mockReputationToken.getTrustedTransferDestinationValue() == mockFirstDisputeBond.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == bondAmount

    assert mockNextReportingWindow.getMigrateMarketInFromSiblingCalled() == True
    assert mockReportingWindow.getIncreaseTotalStakeCalled() == True
    assert mockReportingWindow.getRemoveMarketCalled() == True
    assert mockReportingWindow.getUpdateMarketPhaseCalled() == True

    assert initializedMarket.getFirstReportersDisputeBond() == mockFirstDisputeBond.address

    assert mockFirstDisputeStakeToken.getTrustedBuyAddressValue() == bytesToHexString(tester.a3)
    assert mockFirstDisputeStakeToken.getTrustedBuyAttoTokensValue() == 14
    payoutFirstDisputeHashDisputeValue = payoutFirstDisputeHash
    # verify that best guess second place is updated correctly
    assert mockFirstDisputeStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializedMarket.address, payoutFirstDisputeHashDisputeValue)
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHash
    assert initializedMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutFirstDisputeHash

def test_market_update_tentative_winning_payout(localFixture, constants, initializedMarket, chain, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockStakeToken, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, mockAugur):
    payoutDesignatedNumerators = [numTicks, 0, 0, 0, 0]
    payoutSecondNumeratorsDispute = [0, numTicks, 0, 0, 0]
    payoutThirdNumerators = [0, 0, numTicks, 0, 0]
    payoutFourthNumerators = [0, 0, 0, numTicks, 0]

    payoutDesignatedHashValue = initializedMarket.derivePayoutDistributionHash(payoutDesignatedNumerators, False)
    payoutSecondHashDisputeValue = initializedMarket.derivePayoutDistributionHash(payoutSecondNumeratorsDispute, False)
    payoutThirdHashValue = initializedMarket.derivePayoutDistributionHash(payoutThirdNumerators, False)
    payoutFourthHashValue = initializedMarket.derivePayoutDistributionHash(payoutFourthNumerators, False)

    push_to_designated_dispute_state(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHashValue

    mockReportingWindow.reset()
    # get second token
    mockSecondStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, payoutSecondNumeratorsDispute, mockStakeTokenFactory, 0)

    # verify stake tokens are set
    assert initializedMarket.getOrCreateStakeToken(payoutDesignatedNumerators, False) == mockStakeToken.address
    assert initializedMarket.getOrCreateStakeToken(payoutSecondNumeratorsDispute, False) == mockSecondStakeToken.address

    with raises(TransactionFailed, message="tentative winning payout distro can not be 0 we need stake token with positive supply"):
        mockSecondStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializedMarket.address, payoutSecondHashDisputeValue)

    mockStakeToken.setTotalSupply(105)
    mockSecondStakeToken.setTotalSupply(20)
    assert initializedMarket.getTotalStake() == 0
    assert mockSecondStakeToken.callIncreaseTotalStake(initializedMarket.address, 20)
    assert initializedMarket.getTotalStake() == 20
    assert mockReportingWindow.getIncreaseTotalStakeCalled() == True

    assert mockSecondStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializedMarket.address, payoutSecondHashDisputeValue)
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == payoutDesignatedHashValue
    assert initializedMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutSecondHashDisputeValue
    # buy a third stake token
    mockThirdStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, payoutThirdNumerators, mockStakeTokenFactory, 200)

    # verify stake tokens have correct value
    assert initializedMarket.getPayoutDistributionHashStake(payoutDesignatedHashValue) == 105
    assert initializedMarket.getPayoutDistributionHashStake(payoutSecondHashDisputeValue) == 20
    assert initializedMarket.getPayoutDistributionHashStake(payoutThirdHashValue) == 200

    assert mockThirdStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializedMarket.address, payoutThirdHashValue)
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == payoutThirdHashValue
    assert initializedMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutDesignatedHashValue
    # bump up existing stake token supply
    mockSecondStakeToken.setTotalSupply(500)

    assert mockSecondStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializedMarket.address, payoutSecondHashDisputeValue)
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == payoutSecondHashDisputeValue
    assert initializedMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutThirdHashValue

    # stake token to rule them all
    mockFourthStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, payoutFourthNumerators, mockStakeTokenFactory, 800)

    assert mockFourthStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializedMarket.address, payoutFourthHashValue)
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == payoutFourthHashValue
    assert initializedMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == payoutSecondHashDisputeValue

    mockFourthStakeToken.setTotalSupply(0)
    assert mockFourthStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializedMarket.address, payoutFourthHashValue)
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == payoutSecondHashDisputeValue
    assert initializedMarket.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() == stringToBytes("")

    mockSecondStakeToken.setTotalSupply(0)
    with raises(TransactionFailed, message="can not withdraw stake token supply it leaves no tentative winning payout"):
        mockSecondStakeToken.callUpdateTentativeWinningPayoutDistributionHash(initializedMarket.address, payoutSecondHashDisputeValue)

def test_market_get_payout_distr_hash_stake(localFixture, initializedMarket, mockStakeTokenFactory):
    mockStakeToken_1 = set_mock_stake_token_value(localFixture, initializedMarket, [numTicks, 0, 0, 0, 0], mockStakeTokenFactory, 80)
    assert initializedMarket.getPayoutDistributionHashStake(mockStakeToken_1.getPayoutDistributionHash()) == 80

    mockStakeToken_2 = set_mock_stake_token_value(localFixture, initializedMarket, [0, numTicks, 0, 0, 0], mockStakeTokenFactory, 30)
    assert initializedMarket.getPayoutDistributionHashStake(mockStakeToken_2.getPayoutDistributionHash()) == 30

    mockStakeToken_3 = set_mock_stake_token_value(localFixture, initializedMarket, [0, 0, numTicks, 0, 0], mockStakeTokenFactory, 100)
    assert initializedMarket.getPayoutDistributionHashStake(mockStakeToken_3.getPayoutDistributionHash()) == 100

def test_market_dispute_last_reporter(localFixture, initializedMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow):
    push_to_designated_dispute_state(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, [0,numTicks,0,0,0], mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)

    push_first_dispute_last_reporting(localFixture, chain, mockReputationToken, initializedMarket, mockStakeTokenFactory, mockReportingWindow, mockUniverse, constants, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow)

    with raises(TransactionFailed, message="market needs to be in last dispute state"):
        initializedMarket.disputeLastReporters()

    chain.head_state.timestamp = mockNextReportingWindow.getEndTime() - 1

    mockLastDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockLastDisputeBond');
    mockDisputeBondFactory.setCreateDisputeBond(mockLastDisputeBond.address)
    bondAmount = constants.LAST_REPORTERS_DISPUTE_BOND_AMOUNT()
    extraPaidOut = initializedMarket.getExtraDisputeBondRemainingToBePaidOut()
    totalStake = initializedMarket.getTotalStake()
    # set up new reputation tokan for reporting window
    mockReputationToken.reset()
    mockNextReportingWindow.setIsDisputeActive(True)
    endTime = mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockForkReportingWindow = set_mock_reporting_window(localFixture, initializedMarket, mockUniverse, mockReputationToken, endTime)
    mockUniverse.setReportingWindowForForkEndTime(mockForkReportingWindow.address)

    assert initializedMarket.getReportingState() == constants.LAST_DISPUTE()
    assert initializedMarket.getReportingWindow() == mockNextReportingWindow.address

    assert initializedMarket.disputeLastReporters(sender=tester.k0)

    assert mockDisputeBondFactory.getCreateDisputeBondMarket() == initializedMarket.address
    assert mockDisputeBondFactory.getCreateDisputeBondBondHolder() == bytesToHexString(tester.a0)
    assert mockDisputeBondFactory.getCreateDisputeBondAmountValue() == bondAmount
    assert mockDisputeBondFactory.getCreateDisputeBondPayoutDistributionHash() == initializedMarket.getTentativeWinningPayoutDistributionHash()

    assert mockUniverse.getForkCalled() == True
    assert initializedMarket.getLastReportersDisputeBond() == mockLastDisputeBond.address
    assert initializedMarket.getExtraDisputeBondRemainingToBePaidOut() == extraPaidOut + bondAmount
    assert initializedMarket.getTotalStake() == totalStake + bondAmount

    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a0)
    assert mockReputationToken.getTrustedTransferDestinationValue() == mockLastDisputeBond.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == bondAmount

    assert mockAugur.logReportsDisputedCalled() == True
    assert mockNextReportingWindow.getIncreaseTotalStakeCalled() == True
    assert mockNextReportingWindow.getRemoveMarketCalled() == True
    assert mockNextReportingWindow.getUpdateMarketPhaseCalled() == True
    assert mockForkReportingWindow.getMigrateMarketInFromSiblingCalled() == True

    assert initializedMarket.getReportingWindow() == mockForkReportingWindow.address

def test_market_try_finalize_valid(localFixture, chain, initializedMarket, constants, mockReputationToken, mockStakeToken, mockAugur, mockReportingWindow, mockStakeTokenFactory, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow, mockCash):
    assert initializedMarket.getReportingState() == constants.PRE_REPORTING()
    assert initializedMarket.tryFinalize() == False
    endTime = mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockForkReportingWindow = set_mock_reporting_window(localFixture, initializedMarket, mockUniverse, mockReputationToken, endTime)
    push_to_last_dispute(localFixture, initializedMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow, mockForkReportingWindow)
    assert initializedMarket.tryFinalize() == False
    chain.head_state.timestamp = mockForkReportingWindow.getEndTime() + 1
    assert initializedMarket.getReportingState() == constants.AWAITING_FINALIZATION()
    tentativeWinning = initializedMarket.getTentativeWinningPayoutDistributionHash()
    ownerBalance = chain.head_state.get_balance(tester.a1)
    designatedReporterDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', initializedMarket.getDesignatedReporterDisputeBond())
    firstReporterDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', initializedMarket.getFirstReportersDisputeBond())

    mockReputationToken.setBalanceOfValueFor(designatedReporterDisputeBond.address, 34)
    mockReputationToken.setBalanceOfValueFor(firstReporterDisputeBond.address, 55)

    assert initializedMarket.tryFinalize() == True
    finalPayoutStakeToken = localFixture.upload('solidity_test_helpers/MockStakeToken.sol', initializedMarket.getFinalWinningStakeToken())
    finalPayoutStakeToken.setIsValid(True)
    # since market is not the forking market tentative winning hash will be the winner
    assert initializedMarket.getFinalPayoutDistributionHash() == tentativeWinning
    assert mockForkReportingWindow.getUpdateMarketPhaseCalled() == True
    assert mockAugur.logMarketFinalizedCalled() == True
    # market is valid market owner gets validity bond back
    assert chain.head_state.get_balance(tester.a1) == ownerBalance
    assert chain.head_state.get_balance(initializedMarket.getMarketCreatorMailbox()) == mockUniverse.getOrCacheValidityBond() + mockUniverse.getOrCacheTargetReporterGasCosts()
    mockReputationToken.getTransferValueFor(finalPayoutStakeToken.address) == 34
    mockReputationToken.getTransferValueFor(finalPayoutStakeToken.address) == 55

def test_market_try_finalize_not_valid(localFixture, chain, initializedMarket, constants, mockReputationToken, mockStakeToken, mockAugur, mockReportingWindow, mockStakeTokenFactory, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow, mockCash):
    endTime = mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockForkReportingWindow = set_mock_reporting_window(localFixture, initializedMarket, mockUniverse, mockReputationToken, endTime)
    push_to_last_dispute(localFixture, initializedMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow, mockForkReportingWindow)
    chain.head_state.timestamp = mockForkReportingWindow.getEndTime() + 1
    assert initializedMarket.getReportingState() == constants.AWAITING_FINALIZATION()
    mockReputationToken.reset()

    mockStakeToken.setIsValid(False)
    newOwnerBalance = chain.head_state.get_balance(tester.a1)

    assert initializedMarket.tryFinalize() == True

    # verify market owner does not get back validity bond for invalid finalized markets
    assert mockCash.getDepositEtherForAddressValue() == mockForkReportingWindow.address
    assert chain.head_state.get_balance(tester.a1) == newOwnerBalance

def test_market_try_finalize_forking(localFixture, chain, initializedMarket, constants, mockReputationToken, mockStakeToken, mockAugur, mockReportingWindow, mockStakeTokenFactory, mockUniverse, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow, mockCash):
    endTime = mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS()
    mockForkReportingWindow = set_mock_reporting_window(localFixture, initializedMarket, mockUniverse, mockReputationToken, endTime)
    push_to_last_dispute(localFixture, initializedMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow, mockForkReportingWindow)
    chain.head_state.timestamp = mockForkReportingWindow.getEndTime() - 1
    mockReputationToken.reset()

    mockUniverse.setForkingMarket(initializedMarket.address)
    mockReputationToken.setTopMigrationDestination(longToHexString(0))

    mockUniverse.setForkEndTime(chain.head_state.timestamp + 1)
    mockUniverse.setForkReputationGoal(55)
    mockWinningReputationToken = localFixture.upload('solidity_test_helpers/MockReputationToken.sol', 'mockWinningReputationToken');

    mockReputationToken.setTopMigrationDestination(mockWinningReputationToken.address)
    mockWinningReputationToken.setTotalSupply(10)
    mockWinningReputationToken.setUniverse(mockUniverse.address)

    assert initializedMarket.getReportingState() == constants.FORKING()
    mockDisputeStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, [0, 0, 0, numTicks/2, numTicks/2], mockStakeTokenFactory, 100)
    payoutStakeTokenHashTarget = mockDisputeStakeToken.getPayoutDistributionHash()

    mockUniverse.setForkEndTime(chain.head_state.timestamp - 1)
    mockUniverse.setForkReputationGoal(5500)
    mockUniverse.setParentPayoutDistributionHash(stringToBytes(payoutStakeTokenHashTarget))
    mockWinningReputationToken.setTotalSupply(4000)

    mockDisputeStakeToken.setIsValid(True)
    assert initializedMarket.getOrCreateStakeToken([0, 0, 0, numTicks/2, numTicks/2], False) == mockDisputeStakeToken.address
    assert initializedMarket.tryFinalize() == True
    assert initializedMarket.getFinalPayoutDistributionHash() == payoutStakeTokenHashTarget

def test_market_migrate_due_to_no_reports(localFixture, initializedMarket, chain, mockReportingWindow, mockNextReportingWindow, mockUniverse):
    with raises(TransactionFailed, message="reporting state needs to be AWAITING_NO_REPORT_MIGRATION"):
        initializedMarket.migrateDueToNoReports()

    chain.head_state.timestamp = mockNextReportingWindow.getEndTime()
    assert initializedMarket.migrateDueToNoReports() == True

    mockUniverse.setNextReportingWindow(mockNextReportingWindow.address)
    assert mockReportingWindow.getRemoveMarketCalled() == True
    assert mockNextReportingWindow.getMigrateMarketInFromSiblingCalled() == True
    assert mockNextReportingWindow.getUpdateMarketPhaseCalled() == True
    assert initializedMarket.getReportingWindow() == mockNextReportingWindow.address

def test_market_migrate_through_one_fork(localFixture, initializedMarket, constants, mockMarket, mockUniverse, mockReportingWindow, mockNextReportingWindow):
    mockNewReportingWindow = mockNextReportingWindow
    newTestMarket = localFixture.upload('../source/contracts/reporting/Market.sol', 'newTestMarket')
    with raises(TransactionFailed, message="market state has to be AWAITING_FORK_MIGRATION"):
        newTestMarket.migrateThroughOneFork()

    mockUniverse.setForkingMarket(mockMarket.address)
    mockReportingWindow.setIsForkingMarketFinalized(False)
    with raises(TransactionFailed, message="fork has not be finalized"):
        initializedMarket.migrateThroughOneFork()

    mockReportingWindow.setIsForkingMarketFinalized(True)
    mockMarket.setFinalPayoutDistributionHash(stringToBytes("blahblahblah"))
    mockNewUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'mockNewUniverse');
    mockUniverse.setOrCreateChildUniverse(mockNewUniverse.address)
    mockNewUniverse.setReportingWindowByMarketEndTime(mockNewReportingWindow.address)

    assert initializedMarket.migrateThroughOneFork() == True
    assert mockReportingWindow.getRemoveMarketCalled() == True
    assert mockNewReportingWindow.getMigrateMarketInFromNiblingCalled() == True
    assert initializedMarket.getDesignatedReporterDisputeBond() == longToHexString(0)
    assert initializedMarket.getFirstReportersDisputeBond() == longToHexString(0)
    assert initializedMarket.getLastReportersDisputeBond() == longToHexString(0)
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == initializedMarket.getDesignatedReportPayoutHash()

def test_market_disavow_tokens(localFixture, initializedMarket, mockUniverse, mockReportingWindow, mockMarket, mockStakeTokenFactory):
    stakePayNumeration = [0,0,0,0,numTicks]
    with raises(TransactionFailed, message="market state has to be AWAITING_FORK_MIGRATION"):
        initializedMarket.disavowTokens()

    mockUniverse.setForkingMarket(mockMarket.address)
    mockReportingWindow.setIsForkingMarketFinalized(False)
    with raises(TransactionFailed, message="market needs stake tokens"):
        initializedMarket.disavowTokens()
    
    mockStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, stakePayNumeration, mockStakeTokenFactory, 10)
    assert initializedMarket.isContainerForStakeToken(mockStakeToken.address) == True
    assert initializedMarket.disavowTokens() == True
    assert initializedMarket.isContainerForStakeToken(mockStakeToken.address) == False

def test_market_first_reporter_comp_check(localFixture, initializedMarket, chain, constants, mockUniverse, mockStakeToken, mockReportingWindow, mockMarket, mockStakeTokenFactory, mockReputationToken):
    stakePayNumeration = [0,0,0,0,numTicks]
    existingBalance = chain.head_state.get_balance(tester.a1)
    mockReputationToken.setBalanceOfValueFor(initializedMarket.address, 1000)
    with raises(TransactionFailed, message="sender must be a stake token"):
        initializedMarket.firstReporterCompensationCheck(tester.a1)
    
    mockStakeToken2 = set_mock_stake_token_value(localFixture, initializedMarket, stakePayNumeration, mockStakeTokenFactory, 10)
    assert initializedMarket.isContainerForStakeToken(mockStakeToken2.address) == True
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == stringToBytes("")

    assert mockStakeToken2.callFirstReporterCompensationCheck(initializedMarket.address, tester.a1) == 1000
    assert mockReputationToken.getTransferValueFor(tester.a1) == 1000
    # 15 is the reporter gas costs set in the initialization of the market
    assert chain.head_state.get_balance(tester.a1) == existingBalance + 15

def test_market_first_reporter_comp_check_zero(localFixture, initializedMarket, chain, constants, mockUniverse, mockStakeToken, mockReportingWindow, mockMarket, mockStakeTokenFactory, mockReputationToken):
    payoutDesignatedNumerators = [0,0,numTicks,0,0]
    push_to_designated_dispute_state(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, [0,numTicks,0,0,0], mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    assert initializedMarket.getReportingState() == constants.DESIGNATED_DISPUTE()
    assert mockStakeToken.callFirstReporterCompensationCheck(initializedMarket.address, tester.a1) == 0

    chain.head_state.timestamp = initializedMarket.getDesignatedReportDueTimestamp() - 1
    mockStakeToken2 = set_mock_stake_token_value(localFixture, initializedMarket, payoutDesignatedNumerators, mockStakeTokenFactory, 10)
    assert initializedMarket.getReportingState() == constants.DESIGNATED_REPORTING()
    assert initializedMarket.isContainerForStakeToken(mockStakeToken2.address) == True
    assert mockStakeToken2.callFirstReporterCompensationCheck(initializedMarket.address, tester.a1) == 0

def test_market_increase_total_stake(localFixture, initializedMarket, mockReportingWindow, mockStakeTokenFactory):
    payoutNumerators = [0,0,numTicks,0,0]    
    mockStakeToken2 = set_mock_stake_token_value(localFixture, initializedMarket, payoutNumerators, mockStakeTokenFactory, 10)
    supply = initializedMarket.getTotalStake()
    mockStakeToken2.callIncreaseTotalStake(initializedMarket.address, 100)
    assert initializedMarket.getTotalStake() == supply + 100
    assert mockReportingWindow.getIncreaseTotalStakeCalled() == True

def test_market_approve_spenders(localFixture, initializedMarket, mockCash, mockShareTokenFactory):
    approvalAmount = 2**256-1;
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

def test_market_decrease_extra_dispute_bond_remaining(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow):
    payoutDesignatedNumerators = [0, numTicks, 0, 0, 0]
    assert initializedMarket.isContainerForDisputeBond(mockDisputeBond.address) == False
    with raises(TransactionFailed, message="bond is not contained by market"):
        mockDisputeBond.callDecreaseExtraDisputeBondRemainingToBePaidOut(100)

    push_to_designated_dispute_state(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    push_first_dispute_last_reporting(localFixture, chain, mockReputationToken, initializedMarket, mockStakeTokenFactory, mockReportingWindow, mockUniverse, constants, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow)
    existingValue = initializedMarket.getExtraDisputeBondRemainingToBePaidOut()
    disputeBond = localFixture.applySignature('MockDisputeBond', mockDisputeBondFactory.getCreateDisputeBond())
    assert initializedMarket.isContainerForDisputeBond(disputeBond.address) == True
    assert disputeBond.callDecreaseExtraDisputeBondRemainingToBePaidOut(initializedMarket.address, 100) == True
    assert initializedMarket.getExtraDisputeBondRemainingToBePaidOut() == existingValue - 100

def push_to_last_dispute(localFixture, initializedMarket, constants, mockAugur, mockReportingWindow, mockDisputeBondFactory, mockReputationToken, mockDisputeBond, chain, mockUniverse, mockStakeToken, mockStakeTokenFactory, mockNextReportingWindow, mockForkReportingWindow):
    push_to_designated_dispute_state(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, [0, numTicks, 0, 0, 0], mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants)
    push_first_dispute_last_reporting(localFixture, chain, mockReputationToken, initializedMarket, mockStakeTokenFactory, mockReportingWindow, mockUniverse, constants, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow)
    chain.head_state.timestamp = mockNextReportingWindow.getEndTime() - 1

    mockLastDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockLastDisputeBond');
    mockDisputeBondFactory.setCreateDisputeBond(mockLastDisputeBond.address)
    bondAmount = constants.LAST_REPORTERS_DISPUTE_BOND_AMOUNT()
    extraPaidOut = initializedMarket.getExtraDisputeBondRemainingToBePaidOut()
    totalStake = initializedMarket.getTotalStake()
    mockReputationToken.reset()
    mockNextReportingWindow.setIsDisputeActive(True)

    mockForkReportingWindow.setEndTime(mockNextReportingWindow.getEndTime() + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    mockForkReportingWindow.setReputationToken(mockReputationToken.address)
    mockForkReportingWindow.setUniverse(mockUniverse.address)
    mockUniverse.setReportingWindowForForkEndTime(mockForkReportingWindow.address)
    mockForkReportingWindow.setIsDisputeActive(True)

    assert initializedMarket.disputeLastReporters(sender=tester.k0)
    assert initializedMarket.getReportingWindow() == mockForkReportingWindow.address
    assert initializedMarket.getReportingState() == constants.LAST_DISPUTE()

# create stake token and association with market
def set_mock_stake_token_value(localFixture, initializedMarket, payoutDesignatedNumerators, mockStakeTokenFactory, value):
    payoutDesignatedHashValue = initializedMarket.derivePayoutDistributionHash(payoutDesignatedNumerators, False)
    newMockStakeToken = localFixture.upload('solidity_test_helpers/MockStakeToken.sol', str(payoutDesignatedHashValue));
    newMockStakeToken.setPayoutDistributionHash(payoutDesignatedHashValue)
    mockStakeTokenFactory.setStakeToken(payoutDesignatedHashValue, newMockStakeToken.address)
    assert initializedMarket.getOrCreateStakeToken(payoutDesignatedNumerators, False) == newMockStakeToken.address
    newMockStakeToken.setTotalSupply(value)
    newMockStakeToken.setIsValid(True)
    return newMockStakeToken

def set_mock_reporting_window(localFixture, initializedMarket, mockUniverse, mockReputationToken, endTime):
    mockReportingWindowCreated = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol');
    mockReportingWindowCreated.setReputationToken(mockReputationToken.address)
    mockReportingWindowCreated.setUniverse(mockUniverse.address)
    if endTime:
        mockReportingWindowCreated.setEndTime(endTime)
    return mockReportingWindowCreated

def push_first_dispute_last_reporting(localFixture, chain, mockReputationToken, initializedMarket, mockStakeTokenFactory, mockReportingWindow, mockUniverse, constants, mockDisputeBond, mockDisputeBondFactory, mockNextReportingWindow):
    mockReportingWindow.setEndTime(chain.head_state.timestamp + constants.DESIGNATED_REPORTING_DURATION_SECONDS())
    chain.head_state.timestamp = initializedMarket.getDesignatedReportDisputeDueTimestamp() - 1

    mockDisputeStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, [0, 0, 0, numTicks, 0], mockStakeTokenFactory, 10)

    mockReportingWindow.setIsDisputeActive(True)

    mockDesignatedDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockDesignatedDisputeBond');
    mockDisputeBondFactory.setCreateDisputeBond(mockDesignatedDisputeBond.address)
    assert mockReportingWindow.getReputationToken() == mockReputationToken.address
    assert initializedMarket.getReportingState() == constants.DESIGNATED_DISPUTE()

    assert initializedMarket.disputeDesignatedReport([0, 0, 0, numTicks, 0], 100, False, sender=tester.k2)
    assert initializedMarket.getReportingState() == constants.FIRST_DISPUTE()

    mockFirstDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBond.sol', 'mockFirstDisputeBond');
    mockDisputeBondFactory.setCreateDisputeBond(mockFirstDisputeBond.address)

    mockUniverse.setNextReportingWindow(mockNextReportingWindow.address)
    mockDisputeStakeToken = set_mock_stake_token_value(localFixture, initializedMarket, [0, 0, 0, 0, numTicks], mockStakeTokenFactory, 1000)

    # execute disputeFirstReporters on market
    assert initializedMarket.disputeFirstReporters([0, 0, 0, 0, numTicks], 50, False, sender=tester.k4)
    assert initializedMarket.getReportingWindow() == mockNextReportingWindow.address
    chain.head_state.timestamp = mockNextReportingWindow.getEndTime() - 1
    assert initializedMarket.getReportingState() == constants.LAST_REPORTING()

def push_to_designated_dispute_state(localFixture, mockUniverse, chain, initializedMarket, mockStakeToken, payoutDesignatedNumerators, mockStakeTokenFactory, mockReportingWindow, mockReputationToken, constants):
    chain.head_state.timestamp = initializedMarket.getDesignatedReportDueTimestamp() - 1
    payoutDesignatedHashValue = initializedMarket.derivePayoutDistributionHash(payoutDesignatedNumerators, False)
    mockStakeToken.setPayoutDistributionHash(payoutDesignatedHashValue)
    mockStakeTokenFactory.setStakeToken(payoutDesignatedHashValue, mockStakeToken.address)
    assert initializedMarket.getReportingState() == constants.DESIGNATED_REPORTING()

    assert initializedMarket.getOrCreateStakeToken(payoutDesignatedNumerators, False)
    assert mockStakeTokenFactory.getCreateDistroHashValue() == payoutDesignatedHashValue
    assert mockStakeTokenFactory.getCreateStakeTokenMarketValue() == initializedMarket.address
    assert mockStakeTokenFactory.getCreateStakeTokenPayoutValue() == payoutDesignatedNumerators
    assert initializedMarket.getOrCreateStakeToken(payoutDesignatedNumerators, False) == mockStakeToken.address

    mockReputationToken.setBalanceOf(105)
    ownerBalance = chain.head_state.get_balance(tester.a1)

    assert mockStakeToken.callMarketDesignatedReport(initializedMarket.address)
    assert initializedMarket.getDesignatedReportReceivedTime() == chain.head_state.timestamp
    assert initializedMarket.getTentativeWinningPayoutDistributionHash() == mockStakeToken.getPayoutDistributionHash()
    assert mockReportingWindow.getUpdateMarketPhaseCalled() == True
    assert mockReportingWindow.getNoteDesignatedReport() == True
    assert mockReputationToken.getTransferValueFor(tester.a1) == 105
    assert chain.head_state.get_balance(tester.a1) == ownerBalance
    assert initializedMarket.getReportingState() == constants.DESIGNATED_DISPUTE()

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
    mockStakeTokenFactory = fixture.contracts['MockStakeTokenFactory']

    # pre populate share tokens for max of 8 possible outcomes
    for index in range(8):
        item = fixture.uploadAndAddToController('solidity_test_helpers/MockShareToken.sol', 'newMockShareToken' + str(index));
        mockShareTokenFactory.pushCreateShareToken(item.address)

    controller.registerContract(stringToBytes('Cash'), mockCash.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('ParticipationTokenFactory'), mockReportingParticipationTokenFactory.address, twentyZeros, thirtyTwoZeros)
    controller.registerContract(stringToBytes('ShareTokenFactory'), mockShareTokenFactory.address, twentyZeros, thirtyTwoZeros)
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
def initializedMarket(localFixture, mockReportingWindow, mockUniverse, mockReputationToken, chain, constants, mockCash, mockNextReportingWindow):
    market = localFixture.upload('../source/contracts/reporting/Market.sol', 'market')
    contractMap = localFixture.upload('../source/contracts/libraries/collections/Map.sol', 'Map')
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
