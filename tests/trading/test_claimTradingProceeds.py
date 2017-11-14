#!/usr/bin/env python

from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture
from utils import fix, captureFilteredLogs, bytesToHexString, EtherDelta, TokenDelta
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

def finalizeMarket(fixture, market, payoutNumerators):
    # set timestamp to after market end
    fixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have tester.a0 submit designated report
    fixture.designatedReport(market, payoutNumerators, tester.k0)
    # set timestamp to after designated dispute end
    fixture.chain.head_state.timestamp = market.getDesignatedReportDisputeDueTimestamp() + 1
    # finalize the market
    assert market.tryFinalize()
    # set timestamp to 3 days later (waiting period)
    fixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())

def test_helpers(kitchenSinkFixture, scalarMarket):
    market = scalarMarket
    claimTradingProceeds = kitchenSinkFixture.contracts['ClaimTradingProceeds']
    finalizeMarket(kitchenSinkFixture, market, [0,40*10**18])

    assert claimTradingProceeds.calculateCreatorFee(market.address, fix('3')) == fix('0.03')
    assert claimTradingProceeds.calculateReportingFee(market.address, fix('5')) == fix('0.0005')
    assert claimTradingProceeds.calculateProceeds(market.getFinalWinningStakeToken(), YES, 7) == 7 * market.getNumTicks()
    assert claimTradingProceeds.calculateProceeds(market.getFinalWinningStakeToken(), NO, fix('11')) == fix('0')
    (proceeds, shareholderShare, creatorShare, reporterShare) = claimTradingProceeds.divideUpWinnings(market.address, market.getFinalWinningStakeToken(), YES, 13)
    assert proceeds == 13.0 * market.getNumTicks()
    assert reporterShare == 13.0 * market.getNumTicks() * 0.0001
    assert creatorShare == 13.0 * market.getNumTicks() * .01
    assert shareholderShare == 13.0 * market.getNumTicks() * 0.9899

def test_redeem_shares_in_binary_market(kitchenSinkFixture, universe, cash, market):
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
    finalizeMarket(kitchenSinkFixture, market, [0,10**18])

    logs = []
    captureFilteredLogs(kitchenSinkFixture.chain.head_state, kitchenSinkFixture.contracts['Augur'], logs)

    with EtherDelta(expectedMarketCreatorFees, tester.a0, kitchenSinkFixture.chain, "Market creator fees not paid"):
        with TokenDelta(cash, expectedReporterFees, market.getReportingWindow(), "Reporter fees not paid"):
            # redeem shares with a1
            initialLongHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a1)
            claimTradingProceeds.claimTradingProceeds(market.address, sender = tester.k1)
            # redeem shares with a2
            initialShortHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a2)
            claimTradingProceeds.claimTradingProceeds(market.address, sender = tester.k2)

    # Confirm claim proceeds logging works correctly
    assert len(logs) == 4
    assert logs[1]['_event_type'] == 'TradingProceedsClaimed'
    assert logs[1]['market'] == market.address
    assert logs[1]['shareToken'] == yesShareToken.address
    assert logs[1]['numPayoutTokens'] == expectedPayout
    assert logs[1]['numShares'] == 1
    assert logs[1]['sender'] == bytesToHexString(tester.a1)
    assert logs[1]['finalTokenBalance'] == initialLongHolderETH + expectedPayout

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a1) == initialLongHolderETH + expectedPayout
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a2) == initialShortHolderETH
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 0
    assert universe.getOpenInterestInAttoEth() == 1 * market.getNumTicks() # The corresponding share for tester2's complete set has not been redeemed

def test_redeem_shares_in_categorical_market(kitchenSinkFixture, universe, cash, categoricalMarket):
    market = categoricalMarket
    claimTradingProceeds = kitchenSinkFixture.contracts['ClaimTradingProceeds']
    shareToken2 = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(2))
    shareToken1 = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(1))
    shareToken0 = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(0))
    expectedValue = 1 * market.getNumTicks()
    expectedSettlementFees = expectedValue * 0.0101
    expectedPayout = long(expectedValue - expectedSettlementFees)

    assert universe.getOpenInterestInAttoEth() == 0

    # get long shares with a1
    acquireLongShares(kitchenSinkFixture, cash, market, 2, 1, claimTradingProceeds.address, sender = tester.k1)
    assert universe.getOpenInterestInAttoEth() == 1 * market.getNumTicks()
    # get short shares with a2
    acquireShortShareSet(kitchenSinkFixture, cash, market, 2, 1, claimTradingProceeds.address, sender = tester.k2)
    assert universe.getOpenInterestInAttoEth() == 2 * market.getNumTicks()
    finalizeMarket(kitchenSinkFixture, market, [0, 0, 3 * 10 ** 17])

    # redeem shares with a1
    initialLongHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a1)
    claimTradingProceeds.claimTradingProceeds(market.address, sender = tester.k1)
    # redeem shares with a2
    initialShortHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a2)
    claimTradingProceeds.claimTradingProceeds(market.address, sender = tester.k2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a1) == initialLongHolderETH + expectedPayout
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a2) == initialShortHolderETH
    assert shareToken2.balanceOf(tester.a1) == 0
    assert shareToken2.balanceOf(tester.a2) == 0
    assert shareToken1.balanceOf(tester.a1) == 0
    assert shareToken1.balanceOf(tester.a2) == 0
    assert shareToken0.balanceOf(tester.a1) == 0
    assert shareToken0.balanceOf(tester.a2) == 0
    assert universe.getOpenInterestInAttoEth() == 1 * market.getNumTicks()

def test_redeem_shares_in_scalar_market(kitchenSinkFixture, universe, cash, scalarMarket):
    market = scalarMarket
    claimTradingProceeds = kitchenSinkFixture.contracts['ClaimTradingProceeds']
    yesShareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = kitchenSinkFixture.applySignature('ShareToken', market.getShareToken(NO))
    expectedValue = 1 * market.getNumTicks()
    expectedSettlementFees = expectedValue * 0.0101
    expectedPayout = long(expectedValue - expectedSettlementFees)

    assert universe.getOpenInterestInAttoEth() == 0

    # get YES shares with a1
    acquireLongShares(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k1)
    assert universe.getOpenInterestInAttoEth() == 1 * market.getNumTicks()
    # get NO shares with a2
    acquireShortShareSet(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k2)
    assert universe.getOpenInterestInAttoEth() == 2 * market.getNumTicks()
    finalizeMarket(kitchenSinkFixture, market, [10**19, 3*10**19])

    # redeem shares with a1
    initialLongHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a1)
    claimTradingProceeds.claimTradingProceeds(market.address, sender = tester.k1)
    # redeem shares with a2
    initialShortHolderETH = kitchenSinkFixture.chain.head_state.get_balance(tester.a2)
    claimTradingProceeds.claimTradingProceeds(market.address, sender = tester.k2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a1) == initialLongHolderETH + expectedPayout * 3 / 4
    assert kitchenSinkFixture.chain.head_state.get_balance(tester.a2) == initialShortHolderETH + expectedPayout * 1 / 4
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 0
    assert universe.getOpenInterestInAttoEth() == 1 * market.getNumTicks()

def test_reedem_failure(kitchenSinkFixture, cash, market):
    claimTradingProceeds = kitchenSinkFixture.contracts['ClaimTradingProceeds']

    # get YES shares with a1
    acquireLongShares(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k1)
    # get NO shares with a2
    acquireShortShareSet(kitchenSinkFixture, cash, market, YES, 1, claimTradingProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    kitchenSinkFixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have tester.a0 subimt designated report (75% high, 25% low, range -10*10^18 to 30*10^18)
    kitchenSinkFixture.designatedReport(market, [0, 10**18], tester.k0)
    # set timestamp to after designated dispute end
    kitchenSinkFixture.chain.head_state.timestamp = market.getDesignatedReportDisputeDueTimestamp() + 1

    # market not finalized
    with raises(TransactionFailed):
        claimTradingProceeds.claimTradingProceeds(market.address, sender = tester.k1)
    # finalize the market
    assert market.tryFinalize()
    # waiting period not over
    with raises(TransactionFailed):
        claimTradingProceeds.claimTradingProceeds(market.address, sender = tester.k1)

    # set timestamp to 3 days later (waiting period)
    kitchenSinkFixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())
    # validate that everything else is OK
    assert claimTradingProceeds.claimTradingProceeds(market.address, sender = tester.k1)
