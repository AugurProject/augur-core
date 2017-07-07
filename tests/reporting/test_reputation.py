from ethereum import tester

def test_redeem_legacy_rep(contractsFixture):
    branch = contractsFixture.branch
    reputationToken = contractsFixture.applySignature('reputationToken', branch.getReputationToken())
    legacyRepContract = contractsFixture.contracts['legacyRepContract']
    legacyRepContract.setSaleDistribution([tester.a0], [long(11 * 10**6 * 10**18)])
    contractsFixture.state.block.timestamp += 15000
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract(branch.address)
    balance = reputationToken.balanceOf(tester.a0)

    assert balance == 11 * 10**6 * 10**18
