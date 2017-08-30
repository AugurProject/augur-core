#!/usr/bin/env python

from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture
from utils import fix

NO = 0
YES = 1

def captureLog(contract, logs, message):
    translated = contract.translator.listen(message)
    if not translated: return
    logs.append(translated)

def acquireLongShares(fundedRepFixture, market, outcome, amount, approvalAddress, sender):
    if amount == 0: return

    cash = fundedRepFixture.cash
    shareToken = fundedRepFixture.applySignature('shareToken', market.getShareToken(outcome))
    completeSets = fundedRepFixture.contracts['completeSets']
    makeOrder = fundedRepFixture.contracts['makeOrder']
    takeOrder = fundedRepFixture.contracts['takeOrder']

    cashRequired = amount * market.getCompleteSetCostInAttotokens() / 10**18
    assert cash.depositEther(value=cashRequired, sender = sender)
    assert cash.approve(completeSets.address, cashRequired, sender = sender)
    assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender)
    assert shareToken.approve(approvalAddress, amount, sender = sender)
    for otherOutcome in range(0, market.getNumberOfOutcomes()):
        if otherOutcome == outcome: continue
        otherShareToken = fundedRepFixture.applySignature('shareToken', market.getShareToken(otherOutcome))
        assert otherShareToken.transfer(0, amount, sender = sender)

def acquireShortShareSet(fundedRepFixture, market, outcome, amount, approvalAddress, sender):
    if amount == 0: return

    cash = fundedRepFixture.cash
    shareToken = fundedRepFixture.applySignature('shareToken', market.getShareToken(outcome))
    completeSets = fundedRepFixture.contracts['completeSets']
    makeOrder = fundedRepFixture.contracts['makeOrder']
    takeOrder = fundedRepFixture.contracts['takeOrder']

    cashRequired = amount * market.getCompleteSetCostInAttotokens() / 10**18
    assert cash.depositEther(value=cashRequired, sender = sender)
    assert cash.approve(completeSets.address, cashRequired, sender = sender)
    assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender)
    assert shareToken.transfer(0, amount, sender = sender)
    for otherOutcome in range(0, market.getNumberOfOutcomes()):
        if otherOutcome == outcome: continue
        otherShareToken = fundedRepFixture.applySignature('shareToken', market.getShareToken(otherOutcome))
        assert otherShareToken.approve(approvalAddress, amount, sender = sender)

def test_redeem_shares_in_binary_market(fundedRepFixture):
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket
    claimProceeds = fundedRepFixture.contracts['ClaimProceeds']
    yesShareToken = fundedRepFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('shareToken', market.getShareToken(NO))
    expectedValue = 1.2 * market.getCompleteSetCostInAttotokens()
    expectedFees = expectedValue * 0.0101
    expectedPayout = expectedValue - expectedFees

    # get YES shares with a1
    acquireLongShares(fundedRepFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k1)
    # get NO shares with a2
    acquireShortShareSet(fundedRepFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    fundedRepFixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have tester.a0 submit automated report
    market.automatedReport([0, 2], sender = tester.k0)
    # set timestamp to after automated dispute end
    fundedRepFixture.chain.head_state.timestamp = market.getAutomatedReportDisputeDueTimestamp() + 1
    # finalize the market
    assert market.tryFinalize()
    # set timestamp to 3 days later (waiting period)
    fundedRepFixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())

    # redeem shares with a1
    claimProceeds.claimProceeds(market.address, sender = tester.k1)
    # redeem shares with a2
    claimProceeds.claimProceeds(market.address, sender = tester.k2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert cash.balanceOf(tester.a1) == expectedPayout
    assert cash.balanceOf(tester.a2) == 0
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 0

def test_redeem_shares_in_categorical_market(fundedRepFixture):
    cash = fundedRepFixture.cash
    market = fundedRepFixture.categoricalMarket
    claimProceeds = fundedRepFixture.contracts['ClaimProceeds']
    shareToken2 = fundedRepFixture.applySignature('shareToken', market.getShareToken(2))
    shareToken1 = fundedRepFixture.applySignature('shareToken', market.getShareToken(1))
    shareToken0 = fundedRepFixture.applySignature('shareToken', market.getShareToken(0))
    expectedValue = 1.2 * market.getCompleteSetCostInAttotokens()
    expectedFees = expectedValue * 0.0101
    expectedPayout = expectedValue - expectedFees

    # get long shares with a1
    acquireLongShares(fundedRepFixture, market, 2, fix('1.2'), claimProceeds.address, sender = tester.k1)
    # get short shares with a2
    acquireShortShareSet(fundedRepFixture, market, 2, fix('1.2'), claimProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    fundedRepFixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have a0 submit automated report
    market.automatedReport([0, 0, 3], sender = tester.k0)
    # set timestamp to after automated dispute end
    fundedRepFixture.chain.head_state.timestamp = market.getAutomatedReportDisputeDueTimestamp() + 1
    # finalize the market
    assert market.tryFinalize()
    # set timestamp to 3 days later (waiting period)
    fundedRepFixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())

    # redeem shares with a1
    claimProceeds.claimProceeds(market.address, sender = tester.k1)
    # redeem shares with a2
    claimProceeds.claimProceeds(market.address, sender = tester.k2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert cash.balanceOf(tester.a1) == expectedPayout
    assert cash.balanceOf(tester.a2) == 0
    assert shareToken2.balanceOf(tester.a1) == 0
    assert shareToken2.balanceOf(tester.a2) == 0
    assert shareToken1.balanceOf(tester.a1) == 0
    assert shareToken1.balanceOf(tester.a2) == 0
    assert shareToken0.balanceOf(tester.a1) == 0
    assert shareToken0.balanceOf(tester.a2) == 0

def test_redeem_shares_in_scalar_market(fundedRepFixture):
    cash = fundedRepFixture.cash
    market = fundedRepFixture.scalarMarket
    claimProceeds = fundedRepFixture.contracts['ClaimProceeds']
    yesShareToken = fundedRepFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = fundedRepFixture.applySignature('shareToken', market.getShareToken(NO))
    expectedValue = 1.2 * market.getCompleteSetCostInAttotokens()
    expectedFees = expectedValue * 0.0101
    expectedPayout = expectedValue - expectedFees

    # get YES shares with a1
    acquireLongShares(fundedRepFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k1)
    # get NO shares with a2
    acquireShortShareSet(fundedRepFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    fundedRepFixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have tester.a0 submit automated report (75% high, 25% low, range -10*10^18 to 30*10^18)
    market.automatedReport([10**19, 3*10**19], sender = tester.k0)
    # set timestamp to after automated dispute end
    fundedRepFixture.chain.head_state.timestamp = market.getAutomatedReportDisputeDueTimestamp() + 1
    # finalize the market
    assert market.tryFinalize()
    # set timestamp to 3 days later (waiting period)
    fundedRepFixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())

    # redeem shares with a1
    claimProceeds.claimProceeds(market.address, sender = tester.k1)
    # redeem shares with a2
    claimProceeds.claimProceeds(market.address, sender = tester.k2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert cash.balanceOf(tester.a1) == expectedPayout * 3 / 4
    assert cash.balanceOf(tester.a2) == expectedPayout * 1 / 4
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 0

def test_reedem_failure(fundedRepFixture):
    cash = fundedRepFixture.cash
    market = fundedRepFixture.binaryMarket
    claimProceeds = fundedRepFixture.contracts['ClaimProceeds']

    # get YES shares with a1
    acquireLongShares(fundedRepFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k1)
    # get NO shares with a2
    acquireShortShareSet(fundedRepFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    fundedRepFixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have tester.a0 subimt automated report (75% high, 25% low, range -10*10^18 to 30*10^18)
    market.automatedReport([0, 2], sender = tester.k0)
    # set timestamp to after automated dispute end
    fundedRepFixture.chain.head_state.timestamp = market.getAutomatedReportDisputeDueTimestamp() + 1

    # market not finalized
    with raises(TransactionFailed):
        claimProceeds.claimProceeds(market.address, sender = tester.k1)
    # finalize the market
    assert market.tryFinalize()
    # waiting period not over
    with raises(TransactionFailed):
        claimProceeds.claimProceeds(market.address, sender = tester.k1)

    # set timestamp to 3 days later (waiting period)
    fundedRepFixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())
    # validate that everything else is OK
    assert claimProceeds.claimProceeds(market.address, sender = tester.k1)
