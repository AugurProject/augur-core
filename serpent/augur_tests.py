#!/usr/bin/python2
import sys
import os
import random
import time
oldstderr, oldstdout = sys.stderr, sys.stdout
sys.stdout = open(os.devnull, 'wb')
sys.stderr = sys.stdout
### Replace stderr for this shiz to stop
oldstdout.write("Compiling augur.se ... ")
oldstdout.flush()
start = time.time()
from pyethereum import tester as t
s = t.state()
augur = s.abi_contract("augurLite.se")
oldstdout.write("Done in %f seconds.\n" % (time.time() - start))
oldstdout.flush()
### random shiz from being shizzed onto the terminal
sys.stderr, sys.stdout = oldstderr, oldstdout

balances = []
a_k = zip(t.accounts, t.keys)

for addr, key in a_k:
    print "sending money to %s with faucet" % addr
    print ">>", augur.faucet(sender=key)
    print "Checking balance..."
    balances.append(augur.balance(addr))
    print ">>", balances[-1]

for i, (addr, key) in reversed(list(enumerate(a_k))):
    amt = balances[i] / 2
    to = t.accounts[i-1]
    print "Sending %d to %s from %s" % (amt >> 64, to, addr)
    print ">>", augur.send(to, amt, sender=key)


print "making a subbranch!"
subbranch = augur.makeSubBranch('"test branch"', 100, 1010101)
print '>>', subbranch
print "creating an event!"
event = augur.createEvent(subbranch, '"will jack grow at least six inches in 2014?"', 1000, 0,1, 2)
print '>>', event
print "creating a market!"
market = augur.createMarket(subbranch, '"Market on event %d"' % event, 1 << 63, 10 << 64, 1 << 60, [event])
print '>>', market
for addr, key in a_k:
    x = random.randrange(1)
    print "%s is  buying a share of %d" % (addr, x)
    print '>>', augur.buyShares(subbranch, market, x, 1)

