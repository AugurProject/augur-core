from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import captureFilteredLogs, bytesToHexString

def test_init(contractsFixture, universe):
    reputationTokenFactory = contractsFixture.contracts['ReputationTokenFactory']
    assert reputationTokenFactory
    reputationTokenAddress = reputationTokenFactory.createReputationToken(contractsFixture.contracts['Controller'].address, universe.address)
    reputationToken = contractsFixture.applySignature('ReputationToken', reputationTokenAddress)

    assert reputationToken.name() == "Reputation"
    assert reputationToken.decimals() == 18
    assert reputationToken.symbol() == "REP"

def test_reputation_token_logging(contractsFixture, universe):
    reputationToken = contractsFixture.applySignature("ReputationToken", universe.getReputationToken())

    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)

    assert reputationToken.transfer(tester.a1, 8)

    assert len(logs) == 1
    assert logs[0]['_event_type'] == 'TokensTransferred'
    assert logs[0]['from'] == bytesToHexString(tester.a0)
    assert logs[0]['to'] == bytesToHexString(tester.a1)
    assert logs[0]['token'] == reputationToken.address
    assert logs[0]['universe'] == universe.address
    assert logs[0]['tokenType'] == 0
    assert logs[0]['value'] == 8

    assert reputationToken.approve(tester.a2, 12)

    assert reputationToken.transferFrom(tester.a0, tester.a1, 12, sender=tester.k2)

    assert len(logs) == 2
    assert logs[1]['_event_type'] == 'TokensTransferred'
    assert logs[1]['from'] == bytesToHexString(tester.a0)
    assert logs[1]['to'] == bytesToHexString(tester.a1)
    assert logs[1]['token'] == reputationToken.address
    assert logs[1]['universe'] == universe.address
    assert logs[0]['tokenType'] == 0
    assert logs[1]['value'] == 12

def test_legacy_migration(augurInitializedFixture):
    # Initialize the legacy REP contract with some balances
    legacyReputationToken = augurInitializedFixture.contracts['LegacyReputationToken']
    legacyReputationToken.faucet(11 * 10**6 * 10**18)
    legacyReputationToken.transfer(tester.a1, 100)
    legacyReputationToken.transfer(tester.a2, 100)
    legacyReputationToken.approve(tester.a1, 1000)
    legacyReputationToken.approve(tester.a2, 2000)

    # When we create a genesis universe we'll need to migrate the legacy REP before the contract can be used
    universe = augurInitializedFixture.createUniverse()
    reputationToken = augurInitializedFixture.applySignature("ReputationToken", universe.getReputationToken())

    # We'll only partially migrate right now
    reputationToken.migrateBalancesFromLegacyRep([tester.a1])
    assert reputationToken.balanceOf(tester.a1) == 100

    # Since the migration has not completed we can't transfer or do normal token actions
    assert reputationToken.getIsMigratingFromLegacy()
    with raises(TransactionFailed):
        reputationToken.transfer(tester.a2, 1, sender=tester.k1)

    # Before we finish the migration we'll migrate some allowances
    assert reputationToken.migrateAllowancesFromLegacyRep([tester.a0, tester.a0], [tester.a1, tester.a2])
    assert reputationToken.allowance(tester.a0, tester.a1) == 1000
    assert reputationToken.allowance(tester.a0, tester.a2) == 2000

    # We'll finish the migration now and confirm we can transfer
    reputationToken.migrateBalancesFromLegacyRep([tester.a0, tester.a2])
    assert not reputationToken.getIsMigratingFromLegacy()
    assert reputationToken.transfer(tester.a2, 1, sender=tester.k1)

    # Now that the migration is complete we can no longer migrate balances or allowances from the legacy contract
    with raises(TransactionFailed):
        reputationToken.migrateBalancesFromLegacyRep([tester.a2])

    with raises(TransactionFailed):
        reputationToken.migrateAllowancesFromLegacyRep([tester.a0, tester.a2])