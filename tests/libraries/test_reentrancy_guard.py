#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, mark, raises

@fixture(scope='session')
def testerSnapshot(sessionFixture):
    sessionFixture.uploadAndAddToController('solidity_test_helpers/ReentrancyGuardHelper.sol')
    ReentrancyGuardHelper = sessionFixture.contracts['ReentrancyGuardHelper']
    return sessionFixture.createSnapshot()

@fixture
def testerContractsFixture(sessionFixture, testerSnapshot):
    sessionFixture.resetToSnapshot(testerSnapshot)
    return sessionFixture

def test_nonReentrant(testerContractsFixture):
    ReentrancyGuardHelper = testerContractsFixture.contracts['ReentrancyGuardHelper']
    assert ReentrancyGuardHelper.testerCanReentrant()

    with raises(TransactionFailed):
        ReentrancyGuardHelper.testerCanNotReentrant()
