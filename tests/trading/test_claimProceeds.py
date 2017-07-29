#!/usr/bin/env python

from datetime import timedelta
from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import fix

NO = 0
YES = 1

def captureLog(contract, logs, message):
    translated = contract.translator.listen(message)
    if not translated: return
    logs.append(translated)

def acquireLongShares(contractsFixture, market, outcome, amount, approvalAddress, sender):
    if amount == 0: return

    cash = contractsFixture.cash
    shareToken = contractsFixture.applySignature('shareToken', market.getShareToken(outcome))
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']

    cashRequired = amount * market.getCompleteSetCostInAttotokens() / 10**18
    assert cash.publicDepositEther(value=cashRequired, sender = sender)
    assert cash.approve(completeSets.address, cashRequired, sender = sender)
    assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender)
    assert shareToken.approve(approvalAddress, amount, sender = sender)
    for otherOutcome in range(0, market.getNumberOfOutcomes()):
        if otherOutcome == outcome: continue
        otherShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(otherOutcome))
        assert otherShareToken.transfer(0, amount, sender = sender)

def acquireShortShareSet(contractsFixture, market, outcome, amount, approvalAddress, sender):
    if amount == 0: return

    cash = contractsFixture.cash
    shareToken = contractsFixture.applySignature('shareToken', market.getShareToken(outcome))
    completeSets = contractsFixture.contracts['completeSets']
    makeOrder = contractsFixture.contracts['makeOrder']
    takeOrder = contractsFixture.contracts['takeOrder']

    cashRequired = amount * market.getCompleteSetCostInAttotokens() / 10**18
    assert cash.publicDepositEther(value=cashRequired, sender = sender)
    assert cash.approve(completeSets.address, cashRequired, sender = sender)
    assert completeSets.publicBuyCompleteSets(market.address, amount, sender = sender)
    assert shareToken.transfer(0, amount, sender = sender)
    for otherOutcome in range(0, market.getNumberOfOutcomes()):
        if otherOutcome == outcome: continue
        otherShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(otherOutcome))
        assert otherShareToken.approve(approvalAddress, amount, sender = sender)

def test_redeem_shares_in_binary_market(contractsFixture):
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    claimProceeds = contractsFixture.contracts['claimProceeds']
    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))
    expectedValue = 1.2 * market.getCompleteSetCostInAttotokens()
    expectedFees = expectedValue * 0.0101
    expectedPayout = expectedValue - expectedFees

    # get YES shares with a1
    acquireLongShares(contractsFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k1)
    # get NO shares with a2
    acquireShortShareSet(contractsFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    contractsFixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have tester.a0 submit automated report
    market.automatedReport([0, 2], sender = tester.k0)
    # set timestamp to after automated dispute end
    contractsFixture.chain.head_state.timestamp = market.getAutomatedReportDisputeDueTimestamp() + 1
    # finalize the market
    assert market.tryFinalizeAutomatedReport()
    # set timestamp to 3 days later (waiting period)
    contractsFixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())

    # redeem shares with a1
    claimProceeds.publicClaimProceeds(market.address, sender = tester.k1)
    # redeem shares with a2
    claimProceeds.publicClaimProceeds(market.address, sender = tester.k2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert cash.balanceOf(tester.a1) == expectedPayout
    assert cash.balanceOf(tester.a2) == 0
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 0

def test_redeem_shares_in_categorical_market(contractsFixture):
    cash = contractsFixture.cash
    market = contractsFixture.categoricalMarket
    claimProceeds = contractsFixture.contracts['claimProceeds']
    shareToken2 = contractsFixture.applySignature('shareToken', market.getShareToken(2))
    shareToken1 = contractsFixture.applySignature('shareToken', market.getShareToken(1))
    shareToken0 = contractsFixture.applySignature('shareToken', market.getShareToken(0))
    expectedValue = 1.2 * market.getCompleteSetCostInAttotokens()
    expectedFees = expectedValue * 0.0101
    expectedPayout = expectedValue - expectedFees

    # get long shares with a1
    acquireLongShares(contractsFixture, market, 2, fix('1.2'), claimProceeds.address, sender = tester.k1)
    # get short shares with a2
    acquireShortShareSet(contractsFixture, market, 2, fix('1.2'), claimProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    contractsFixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have a0 submit automated report
    market.automatedReport([0, 0, 3], sender = tester.k0)
    # set timestamp to after automated dispute end
    contractsFixture.chain.head_state.timestamp = market.getAutomatedReportDisputeDueTimestamp() + 1
    # finalize the market
    assert market.tryFinalizeAutomatedReport()
    # set timestamp to 3 days later (waiting period)
    contractsFixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())

    # redeem shares with a1
    claimProceeds.publicClaimProceeds(market.address, sender = tester.k1)
    # redeem shares with a2
    claimProceeds.publicClaimProceeds(market.address, sender = tester.k2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert cash.balanceOf(tester.a1) == expectedPayout
    assert cash.balanceOf(tester.a2) == 0
    assert shareToken2.balanceOf(tester.a1) == 0
    assert shareToken2.balanceOf(tester.a2) == 0
    assert shareToken1.balanceOf(tester.a1) == 0
    assert shareToken1.balanceOf(tester.a2) == 0
    assert shareToken0.balanceOf(tester.a1) == 0
    assert shareToken0.balanceOf(tester.a2) == 0

def test_redeem_shares_in_scalar_market(contractsFixture):
    cash = contractsFixture.cash
    market = contractsFixture.scalarMarket
    claimProceeds = contractsFixture.contracts['claimProceeds']
    yesShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('shareToken', market.getShareToken(NO))
    expectedValue = 1.2 * market.getCompleteSetCostInAttotokens()
    expectedFees = expectedValue * 0.0101
    expectedPayout = expectedValue - expectedFees

    # get YES shares with a1
    acquireLongShares(contractsFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k1)
    # get NO shares with a2
    acquireShortShareSet(contractsFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    contractsFixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have tester.a0 submit automated report (75% high, 25% low, range -10*10^18 to 30*10^18)
    market.automatedReport([10**19, 3*10**19], sender = tester.k0)
    # set timestamp to after automated dispute end
    contractsFixture.chain.head_state.timestamp = market.getAutomatedReportDisputeDueTimestamp() + 1
    # finalize the market
    assert market.tryFinalizeAutomatedReport()
    # set timestamp to 3 days later (waiting period)
    contractsFixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())

    # redeem shares with a1
    claimProceeds.publicClaimProceeds(market.address, sender = tester.k1)
    # redeem shares with a2
    claimProceeds.publicClaimProceeds(market.address, sender = tester.k2)

    # assert a1 ends up with cash (minus fees) and a2 does not
    assert cash.balanceOf(tester.a1) == expectedPayout * 3 / 4
    assert cash.balanceOf(tester.a2) == expectedPayout * 1 / 4
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert yesShareToken.balanceOf(tester.a2) == 0
    assert noShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a2) == 0

def test_reedem_failure(contractsFixture):
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket
    claimProceeds = contractsFixture.contracts['claimProceeds']

    # get YES shares with a1
    acquireLongShares(contractsFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k1)
    # get NO shares with a2
    acquireShortShareSet(contractsFixture, market, YES, fix('1.2'), claimProceeds.address, sender = tester.k2)
    # set timestamp to after market end
    contractsFixture.chain.head_state.timestamp = market.getEndTime() + 1
    # have tester.a0 subimt automated report (75% high, 25% low, range -10*10^18 to 30*10^18)
    market.automatedReport([0, 2], sender = tester.k0)
    # set timestamp to after automated dispute end
    contractsFixture.chain.head_state.timestamp = market.getAutomatedReportDisputeDueTimestamp() + 1

    # market not finalized
    with raises(TransactionFailed):
        claimProceeds.publicClaimProceeds(market.address, sender = tester.k1)
    # finalize the market
    assert market.tryFinalizeAutomatedReport()
    # waiting period not over
    with raises(TransactionFailed):
        claimProceeds.publicClaimProceeds(market.address, sender = tester.k1)

    # set timestamp to 3 days later (waiting period)
    contractsFixture.chain.head_state.timestamp += long(timedelta(days = 3, seconds = 1).total_seconds())
    # validate that everything else is OK
    assert claimProceeds.publicClaimProceeds(market.address, sender = tester.k1)
