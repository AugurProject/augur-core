#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import AssertLog, bytesToHexString, garbageBytes20, garbageBytes32, stringToBytes

def test_init(contractsFixture, market):
    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken())

    assert shareToken.name() == "Shares", "currency name"
    assert shareToken.decimals() == 0, "number of decimals"
    assert shareToken.symbol() == "SHARE", "currency symbol"

    assert shareToken.getTypeName() == stringToBytes("ShareToken")

def test_createShares(contractsFixture, market):
    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken())
    initialTotalSupply = shareToken.totalSupply()
    initialBalance = shareToken.balanceOf(tester.a1)

    with raises(TransactionFailed):
        shareToken.createShares(tester.a1, 7, sender=tester.k1)

    # NOTE: only works because controller is in dev mode and k0 is whitelisted
    assert shareToken.createShares(tester.a1, 7, sender=tester.k0) == 1, "Create share tokens for address 1"
    assert shareToken.totalSupply() - initialTotalSupply == 7, "Total supply increase should equal the number of tokens created"
    assert shareToken.balanceOf(tester.a1) - initialBalance == 7, "Address 1 token balance increase should equal the number of tokens created"

def test_destroyShares(contractsFixture, market):
    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken())
    shareToken.createShares(tester.a1, 7, sender=tester.k0)
    initialTotalSupply = shareToken.totalSupply()
    initialBalance = shareToken.balanceOf(tester.a1)

    with raises(TransactionFailed):
        shareToken.destroyShares(tester.a0, 7, sender=tester.k1)

    # NOTE: only works because controller is in dev mode and k0 is whitelisted
    assert shareToken.destroyShares(tester.a1, 7, sender=tester.k0) == 1, "Destroy share tokens owned by address 1"
    assert initialTotalSupply - shareToken.totalSupply() == 7, "Total supply decrease should equal the number of tokens destroyed"
    assert initialBalance - shareToken.balanceOf(tester.a1) == 7, "Address 1 token balance decrease should equal the number of tokens destroyed"

def test_transfer(contractsFixture, market):
    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken())
    shareToken.createShares(tester.a0, 7, sender=tester.k0)
    initialTotalSupply = shareToken.totalSupply()
    initialBalance0 = shareToken.balanceOf(tester.a0)
    initialBalance1 = shareToken.balanceOf(tester.a1)

    with raises(TransactionFailed):
        shareToken.transfer(tester.a0, 11, sender=tester.k0)
    with raises(TransactionFailed):
        shareToken.transfer(tester.a0, 5, sender = tester.k1)

    transferLog = {
        "_event_type": "Transfer",
        "from": bytesToHexString(tester.a0),
        "to": bytesToHexString(tester.a1),
        "value": 5,
    }

    tokensTransferredLog = {
        "_event_type": "TokensTransferred",
        "token": shareToken.address,
        "from": bytesToHexString(tester.a0),
        "to": bytesToHexString(tester.a1),
        "universe": market.getUniverse(),
        "tokenType": 1,
        "market": market.address,
        "value": 5
    }

    with AssertLog(contractsFixture, "Transfer", transferLog, contract=shareToken):
        with AssertLog(contractsFixture, "TokensTransferred", tokensTransferredLog):
            assert shareToken.transfer(tester.a1, 5, sender=tester.k0)

    afterTransferBalance0 = shareToken.balanceOf(tester.a0)
    afterTransferBalance1 = shareToken.balanceOf(tester.a1)

    assert(initialBalance0 - 5 == afterTransferBalance0), "Decrease in address 1's balance should equal amount transferred"
    assert(initialBalance1 + 5 == afterTransferBalance1), "Increase in address 2's balance should equal amount transferred"
    assert(shareToken.totalSupply() == initialTotalSupply), "Total supply should be unchanged"

def test_approve(contractsFixture, market):
    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken())
    shareToken.createShares(tester.a0, 7, sender=tester.k0)

    assert(shareToken.allowance(tester.a0, tester.a1) == 0), "initial allowance is 0"

    approvalLog = {
        "owner": bytesToHexString(tester.a0),
        "spender": bytesToHexString(tester.a1),
        "value": 10
    }

    with AssertLog(contractsFixture, "Approval", approvalLog, contract=shareToken):
        assert shareToken.approve(tester.a1, 10, sender=tester.k0)
    assert(shareToken.allowance(tester.a0, tester.a1) == 10), "allowance is 10 after approval"

    transferLog = {
        "from": bytesToHexString(tester.a0),
        "to": bytesToHexString(tester.a1),
        "value": 7
    }

    tokensTransferredLog = {
        "token": shareToken.address,
        "from": bytesToHexString(tester.a0),
        "to": bytesToHexString(tester.a1),
        "universe": market.getUniverse(),
        "tokenType": 1,
        "market": market.address,
        "value": 7
    }

    with AssertLog(contractsFixture, "Transfer", transferLog, contract=shareToken):
        with AssertLog(contractsFixture, "TokensTransferred", tokensTransferredLog):
            assert shareToken.transferFrom(tester.a0, tester.a1, 7, sender=tester.k1)

def test_transferFrom(contractsFixture, market):
    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken())
    shareToken.createShares(tester.a1, 7, sender=tester.k0)

    with raises(TransactionFailed):
        shareToken.transferFrom(tester.a0, tester.a1, 7, sender=tester.k1)

def test_suicideFunds(contractsFixture, market):
    shareToken = contractsFixture.applySignature('ShareToken', market.getShareToken())

    with raises(TransactionFailed):
        shareToken.suicideFunds(tester.a0, [], sender=tester.k0)
