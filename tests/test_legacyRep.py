from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises

def test_legacyRepToken(contractsFixture):
    legacyRep = contractsFixture.contracts['LegacyRepContract']
    amounts = [1, 3, 7, 11, 13, 17]
    accounts = [tester.a0, tester.a1, tester.a2, tester.a3, tester.a4, tester.a5]
    legacyRep.setSaleDistribution(accounts, amounts)
    legacyRep.setSaleDistribution([tester.a6], [11 * 10 ** 6 * 10 ** 18 - sum(amounts)])
    contractsFixture.chain.head_state.timestamp += 15000
    assert legacyRep.getSeeded()
    assert legacyRep.decimals() == 18
    assert legacyRep.totalSupply() == 11 * 10 ** 6 * 10 ** 18

    for x in range(6):
        assert legacyRep.balanceOf(accounts[x]) == amounts[x]
    assert legacyRep.balanceOf(tester.a6) == 11 * 10 ** 6 * 10 ** 18 - sum(amounts)

    assert legacyRep.approve(tester.a0, 17, sender = tester.k5)
    assert legacyRep.allowance(tester.a5, tester.a0) == 17
    assert legacyRep.transferFrom(tester.a5, tester.a1, 17, sender = tester.k0)
    assert legacyRep.balanceOf(tester.a5) == 0
    assert legacyRep.balanceOf(tester.a1) == 20
    assert legacyRep.totalSupply() == 11 * 10 ** 6 * 10 ** 18

    assert legacyRep.transfer(tester.a3, 7, sender = tester.k2)
    assert legacyRep.balanceOf(tester.a3) == 18
    assert legacyRep.balanceOf(tester.a2) == 0

def test_legacyRepFaucet(contractsFixture):
    legacyRep = contractsFixture.contracts['LegacyRepContract']
    amounts = [1, 3, 7, 11, 13, 17]
    accounts = [tester.a0, tester.a1, tester.a2, tester.a3, tester.a4, tester.a5]
    legacyRep.setSaleDistribution(accounts, amounts)
    legacyRep.setSaleDistribution([legacyRep.address], [11 * 10 ** 6 * 10 ** 18 - sum(amounts)])
    contractsFixture.chain.head_state.timestamp += 15000
    assert legacyRep.getSeeded()
    assert legacyRep.decimals() == 18
    assert legacyRep.totalSupply() == 11 * 10 ** 6 * 10 ** 18

    assert legacyRep.balanceOf(legacyRep.address) == 11 * 10 ** 6 * 10 ** 18 - sum(amounts)

    # With the legacyRep contract funded we can now use its faucet method to distribute REP to new test users
    assert legacyRep.balanceOf(tester.a6) == 0
    assert legacyRep.faucet(sender=tester.k6)
    assert legacyRep.balanceOf(tester.a6) == 47 * 10 ** 18

    # We cannot double fund a test account
    with raises(TransactionFailed, message="Double tapping a faucet"):
        legacyRep.faucet(sender=tester.k6)

def test_legacyRepDusting(contractsFixture):
    legacyRep = contractsFixture.contracts['LegacyRepContract']
    amounts = [1, 2]
    accounts = [0, tester.a0]
    legacyRep.setSaleDistribution(accounts, amounts)
    legacyRep.setSaleDistribution([tester.a1], [11 * 10 ** 6 * 10 ** 18 - sum(amounts)])
    contractsFixture.chain.head_state.timestamp += 15000
    assert legacyRep.getSeeded()
    assert legacyRep.decimals() == 18
    assert legacyRep.totalSupply() == 11 * 10 ** 6 * 10 ** 18

    # We have a convenience function for eliminating dusted REP
    assert legacyRep.balanceOf(0) == 1
    assert legacyRep.getRidOfDustForLaunch()
    assert legacyRep.balanceOf(0) == 0