#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture as pytest_fixture
from utils import stringToBytes, AssertLog


def test_default_controlled_time(localFixture, controller, time):
    # By default in testing we upload a controlled version of time to the controller which we control
    assert time.getTimestamp() == controller.getTimestamp() > 0

    # We can verify that it is the controller version of time
    assert controller.lookup("Time") == time.address

    assert time.getTypeName() == stringToBytes("TimeControlled")

    # The owner of the uploaded Time contract can change this time at will
    newTime = time.getTimestamp() + 1
    with AssertLog(localFixture, "TimestampSet", {"newTimestamp": newTime}):
        assert time.setTimestamp(newTime)
    assert time.getTimestamp() == controller.getTimestamp() == newTime

    # Other users cannot
    with raises(TransactionFailed):
        time.setTimestamp(newTime + 1, sender=tester.k1)

    # We can also increment the time
    with AssertLog(localFixture, "TimestampSet", {"newTimestamp": newTime + 1}):
        assert time.incrementTimestamp(1)
    assert time.getTimestamp() == controller.getTimestamp() == newTime + 1

def test_real_time(localFixture, controller):
    # Let's test a real Time provider implementation
    time = localFixture.uploadAndAddToController("../source/contracts/Time.sol", lookupKey="RealTime")

    # We can verify that it is the controller version of time
    assert controller.lookup("RealTime") == time.address

    assert time.getTypeName() == stringToBytes("Time")

    # If we change the block timestamp it will be reflected in the new time
    localFixture.chain.head_state.timestamp = 500

    assert time.getTimestamp() == 500


@pytest_fixture(scope="session")
def localSnapshot(fixture, augurInitializedSnapshot):
    fixture.resetToSnapshot(augurInitializedSnapshot)
    return augurInitializedSnapshot

@pytest_fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@pytest_fixture
def controller(localFixture, localSnapshot):
    return localFixture.contracts["Controller"]

@pytest_fixture
def time(localFixture, localSnapshot):
    return localFixture.contracts["Time"]
