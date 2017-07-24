from ethereum.tools import tester
from datetime import timedelta

tester.STARTGAS = long(6.7 * 10**6)

def test_reporting(contractsFixture):
    # seed legacy rep contract
    legacyRepContract = contractsFixture.contracts['legacyRepContract']
    legacyRepContract.setSaleDistribution([tester.a0], [long(11 * 10**6 * 10**18)])
    contractsFixture.chain.head_state.timestamp += 15000
    branch = contractsFixture.branch
    cash = contractsFixture.cash
    market = contractsFixture.binaryMarket

    # get the reputation token for this branch and migrate legacy REP to it
    reputationToken = contractsFixture.applySignature('ReputationToken', branch.getReputationToken())
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract()

    # give some REP to someone else to make things interesting
    reputationToken.transfer(tester.a1, 4 * 10**6 * 10**18)
    reputationToken.transfer(tester.a2, 1 * 10**6 * 10**18)

    # buy registration tokens
    reportingWindow = contractsFixture.applySignature('reportingWindow', market.getReportingWindow())
    registrationToken = contractsFixture.applySignature('registrationToken', reportingWindow.getRegistrationToken())
    registrationToken.register(sender=tester.k0)
    assert registrationToken.balanceOf(tester.a0) == 1
    assert reputationToken.balanceOf(tester.a0) == 6 * 10**6 * 10**18 - 10**18
    registrationToken.register(sender=tester.k1)
    assert registrationToken.balanceOf(tester.a1) == 1
    assert reputationToken.balanceOf(tester.a1) == 4 * 10**6 * 10**18 - 10**18

    # fast forward to one second after the next reporting window
    reportingWindow = contractsFixture.applySignature('reportingWindow', branch.getNextReportingWindow())
    contractsFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1

    # both reporters report on the outcome
    reportingTokenNo = contractsFixture.getReportingToken(market, [2,0])
    reportingTokenYes = contractsFixture.getReportingToken(market, [0,2])
    reportingTokenNo.buy(100, sender=tester.k0)
    assert reportingTokenNo.balanceOf(tester.a0) == 100
    assert reputationToken.balanceOf(tester.a0) == 6 * 10**6 * 10 **18 - 10**18 - 100
    reportingTokenYes.buy(101, sender=tester.k1)
    assert reportingTokenYes.balanceOf(tester.a1) == 101
    assert reputationToken.balanceOf(tester.a1) == 4 * 10**6 * 10 **18 - 10**18 - 101
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenYes.getPayoutDistributionHash()

    # contest the results
    contractsFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    market.disputeLimitedReporters(sender=tester.k0)
    assert not reportingWindow.isContainerForMarket(market.address)
    assert branch.isContainerForMarket(market.address)
    reportingWindow = contractsFixture.applySignature('reportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)

    # register new reporter for new reporting window
    registrationToken = contractsFixture.applySignature('registrationToken', reportingWindow.getRegistrationToken())
    registrationToken.register(sender=tester.k2)
    assert registrationToken.balanceOf(tester.a2) == 1
    assert reputationToken.balanceOf(tester.a2) == 1 * 10**6 * 10**18 - 10**18

    # report some more
    contractsFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1
    reportingTokenNo.buy(2, sender=tester.k2)
    assert reportingTokenNo.balanceOf(tester.a2) == 2
    assert reputationToken.balanceOf(tester.a2) == 1 * 10**6 * 10 **18 - 10**18 - 2

    # fork
    contractsFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1
    market.disputeAllReporters(sender=tester.k1)
    assert branch.getForkingMarket() == market.address
    assert not reportingWindow.isContainerForMarket(market.address)
    assert branch.isContainerForMarket(market.address)
    reportingWindow = contractsFixture.applySignature('reportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)

    # participate in the fork by moving REP
    noBranch = contractsFixture.getChildBranch(branch, market, [2,0])
    noBranchReputationToken = contractsFixture.applySignature('ReputationToken', noBranch.getReputationToken())
    assert noBranch.address != branch.address
    yesBranch = contractsFixture.getChildBranch(branch, market, [0,2])
    yesBranchReputationToken = contractsFixture.applySignature('ReputationToken', yesBranch.getReputationToken())
    assert yesBranch.address != branch.address
    assert yesBranch.address != noBranch.address

    reputationToken.migrateOut(noBranchReputationToken.address, tester.a0, reputationToken.balanceOf(tester.a0), sender = tester.k0)
    assert not reputationToken.balanceOf(tester.a0)
    assert noBranchReputationToken.balanceOf(tester.a0) == 6 * 10**6 * 10**18 - 10**18 - 100 - 11000 * 10**18
    reputationToken.migrateOut(yesBranchReputationToken.address, tester.a1, reputationToken.balanceOf(tester.a1), sender = tester.k1)
    assert not reputationToken.balanceOf(tester.a1)
    assert yesBranchReputationToken.balanceOf(tester.a1) == 4 * 10**6 * 10**18 - 10**18 - 101 - 110000 * 10**18
    reputationToken.migrateOut(noBranchReputationToken.address, tester.a2, reputationToken.balanceOf(tester.a2), sender = tester.k2)
    assert not reputationToken.balanceOf(tester.a2)
    assert noBranchReputationToken.balanceOf(tester.a2) == 1 * 10**6 * 10**18 - 10**18 - 2

    # finalize
    contractsFixture.chain.head_state.timestamp = branch.getForkEndTime() + 1
    market.tryFinalize()
    assert market.isFinalized()
    assert market.getFinalWinningReportingToken() == reportingTokenNo.address

    # TODO: redeem REP
    # TODO: redeem registration tokens
