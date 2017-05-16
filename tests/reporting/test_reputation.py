from ethereum import tester
from ContractsFixture import ContractsFixture

def test_redeem_legacy_rep():
    fixture = ContractsFixture()

    branch = fixture.createBranch(0, 0)
    reputationToken = fixture.applySignature('reputationToken', branch.getReputationToken())
    legacyRepContract = fixture.uploadAndAddToController('../src/legacyRepContract.se')
    legacyRepContract.setSaleDistribution([tester.a0], [long(11 * 10**6 * 10**18)])
    fixture.state.block.timestamp += 15000
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract(branch.address)
    balance = reputationToken.balanceOf(tester.a0)

    assert balance == 11 * 10**6 * 10**18
