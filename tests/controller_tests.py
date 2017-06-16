#!/usr/bin/env python

# Test the functions in src/functions/controller.se
# Uses tests/controller_test.se as a helper (to set the controller, etc.)

import ethereum.tester
import ethereum.abi
import serpent
import binascii
import re
import os
import sys
import time
import random
from binascii import hexlify
from ethereum import tester as t
state = t.state()
c = state.abi_contract('../src/functions/controller.se')
d = state.abi_contract('controller_test.se')

def set_controller():
	global d
	d.getController(value=500)
	# Test a suicide failure
	try:
		raise Exception(d.suicideFunds(t.a2, sender=t.k1))
	except Exception as exc:
		assert(isinstance(exc, ethereum.tester.TransactionFailed)), "setController should fail when attempted by non-controller address"
	d.suicideFunds(t.a0, sender=t.k0)
	d = state.abi_contract('controller_test.se')
	out = d.setController(c.address)
	assert(out == 1), "setController succeeded"
	# Test a setController failure
	try:
		raise Exception(d.setController(binascii.hexlify(d.address)))
	except Exception as exc:
		assert(isinstance(exc, ethereum.tester.TransactionFailed)), "setController should fail when attempted by non-controller address"
	print "Controller Set"

def test_whitelists():
	print("Testing Whitelists")

	try:
		raise Exception(c.addToWhitelist(2342, sender=t.k2))
	except Exception as exc:
		assert(isinstance(exc, ethereum.tester.TransactionFailed)), "adding to whitelist with an invalid sender should fail"

	# Test addToWhiteList
	out = c.addToWhitelist(t.a1)

	# Check that address is now Whitelisted:
	out = c.assertIsWhitelisted(t.a1, sender=t.k2)
	assert (out == 1), "assertIsWhitelisted failed."

	assert(c.assertIsWhitelisted(443434, sender=t.k0)), "Dev owner should be whitelisted in dev mode"

	# Check an address that shouldn't be Whitelisted:
	try:
		raise Exception(c.assertIsWhitelisted(t.a2, sender=t.k1))
	except Exception as exc:
		assert(isinstance(exc, ethereum.tester.TransactionFailed)), "assertIsWhitelisted should fail when address is not Whitelisted"

	# Test removeFromWhitelist
	out = c.removeFromWhitelist(t.a1)
	assert (out == 1), "removeFromWhitelist failed."

def test_registry():
	print("Testing lookup functions")
	out = c.setValue(t.a2, 23)
	print "setValue output: %s" % out
	assert(out == 1), "setValue failed to set t.a2 into registry"
	# Test with t.k0
	print "passed key: %s" % binascii.hexlify(t.k0)
	out = c.lookup(t.k0)
	print "lookup output: %s" % out
	assert(out == 0), "test_lookup didn't fail"
	# Test with t.a1
	print "passed key: %s" % binascii.hexlify(t.a1)
	out = c.lookup(t.a1)
	print "lookup output: %s" % out
	assert(out == 0), "test_lookup didn't fail but should've"
	# Test with t.a2
	print "passed key: %s" % binascii.hexlify(t.k2)
	out = c.lookup(t.a2)
	print "lookup output: %s" % out
	assert(out == 23), "test_lookup should have returned 23"

def test_contractAdmin():
	print("Testing suicideFunds")
	# Test with non-controller addresses
	try:
		raise Exception(d.suicideFunds(t.a1, sender=t.k1))
	except Exception as exc:
		assert(isinstance(exc, ethereum.tester.TransactionFailed)), "suicideFunds should fail when attempted by non-controller address"
	# Test with another non-controller address
	try:
		raise Exception(d.suicideFunds(t.a2, sender=t.k2))
	except Exception as exc:
		assert(isinstance(exc, ethereum.tester.TransactionFailed)), "suicideFunds should fail when attempted by non-controller address"

def test_controllerAdmin():

	address1 = long(t.a1.encode("hex"), 16)

	# Check the current mode
	out = c.getMode()
	print "getMode output: %s" % out
	assert(out == 45410550817938176941147246367785497464285552864458998948296910157280029179904), "getMode should be dev"    # numeric string for 'dev'
	# setMode to something other than dev to test
	out = c.switchModeSoOnlyEmergencyStopsAndEscapeHatchesCanBeUsed()
	print "switchMode output: %s" % out
	# Mode should now be 'Decentralized':
	out = c.getMode()
	print "getMode output: %s" % out
	assert(out == 30936411264679932392881305702504462444513638254699919670237862177711222423552), "getMode should be Decentralized"    # numeric string for 'Decentralized'


	print("Testing ownership functions")
	address0 = long(t.a0.encode("hex"), 16)
	address1 = long(t.a1.encode("hex"), 16)
	#print "self.owner: %s" % self.owner
	out = c.getOwner()
	print "getOwner output: %s" % out
	assert(out == address0), "Owner should start out as address0"

	# Test transferOwnership
	out = c.transferOwnership(t.k1, t.a1, 0)
	print "transferOwnership output: %s" % out
	assert(out == 1), "transferOwnsership did not succeed"

	out = c.getOwner()
	print "getOwner output: %s" % out
	# if newowner == t.a1 ...
	assert(out == address1), "Owner should now be address1"

	# transferOwnership back to original msg.sender
	# sender must be t.k1 now or this call won't work
	out = c.transferOwnership(t.k0, t.a0, 0, sender=t.k1)
	print "transferOwnership output: %s" % out

	out = c.getOwner()
	print "getOwner output: %s" % out
	# if newowner == t.a0 ...
	assert(out == address0), "Owner should now be the original address0"

	# Try updateController:
	# Need to run transferOwnership first I think.  self.owner must be msg.sender
	out = c.updateController(c.address, t.a0)
	print "updateController output: %s" % out
	assert(out == 1), "updateController did not succeed"
	# todo check it on controller test


# Call tests
if __name__ == "__main__":
	set_controller()
	test_whitelists()
	test_registry()
	test_contractAdmin()
	# test_controllerAdmin()
	# test_emergencyStops()

	### redo after decentralized mode enabled
	# test_whitelists()
	# test_registry()
	# test_contractAdmin()
	# test_controllerAdmin()
	# test_emergencyStops()
