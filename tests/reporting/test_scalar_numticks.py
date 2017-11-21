#!/usr/bin/env python

from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises, mark
from utils import stringToBytes

# Values of 0, or other _abnormal_ values will be rejected if they are ultimately unusable by the market. 0 for example cannot be a multiple of the numebr of outcomes and will be rejected if used to create a market
@mark.parametrize('minPrice, maxPrice, tickShift, expectedValue', [
    (1,     2,      2,    100),
    (0,     15,     2,    1500),
    (-10,   30,     1,    400),
    (1,     2,      0,    1),
    (5,     10,     -1,   0),
    (0,     10**20, -10,  10**10),
    (0,     10,     -10,  0),
    (0,     1,      10,   10**10),
])
def test_scalar_num_ticks(minPrice, maxPrice, tickShift, expectedValue, localFixture):
    constants = localFixture.contracts['Constants']
    assert constants.getScalarMarketNumTicks(minPrice, maxPrice, tickShift) == expectedValue

@fixture(scope="session")
def localSnapshot(fixture, controllerSnapshot):
    fixture.resetToSnapshot(controllerSnapshot)
    fixture.upload("solidity_test_helpers/Constants.sol")
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture
