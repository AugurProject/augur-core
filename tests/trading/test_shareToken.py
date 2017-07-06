#!/usr/bin/env python

from ContractsFixture import ContractsFixture
from ethereum import tester
from ethereum.tester import TransactionFailed
from iocapture import capture
from pytest import raises
from utils import parseCapturedLogs

def test_init():
    fixture = ContractsFixture()
    shareToken = fixture.upload('../src/trading/shareToken.se')

    assert shareToken.getName() == 0x5368617265730000000000000000000000000000000000000000000000000000, "currency name"
    assert shareToken.getDecimals() == 18, "number of decimals"
    assert shareToken.getSymbol() == 0x5348415245000000000000000000000000000000000000000000000000000000, "currency symbol"

def test_createShares():
    fixture = ContractsFixture()
    shareToken = fixture.uploadShareToken()
    fixture.controller.addToWhitelist(tester.a0)
    initialTotalSupply = shareToken.totalSupply()
    initialBalance = shareToken.balanceOf(tester.a1)

    with raises(TransactionFailed):
        shareToken.createShares(tester.a1, 7, sender=tester.k1)

    assert shareToken.createShares(tester.a1, 7, sender=tester.k0) == 1, "Create share tokens for address 1"
    assert shareToken.totalSupply() - initialTotalSupply == 7, "Total supply increase should equal the number of tokens created"
    assert shareToken.balanceOf(tester.a1) - initialBalance == 7, "Address 1 token balance increase should equal the number of tokens created"

def test_destroyShares():
    fixture = ContractsFixture()
    shareToken = fixture.uploadShareToken()
    fixture.controller.addToWhitelist(tester.a0)
    shareToken.createShares(tester.a1, 7, sender=tester.k0)
    initialTotalSupply = shareToken.totalSupply()
    initialBalance = shareToken.balanceOf(tester.a1)

    with raises(TransactionFailed):
        shareToken.destroyShares(tester.a0, 7, sender=tester.k1)

    assert shareToken.destroyShares(tester.a1, 7, sender=tester.k0) == 1, "Destroy share tokens owned by address 1"
    assert initialTotalSupply - shareToken.totalSupply() == 7, "Total supply decrease should equal the number of tokens destroyed"
    assert initialBalance - shareToken.balanceOf(tester.a1) == 7, "Address 1 token balance decrease should equal the number of tokens destroyed"

def test_transfer():
    fixture = ContractsFixture()
    shareToken = fixture.uploadShareToken()
    fixture.controller.addToWhitelist(tester.a0)
    shareToken.createShares(tester.a0, 7, sender=tester.k0)
    initialTotalSupply = shareToken.totalSupply()
    initialBalance0 = shareToken.balanceOf(tester.a0)
    initialBalance1 = shareToken.balanceOf(tester.a1)

    with raises(TransactionFailed):
        shareToken.transfer(tester.a0, 11, sender=tester.k0)
    with raises(TransactionFailed):
        shareToken.transfer(tester.a0, -13, sender=tester.k0)
    with raises(TransactionFailed):
        shareToken.transfer(tester.a0, 0, sender = tester.k0)
    with raises(TransactionFailed):
        shareToken.transfer(tester.a0, 5, sender = tester.k1)
    with capture() as captured:
        retval = shareToken.transfer(tester.a1, 5, sender=tester.k0)
        logged = parseCapturedLogs(captured.stdout)[-1]
    afterTransferBalance0 = shareToken.balanceOf(tester.a0)
    afterTransferBalance1 = shareToken.balanceOf(tester.a1)

    assert(retval == 1), "transfer should succeed"
    assert(logged["_event_type"] == "Transfer")
    assert(logged["from"] == tester.a0.encode('hex'))
    assert(logged["to"] == tester.a1.encode('hex'))
    assert(logged["value"] == 5)
    assert(initialBalance0 - 5 == afterTransferBalance0), "Decrease in address 1's balance should equal amount transferred"
    assert(initialBalance1 + 5 == afterTransferBalance1), "Increase in address 2's balance should equal amount transferred"
    assert(shareToken.totalSupply() == initialTotalSupply), "Total supply should be unchanged"
    assert(retval == 1), "transfer with 0 value should succeed"

def test_approve():
    fixture = ContractsFixture()
    shareToken = fixture.uploadShareToken()
    fixture.controller.addToWhitelist(tester.a0)
    shareToken.createShares(tester.a0, 7, sender=tester.k0)

    assert(shareToken.allowance(tester.a0, tester.a1) == 0), "initial allowance is 0"
    with capture() as captured:
        retval = shareToken.approve(tester.a1, 10, sender=tester.k0)
        logged = parseCapturedLogs(captured.stdout)[-1]
    assert(retval == 1), "approve a2 to spend 10 cash from a1"
    assert(logged["_event_type"] == "Approval")
    assert(logged["owner"] == tester.a0.encode('hex'))
    assert(logged["spender"] == tester.a1.encode('hex'))
    assert(logged["value"] == 10)
    assert(shareToken.allowance(tester.a0, tester.a1) == 10), "allowance is 10 after approval"
    with capture() as captured:
        retval = shareToken.transferFrom(tester.a0, tester.a1, 7, sender=tester.k1)
        logged = parseCapturedLogs(captured.stdout)[-1]
    assert(retval == 1), "transferFrom should succeed"
    assert(logged["_event_type"] == "Transfer")
    assert(logged["from"] == tester.a0.encode('hex'))
    assert(logged["to"] == tester.a1.encode('hex'))
    assert(logged["value"] == 7)

def test_transferFrom():
    fixture = ContractsFixture()
    shareToken = fixture.uploadShareToken()
    fixture.controller.addToWhitelist(tester.a0)
    shareToken.createShares(tester.a1, 7, sender=tester.k0)

    with raises(TransactionFailed):
        shareToken.transferFrom(tester.a0, tester.a1, 7, sender=tester.k1)

def test_setController():
    fixture = ContractsFixture()
    shareToken = fixture.uploadShareToken()
    newController = fixture.upload('../src/controller.se', 'newController')
    newController.setValue('shareToken'.ljust(32, '\x00'), shareToken.address)

    # FIXME: this depends on dev mode to work
    fixture.controller.updateController(shareToken.address, newController.address, sender=tester.k0)
    with raises(TransactionFailed):
        shareToken.setController(tester.a0, sender=tester.k0)

def test_suicideFunds():
    fixture = ContractsFixture()
    shareToken = fixture.uploadShareToken()

    with raises(TransactionFailed):
        shareToken.suicideFunds(tester.a0, sender=tester.k0)
