from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises

def test_legacyRepFaucet(contractsFixture):
    legacyRep = contractsFixture.contracts['LegacyRepContract']
    assert legacyRep.decimals() == 18
    assert legacyRep.getTotalSupply() == 0

    # With the legacyRep contract funded we can now use its faucet method to distribute REP to new test users
    assert legacyRep.balanceOf(tester.a0) == 0
    assert legacyRep.faucet(sender=tester.k0)
    assert legacyRep.balanceOf(tester.a0) == 47 * 10 ** 18

    # Total supply increases by the amount funded
    assert legacyRep.getTotalSupply() == 47 * 10 ** 18

    # We can request a specific amount from the faucet too
    assert legacyRep.faucet(10)
    assert legacyRep.balanceOf(tester.a0) == 47 * 10 ** 18 + 10
