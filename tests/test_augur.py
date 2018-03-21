#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture as pytest_fixture


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
