#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture
from ethereum.config import config_metropolis

def test_contract_exists(localFixture):
    contractExistsHelper = localFixture.contracts['ContractExistsHelper']

    assert contractExistsHelper.doesContractExist(contractExistsHelper.address)
    assert not contractExistsHelper.doesContractExist(0)

@fixture(scope="session")
def localSnapshot(fixture, baseSnapshot):
    fixture.resetToSnapshot(baseSnapshot)
    fixture.upload('solidity_test_helpers/ContractExistsHelper.sol')
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture
