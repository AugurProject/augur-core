#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture as pytest_fixture


def test_is_known_universe(augur, universe):
    assert augur.isKnownUniverse(universe.address)
    assert not augur.isKnownUniverse(augur.address)

def test_known_universe_child_creation_failure(augur):
    with raises(TransactionFailed):
        augur.createChildUniverse("", [0, 10000], False)

def test_trusted_transfer_amount_failure(augur):
    with raises(TransactionFailed):
        augur.trustedTransfer(augur.address, augur.address, augur.address, 0)

def test_log_requires(augur, universe):
    with raises(TransactionFailed):
        augur.logMarketCreated("", "", "", universe.address, universe.address, universe.address, 0, 100, 0)

    with raises(TransactionFailed):
        augur.logMarketCreated("", "", "", augur.address, augur.address, augur.address, 0, 100, 0)

    with raises(TransactionFailed):
        augur.logInitialReportSubmitted(universe.address, universe.address, universe.address, 1, False, [0, 10000], False)

    with raises(TransactionFailed):
        augur.logInitialReportSubmitted(augur.address, augur.address, augur.address, 1, False, [0, 10000], False)

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
