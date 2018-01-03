#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises
from utils import stringToBytes, EtherDelta, TokenDelta

def test_mailbox_eth_happy_path(localFixture, mailbox):
    # We can send some ETH to the mailbox
    with EtherDelta(100, mailbox.address, localFixture.chain, "Deposit did not work"):
        assert mailbox.depositEther(value=100)

    # We can also withdraw the ETH balance of the mailbox
    with EtherDelta(100, tester.a0, localFixture.chain, "Withdraw did not work"):
        assert mailbox.withdrawEther()

def test_mailbox_tokens_happy_path(localFixture, mailbox, token):
    # We can send some Tokens to the mailbox
    assert token.faucet(100)

    with TokenDelta(token, 100, mailbox.address, "Token deposit did not work"):
        with TokenDelta(token, -100, tester.a0, "Token deposit did not work"):
            token.transfer(mailbox.address, 100)

    # The mailbox owner can withdraw these tokens
    with TokenDelta(token, 100, tester.a0, "Token withdraw did not work"):
        with TokenDelta(token, -100, mailbox.address, "Token withdraw did not work"):
            mailbox.withdrawTokens(token.address)

def test_mailbox_eth_failure(localFixture, mailbox):
    # We send some ETH to the mailbox
    with EtherDelta(100, mailbox.address, localFixture.chain, "Deposit did not work"):
        assert mailbox.depositEther(value=100)

    # Withdrawing as someone other than the owner will fail
    with raises(TransactionFailed):
        mailbox.withdrawEther(sender=tester.k1)

def test_mailbox_tokens_failure(localFixture, mailbox, token):
    # We send some Tokens to the mailbox
    assert token.faucet(100)

    with TokenDelta(token, 100, mailbox.address, "Token deposit did not work"):
        with TokenDelta(token, -100, tester.a0, "Token deposit did not work"):
            token.transfer(mailbox.address, 100)

    # Withdrawing as someone other than the owner will fail
    with raises(TransactionFailed):
        mailbox.withdrawTokens(token.address, sender=tester.k1)

def test_mailbox_cash_happy_path(localFixture, mailbox, cash):
    # We can send some Cash to the mailbox
    assert cash.depositEther(value=100)
    assert cash.balanceOf(tester.a0) == 100

    with TokenDelta(cash, 100, mailbox.address, "Deposit did not work"):
        assert cash.transfer(mailbox.address, 100)

    # We can withdraw "Ether" and the Cash balance in the mailbox will be given to the owner as Ether
    with EtherDelta(100, tester.a0, localFixture.chain, "Withdraw did not work"):
        assert mailbox.withdrawEther()

@fixture(scope="session")
def localSnapshot(fixture, controllerSnapshot):
    fixture.resetToSnapshot(controllerSnapshot)

    fixture.uploadAugur()

    # Upload a token
    fixture.uploadAndAddToController("solidity_test_helpers/StandardTokenHelper.sol")

    # Upload Cash
    cash = fixture.uploadAndAddToController("../source/contracts/trading/Cash.sol")
    cash.setController(fixture.contracts['Controller'].address)

    # Upload the mailbox
    name = "Mailbox"
    targetName = "MailboxTarget"
    fixture.uploadAndAddToController("../source/contracts/reporting/Mailbox.sol", targetName, name)
    fixture.uploadAndAddToController("../source/contracts/libraries/Delegator.sol", name, "delegator", constructorArgs=[fixture.contracts['Controller'].address, stringToBytes(targetName)])
    fixture.contracts[name] = fixture.applySignature(name, fixture.contracts[name].address)
    fixture.contracts[name].initialize(tester.a0)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def mailbox(localFixture):
    return localFixture.contracts['Mailbox']

@fixture
def token(localFixture):
    return localFixture.contracts['StandardTokenHelper']

@fixture
def cash(localFixture):
    return localFixture.contracts['Cash']
