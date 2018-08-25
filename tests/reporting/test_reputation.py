from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import AssertLog, bytesToHexString

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

    tokensTransferredLog = {
        'from': bytesToHexString(tester.a0),
        'to': bytesToHexString(tester.a1),
        'token': reputationToken.address,
        'universe': universe.address,
        'tokenType': 0,
        'value': 8,
    }

    with AssertLog(contractsFixture, 'TokensTransferred', tokensTransferredLog):
        assert reputationToken.transfer(tester.a1, 8)

    assert reputationToken.approve(tester.a2, 12)

    tokensTransferredLog['value'] = 12
    with AssertLog(contractsFixture, 'TokensTransferred', tokensTransferredLog):
        assert reputationToken.transferFrom(tester.a0, tester.a1, 12, sender=tester.k2)

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
    legacyReputationToken.approve(reputationToken.address, 100, sender=tester.k1)
    reputationToken.migrateFromLegacyReputationToken(sender=tester.k1)
    assert reputationToken.balanceOf(tester.a1) == 100

    # Doing again is a noop
    reputationToken.migrateFromLegacyReputationToken(sender=tester.k1)
    assert reputationToken.balanceOf(tester.a1) == 100

    # Doing with an account which has no legacy REP is a noop
    legacyReputationToken.approve(reputationToken.address, 100)
    reputationToken.migrateFromLegacyReputationToken(sender=tester.k6)
    assert reputationToken.balanceOf(tester.a6) == 0

    # We'll finish the migration now
    legacyReputationToken.approve(reputationToken.address, 11 * 10**6 * 10**18, sender=tester.k0)
    reputationToken.migrateFromLegacyReputationToken(sender=tester.k0)
    assert reputationToken.balanceOf(tester.a0) == 11 * 10**6 * 10**18 - 200

    legacyReputationToken.approve(reputationToken.address, 100, sender=tester.k2)
    reputationToken.migrateFromLegacyReputationToken(sender=tester.k2)
    assert reputationToken.balanceOf(tester.a2) == 100
