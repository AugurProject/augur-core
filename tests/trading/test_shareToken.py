#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import captureFilteredLogs, bytesToHexString

def test_init(contractsFixture):
    shareToken = contractsFixture.applySignature('ShareToken', contractsFixture.binaryMarket.getShareToken())

    # FIXME: enable after we fix Delegated contract string handling
    # assert shareToken.name() == "Shares", "currency name"
    assert shareToken.decimals() == 0, "number of decimals"
    # assert shareToken.symbol() == "SHARE", "currency symbol"

def test_createShares(contractsFixture):
    shareToken = contractsFixture.applySignature('ShareToken', contractsFixture.binaryMarket.getShareToken())
    initialTotalSupply = shareToken.totalSupply()
    initialBalance = shareToken.balanceOf(tester.a1)

    with raises(TransactionFailed):
        shareToken.createShares(tester.a1, 7, sender=tester.k1)

    # NOTE: only works because controller is in dev mode and k0 is whitelisted
    assert shareToken.createShares(tester.a1, 7, sender=tester.k0) == 1, "Create share tokens for address 1"
    assert shareToken.totalSupply() - initialTotalSupply == 7, "Total supply increase should equal the number of tokens created"
    assert shareToken.balanceOf(tester.a1) - initialBalance == 7, "Address 1 token balance increase should equal the number of tokens created"

def test_destroyShares(contractsFixture):
    shareToken = contractsFixture.applySignature('ShareToken', contractsFixture.binaryMarket.getShareToken())
    shareToken.createShares(tester.a1, 7, sender=tester.k0)
    initialTotalSupply = shareToken.totalSupply()
    initialBalance = shareToken.balanceOf(tester.a1)

    with raises(TransactionFailed):
        shareToken.destroyShares(tester.a0, 7, sender=tester.k1)

    # NOTE: only works because controller is in dev mode and k0 is whitelisted
    assert shareToken.destroyShares(tester.a1, 7, sender=tester.k0) == 1, "Destroy share tokens owned by address 1"
    assert initialTotalSupply - shareToken.totalSupply() == 7, "Total supply decrease should equal the number of tokens destroyed"
    assert initialBalance - shareToken.balanceOf(tester.a1) == 7, "Address 1 token balance decrease should equal the number of tokens destroyed"

def test_transfer(contractsFixture):
    shareToken = contractsFixture.applySignature('ShareToken', contractsFixture.binaryMarket.getShareToken())
    shareToken.createShares(tester.a0, 7, sender=tester.k0)
    initialTotalSupply = shareToken.totalSupply()
    initialBalance0 = shareToken.balanceOf(tester.a0)
    initialBalance1 = shareToken.balanceOf(tester.a1)
    logs = []

    with raises(TransactionFailed):
        shareToken.transfer(tester.a0, 11, sender=tester.k0)
    with raises(TransactionFailed):
        shareToken.transfer(tester.a0, 5, sender = tester.k1)

    captureFilteredLogs(contractsFixture.chain.head_state, shareToken, logs)
    retval = shareToken.transfer(tester.a1, 5, sender=tester.k0)
    afterTransferBalance0 = shareToken.balanceOf(tester.a0)
    afterTransferBalance1 = shareToken.balanceOf(tester.a1)

    assert(retval == 1), "transfer should succeed"
    assert logs == [
        {
            "_event_type": "Transfer",
            "from": bytesToHexString(tester.a0),
            "to": bytesToHexString(tester.a1),
            "value": 5
        }
    ]
    assert(initialBalance0 - 5 == afterTransferBalance0), "Decrease in address 1's balance should equal amount transferred"
    assert(initialBalance1 + 5 == afterTransferBalance1), "Increase in address 2's balance should equal amount transferred"
    assert(shareToken.totalSupply() == initialTotalSupply), "Total supply should be unchanged"
    assert(retval == 1), "transfer with 0 value should succeed"

def test_approve(contractsFixture):
    shareToken = contractsFixture.applySignature('ShareToken', contractsFixture.binaryMarket.getShareToken())
    shareToken.createShares(tester.a0, 7, sender=tester.k0)
    logs = []

    assert(shareToken.allowance(tester.a0, tester.a1) == 0), "initial allowance is 0"
    captureFilteredLogs(contractsFixture.chain.head_state, shareToken, logs)
    retval = shareToken.approve(tester.a1, 10, sender=tester.k0)
    assert(retval == 1), "approve a2 to spend 10 cash from a1"
    assert(shareToken.allowance(tester.a0, tester.a1) == 10), "allowance is 10 after approval"
    retval = shareToken.transferFrom(tester.a0, tester.a1, 7, sender=tester.k1)
    assert(retval == 1), "transferFrom should succeed"
    assert logs == [
        {
            "_event_type": "Approval",
            "owner": bytesToHexString(tester.a0),
            "spender": bytesToHexString(tester.a1),
            "value": 10
        },
        {
            "_event_type": "Transfer",
            "from": bytesToHexString(tester.a0),
            "to": bytesToHexString(tester.a1),
            "value": 7
        },
    ]

def test_transferFrom(contractsFixture):
    shareToken = contractsFixture.applySignature('ShareToken', contractsFixture.binaryMarket.getShareToken())
    shareToken.createShares(tester.a1, 7, sender=tester.k0)

    with raises(TransactionFailed):
        shareToken.transferFrom(tester.a0, tester.a1, 7, sender=tester.k1)

def test_setController(contractsFixture):
    shareToken = contractsFixture.applySignature('ShareToken', contractsFixture.binaryMarket.getShareToken())
    newController = contractsFixture.upload('../src/Controller.sol', 'newController')
    newController.setValue('shareToken'.ljust(32, '\x00'), shareToken.address)

    contractsFixture.controller.updateController(shareToken.address, newController.address, sender=tester.k0)
    with raises(TransactionFailed):
        shareToken.setController(tester.a0, sender=tester.k0)

def test_suicideFunds(contractsFixture):
    shareToken = contractsFixture.applySignature('ShareToken', contractsFixture.binaryMarket.getShareToken())

    with raises(TransactionFailed):
        shareToken.suicideFunds(tester.a0, sender=tester.k0)
