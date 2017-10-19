from ethereum.tools import tester

def test_decimals(contractsFixture, universe):
    reputationTokenFactory = contractsFixture.contracts['ReputationTokenFactory']
    assert reputationTokenFactory
    reputationTokenAddress = reputationTokenFactory.createReputationToken(contractsFixture.contracts['Controller'].address, universe.address)
    reputationToken = contractsFixture.applySignature('ReputationToken', reputationTokenAddress)

    assert reputationToken.decimals() == 18

''' TODO: When we get finer grained test fixture/setup in place make this use a more base fixture without the rep distributed, as without that there is nothing here to test
def test_redeem_legacy_rep(contractsFixture, universe):
    reputationToken = contractsFixture.applySignature('ReputationToken', universe.getReputationToken())
    legacyReputationToken = contractsFixture.contracts['LegacyReputationToken']
    legacyReputationToken.faucet(long(11 * 10**6 * 10**18))
    legacyReputationToken.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyReputationToken()
    balance = reputationToken.balanceOf(tester.a0)
    import pdb;pdb.set_trace()
    assert balance == 11 * 10**6 * 10**18
'''
