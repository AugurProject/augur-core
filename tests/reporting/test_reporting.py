from ethereum import tester
from ContractsFixture import ContractsFixture
from datetime import timedelta

tester.gas_limit = long(4.2 * 10**6)

def test_reporting():
    fixture = ContractsFixture()

    # seed legacy rep contract
    legacyRepContract = fixture.uploadAndAddToController('../src/legacyRepContract.se')
    legacyRepContract.setSaleDistribution([tester.a0], [long(11 * 10**6 * 10**18)])
    fixture.state.block.timestamp += 15000

    # create the root branch
    branch = fixture.createBranch(0, 0)

    # get the reputation token for this branch and migrate legacy REP to it
    reputationToken = fixture.applySignature('reputationToken', branch.getReputationToken())
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract(branch.address)

    # give some REP to someone else to make things interesting
    reputationToken.transfer(tester.a1, 4 * 10**6 * 10**18)
    reputationToken.transfer(tester.a2, 1 * 10**6 * 10**18)

    # create a market
    cash = fixture.getSeededCash()
    market = fixture.createReasonableBinaryMarket(branch, cash)
    reportingWindow = fixture.applySignature('reportingWindow', market.getReportingWindow())

    # buy registration tokens
    registrationToken = fixture.applySignature('registrationToken', reportingWindow.getRegistrationToken())
    registrationToken.register(sender=tester.k0)
    assert registrationToken.balanceOf(tester.a0) == 1
    assert reputationToken.balanceOf(tester.a0) == 6 * 10**6 * 10**18 - 10**18
    registrationToken.register(sender=tester.k1)
    assert registrationToken.balanceOf(tester.a1) == 1
    assert reputationToken.balanceOf(tester.a1) == 4 * 10**6 * 10**18 - 10**18

    # fast forward to one second after the next reporting window
    reportingWindow = fixture.applySignature('reportingWindow', branch.getNextReportingWindow())
    fixture.state.block.timestamp = reportingWindow.getStartTime() + 1

    # both reporters report on the outcome
    reportingTokenNo = fixture.getReportingToken(market, [2,0])
    reportingTokenYes = fixture.getReportingToken(market, [0,2])
    reportingTokenNo.buy(100, sender=tester.k0)
    assert reportingTokenNo.balanceOf(tester.a0) == 100
    assert reputationToken.balanceOf(tester.a0) == 6 * 10**6 * 10 **18 - 10**18 - 100
    reportingTokenYes.buy(101, sender=tester.k1)
    assert reportingTokenYes.balanceOf(tester.a1) == 101
    assert reputationToken.balanceOf(tester.a1) == 4 * 10**6 * 10 **18 - 10**18 - 101
    tentativeWinner = market.getTentativeWinningPayoutDistributionHash()
    assert tentativeWinner == reportingTokenYes.getPayoutDistributionHash()

    # contest the results
    fixture.state.block.timestamp = reportingWindow.getDisputeStartTime() + 1
    market.disputeLimitedReporters(sender=tester.k0)
    assert not reportingWindow.isContainerForMarket(market.address)
    assert branch.isContainerForMarket(market.address)
    reportingWindow = fixture.applySignature('reportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)

    # register new reporter for new reporting window
    registrationToken = fixture.applySignature('registrationToken', reportingWindow.getRegistrationToken())
    registrationToken.register(sender=tester.k2)
    assert registrationToken.balanceOf(tester.a2) == 1
    assert reputationToken.balanceOf(tester.a2) == 1 * 10**6 * 10**18 - 10**18

    # report some more
    fixture.state.block.timestamp = reportingWindow.getStartTime() + 1
    reportingTokenNo.buy(2, sender=tester.k2)
    assert reportingTokenNo.balanceOf(tester.a2) == 2
    assert reputationToken.balanceOf(tester.a2) == 1 * 10**6 * 10 **18 - 10**18 - 2

    # fork
    fixture.state.block.timestamp = reportingWindow.getDisputeStartTime() + 1
    market.disputeAllReporters(sender=tester.k1)
    assert branch.getForkingMarket() == market.address
    assert not reportingWindow.isContainerForMarket(market.address)
    assert branch.isContainerForMarket(market.address)
    reportingWindow = fixture.applySignature('reportingWindow', market.getReportingWindow())
    assert reportingWindow.isContainerForMarket(market.address)

    # participate in the fork by moving REP
    noBranch = fixture.getChildBranch(branch, market, [2,0])
    noBranchReputationToken = fixture.applySignature('reputationToken', noBranch.getReputationToken())
    assert noBranch.address != branch.address
    yesBranch = fixture.getChildBranch(branch, market, [0,2])
    yesBranchReputationToken = fixture.applySignature('reputationToken', yesBranch.getReputationToken())
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
    fixture.state.block.timestamp = branch.getForkEndTime() + 1
    market.tryFinalize()
    assert market.isFinalized()
    assert market.getFinalWinningReportingToken() == reportingTokenNo.address

    # TODO: redeem REP
    # TODO: redeem registration tokens
