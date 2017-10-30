#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture as pytest_fixture
from utils import bytesToHexString


def test_eth_extraction_happy_path(extractable, token, chain):
    extractable.deposit(value=11)
    assert chain.head_state.get_balance(extractable.address) == 11
    startBalance = chain.head_state.get_balance(tester.a0)

    assert extractable.extractEther(tester.a0)

    assert chain.head_state.get_balance(extractable.address) == 0
    assert chain.head_state.get_balance(tester.a0) == startBalance + 11

def test_eth_extraction_failure(extractable, token, chain):
    extractable.deposit(value=11)
    extractable.setProtectedToken(1)

    with raises(TransactionFailed):
        extractable.extractEther(tester.a0)

    with raises(TransactionFailed):
        extractable.extractEther(tester.a0)

def test_token_extraction_happy_path(extractable, token):
    token.faucet(7)
    token.transfer(extractable.address, 7)
    assert token.balanceOf(tester.a0) == 0
    assert token.balanceOf(extractable.address) == 7

    assert extractable.extractTokens(tester.a0, token.address, )

    assert token.balanceOf(tester.a0) == 7
    assert token.balanceOf(extractable.address) == 0

def test_token_extraction_failure(extractable, token, chain):
    token.faucet(7)
    token.transfer(extractable.address, 7)
    extractable.setProtectedToken(token.address)

    with raises(TransactionFailed):
        extractable.extractTokens(tester.a0, token.address)

    with raises(TransactionFailed):
        extractable.extractTokens(tester.a0, token.address)


def test_token_extraction_failure(extractable, token, chain):
    token.faucet(7)
    token.transfer(extractable.address, 7)
    extractable.setProtectedToken(token.address)

    with raises(TransactionFailed):
        extractable.extractTokens(tester.a0, token.address)

    with raises(TransactionFailed):
        extractable.extractTokens(tester.a0, token.address)

@pytest_fixture(scope="session")
def localSnapshot(fixture, baseSnapshot):
    fixture.resetToSnapshot(baseSnapshot)
    fixture.upload('solidity_test_helpers/ExtractableHelper.sol')
    fixture.upload('solidity_test_helpers/StandardTokenHelper.sol')
    return fixture.createSnapshot()

@pytest_fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@pytest_fixture
def extractable(localFixture):
    return localFixture.contracts['ExtractableHelper']

@pytest_fixture
def token(localFixture):
    return localFixture.contracts['StandardTokenHelper']

@pytest_fixture
def chain(localFixture):
    return localFixture.chain
