from ethereum.tools import tester

def test_redeem_legacy_rep(contractsFixture):
    branch = contractsFixture.branch
    reputationToken = contractsFixture.applySignature('ReputationToken', branch.getReputationToken())
    legacyRepContract = contractsFixture.contracts['legacyRepContract']
    legacyRepContract.setSaleDistribution([tester.a0], [long(11 * 10**6 * 10**18)])
    contractsFixture.chain.head_state.timestamp += 15000
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract()
    balance = reputationToken.balanceOf(tester.a0)

    assert balance == 11 * 10**6 * 10**18
