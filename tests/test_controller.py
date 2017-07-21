#!/usr/bin/env python

# Test the functions in src/functions/controller.se
# Uses tests/controller_test.se as a helper (to set the controller, etc.)

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture
from utils import bytesToLong, longToHexString, bytesToHexString

def test_whitelists(controller):
    assert controller.assertIsWhitelisted(tester.a0, sender = tester.k2)
    with raises(TransactionFailed): controller.addToWhitelist(tester.a1, sender = tester.k1)
    with raises(TransactionFailed): controller.addToWhitelist(tester.a1, sender = tester.k2)
    assert controller.addToWhitelist(tester.a1, sender = tester.k0)
    assert controller.assertIsWhitelisted(tester.a1, sender = tester.k2)
    with raises(TransactionFailed): controller.assertIsWhitelisted(tester.a2, sender = tester.k2)
    with raises(TransactionFailed): controller.removeFromWhitelist(tester.a1, sender = tester.k2)
    assert controller.removeFromWhitelist(tester.a1, sender = tester.k1)
    with raises(TransactionFailed): controller.assertIsWhitelisted(tester.a1, sender = tester.k0)

def test_registry(controller, decentralizedController):
    key1 = 'abc'.ljust(32, '\x00')
    key2 = 'foo'.ljust(32, '\x00')
    with raises(TransactionFailed): controller.setValue(key1, 123, sender = tester.k2)
    assert controller.lookup(key1, sender = tester.k2) == longToHexString(0)
    assert controller.addToWhitelist(tester.a1, sender = tester.k0)
    assert controller.setValue(key1, 123, sender = tester.k1)
    assert controller.lookup(key1, sender = tester.k2) == longToHexString(123)
    with raises(TransactionFailed): controller.assertOnlySpecifiedCaller(tester.a1, key2, sender = tester.k2)
    assert controller.setValue(key2, tester.a1, sender = tester.k0)
    assert controller.assertOnlySpecifiedCaller(tester.a1, key2, sender = tester.k2)
    # dev mode special
    assert controller.assertOnlySpecifiedCaller(tester.a1, key2, sender = tester.k0)
    with raises(TransactionFailed): decentralizedController.assertOnlySpecifiedCaller(tester.a2, key2, sender = tester.k0)
    with raises(TransactionFailed): controller.assertOnlySpecifiedCaller(tester.a2, key2, sender = tester.k2)

def test_suicide(controller, decentralizedController, controllerUser):
    with raises(TransactionFailed): controller.suicide(controllerUser.address, tester.a0, sender = tester.k2)
    assert decentralizedController.owner() == bytesToHexString(tester.a0)
    with raises(TransactionFailed): decentralizedController.suicide(controllerUser.address, tester.a0, sender = tester.k0)
    assert controller.suicide(controllerUser.address, tester.a0, sender = tester.k0)
    assert controllerUser.getSuicideFundsDestination() == bytesToLong(tester.a0)

def test_updateController(controller, decentralizedController, controllerUser):
    with raises(TransactionFailed): controller.updateController(controllerUser.address, tester.a0, sender = tester.k2)
    with raises(TransactionFailed): decentralizedController.updateController(controllerUser.address, tester.a0, sender = tester.k0)
    assert controller.updateController(controllerUser.address, tester.a0, sender = tester.k0)
    assert controllerUser.getUpdatedController() == bytesToLong(tester.a0)

def test_transferOwnership(controller, decentralizedController):
    with raises(TransactionFailed): controller.transferOwnership(tester.a1, sender = tester.k2)
    assert controller.transferOwnership(tester.a1, sender = tester.k0)
    with raises(TransactionFailed): controller.assertIsWhitelisted(tester.a0, sender = tester.k2)
    assert controller.assertIsWhitelisted(tester.a1, sender = tester.k2)
    assert controller.owner() == bytesToLong(tester.a1)

    assert decentralizedController.transferOwnership(tester.a1, sender = tester.k0)
    with raises(TransactionFailed): decentralizedController.assertIsWhitelisted(tester.a0, sender = tester.k2)
    with raises(TransactionFailed): decentralizedController.assertIsWhitelisted(tester.a1, sender = tester.k2)
    assert decentralizedController.getOwner() == bytesToLong(tester.a1)

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

@fixture
def controller(contractsFixture):
    return contractsFixture.controller

@fixture
def controllerUser(contractsFixture):
    return contractsFixture.upload('serpent_test_helpers/controllerUser.se')

@fixture(scope="session")
def decentralizedControllerSnapShot(sessionFixture):
    decentralizedController = sessionFixture.upload('../src/Controller.sol', 'decentralizedController')
    assert decentralizedController.foo()
    assert decentralizedController.assertIsWhitelisted(tester.a0)
    assert decentralizedController.owner() == bytesToHexString(tester.a0)
    decentralizedController.switchModeSoOnlyEmergencyStopsAndEscapeHatchesCanBeUsed(sender = tester.k0)
    return sessionFixture.chain.snapshot()

@fixture
def decentralizedController(sessionFixture, decentralizedControllerSnapShot):
    sessionFixture.chain.revert(decentralizedControllerSnapShot)
    return sessionFixture.contracts['decentralizedController']
