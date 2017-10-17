from ethereum.tools import tester
from datetime import timedelta
from utils import longToHexString, stringToBytes
from pytest import fixture, raises
from ethereum.tools.tester import ABIContract, TransactionFailed
from reporting_utils import proceedToDesignatedReporting, proceedToRound1Reporting, proceedToRound2Reporting, proceedToForking, finalizeForkingMarket, initializeReportingFixture

def test_stake_token_creation_binary(tokenFixture, binaryMarket):
    bin_market = binaryMarket
    numTicks = 10 ** 18
    stakeToken_bin = tokenFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    # stake token needs same payout numerators as market
    with raises(TransactionFailed, message="payout numerators can not be more than market"):
        stakeToken_bin.initialize(bin_market.address, [0, 1, numTicks -1])
    # stake token outcomes are incorrect, payout numerators need to add up to numTicks    
    with raises(TransactionFailed, message="payout numerators need to add up to market numTicks"):
        stakeToken_bin.initialize(bin_market.address, [0, 1, numTicks])

    # outcomes are correct
    assert stakeToken_bin.initialize(bin_market.address, [0, numTicks], False)        
    assert stakeToken_bin.isValid()

    assert stakeToken_bin.getPayoutNumerator(0) == 0
    assert stakeToken_bin.getPayoutNumerator(1) == numTicks
    assert stakeToken_bin.isValid()
    # can not get more stake token payout numerators than exists
    with raises(TransactionFailed, message="Stake Token has only 3 payoutNumerators"):
        stakeToken_bin.getPayoutNumerator(2)

def test_stake_token_creation_category(tokenFixture, categoricalMarket):
    stakeToken_cat = tokenFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    cat_market = categoricalMarket
    numTicks = 3 * 10 ** 17
    # stake token needs same payout numerators as market
    with raises(TransactionFailed, message="payout numerators can not be more than market"):
        stakeToken_cat.initialize(cat_market.address, [0, numTicks])

    assert stakeToken_cat.initialize(cat_market.address, [0, 1, numTicks - 1])        
    assert stakeToken_cat.getPayoutNumerator(0) == 0
    assert stakeToken_cat.getPayoutNumerator(1) == 1
    assert stakeToken_cat.getPayoutNumerator(2) == numTicks - 1
    # can not get more stake token payout numerators than exists
    with raises(TransactionFailed, message="Stake Token has only 3 payoutNumerators"):
        stakeToken_cat.getPayoutNumerator(3)

def test_stake_token_getters(tokenFixture, categoricalMarket, universe):
    stakeToken = tokenFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    market = categoricalMarket

    numTicks = 3 * 10 ** 17
    assert stakeToken.initialize(market.address, [0, 1, numTicks - 1], False)        
    assert stakeToken.getTypeName() == stringToBytes("StakeToken")
    assert stakeToken.getUniverse() == universe.address
    assert stakeToken.getMarket() == market.address
    assert stakeToken.getPayoutDistributionHash() == market.derivePayoutDistributionHash([0, 1, numTicks - 1], False)
    assert stakeToken.getReportingWindow() == market.getReportingWindow()
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())
    assert stakeToken.getReputationToken() == reportingWindow.getReputationToken()
    assert stakeToken.isValid()

def test_stake_token_valid_checks(tokenFixture, universe, cash):
    stakeToken = tokenFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    market = tokenFixture.createReasonableCategoricalMarket(universe, 5, cash)
    numTicks = 3 * 10 ** 17
    assert stakeToken.initialize(market.address, [numTicks/5, numTicks/5, numTicks/5, numTicks/5, numTicks/5], False)
    assert stakeToken.isValid()
    with raises(AttributeError, message="method not reachable because it's private"):
        stakeToken.isInvalidOutcome()

    with raises(TransactionFailed, message="Stake Token can not be initialized invalid"):
        stakeToken.initialize(market.address, [numTicks/5, numTicks/5, numTicks/5, numTicks/5, numTicks/5], True)

def test_stake_token_buy_no_report_state(tokenFixture, universe, cash):
    numTicks = 3 * 10 ** 17
    testerAddress = tester.a0
    market = tokenFixture.createReasonableCategoricalMarket(universe, 3, cash)
    stakeToken = tokenFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())

    assert stakeToken.initialize(market.address, [numTicks/3, numTicks/3, numTicks/3], False)
    # Stake token not associated with market fails
    with raises(TransactionFailed, message="Stake Token can not be bought, not assoc. to market"):
        stakeToken.buy(1) 

    tokenFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == tokenFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()

    stakeToken = tokenFixture.applySignature('StakeToken', market.getStakeToken([0, 0, numTicks]))
    designatedReporterStake = universe.getDesignatedReportStake()
    originalTesterBalance = stakeToken.balanceOf(testerAddress)
    newTesterBalance = originalTesterBalance + 1 + designatedReporterStake
    assert stakeToken.buy(1)
    assert stakeToken.balanceOf(testerAddress) == newTesterBalance
    
def test_stake_token_buy_get_more(tokenFixture, universe, cash):
    numTicks = 3 * 10 ** 17
    testerAddress = tester.a0
    market = tokenFixture.createReasonableCategoricalMarket(universe, 3, cash)
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())
    stakeToken = tokenFixture.applySignature('StakeToken', market.getStakeToken([0, 0, numTicks]))
    tokenFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    assert market.getReportingState() == tokenFixture.contracts['Constants'].AWAITING_NO_REPORT_MIGRATION()
    stakeToken.buy(1)
    assert market.getReportingState() == tokenFixture.contracts['Constants'].ROUND1_REPORTING()
    stakeToken.buy(1)
    assert market.getReportingState() == tokenFixture.contracts['Constants'].ROUND1_REPORTING()

def test_stake_token_buy_designated_reporter_state(tokenFixture, categoricalMarket, universe):    
    market = categoricalMarket
    testerAddress = tester.a0
    otherAddress = tester.a1
    reputationToken = tokenFixture.applySignature('ReputationToken', universe.getReputationToken())
    numTicks = 3 * 10 ** 17
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())
    stakeToken = tokenFixture.applySignature('StakeToken', market.getStakeToken([numTicks/3, numTicks/3, numTicks/3]))
    
    with raises(TransactionFailed, message="Reporter can not buy a token in early market states"):    
        stakeToken.buy(2, sender=tester.k1)

    # Proceed to the DESIGNATED REPORTING phase
    proceedToDesignatedReporting(tokenFixture, universe, market, [0, 0, numTicks])
    assert market.getReportingState() == tokenFixture.contracts['Constants'].DESIGNATED_REPORTING()

    # Not designated reporter throws error
    with raises(TransactionFailed, message="Only designated reporter can buy a token in DESIGNATED_REPORTING"):
        stakeToken.buy(1, sender=tester.k1)

    # buy not correct amount
    with raises(TransactionFailed, message="Designated reporter needs to buy same as bond amount in DESIGNATED_REPORTING"):
        stakeToken.buy(1)

    designatedReporterStake = universe.getDesignatedReportStake()
    # need to buy the correct bond amount
    with raises(TransactionFailed, message="Designated reporter needs to buy same as bond amount in DESIGNATED_REPORTING"):
        stakeToken.buy(designatedReporterStake + 1)

    originalTesterBalance = stakeToken.balanceOf(testerAddress)
    newTesterBalance = originalTesterBalance + designatedReporterStake
    assert stakeToken.buy(designatedReporterStake)
    assert stakeToken.balanceOf(testerAddress) == newTesterBalance

def test_stake_token_redeem(tokenFixture, universe, cash):
    numTicks = 10 ** 18
    denominationToken = cash
    feePerEthInWei = 10**10
    endTime = long(tokenFixture.chain.head_state.timestamp + timedelta(days=1).total_seconds())

    market_other = tokenFixture.createBinaryMarket(universe, endTime, feePerEthInWei, denominationToken, tester.a8, numTicks, tester.k9)
    market_forking = tokenFixture.createBinaryMarket(universe, endTime, feePerEthInWei, denominationToken, tester.a1, numTicks)
    designatedReporterStake = universe.getDesignatedReportStake()
    reputationToken = tokenFixture.applySignature('ReputationToken', universe.getReputationToken())
    stakeToken_other = tokenFixture.getStakeToken(market_other, [0, numTicks])
    original_dr_other = stakeToken_other.balanceOf(tester.a8) 
    original_market_creator_other = stakeToken_other.balanceOf(tester.a9) 

    # Designated Report votes that Market is invalid
    proceedToDesignatedReporting(tokenFixture, universe, market_other, [0, numTicks])
    assert market_other.getReportingState() == tokenFixture.contracts['Constants'].DESIGNATED_REPORTING()
    stakeToken_other.buy(designatedReporterStake, sender=tester.k8)
    assert stakeToken_other.balanceOf(tester.a8) == designatedReporterStake
    assert market_other.isContainerForStakeToken(stakeToken_other.address)

    # kick this market into the DESIGNATED_REPORTING phase
    proceedToDesignatedReporting(tokenFixture, universe, market_forking, [0, numTicks])

    proceedToRound1Reporting(tokenFixture, universe, market_forking, False, tester.a6, [0, numTicks], [numTicks, 0])
    assert market_forking.getReportingState() == tokenFixture.contracts['Constants'].ROUND1_REPORTING()

    proceedToRound2Reporting(tokenFixture, universe, market_forking, False, tester.a6, tester.k3, [numTicks, 0], [0, numTicks], tester.k2, [0, numTicks], [numTicks, 0])
    assert market_forking.getReportingState() == tokenFixture.contracts['Constants'].ROUND2_REPORTING()

    # Proceed to the FORKING phase
    proceedToForking(tokenFixture, universe, market_forking, True, tester.k1, tester.k3, tester.k4, [0,numTicks], [numTicks,0], tester.k2, [numTicks,0], [numTicks,0], [0,numTicks])
    assert market_forking.getReportingState() == tokenFixture.contracts['Constants'].FORKING()

    # during a fork non-forking markets should be in limbo and allow users to redeemDisavowedTokens
    assert market_other.getReportingState() == tokenFixture.contracts['Constants'].AWAITING_FORK_MIGRATION()
    stakeToken_non_forking = tokenFixture.applySignature('StakeToken', market_other.getStakeToken([0, numTicks]))
    assert market_other.isContainerForStakeToken(stakeToken_non_forking.address) == True

    # Finalize the market
    #finalizeForkingMarket(tokenFixture, universe, market_forking, True, tester.a1, tester.k1, tester.a0, tester.k0, tester.a2, tester.k2, [0,numTicks], [numTicks,0])
    #market_forking.getReportingState() == tokenFixture.contracts['Constants'].FINALIZED()

    # users of non-forking unresolved markets should get tokens back
    #assert stakeToken_non_forking.redeemDisavowedTokens(tester.a9)
    #assert stakeToken_non_forking.balanceOf(tester.a9) == original_a9

    # progress to next reporting window
    #reportingWindow = tokenFixture.applySignature('ReportingWindow', universe.getNextReportingWindow())
    #tokenFixture.chain.head_state.timestamp = market_forking.getEndTime() + 1

    # how does a stake token not be associated with market
    #assert market_other.isContainerForStakeToken(stakeToken_other.address) == False
    #assert stakeToken_other.redeemDisavowedTokens(tester.a8)
    #assert stakeToken_other.balanceOf(tester.a8) == original_dr_other + designatedReporterStake

    #assert stakeToken_other.redeemDisavowedTokens(tester.a9)
    #assert stakeToken_other.balanceOf(tester.a8) == original_market_creator_other + designatedReporterStake

    # (Direction) When a market needs to be reset (reporting wise), 
    # all associated dispute bonds and tokens become "disavowed".  
    # This means that anyone who holds the token/bond can redeem it at face value.  
    # No loss, no gain.

def test_stake_token_verify_designated_reporter_stake(tokenFixture, binaryMarket):
    numTicks = 10 ** 18

    market = binaryMarket
    universe = tokenFixture.applySignature('Universe', market.getUniverse())
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())

    stakeToken = tokenFixture.getStakeToken(market, [0, numTicks])
    original = stakeToken.balanceOf(tester.a0)

    # Go to designated reporting time window
    tokenFixture.chain.head_state.timestamp = market.getEndTime() + 1    
    designatedReporterStake = universe.getDesignatedReportStake()
    tokenFixture.designatedReport(market, [0, numTicks], tester.k0)

    tokenFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    endBalance = stakeToken.balanceOf(tester.a0)
    assert endBalance == designatedReporterStake

def test_stake_token_trusted_buy_fails(tokenFixture, binaryMarket):
    numTicks = 10 ** 18
    market = binaryMarket
    universe = tokenFixture.applySignature('Universe', market.getUniverse())
    stakeToken = tokenFixture.getStakeToken(market, [0, numTicks])
    reportingWindow = tokenFixture.applySignature('ReportingWindow', market.getReportingWindow())

    with raises(TransactionFailed, message="only market can call this method"):
        stakeToken.trustedBuy(tester.a2, 1)

    proceedToRound1Reporting(tokenFixture, universe, market, False, tester.a1, [numTicks, 0], [numTicks/2, numTicks/2])
    assert market.getReportingState() == tokenFixture.contracts['Constants'].ROUND1_REPORTING()
    with raises(TransactionFailed, message="trusted buy can only occur buy trusted contract"):
        stakeToken.trustedBuy(tester.a2, 1)

    with raises(Exception, message="address isn't in format that can be used as Market"):
        stakeToken.trustedBuy(tester.a2, 1, sender=market.address)

def test_stake_token_verify_trusted_buy(tokenFixture, universe):
    numTicks = 10 ** 18
    mockMarket = tokenFixture.contracts['MockMarket']
    mockMarket.setNumberOfOutcomes(2)
    mockMarket.setNumTicks(numTicks)
    mockMarket.setUniverse(universe.address)
    reportingWindow = tokenFixture.applySignature('ReportingWindow', universe.getCurrentReportingWindow())
    reputationToken = tokenFixture.applySignature('ReputationToken', reportingWindow.getReputationToken())
    assert reputationToken.balanceOf(tester.a1) > 0
    reputationToken.transfer(mockMarket.address, 100)

    mockMarket.setReportingWindow(reportingWindow.address)
    mockMarketReportingWindow = tokenFixture.applySignature('ReportingWindow', mockMarket.getReportingWindow())
    assert mockMarketReportingWindow.isContainerForMarket(mockMarket.address)
    assert universe.isContainerForReportingWindow(mockMarketReportingWindow.address)
    assert universe.isContainerForMarket(mockMarket.address)

    stakeToken = tokenFixture.upload('../source/contracts/reporting/StakeToken.sol', 'stakeToken')
    assert stakeToken.initialize(mockMarket.address, [0, numTicks], False)       
    assert universe.isContainerForStakeToken(stakeToken.address)
    
    mockMarket.setReportingState(tokenFixture.contracts['Constants'].PRE_REPORTING()) 
    
    with raises(Exception, message="market can't call trust buy unless market state is round 1 or round 2"):
        mockMarket.callStakeTokenTrustedBuy(stakeToken, tester.a1, 1)

    mockMarket.setReportingState(tokenFixture.contracts['Constants'].ROUND1_REPORTING()) 
    mockMarket.setIsContainerForStakeToken(True)
    # market isn't in reporting windows
    assert mockMarket.callStakeTokenTrustedBuy(stakeToken.address, tester.a1, 1) == False

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    fixture.uploadAndAddToController('solidity_test_helpers/MockMarket.sol')
    fixture.uploadAndAddToController('solidity_test_helpers/MockReportingWindow.sol')
    assert fixture.contracts['MockReportingWindow']
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