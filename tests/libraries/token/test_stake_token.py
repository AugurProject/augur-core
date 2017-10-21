from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes, bytesToHexString
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed
from reporting_utils import proceedToDesignatedReporting, proceedToFirstReporting, proceedToLastReporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture


def test_stake_token_creation_binary(localFixture, mockMarket):
    numTicks = 10 ** 18
    mockMarket.setNumberOfOutcomes(2)
    mockMarket.setNumTicks(numTicks)
    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')

    with raises(TransactionFailed, message="payout numerators can not be more than market"):
        stakeToken.initialize(mockMarket.address, [0, 1, numTicks -1])

    with raises(TransactionFailed, message="payout numerators need to add up to market numTicks"):
        stakeToken.initialize(mockMarket.address, [0, 1, numTicks])

    # outcomes are correct
    assert stakeToken.initialize(mockMarket.address, [0, numTicks], False)        
    assert stakeToken.isValid()

    assert stakeToken.getPayoutNumerator(0) == 0
    assert stakeToken.getPayoutNumerator(1) == numTicks
    assert stakeToken.isValid()

    with raises(TransactionFailed, message="Stake Token has only 3 payoutNumerators"):
        stakeToken.getPayoutNumerator(2)

def test_stake_token_creation_category(localFixture, mockMarket):
    numTicks = 3 * 10 ** 17
    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    mockMarket.setNumTicks(numTicks)
    mockMarket.setNumberOfOutcomes(3)

    with raises(TransactionFailed, message="payout numerators can not be more than market"):
        stakeToken.initialize(mockMarket.address, [0, numTicks])

    assert stakeToken.initialize(mockMarket.address, [0, 1, numTicks - 1])        
    assert stakeToken.getPayoutNumerator(0) == 0
    assert stakeToken.getPayoutNumerator(1) == 1
    assert stakeToken.getPayoutNumerator(2) == numTicks - 1

    with raises(TransactionFailed, message="Stake Token has only 3 payoutNumerators"):
        stakeToken.getPayoutNumerator(3)

def test_stake_token_getters(localFixture, mockMarket, mockUniverse, mockReportingWindow, mockReputationToken):
    numTicks = 3 * 10 ** 17
    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    mockMarket.setNumTicks(numTicks)
    mockMarket.setNumberOfOutcomes(3)

    assert stakeToken.initialize(mockMarket.address, [0, 1, numTicks - 1], False)        
    assert stakeToken.getTypeName() == stringToBytes("StakeToken")
    assert stakeToken.getUniverse() == mockUniverse.address
    assert stakeToken.getMarket() == mockMarket.address
    assert stakeToken.getPayoutDistributionHash() == mockMarket.derivePayoutDistributionHash([0, 1, numTicks - 1], False)
    assert stakeToken.getReportingWindow() == mockMarket.getReportingWindow()
    assert stakeToken.getReputationToken() == mockReportingWindow.getReputationToken()
    assert stakeToken.isValid()

def test_stake_token_valid_checks(localFixture, mockMarket, mockUniverse):
    numTicks = 3 * 10 ** 17
    mockMarket.setNumTicks(numTicks)
    mockMarket.setNumberOfOutcomes(5)
    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [numTicks/5, numTicks/5, numTicks/5, numTicks/5, numTicks/5], False)
    assert stakeToken.isValid()

    with raises(AttributeError, message="method not reachable because it's private"):
        stakeToken.isInvalidOutcome()

    with raises(TransactionFailed, message="Stake Token can not be initialized invalid"):
        stakeToken.initialize(mockMarket.address, [numTicks/5, numTicks/5, numTicks/5, numTicks/5, numTicks/5], True)

def test_stake_token_buy_no_report_state(localFixture, mockMarket, mockUniverse):
    numTicks = 3 * 10 ** 17
    mockMarket.setNumTicks(numTicks)
    mockMarket.setNumberOfOutcomes(3)

    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [numTicks/3, numTicks/3, numTicks/3], False)

    mockMarket.setIsContainerForStakeToken(False)
    with raises(TransactionFailed, message="Stake Token can not be bought, not assoc. to market"):
        stakeToken.buy(1) 

    mockMarket.setDesignatedReport(True)
    mockMarket.setIsContainerForStakeToken(True)
    mockMarket.setReportingState(localFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()) 
    mockUniverse.setDesignatedReportStake(100);
    assert stakeToken.buy(1)
    assert stakeToken.balanceOf(tester.a0) == 1
    
def test_stake_token_buy_check_state(localFixture, mockMarket, mockReportingWindow):
    numTicks = 3 * 10 ** 17
    mockMarket.setNumTicks(numTicks)
    mockMarket.setNumberOfOutcomes(3)

    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [numTicks/3, numTicks/3, numTicks/3], False)
    mockMarket.setReportingState(localFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()) 
    assert stakeToken.buy(1)
    mockMarket.setReportingState(localFixture.contracts['Constants'].FIRST_REPORTING()) 
    assert stakeToken.buy(1)
    mockMarket.setReportingState(localFixture.contracts['Constants'].LAST_REPORTING()) 
    assert stakeToken.buy(1)
    
    mockMarket.setReportingState(localFixture.contracts['Constants'].PRE_REPORTING())
    with raises(TransactionFailed, message="market not in correct state, PRE_REPORTING"):
        stakeToken.buy(1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].DESIGNATED_REPORTING())
    with raises(TransactionFailed, message="market not in correct state, DESIGNATED_REPORTING"):
        stakeToken.buy(1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].DESIGNATED_DISPUTE())
    with raises(TransactionFailed, message="market not in correct state, DESIGNATED_DISPUTE"):
        stakeToken.buy(1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].AWAITING_FORK_MIGRATION())
    with raises(TransactionFailed, message="market not in correct state, AWAITING_FORK_MIGRATION"):
        stakeToken.buy(1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].FIRST_DISPUTE())
    with raises(TransactionFailed, message="market not in correct state, FIRST_DISPUTE"):
        stakeToken.buy(1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].LAST_DISPUTE()) 
    with raises(TransactionFailed, message="market not in correct state, LAST_DISPUTE"):
        stakeToken.buy(1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].FORKING()) 
    with raises(TransactionFailed, message="market not in correct state, FORKING"):
        stakeToken.buy(1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].AWAITING_FINALIZATION()) 
    with raises(TransactionFailed, message="market not in correct state, AWAITING_FINALIZATION"):
        stakeToken.buy(1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    with raises(TransactionFailed, message="market not in correct state, FINALIZED"):
        stakeToken.buy(1)

def test_stake_token_buy_designated_reporter_state(localFixture, mockMarket, mockUniverse, mockReputationToken, mockReportingWindow):    
    numTicks = 3 * 10 ** 17
    mockMarket.setNumTicks(numTicks)
    mockMarket.setNumberOfOutcomes(3)
    mockMarket.setIsContainerForStakeToken(True)
    mockMarket.setDerivePayoutDistributionHash(stringToBytes("1"))
    mockMarket.setDesignatedReport(True)
    mockReportingWindow.setNoteReportingGasPrice(True)

    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [numTicks/3, numTicks/3, numTicks/3], False)
    designatedReporterStake = 100
    mockUniverse.setDesignatedReportStake(designatedReporterStake)

    mockMarket.setReportingState(localFixture.contracts['Constants'].DESIGNATED_REPORTING()) 
    with raises(TransactionFailed, message="Designated reporter needs to buy DESIGNATED REPORTER bond not more"):
        stakeToken.buy(designatedReporterStake + 1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].DESIGNATED_REPORTING()) 
    with raises(TransactionFailed, message="Designated reporter needs to buy DESIGNATED REPORTER bond not less"):
        stakeToken.buy(designatedReporterStake - 1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].DESIGNATED_REPORTING()) 
    with raises(TransactionFailed, message="Only Designated reporter can buy stake during designated reporting window"):
        stakeToken.buy(designatedReporterStake, sender=tester.k8)

    mockMarket.setReportingState(localFixture.contracts['Constants'].DESIGNATED_REPORTING()) 
    assert stakeToken.buy(designatedReporterStake)

    # call tests
    assert mockMarket.getUpdateDerivePayoutDistributionHashValue() == stringToBytes("1")
    assert mockReputationToken.getTrustedTransferSourceValue() == bytesToHexString(tester.a0)
    assert mockReputationToken.getTrustedTransferDestinationValue() == stakeToken.address
    assert mockReputationToken.getTrustedTransferAttotokensValue() == designatedReporterStake


def test_stake_token_redeem(localFixture, mockMarket, mockReputationToken, mockReportingWindow):
    numTicks = 10 ** 18
    mockMarket.setNumberOfOutcomes(2)
    mockMarket.setNumTicks(numTicks)
    mockMarket.setIsContainerForStakeToken(True)
    mockMarket.setDerivePayoutDistributionHash(stringToBytes("1"))
    mockMarket.setDesignatedReport(True)
    mockReportingWindow.setNoteReportingGasPrice(True)
    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [0, numTicks], False)      
    
    mockMarket.setReportingState(localFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()) 
    assert stakeToken.buy(10)
    assert stakeToken.buy(20, sender=tester.k2)
    
    mockReputationToken.setBalanceOf(1000)
    mockMarket.setIsContainerForStakeToken(False)

    assert stakeToken.redeemDisavowedTokens(tester.a0)
    assert mockReputationToken.getTransferToValue() == bytesToHexString(tester.a0)
    # 1000 * 10 / 30 = 333
    assert mockReputationToken.getTransferValueValue() == 333

    assert stakeToken.redeemDisavowedTokens(tester.a2)
    assert mockReputationToken.getTransferToValue() == bytesToHexString(tester.a2)
    # 1000 * 20 / 20 = 1000
    assert mockReputationToken.getTransferValueValue() == 1000

    assert stakeToken.balanceOf(tester.a0) == 0
    assert stakeToken.balanceOf(tester.a2) == 0

    mockMarket.setIsContainerForStakeToken(True)
    with raises(TransactionFailed, message="market should not contain stake token"):
        stakeToken.redeemDisavowedTokens(tester.a0)

def test_stake_token_trusted_buy_fails(localFixture, binaryMarket):
    numTicks = 10 ** 18
    market = binaryMarket
    universe = localFixture.applySignature('Universe', market.getUniverse())
    stakeToken = localFixture.getStakeToken(market, [0, numTicks])
    reportingWindow = localFixture.applySignature('ReportingWindow', market.getReportingWindow())

    with raises(TransactionFailed, message="only market can call this method"):
        stakeToken.trustedBuy(tester.a2, 1)

    proceedToFirstReporting(localFixture, universe, market, False, tester.a1, [numTicks, 0], [numTicks/2, numTicks/2])
    assert market.getReportingState() == localFixture.contracts['Constants'].FIRST_REPORTING()

    with raises(TransactionFailed, message="trusted buy can only occur buy trusted contract"):
        stakeToken.trustedBuy(tester.a2, 1)

    with raises(Exception, message="address isn't in format that can be used as Market"):
        stakeToken.trustedBuy(tester.a2, 1, sender=market.address)

def test_stake_token_verify_trusted_buy(localFixture, mockUniverse, mockMarket, mockReportingWindow, mockReputationToken):
    numTicks = 10 ** 18
    mockMarket.setNumberOfOutcomes(2)
    mockMarket.setNumTicks(numTicks)

    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [0, numTicks], False)       
    
    mockMarket.setReportingState(localFixture.contracts['Constants'].PRE_REPORTING()) 
    with raises(Exception, message="market can't call trust buy unless market state is first or last"):
        mockMarket.callStakeTokenTrustedBuy(stakeToken, tester.a1, 1)

    # call stake token successfully
    mockMarket.setReportingState(localFixture.contracts['Constants'].FIRST_REPORTING()) 
    assert mockMarket.callStakeTokenTrustedBuy(stakeToken.address, tester.a1, 1)
    mockMarket.setReportingState(localFixture.contracts['Constants'].LAST_REPORTING()) 
    assert mockMarket.callStakeTokenTrustedBuy(stakeToken.address, tester.a1, 1)

    mockMarket.setReportingState(localFixture.contracts['Constants'].LAST_DISPUTE()) 
    with raises(Exception, message="market can't call trust buy unless market state is first or last"):
        mockMarket.callStakeTokenTrustedBuy(stakeToken, tester.a1, 1)

def test_stake_token_verify_redeem_forked_tokens(localFixture, mockUniverse, mockMarket, mockReportingWindow, mockReputationToken):
    numTicks = 10 ** 18
    mockMarket.setNumberOfOutcomes(2)
    mockMarket.setNumTicks(numTicks)

    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [0, numTicks], False)       

    mockMarket.setIsContainerForStakeToken(False)
    with raises(TransactionFailed, message="market does not contain stake token"):
        stakeToken.redeemForkedTokens(sender = tester.k0)
    
    mockMarket.setIsContainerForStakeToken(True)
    with raises(TransactionFailed, message="market is not forking"):
        stakeToken.redeemForkedTokens(sender = tester.k0)
    
    # wire up child Universe
    mockChildUniverse = localFixture.upload('solidity_test_helpers/MockUniverse.sol', 'mockChildUniverse')
    mockChildReputationToken = localFixture.upload('solidity_test_helpers/MockReputationToken.sol', 'mockChildReputationToken')
    mockChildReportingWindow = localFixture.upload('solidity_test_helpers/MockReportingWindow.sol', 'mockChildReportingWindow')

    mockChildReportingWindow.setUniverse(mockChildUniverse.address)
    mockUniverse.setForkingMarket(mockMarket.address)
    mockChildReportingWindow.setReputationToken(mockChildReputationToken.address)
    mockUniverse.setOrCreateChildUniverse(mockChildUniverse.address)
    mockChildUniverse.setReputationToken(mockChildReputationToken.address)
    mockReputationToken.setBalanceOf(1000)
    mockMarket.setReportingState(localFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()) 
    assert stakeToken.buy(10, sender=tester.k0)
    assert stakeToken.buy(20, sender=tester.k2)

    stakeToken.redeemForkedTokens(sender=tester.k0)
    assert mockChildReputationToken.getTransferToValue() == bytesToHexString(tester.a0)
    # 1000 * 10 / 30 = 333
    assert mockChildReputationToken.getTransferValueValue() == 333

    assert mockReputationToken.getMigrateOutDestinationValue() == mockChildReputationToken.address
    assert mockReputationToken.getMigrateOutReporterValue() == stakeToken.address
    assert mockReputationToken.getMigrateOutAttoTokens() == 10

    assert stakeToken.balanceOf(tester.a0) == 0

    stakeToken.redeemForkedTokens(sender=tester.k2)
    assert mockChildReputationToken.getTransferToValue() == bytesToHexString(tester.a2)
    # 1000 * 20 / 20 = 1000
    assert mockChildReputationToken.getTransferValueValue() == 1000

    assert mockReputationToken.getMigrateOutDestinationValue() == mockChildReputationToken.address
    assert mockReputationToken.getMigrateOutReporterValue() == stakeToken.address
    assert mockReputationToken.getMigrateOutAttoTokens() == 20

    assert stakeToken.balanceOf(tester.a2) == 0
    assert stakeToken.totalSupply() == 0

def test_stake_token_verify_redeem_winning_tokens(localFixture, mockUniverse, mockMarket, mockReportingWindow, mockReputationToken):
    numTicks = 10 ** 18
    mockMarket.setNumberOfOutcomes(2)
    mockMarket.setNumTicks(numTicks)

    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [0, numTicks], False)       
    mockMarket.setReportingState(localFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()) 
    mockMarket.setIsContainerForStakeToken(True)

    with raises(TransactionFailed, message="market is not finialized"):
        stakeToken.redeemWinningTokens(True)

    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    mockMarket.setIsContainerForStakeToken(False)
    with raises(TransactionFailed, message="market does not contain this stake token"):
        stakeToken.redeemWinningTokens(True)

    mockMarket.setIsContainerForStakeToken(True)
    mockUniverse.setForkingMarket(mockMarket.address)
    with raises(TransactionFailed, message="market is in fork"):
        stakeToken.redeemWinningTokens(True)
    
    mockUniverse.setForkingMarket()
    mockMarket.setFinalWinningStakeToken()
    with raises(TransactionFailed, message="this stake token isn't market final winning stake token"):
        stakeToken.redeemWinningTokens(True)
    
    mockReportingWindow.setAllMarketsFinalized(False)
    with raises(TransactionFailed, message="can not forgo fees until all markets are finalized"):
        stakeToken.redeemWinningTokens(False)
    
    mockMarket.setFinalWinningStakeToken(stakeToken.address)
    mockReportingWindow.setAllMarketsFinalized(True)    
    
    mockMarket.setReportingState(localFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()) 
    mockReputationToken.setBalanceOf(1000)
    assert stakeToken.buy(10, sender=tester.k0)
    assert stakeToken.buy(20, sender=tester.k2)

    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    assert stakeToken.redeemWinningTokens(False, sender=tester.k0)
    assert mockReputationToken.getTransferToValue() == bytesToHexString(tester.a0)
    # 1000 * 10 / 30 = 333
    assert mockReputationToken.getTransferValueValue() == 333
    assert mockReportingWindow.getCollectReporterAddress() == bytesToHexString(tester.a0)
    assert mockReportingWindow.getCollectAttoStakeTokens() == 10
    assert mockReportingWindow.getCollectForgoFees() == False
    assert stakeToken.balanceOf(tester.a0) == 0

    # user has no stake tokens
    mockReputationToken.resetTransferToValues()
    assert stakeToken.redeemWinningTokens(False, sender=tester.k5)
    assert mockReputationToken.getTransferToValue() == "0x0000000000000000000000000000000000000000"
    assert mockReputationToken.getTransferValueValue() == 0
    assert mockReportingWindow.getCollectReporterAddress() == bytesToHexString(tester.a5)
    assert mockReportingWindow.getCollectAttoStakeTokens() == 0
    assert mockReportingWindow.getCollectForgoFees() == False
    assert stakeToken.balanceOf(tester.a5) == 0

    # forgo fees when all markets are finalized
    assert stakeToken.redeemWinningTokens(True, sender=tester.k2)
    assert mockReputationToken.getTransferToValue() == bytesToHexString(tester.a2)
    # 1000 * 20 / 20 = 1000
    assert mockReputationToken.getTransferValueValue() == 1000
    assert mockReportingWindow.getCollectReporterAddress() == bytesToHexString(tester.a2)
    assert mockReportingWindow.getCollectAttoStakeTokens() == 20
    assert mockReportingWindow.getCollectForgoFees() == True
    assert stakeToken.balanceOf(tester.a2) == 0

    assert stakeToken.totalSupply() == 0

def test_stake_token_migrate_losing_tokens(localFixture, mockUniverse, mockMarket, mockReportingWindow, mockReputationToken, mockDisputeBondToken):
    numTicks = 10 ** 18
    mockMarket.setNumberOfOutcomes(2)
    mockMarket.setNumTicks(numTicks)

    stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [0, numTicks], False)       
    
    winning_stakeToken = localFixture.upload('../source/contracts/reporting/StakeToken.sol', 'winning_stakeToken')
    assert winning_stakeToken.initialize(mockMarket.address, [numTicks, 0], False)       

    mockMarket.setReportingState(localFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()) 
    with raises(TransactionFailed, message="market is not finialized"):
        stakeToken.migrateLosingTokens()

    mockMarket.setReportingState(localFixture.contracts['Constants'].FINALIZED()) 
    mockMarket.setIsContainerForStakeToken(False)
    with raises(TransactionFailed, message="market does not contain this stake token"):
        stakeToken.migrateLosingTokens()

    mockMarket.setIsContainerForStakeToken(True)
    mockUniverse.setForkingMarket(mockMarket.address)
    with raises(TransactionFailed, message="market is in fork"):
        stakeToken.migrateLosingTokens()
    
    mockUniverse.setForkingMarket()
    mockMarket.setFinalWinningStakeToken(stakeToken.address)
    with raises(TransactionFailed, message="can not migrate losing tokens on final winning stake token"):
        stakeToken.migrateLosingTokens()
    
    designatedRepoertDisputeBond = mockDisputeBondToken
    firstDisputeBond = localFixture.upload('solidity_test_helpers/MockDisputeBondToken.sol', 'firstDisputeBond')

    # no dispute bonds, no transfer
    mockReputationToken.setBalanceOf(0)
    mockMarket.setDesignatedReporterDisputeBondToken()
    mockMarket.setFirstReportersDisputeBondToken()
    mockMarket.setFinalWinningStakeToken()
    mockReputationToken.resetTransferToValues()
    assert stakeToken.migrateLosingTokens()
    assert mockReputationToken.getTransferToValue() == "0x0000000000000000000000000000000000000000"
    assert mockReputationToken.getTransferValueValue() == 0

    # only designated reporting dispute bond payout distribution hash same
    # no first dispute bond
    mockMarket.setDesignatedReporterDisputeBondToken(designatedRepoertDisputeBond.address)
    mockMarket.setFinalPayoutDistributionHash(stringToBytes("101"))
    designatedRepoertDisputeBond.setDisputedPayoutDistributionHash(stringToBytes("101"))
    assert stakeToken.migrateLosingTokens()

    # only designated reporting dispute bond payout distribution hash different hash value
    # stake token rep balance is 0
    mockReputationToken.resetTransferToValues()
    designatedRepoertDisputeBond.setDisputedPayoutDistributionHash(stringToBytes("99"))
    designatedRepoertDisputeBond.setBondRemainingToBePaidOut(0)
    mockReputationToken.setBalanceOf(0)
    assert stakeToken.migrateLosingTokens()
    assert mockReputationToken.getTransferToValue() == "0x0000000000000000000000000000000000000000"
    assert mockReputationToken.getTransferValueValue() == 0

    # only designated reporting displute bond
    # paid out bond == dispute bond
    mockReputationToken.resetTransferToValues()
    mockReputationToken.resetBalanceOfValues()
    mockMarket.setDesignatedReporterDisputeBondToken(designatedRepoertDisputeBond.address)
    mockMarket.setFinalWinningStakeToken(winning_stakeToken.address)
    designatedRepoertDisputeBond.setBondRemainingToBePaidOut(300)
    mockReputationToken.setBalanceOfValueFor(designatedRepoertDisputeBond.address, 300)
    mockReputationToken.setBalanceOf(8)

    assert stakeToken.migrateLosingTokens()
    assert mockReputationToken.getTransferValueFor(designatedRepoertDisputeBond.address) == 0
    # winning stake gets balance
    assert mockReputationToken.getTransferValueFor(winning_stakeToken.address) == 8

    mockReputationToken.resetTransferToValues()
    mockReputationToken.resetBalanceOfValues()

    # only designated reporting displute bond
    # dispute bond not paid out
    mockReputationToken.resetTransferToValues()
    mockReputationToken.resetBalanceOfValues()
    mockMarket.setDesignatedReporterDisputeBondToken(designatedRepoertDisputeBond.address)
    mockMarket.setFinalWinningStakeToken(winning_stakeToken.address)
    designatedRepoertDisputeBond.setBondRemainingToBePaidOut(300)
    mockReputationToken.setBalanceOfValueFor(designatedRepoertDisputeBond.address, 0)
    mockReputationToken.setBalanceOfValueFor(stakeToken.address, 1000)

    assert stakeToken.migrateLosingTokens()
    assert mockReputationToken.getTransferValueFor(designatedRepoertDisputeBond.address) == 300
    assert mockReputationToken.getTransferValueFor(winning_stakeToken.address) == 1000

    mockReputationToken.resetTransferToValues()
    mockReputationToken.resetBalanceOfValues()

    # only first dispute bond
    mockMarket.setDesignatedReporterDisputeBondToken()
    firstDisputeBond.setDisputedPayoutDistributionHash(stringToBytes("111"))
    mockMarket.setFinalWinningStakeToken(winning_stakeToken.address)
    firstDisputeBond.setBondRemainingToBePaidOut(55)
    mockMarket.setFirstReportersDisputeBondToken(firstDisputeBond.address)
    mockReputationToken.setBalanceOfValueFor(stakeToken.address, 99)
    mockReputationToken.setBalanceOfValueFor(firstDisputeBond.address, 12)

    assert stakeToken.migrateLosingTokens()
    assert mockReputationToken.getTransferValueFor(firstDisputeBond.address) == 43
    assert mockReputationToken.getTransferValueFor(winning_stakeToken.address) == 99

    # designated reporter bond and first dispute bond
    mockReputationToken.resetTransferToValues()
    mockReputationToken.resetBalanceOfValues()

    mockMarket.setDesignatedReporterDisputeBondToken(designatedRepoertDisputeBond.address)
    mockMarket.setFinalWinningStakeToken(winning_stakeToken.address)
    mockMarket.setFirstReportersDisputeBondToken(firstDisputeBond.address)
    # set values for math
    designatedRepoertDisputeBond.setBondRemainingToBePaidOut(300)
    firstDisputeBond.setBondRemainingToBePaidOut(65)
    mockReputationToken.setBalanceOfValueFor(designatedRepoertDisputeBond.address, 22)
    mockReputationToken.setBalanceOfValueFor(firstDisputeBond.address, 32)
    mockReputationToken.setBalanceOfValueFor(stakeToken.address, 120)
    assert stakeToken.migrateLosingTokens()
    # stake token has lower balance
    assert mockReputationToken.getTransferValueFor(designatedRepoertDisputeBond.address) == 120
    assert mockReputationToken.getTransferValueFor(firstDisputeBond.address) == 33
    # gets the rest of the reputation tokens 
    assert mockReputationToken.getTransferValueFor(winning_stakeToken.address) == 120

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    fixture.uploadAndAddToController('solidity_test_helpers/MockMarket.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockReportingWindow.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockUniverse.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockReputationToken.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockDisputeBondToken.sol')
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    value = 1 * 10**6 * 10**18
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    # Give tester reputation tokens
    for testAccount in [tester.a4, tester.a5, tester.a6, tester.a7, tester.a8, tester.a9]:
        reputationToken.transfer(testAccount, value)

    return initializeReportingFixture(fixture, universe, market)

@fixture
def universe(localFixture, chain, kitchenSinkSnapshot):
    universe = ABIContract(chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    return universe

@fixture
def binaryMarket(localFixture, chain, kitchenSinkSnapshot):
    market = ABIContract(chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    return market

@fixture
def cash(localFixture, chain, kitchenSinkSnapshot):
    cash = ABIContract(chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
    return cash

@fixture
def categoricalMarket(localFixture, chain, kitchenSinkSnapshot):
    market = ABIContract(chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)
    return market

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def chain(localFixture):
    return localFixture.chain

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
def mockDisputeBondToken(localFixture):
    mockDisputeBondToken = localFixture.contracts['MockDisputeBondToken']
    return mockDisputeBondToken

@fixture
def mockReportingWindow(localFixture, mockUniverse, mockReputationToken):
    # wire up mock reporting window    
    mockReportingWindow = localFixture.contracts['MockReportingWindow']
    mockReportingWindow.setReputationToken(mockReputationToken.address)
    mockReportingWindow.setUniverse(mockUniverse.address)
    mockReportingWindow.setIsContainerForMarket(True)
    mockReportingWindow.setNoteReportingGasPrice(True)
    return mockReportingWindow

@fixture
def mockMarket(localFixture, mockUniverse, mockReportingWindow):
    # wire up mock market
    mockMarket = localFixture.contracts['MockMarket']
    mockMarket.setDesignatedReporter(bytesToHexString(tester.a0))
    mockMarket.setUniverse(mockUniverse.address)
    mockMarket.setReportingWindow(mockReportingWindow.address)
    mockMarket.setIsContainerForStakeToken(True)
    mockMarket.setMigrateDueToNoReports(True)
    mockMarket.setMigrateDueToNoReportsNextState(localFixture.contracts['Constants'].FIRST_REPORTING())
    mockMarket.setFirstReporterCompensationCheck(0)
    mockMarket.setDerivePayoutDistributionHash(stringToBytes("1"))
    return mockMarket
