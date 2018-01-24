#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture as pytest_fixture


def test_augur_central_authority_for_cash(augur, cash):
    # In testing we automatically provide the augur central authority contract with approval to transfer on behalf of the tester accounts
    testers = [(getattr(tester, 'k%i' % x), getattr(tester, 'a%i' % x)) for x in range(0,10)]
    # We will prove this by having testers dust some of their Cash through a trusted request to the Augur contract
    for (testerKey, testerAddress) in testers:
        assert cash.depositEther(sender=testerKey, value=100)
        originalTesterBalance = cash.balanceOf(testerAddress)
        originalVoidBalance = cash.balanceOf(0)
        assert augur.trustedTransfer(cash.address, testerAddress, 0, 40)
        assert cash.balanceOf(testerAddress) == originalTesterBalance - 40
        assert cash.balanceOf(0) == originalVoidBalance + 40

def test_is_known_universe(augur, universe):
    assert augur.isKnownUniverse(universe.address)
    assert not augur.isKnownUniverse(augur.address)

@pytest_fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    snapshot = fixture.createSnapshot()
    return snapshot

@pytest_fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@pytest_fixture
def augur(localFixture, localSnapshot):
    return localFixture.contracts["Augur"]

@pytest_fixture
def cash(localFixture, localSnapshot):
    return localFixture.contracts["Cash"]
