from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed
from reporting_utils import proceedToDesignatedReporting, proceedToRound1Reporting, proceedToRound2Reporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture


def test_reporting_token_creation_binary(tokenFixture, binaryMarket):
    bin_market = binaryMarket
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

def test_reporting_token_creation_category(tokenFixture, categoricalMarket):
    reportingToken_cat = tokenFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'reportingToken')
    cat_market = categoricalMarket
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

def test_reporting_token_getters(tokenFixture, categoricalMarket, universe):
    reportingToken = tokenFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'reportingToken')
    market = categoricalMarket

    numTicks = 3 * 10 ** 17
    assert reportingToken.initialize(market.address, [0, 1, numTicks - 1], False)        
    assert reportingToken.getTypeName() == stringToBytes("ReportingToken")
    assert reportingToken.getUniverse() == universe.address
    assert reportingToken.getMarket() == market.address
    assert reportingToken.getPayoutDistributionHash() == market.derivePayoutDistributionHash([0, 1, numTicks - 1], False)
    assert reportingToken.getReportingWindow() == market.getReportingWindow()
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert reportingToken.getReputationToken() == reportingWindow.getReputationToken()
    assert reportingToken.isValid()

def test_reporting_token_valid_checks(tokenFixture, universe, cash):
    reportingToken = tokenFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'reportingToken')
    market = tokenFixture.createReasonableCategoricalMarket(universe, 5, cash)
    numTicks = 3 * 10 ** 17
    assert reportingToken.initialize(market.address, [numTicks/5, numTicks/5, numTicks/5, numTicks/5, numTicks/5], False)
    assert reportingToken.isValid()

    with raises(TransactionFailed, message="Reporting Token can not be initialized invalid"):
        reportingToken.initialize(market.address, [numTicks/5, numTicks/5, numTicks/5, numTicks/5, numTicks/5], True)

def test_reporting_token_buy_no_report_state(tokenFixture, universe, cash):
    numTicks = 3 * 10 ** 17
    testerAddress = tester.a0
    market = tokenFixture.createReasonableCategoricalMarket(universe, 3, cash)
    reportingToken = tokenFixture.upload('../source/contracts/reporting/ReportingToken.sol', 'reportingToken')
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())

    assert reportingToken.initialize(market.address, [numTicks/3, numTicks/3, numTicks/3], False)
    # Reporting token not associated with market fails
    with raises(TransactionFailed, message="Reporting Token can not be bought, not assoc. to market"):
        reportingToken.buy(1) 

    tokenFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == tokenFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()

    reportingToken = tokenFixture.applySignature('ReportingToken', market.getReportingToken([0, 0, numTicks]))
    designatedReporterStake = universe.getDesignatedReportStake()
    originalTesterBalance = reportingToken.balanceOf(testerAddress)
    newTesterBalance = originalTesterBalance + 1 + designatedReporterStake
    assert reportingToken.buy(1)
    assert reportingToken.balanceOf(testerAddress) == newTesterBalance
    
def test_reporting_token_buy_get_more(tokenFixture, universe, cash):
    numTicks = 3 * 10 ** 17
    testerAddress = tester.a0
    market = tokenFixture.createReasonableCategoricalMarket(universe, 3, cash)
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reportingToken = tokenFixture.applySignature('ReportingToken', market.getReportingToken([0, 0, numTicks]))
    tokenFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == tokenFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()
    reportingToken.buy(1)
    assert market.getReportingState() == tokenFixture.contracts['Constants'].ROUND1_REPORTING()

    #with raises(TransactionFailed, message="Can not buy when market is in AWAITING_NO_REPORT_MIGRATION"):
    #    reportingToken.buy(1)


def test_reporting_token_buy_designated_reporter_state(tokenFixture, categoricalMarket, universe):    
    market = categoricalMarket
    testerAddress = tester.a0
    otherAddress = tester.a1
    reputationToken = tokenFixture.applySignature('ReputationToken', universe.getReputationToken())
    numTicks = 3 * 10 ** 17
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())
    reportingToken = tokenFixture.applySignature('ReportingToken', market.getReportingToken([numTicks/3, numTicks/3, numTicks/3]))
    
    with raises(TransactionFailed, message="Reporter can not buy a token in early market states"):    
        reportingToken.buy(2, sender=tester.k1)

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(tokenFixture, universe, market, [0, 0, numTicks])
    assert market.getReportingState() == tokenFixture.contracts['Constants'].DESIGNATED_REPORTING()

    # Not designated reporter throws error
    with raises(TransactionFailed, message="Only designated reporter can buy a token in DESIGNATED_REPORTING"):
        reportingToken.buy(1, sender=tester.k1)

    # buy not correct amount
    with raises(TransactionFailed, message="Designated reporter needs to buy same as bond amount in DESIGNATED_REPORTING"):
        reportingToken.buy(1)

    designatedReporterStake = universe.getDesignatedReportStake()
    # need to buy the correct bond amount
    with raises(TransactionFailed, message="Designated reporter needs to buy same as bond amount in DESIGNATED_REPORTING"):
        reportingToken.buy(designatedReporterStake + 1)

    originalTesterBalance = reportingToken.balanceOf(testerAddress)
    newTesterBalance = originalTesterBalance + designatedReporterStake
    assert reportingToken.buy(designatedReporterStake)
    assert reportingToken.balanceOf(testerAddress) == newTesterBalance

def test_reporting_token_redeem(tokenFixture, universe, cash):
    numTicks = 10 ** 18
    denominationToken = cash
    feePerEthInWei = 10**10
    endTime = long(tokenFixture.chain.head_state.timestamp + timedelta(days=1).total_seconds())

    market_other = tokenFixture.createBinaryMarket(universe, endTime, feePerEthInWei, denominationToken, tester.a8, numTicks, tester.k9)
    market_forking = tokenFixture.createBinaryMarket(universe, endTime, feePerEthInWei, denominationToken, tester.a1, numTicks)
    designatedReporterStake = universe.getDesignatedReportStake()
    reputationToken = tokenFixture.applySignature('ReputationToken', universe.getReputationToken())
    reportingToken_other = tokenFixture.getReportingToken(market_other, [0, numTicks])
    original_dr_other = reportingToken_other.balanceOf(tester.a8) 
    original_market_creator_other = reportingToken_other.balanceOf(tester.a9) 

    # Designated Report votes that Market is invalid
    proceedToDesignatedReporting(tokenFixture, universe, market_other, [0, numTicks])
    assert market_other.getReportingState() == tokenFixture.contracts['Constants'].DESIGNATED_REPORTING()
    reportingToken_other.buy(designatedReporterStake, sender=tester.k8)
    assert reportingToken_other.balanceOf(tester.a8) == designatedReporterStake
    assert market_other.isContainerForReportingToken(reportingToken_other.address)

    # kick this market into the DESIGNATED_REPORTING phase
    proceedToDesignatedReporting(tokenFixture, universe, market_forking, [0, numTicks])

    proceedToRound1Reporting(tokenFixture, universe, market_forking, False, tester.a6, [0, numTicks], [numTicks, 0])
    assert market_forking.getReportingState() == tokenFixture.contracts['Constants'].ROUND1_REPORTING()

    proceedToRound2Reporting(tokenFixture, universe, market_forking, False, tester.a6, tester.k3, [numTicks, 0], [0, numTicks], tester.k2, [0, numTicks], [numTicks, 0])
    assert market_forking.getReportingState() == tokenFixture.contracts['Constants'].ROUND2_REPORTING()

    # Proceed to the FORKING phase
    proceedToForking(tokenFixture, universe, market_forking, True, tester.k1, tester.k3, tester.k4, [0,numTicks], [numTicks,0], tester.k2, [numTicks,0], [numTicks,0], [0,numTicks])
    assert market_forking.getReportingState() == tokenFixture.contracts['Constants'].FORKING()

    # durring a fork non-forking markets should be in limbo and allow users to redeemDisavowedTokens
    assert market_other.getReportingState() == tokenFixture.contracts['Constants'].DESIGNATED_DISPUTE()
    reportingToken_non_forking = tokenFixture.applySignature('ReportingToken', market_other.getReportingToken([0, numTicks]))
    assert market_other.isContainerForReportingToken(reportingToken_non_forking.address) == True

    # Finalize the market
    #finalizeForkingMarket(tokenFixture, universe, market_forking, True, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,numTicks], [numTicks,0])
    #market_forking.getReportingState() == tokenFixture.contracts['Constants'].FINALIZED()

    # users of non-forking unresolved markets should get tokens back
    assert reportingToken_other.redeemDisavowedTokens(tester.a9)
    assert reportingToken_other.balanceOf(tester.a9) == original_a9

    # progress to next reporting window
    reportingWindow = tokenFixture.applySignature('ReportingWindow', universe.getNextReportingWindow())
    tokenFixture.chain.head_state.timestamp = market_forking.getEndTime() + 1

    # how does a reporting token not be associated with market
    assert market_other.isContainerForReportingToken(reportingToken_other.address) == False
    assert reportingToken_other.redeemDisavowedTokens(tester.a8)
    assert reportingToken_other.balanceOf(tester.a8) == original_dr_other + designatedReporterStake

    assert reportingToken_other.redeemDisavowedTokens(tester.a9)
    assert reportingToken_other.balanceOf(tester.a8) == original_market_creator_other + designatedReporterStake

    # (Direction) When a market needs to be reset (reporting wise), 
    # all associated dispute bonds and tokens become "disavowed".  
    # This means that anyone who holds the token/bond can redeem it at face value.  
    # No loss, no gain.

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    return initializeReportingFixture(fixture, universe, market)

@fixture
def universe(fixture, kitchenSinkSnapshot):
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    return universe

@fixture
def binaryMarket(fixture, kitchenSinkSnapshot):
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    return market

@fixture
def cash(fixture, kitchenSinkSnapshot):
    cash = ABIContract(fixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
    return cash

@fixture
def categoricalMarket(fixture, kitchenSinkSnapshot):
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)
    return market

@fixture
def tokenFixture(fixture, universe, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    value = 1 * 10**6 * 10**18
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    # Give tester reputation tokens
    for testAccount in [tester.a4, tester.a5, tester.a6, tester.a7, tester.a8, tester.a9]:
        reputationToken.transfer(testAccount, value)
    return fixture