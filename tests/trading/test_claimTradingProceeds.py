#!/usr/bin/env python

from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture, mark
from utils import fix, AssertLog, bytesToHexString, EtherDelta, TokenDelta
from constants import YES, NO


def captureLog(contract, logs, message):
    translated = contract.translator.listen(message)
    if not translated: return
    logs.append(translated)

def acquireLongShares(kitchenSinkFixture, cash, market, outcome, amount, approvalAddress, sender):
    if amount == 0: return

    shareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(outcome))
    completeSets = kitchenSinkFixture.contracts['CompleteSets']
    createOrder = kitchenSinkFixture.contracts['CreateOrder']
    fillOrder = kitchenSinkFixture.contracts['FillOrder']
    cost = amount * market.getNumTicks()

    assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender, value = cost)
    assert shareToken.approve(approvalAddress, amount, sender = sender)
    for otherOutcome in range(0, market.getNumberOfOutcomes()):
        if otherOutcome == outcome: continue
        otherShareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(otherOutcome))
        assert otherShareToken.transfer(0, amount, sender = sender)

def acquireShortShareSet(kitchenSinkFixture, cash, market, outcome, amount, approvalAddress, sender):
    if amount == 0: return
    cost = amount * market.getNumTicks()

    shareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(outcome))
    completeSets = kitchenSinkFixture.contracts['CompleteSets']
    createOrder = kitchenSinkFixture.contracts['CreateOrder']
    fillOrder = kitchenSinkFixture.contracts['FillOrder']

    assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender, value = cost)
    assert shareToken.transfer(0, amount, sender = sender)
    for otherOutcome in range(0, market.getNumberOfOutcomes()):
        if otherOutcome == outcome: continue
        otherShareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(otherOutcome))
        assert otherShareToken.approve(approvalAddress, amount, sender = sender)

def finalizeMarket(fixture, market, payoutNumerators, invalid=False):
    # set timestamp to after market end
    fixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)
    # have tester.a0 submit designated report
    market.doInitialReport(payoutNumerators, invalid)
    # set timestamp to after designated dispute end
    feeWindow = fixture.applySignature('FeeWindow', market.getFeeWindow())
    fixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    # finalize the market
    assert market.finalize()
    # set timestamp to 3 days later (waiting period)
    fixture.contracts["Time"].incrementTimestamp(long(timedelta(days = 3, seconds = 1).total_seconds()))

def test_helpers(kitchenSinkFixture, scalarMarket):
    market = scalarMarket
    claimTradingProceeds = kitchenSinkFixture.contracts['ClaimTradingProceeds']
    finalizeMarket(kitchenSinkFixture, market, [0,40*10**4])

    assert claimTradingProceeds.calculateCreatorFee(market.address, fix('3')) == fix('0.03')
    assert claimTradingProceeds.calculateReportingFee(market.address, fix('5')) == fix('0.05')
    assert claimTradingProceeds.calculateProceeds(market.address, YES, 7) == 7 * market.getNumTicks()
    assert claimTradingProceeds.calculateProceeds(market.address, NO, fix('11')) == fix('0')
    (proceeds, shareholderShare, creatorShare, reporterShare) = claimTradingProceeds.divideUpWinnings(market.address, YES, 13)
    assert proceeds == 13.0 * market.getNumTicks()
    assert reporterShare == 13.0 * market.getNumTicks() * 0.01
    assert creatorShare == 13.0 * market.getNumTicks() * 0.01
    assert shareholderShare == 13.0 * market.getNumTicks() * 0.98

def test_redeem_shares_in_yesNo_market(kitchenSinkFixture, universe, cash, market):
    claimTradingProceeds = kitchenSinkFixture.contracts['ClaimTradingProceeds']
    yesShareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(NO))
    expectedValue = 1 * market.getNumTicks()
    expectedReporterFees = expectedValue / universe.getOrCacheReportingFeeDivisor()
    expectedMarketCreatorFees = expectedValue / market.getMarketCreatorSettlementFeeDivisor()
    expectedSettlementFees = expectedReporterFees + expectedMarketCreatorFees
    expectedPayout = long(expectedValue - expectedSettlementFees)

    assert universe.getOpenInterestInAttoEth() == 0

    # get YES shares with a1
    acquireLongShares(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k1)
    assert universe.getOpenInterestInAttoEth() == 1 * market.getNumTicks()
    # get NO shares with a2
    acquireShortShareSet(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k2)
    assert universe.getOpenInterestInAttoEth() == 2 * market.getNumTicks()
    finalizeMarket(kitchenSinkFixture, market, [0,10**4])

    initialLongHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a1)
    initialShortHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a2)

    tradingProceedsClaimedLog = {
        'market': market.address,
        'shareToken': yesShareToken.address,
        'numPayoutTokens': expectedPayout,
        'numShares': 1,
        'sender': bytesToHexString(tester.a1),
        'finalTokenBalance': initialLongHolderETH + expectedPayout,
    }

    with TokenDelta(cash, expectedMarketCreatorFees, market.getMarketCreatorMailbox(), "Market creator fees not paid"):
        with TokenDelta(cash, expectedReporterFees, universe.getOrCreateNextFeeWindow(), "Reporter fees not paid"):
            # redeem shares with a1
            with AssertLog(kitchenSinkFixture, "TradingProceedsClaimed", tradingProceedsClaimedLog):
                claimTradingProceeds.claimTradingProceeds(market.address, tester.a1)
            # redeem shares with a2
            claimTradingProceeds.claimTradingProceeds(market.address, tester.a2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a1) == initialLongHolderETH + expectedPayout
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a2) == initialShortHolderETH
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 0

@mark.parametrize('isInvalid', [
    True,
    False
])
def test_redeem_shares_in_categorical_market(isInvalid, kitchenSinkFixture, universe, cash, categoricalMarket):
    market = categoricalMarket
    claimTradingProceeds = kitchenSinkFixture.contracts['ClaimTradingProceeds']
    shareToken2 = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(2))
    shareToken1 = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(1))
    shareToken0 = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(0))
    numTicks = market.getNumTicks()
    expectedValue = numTicks if not isInvalid else numTicks / 3
    expectedSettlementFees = expectedValue * 0.02
    expectedPayout = long(expectedValue - expectedSettlementFees)
    if (isInvalid):
        expectedPayout += 1 # rounding errors

    assert universe.getOpenInterestInAttoEth() == 0

    # get long shares with a1
    acquireLongShares(kitchenSinkFixture, cash, market, 2, 1, claimTradingProceeds.address, sender = tester.k1)
    assert universe.getOpenInterestInAttoEth() == 1 * numTicks
    # get short shares with a2
    acquireShortShareSet(kitchenSinkFixture, cash, market, 2, 1, claimTradingProceeds.address, sender = tester.k2)
    assert universe.getOpenInterestInAttoEth() == 2 * numTicks

    if (isInvalid):
        invalidPayout = numTicks / 3
        finalizeMarket(kitchenSinkFixture, market, [invalidPayout, invalidPayout, invalidPayout], True)
    else:
        finalizeMarket(kitchenSinkFixture, market, [0, 0, numTicks])

    assert universe.getOpenInterestInAttoEth() == 0

    # redeem shares with a1
    initialLongHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a1)
    claimTradingProceeds.claimTradingProceeds(market.address, tester.a1)
    # redeem shares with a2
    initialShortHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a2)
    claimTradingProceeds.claimTradingProceeds(market.address, tester.a2)

    # assert both accounts are paid (or not paid) accordingly
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a1) == initialLongHolderETH + expectedPayout
    shortHolderPayout = 2 * expectedPayout if isInvalid else 0
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a2) == initialShortHolderETH + shortHolderPayout
    assert shareToken2.balanceOf(tester.a1) == 0
    assert shareToken2.balanceOf(tester.a2) == 0
    assert shareToken1.balanceOf(tester.a1) == 0
    assert shareToken1.balanceOf(tester.a2) == 0
    assert shareToken0.balanceOf(tester.a1) == 0
    assert shareToken0.balanceOf(tester.a2) == 0

def test_redeem_shares_in_scalar_market(kitchenSinkFixture, universe, cash, scalarMarket):
    market = scalarMarket
    claimTradingProceeds = kitchenSinkFixture.contracts['ClaimTradingProceeds']
    yesShareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(NO))
    expectedValue = 1 * market.getNumTicks()
    expectedSettlementFees = expectedValue * 0.02
    expectedPayout = long(expectedValue - expectedSettlementFees)

    assert universe.getOpenInterestInAttoEth() == 0

    # get YES shares with a1
    acquireLongShares(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k1)
    assert universe.getOpenInterestInAttoEth() == 1 * market.getNumTicks()
    # get NO shares with a2
    acquireShortShareSet(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k2)
    assert universe.getOpenInterestInAttoEth() == 2 * market.getNumTicks()
    finalizeMarket(kitchenSinkFixture, market, [10**5, 3*10**5])

    # redeem shares with a1
    initialLongHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a1)
    claimTradingProceeds.claimTradingProceeds(market.address, tester.a1)
    # redeem shares with a2
    initialShortHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a2)
    claimTradingProceeds.claimTradingProceeds(market.address, tester.a2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a1) == initialLongHolderETH + expectedPayout * 3 / 4
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a2) == initialShortHolderETH + expectedPayout * 1 / 4
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 0

def test_reedem_failure(kitchenSinkFixture, cash, market):
    claimTradingProceeds = kitchenSinkFixture.contracts['ClaimTradingProceeds']

    # get YES shares with a1
    acquireLongShares(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k1)
    # get NO shares with a2
    acquireShortShareSet(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    kitchenSinkFixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)
    # have tester.a0 subimt designated report (75% high, 25% low, range -10*10^18 to 30*10^18)
    market.doInitialReport([0, 10**4], False)
    # set timestamp to after designated dispute end
    feeWindow = kitchenSinkFixture.applySignature('FeeWindow', market.getFeeWindow())
    kitchenSinkFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)

    # market not finalized
    with raises(TransactionFailed):
        claimTradingProceeds.claimTradingProceeds(market.address, tester.a1)
    # finalize the market
    assert market.finalize()
    # waiting period not over
    with raises(TransactionFailed):
        claimTradingProceeds.claimTradingProceeds(market.address, tester.a1)

    # set timestamp to 3 days later (waiting period)
    kitchenSinkFixture.contracts["Time"].incrementTimestamp(long(timedelta(days = 3, seconds = 1).total_seconds()))
    # validate that everything else is OK
    assert claimTradingProceeds.claimTradingProceeds(market.address, tester.a1)
