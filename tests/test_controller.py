#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture
from utils import AssertLog, longToHexString, bytesToHexString, stringToBytes, longTo32Bytes, garbageAddress, garbageBytes20, garbageBytes32, twentyZeros, thirtyTwoZeros
from struct import pack

def test_whitelists(localFixture, controller):
    assert controller.assertIsWhitelisted(tester.a0, sender = tester.k2)
    with raises(TransactionFailed): controller.addToWhitelist(tester.a1, sender = tester.k1)
    with raises(TransactionFailed): controller.addToWhitelist(tester.a1, sender = tester.k2)

    whitelistAdditionLog = {"addition": bytesToHexString(tester.a1)}
    with AssertLog(localFixture, "WhitelistAddition", whitelistAdditionLog):
        assert controller.addToWhitelist(tester.a1, sender = tester.k0)
    
    assert controller.assertIsWhitelisted(tester.a1, sender = tester.k2)
    with raises(TransactionFailed): controller.assertIsWhitelisted(tester.a2, sender = tester.k2)
    with raises(TransactionFailed): controller.removeFromWhitelist(tester.a1, sender = tester.k2)
    assert controller.removeFromWhitelist(tester.a1, sender = tester.k1)
    with raises(TransactionFailed): controller.assertIsWhitelisted(tester.a1, sender = tester.k0)

def test_registry(controller, decentralizedController):
    key1 = 'abc'.ljust(32, '\x00')
    key2 = 'foo'.ljust(32, '\x00')
    with raises(TransactionFailed): controller.registerContract(key1, 123, garbageBytes20, garbageBytes32, sender = tester.k2)
    assert controller.lookup(key1, sender = tester.k2) == longToHexString(0)
    assert controller.addToWhitelist(tester.a1, sender = tester.k0)
    assert controller.registerContract(key1, 123, garbageBytes20, garbageBytes32, sender = tester.k0)
    assert controller.lookup(key1, sender = tester.k2) == longToHexString(123)
    with raises(TransactionFailed): controller.assertOnlySpecifiedCaller(tester.a1, key2, sender = tester.k2)
    assert controller.registerContract(key2, tester.a1, garbageBytes20, garbageBytes32, sender = tester.k0)
    assert controller.assertOnlySpecifiedCaller(tester.a1, key2, sender = tester.k2)
    # dev mode special
    assert controller.assertOnlySpecifiedCaller(tester.a1, key2, sender = tester.k0)
    with raises(TransactionFailed): decentralizedController.assertOnlySpecifiedCaller(tester.a2, key2, sender = tester.k0)
    with raises(TransactionFailed): controller.assertOnlySpecifiedCaller(tester.a2, key2, sender = tester.k2)

def test_suicide(controller, decentralizedController, controllerUser):
    with raises(TransactionFailed): controller.suicideFunds(controllerUser.address, tester.a0, [tester.a2], sender = tester.k2)
    assert decentralizedController.owner() == bytesToHexString(tester.a0)
    with raises(TransactionFailed): decentralizedController.suicideFunds(controllerUser.address, tester.a0, [tester.a2], sender = tester.k0)
    assert controller.suicideFunds(controllerUser.address, tester.a1, [tester.a2], sender = tester.k0)
    assert controllerUser.suicideFundsDestination() == bytesToHexString(tester.a1)
    assert controllerUser.suicideFundsTokens(0) == bytesToHexString(tester.a2)

def test_updateController(controller, decentralizedController, controllerUser):
    with raises(TransactionFailed): controller.updateController(controllerUser.address, tester.a0, sender = tester.k2)
    with raises(TransactionFailed): decentralizedController.updateController(controllerUser.address, tester.a0, sender = tester.k0)
    assert controllerUser.setController(controller.address)
    assert controller.updateController(controllerUser.address, tester.a0, sender = tester.k0)
    assert controllerUser.updatedController() == bytesToHexString(tester.a0)

def test_transferOwnership(controller, decentralizedController):
    with raises(TransactionFailed): controller.transferOwnership(tester.a1, sender = tester.k2)
    assert controller.transferOwnership(tester.a1, sender = tester.k0)
    with raises(TransactionFailed): controller.assertIsWhitelisted(tester.a0, sender = tester.k2)
    assert controller.assertIsWhitelisted(tester.a1, sender = tester.k2)
    assert controller.owner() == bytesToHexString(tester.a1)

    assert decentralizedController.transferOwnership(tester.a1, sender = tester.k0)
    with raises(TransactionFailed): decentralizedController.assertIsWhitelisted(tester.a0, sender = tester.k2)
    with raises(TransactionFailed): decentralizedController.assertIsWhitelisted(tester.a1, sender = tester.k2)
    assert decentralizedController.owner() == bytesToHexString(tester.a1)

def test_emergencyStop(controller):
    with raises(TransactionFailed): controller.emergencyStop(sender = tester.k2)
    with raises(TransactionFailed): controller.release(sender = tester.k2)
    assert controller.stopInEmergency(sender = tester.k2)
    with raises(TransactionFailed): controller.onlyInEmergency(sender = tester.k2)
    assert controller.emergencyStop(sender = tester.k0)
    assert controller.onlyInEmergency(sender = tester.k2)
    with raises(TransactionFailed): controller.stopInEmergency(sender = tester.k2)
    assert controller.release(sender = tester.k0)
    assert controller.stopInEmergency(sender = tester.k2)
    with raises(TransactionFailed): controller.onlyInEmergency(sender = tester.k2)

def test_switchModeSoOnlyEmergencyStopsAndEscapeHatchesCanBeUsed_failures(controller):
    with raises(TransactionFailed): controller.switchModeSoOnlyEmergencyStopsAndEscapeHatchesCanBeUsed(sender = tester.k2)

def test_getContractDetails(controller):
    key = stringToBytes('lookup key')
    address = garbageAddress
    commitHash = garbageBytes20
    fileHash = garbageBytes32

    assert controller.getContractDetails(key, sender = tester.k2) == [ longToHexString(0), twentyZeros, thirtyTwoZeros ]
    assert controller.registerContract(key, address, commitHash, fileHash, sender = tester.k0)
    assert controller.getContractDetails(key, sender = tester.k2) == [ address, commitHash, fileHash ]

@fixture(scope='session')
def localSnapshot(fixture, controllerSnapshot):
    fixture.resetToSnapshot(controllerSnapshot)
    fixture.upload('solidity_test_helpers/ControllerUser.sol')
    fixture.uploadAndAddToController('../source/contracts/Augur.sol')
    fixture.contracts["Augur"].setController(fixture.contracts['Controller'].address)
    decentralizedController = fixture.upload('../source/contracts/Controller.sol', 'decentralizedController')
    decentralizedController.switchModeSoOnlyEmergencyStopsAndEscapeHatchesCanBeUsed(sender = tester.k0)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def controller(localFixture):
    return localFixture.contracts['Controller']

@fixture
def controllerUser(localFixture):
    return localFixture.contracts['ControllerUser']

@fixture
def decentralizedController(localFixture):
    return localFixture.contracts['decentralizedController']
