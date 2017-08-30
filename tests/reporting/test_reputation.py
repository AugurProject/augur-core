from ethereum.tools import tester
from utils import longToHexString

def test_decimals(contractsFixture):
    reputationTokenFactory = contractsFixture.contracts['ReputationTokenFactory']
    assert reputationTokenFactory
    reputationTokenAddress = reputationTokenFactory.createReputationToken(contractsFixture.controller.address, contractsFixture.branch.address)
    reputationToken = contractsFixture.applySignature('ReputationToken', reputationTokenAddress)

    assert reputationToken.decimals() == 18

def test_redeem_legacy_rep(contractsFixture):
    branch = contractsFixture.branch
    reputationToken = contractsFixture.applySignature('ReputationToken', branch.getReputationToken())
    legacyRepContract = contractsFixture.contracts['LegacyRepContract']
    legacyRepContract.setSaleDistribution([tester.a0], [long(11 * 10**6 * 10**18)])
    contractsFixture.chain.head_state.timestamp += 15000
    legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
    reputationToken.migrateFromLegacyRepContract()
    balance = reputationToken.balanceOf(tester.a0)

    assert balance == 11 * 10**6 * 10**18
