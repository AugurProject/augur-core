from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes
from pytest import fixture, raises
from ethereum.tools.tester import TransactionFailed
from reporting_utils import proceedToDesignatedReporting, proceedToRound1Reporting, proceedToRound2Reporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture


def test_reporting_token_creation_binary(tokenFixture):
    bin_market = tokenFixture.binaryMarket
    numTicks = 10 ** 18
    reportingToken_bin = tokenFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'reportingToken')
    # reporting token needs same payout numerators as market
    with raises(TransactionFailed, message="payout numerators can not be more than market"):
        reportingToken_bin.initialize(bin_market.address, [0, 1, numTicks -1])
    # reporting token outcomes are incorrect, payout numerators need to add up to numTicks    
    with raises(TransactionFailed, message="payout numerators need to add up to market numTicks"):
        reportingToken_bin.initialize(bin_market.address, [0, 1, numTicks])

    # outcomes are correct
    assert reportingToken_bin.initialize(bin_market.address, [0, numTicks], False)        
    assert reportingToken_bin.isValid()

    assert reportingToken_bin.getPayoutNumerator(0) == 0
    assert reportingToken_bin.getPayoutNumerator(1) == numTicks
    assert reportingToken_bin.isValid()
    # can not get more reporting token payout numerators than exists
    with raises(TransactionFailed, message="Reporting Token has only 3 payoutNumerators"):
        reportingToken_bin.getPayoutNumerator(2)

def test_reporting_token_creation_category(tokenFixture):
    reportingToken_cat = tokenFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'reportingToken')
    cat_market = tokenFixture.categoricalMarket
    numTicks = 3 * 10 ** 17
    # reporting token needs same payout numerators as market
    with raises(TransactionFailed, message="payout numerators can not be more than market"):
        reportingToken_cat.initialize(cat_market.address, [0, numTicks])

    assert reportingToken_cat.initialize(cat_market.address, [0, 1, numTicks - 1])        
    assert reportingToken_cat.getPayoutNumerator(0) == 0
    assert reportingToken_cat.getPayoutNumerator(1) == 1
    assert reportingToken_cat.getPayoutNumerator(2) == numTicks - 1
    # can not get more reporting token payout numerators than exists
    with raises(TransactionFailed, message="Reporting Token has only 3 payoutNumerators"):
        reportingToken_cat.getPayoutNumerator(3)

def test_reporting_token_getters(tokenFixture):
    reportingToken = tokenFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'reportingToken')
    market = tokenFixture.categoricalMarket

    numTicks = 3 * 10 ** 17
    assert reportingToken.initialize(market.address, [0, 1, numTicks - 1], False)        
    assert reportingToken.getTypeName() == stringToBytes("ReportingToken")
    assert reportingToken.getUniverse() == tokenFixture.universe.address
    assert reportingToken.getMarket() == market.address
    assert reportingToken.getPayoutDistributionHash() == market.derivePayoutDistributionHash([0, 1, numTicks - 1], False)
    assert reportingToken.getReportingWindow() == market.getReportingWindow()
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert reportingToken.getReputationToken() == reportingWindow.getReputationToken()
    assert reportingToken.isValid()

def test_reporting_token_valid_checks(tokenFixture):
    reportingToken = tokenFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'reportingToken')
    market = tokenFixture.createReasonableCategoricalMarket(tokenFixture.universe, 5, tokenFixture.cash)
    numTicks = 3 * 10 ** 17
    assert reportingToken.initialize(market.address, [numTicks/5, numTicks/5, numTicks/5, numTicks/5, numTicks/5], False)
    assert reportingToken.isValid()

    with raises(TransactionFailed, message="Reporting Token can not be initialized invalid"):
        reportingToken.initialize(market.address, [numTicks/5, numTicks/5, numTicks/5, numTicks/5, numTicks/5], True)

def test_reporting_token_buy_no_report_state(tokenFixture):
    numTicks = 3 * 10 ** 17
    testerAddress = tester.a0
    market = tokenFixture.createReasonableCategoricalMarket(tokenFixture.universe, 3, tokenFixture.cash)
    reportingToken = tokenFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'reportingToken')
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())

    assert reportingToken.initialize(market.address, [numTicks/3, numTicks/3, numTicks/3], False)
    # Reporting token not associated with market fails
    with raises(TransactionFailed, message="Reporting Token can not be bought, not assoc. to market"):
        reportingToken.buy(1) 

    tokenFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == tokenFixture.constants.AWAITING_NO_REPORT_MIGRATION()

    reportingToken = tokenFixture.applySignature('ReportingToken', market.getReportingToken([0, 0, numTicks]))
    designatedReporterStake = tokenFixture.universe.getDesignatedReportStake()
    originalTesterBalance = reportingToken.balanceOf(testerAddress)
    newTesterBalance = originalTesterBalance + 1 + designatedReporterStake
    assert reportingToken.buy(1)
    assert reportingToken.balanceOf(testerAddress) == newTesterBalance
    
def test_reporting_token_buy_get_more(tokenFixture):
    numTicks = 3 * 10 ** 17
    testerAddress = tester.a0
    market = tokenFixture.createReasonableCategoricalMarket(tokenFixture.universe, 3, tokenFixture.cash)
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reportingToken = tokenFixture.applySignature('ReportingToken', market.getReportingToken([0, 0, numTicks]))
    tokenFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == tokenFixture.constants.AWAITING_NO_REPORT_MIGRATION()
    reportingToken.buy(1)
    assert market.getReportingState() == tokenFixture.constants.ROUND1_REPORTING()

    #with raises(TransactionFailed, message="Can not buy when market is in AWAITING_NO_REPORT_MIGRATION"):
    #    reportingToken.buy(1)


def test_reporting_token_buy_designated_reporter_state(tokenFixture):    
    market = tokenFixture.categoricalMarket
    testerAddress = tester.a0
    otherAddress = tester.a1
    reputationToken = tokenFixture.applySignature('ReputationToken', tokenFixture.universe.getReputationToken())
    numTicks = 3 * 10 ** 17
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reportingToken = tokenFixture.applySignature('ReportingToken', market.getReportingToken([numTicks/3, numTicks/3, numTicks/3]))
    
    with raises(TransactionFailed, message="Reporter can not buy a token in early market states"):    
        reportingToken.buy(2, sender=tester.k1)

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(tokenFixture, market, [0, 0, numTicks])
    assert market.getReportingState() == tokenFixture.constants.DESIGNATED_REPORTING()

    # Not designated reporter throws error
    with raises(TransactionFailed, message="Only designated reporter can buy a token in DESIGNATED_REPORTING"):
        reportingToken.buy(1, sender=tester.k1)

    # buy not correct amount
    with raises(TransactionFailed, message="Designated reporter needs to buy same as bond amount in DESIGNATED_REPORTING"):
        reportingToken.buy(1)

    designatedReporterStake = tokenFixture.universe.getDesignatedReportStake()
    # need to buy the correct bond amount
    with raises(TransactionFailed, message="Designated reporter needs to buy same as bond amount in DESIGNATED_REPORTING"):
        reportingToken.buy(designatedReporterStake + 1)

    originalTesterBalance = reportingToken.balanceOf(testerAddress)
    newTesterBalance = originalTesterBalance + designatedReporterStake
    assert reportingToken.buy(designatedReporterStake)
    assert reportingToken.balanceOf(testerAddress) == newTesterBalance

def test_reporting_token_redeem(tokenFixture):
    numTicks = 10 ** 18
    denominationToken = tokenFixture.cash
    feePerEthInWei = 10**10
    endTime = long(tokenFixture.chain.head_state.timestamp + timedelta(days=1).total_seconds())
    universe = tokenFixture.universe

    market_other = tokenFixture.createBinaryMarket(universe, endTime, feePerEthInWei, denominationToken, tester.a8, numTicks, tester.k9)
    market_forking = tokenFixture.createBinaryMarket(universe, endTime, feePerEthInWei, denominationToken, tester.a1, numTicks)
    designatedReporterStake = universe.getDesignatedReportStake()
    reputationToken = tokenFixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingToken_other = tokenFixture.getReportingToken(market_other, [0, numTicks])
    original_dr_other = reportingToken_other.balanceOf(tester.a8) 
    original_market_creator_other = reportingToken_other.balanceOf(tester.a9) 

    # Designated Report votes that Market is invalid
    proceedToDesignatedReporting(tokenFixture, market_other, [0, numTicks])
    assert market_other.getReportingState() == tokenFixture.constants.DESIGNATED_REPORTING()
    reportingToken_other.buy(designatedReporterStake, sender=tester.k8)
    assert reportingToken_other.balanceOf(tester.a8) == designatedReporterStake
    assert market_other.isContainerForReportingToken(reportingToken_other.address)

    # kick this market into the DESIGNATED_REPORTING phase
    proceedToDesignatedReporting(tokenFixture, market_forking, [0, numTicks])

    proceedToRound1Reporting(tokenFixture, market_forking, False, tester.a6, [0, numTicks], [numTicks, 0])
    assert market_forking.getReportingState() == tokenFixture.constants.ROUND1_REPORTING()

    proceedToRound2Reporting(tokenFixture, market_forking, False, tester.a6, tester.k3, [numTicks, 0], [0, numTicks], tester.k2, [0, numTicks], [numTicks, 0])
    assert market_forking.getReportingState() == tokenFixture.constants.ROUND2_REPORTING()

    # Proceed to the FORKING phase
    proceedToForking(tokenFixture, market_forking, False, tester.k1, tester.k3, tester.k4, [0,numTicks], [numTicks,0], tester.k2, [numTicks,0], [numTicks,0], [0,numTicks])
    assert market_forking.getReportingState() == tokenFixture.constants.FORKING()

    # Finalize the market
    finalizeForkingMarket(tokenFixture, market_forking, True, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,numTicks], [numTicks,0])
    market_forking.getReportingState() == tokenFixture.constants.FINALIZED()

    # progress to next reporting window
    reportingWindow = tokenFixture.applySignature('ReportingWindow', universe.getNextReportingWindow())
    tokenFixture.chain.head_state.timestamp = market_forking.getEndTime() + 1

    # how does a reporting token not be associated with market
    assert market_other.isContainerForReportingToken(reportingToken_other.address) == False
    assert reportingToken_other.redeemDisavowedTokens(tester.a8)
    assert reportingToken_other.balanceOf(tester.a8) == original_dr_other + designatedReporterStake

    assert reportingToken_other.redeemDisavowedTokens(tester.a9)
    assert reportingToken_other.balanceOf(tester.a8) == original_market_creator_other + designatedReporterStake

    # users of non-forking unresolved markets should get tokens back
    #assert reportingToken_other.redeemDisavowedTokens(tester.a9)
    #assert reportingToken_other.balanceOf(tester.a9) == original_a9
    
    # (Direction) When a market needs to be reset (reporting wise), 
    # all associated dispute bonds and tokens become "disavowed".  
    # This means that anyone who holds the token/bond can redeem it at face value.  
    # No loss, no gain.

@fixture
def sessionSnapshot(contractsFixture):
    contractsFixture.resetSnapshot()
    return contractsFixture.createSnapshot()

@fixture
def tokenFixture(contractsFixture, sessionSnapshot):
    contractsFixture.resetToSnapshot(sessionSnapshot)
    value = 1 * 10**6 * 10**18
    testerAddress = tester.a0
    tester1Address = tester.a1
    reputationToken = contractsFixture.applySignature('ReputationToken', contractsFixture.universe.getReputationToken())
    legacyRepContract = contractsFixture.contracts['LegacyRepContract']
    legacyRepContract.faucet(long(11 * 10**6 * 10**18))
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract()
    # Give tester reputation tokens
    for testAccount in [tester.a1, tester.a2, tester.a3, tester.a4, tester.a5, tester.a6, tester.a7, tester.a8, tester.a9]:
        reputationToken.transfer(testAccount, value)
    return contractsFixture