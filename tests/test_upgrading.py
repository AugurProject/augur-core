#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture as pytest_fixture
from utils import garbageBytes20, garbageBytes32, stringToBytes


def test_contract_upgrading(localFixture, universe, controller):
    # Get the fork REP migration goal from the universe
    originalForkGoal = universe.getForkReputationGoal()

    # Upgrade the Universe contract
    newUniverseTarget = localFixture.uploadAndAddToController("../tests/solidity_test_helpers/UpgradedUniverse.sol", "Universe", "UpgradedUniverse", force=True)

    # The universe instance we have will delegate to this new contract.
    upgradedUniverse = localFixture.applySignature("UpgradedUniverse", universe.address)

    # Old data is kept
    assert universe.getForkReputationGoal() == originalForkGoal
    assert upgradedUniverse.getNewForkReputationGoal() == originalForkGoal + 1

    # New data works correctly
    assert upgradedUniverse.newData() == 0
    assert upgradedUniverse.setNewData(1)
    assert upgradedUniverse.newData() == 1

    # Overriden functions work
    assert upgradedUniverse.getTypeName() == stringToBytes("UpgradedUniverse")

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
def controller(localFixture):
    return localFixture.contracts["Controller"]
