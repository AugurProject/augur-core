#!/usr/bin/python2
import time
import random
from pyethereum import tester as t
import gmpy2
gmpy2.get_context().precision = 256

FILE = "augurLite.se"

print "Compiling %s ... " % FILE
start = time.time()
s = t.state()
augur = s.abi_contract("augurLite.se")
print "Done compiling in %f seconds." % (time.time() - start)

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

print "making a subbranch:", 
subbranch = augur.makeSubBranch('"test branch"', 100, 1010101)
print subbranch

print "creating some events:",
event1 = augur.createEvent(
    subbranch,                                           #branch 
    '"Will Jack grow at least san inch in March 2015?"', #description
    31*24*60*5,                                          #expiration block
    0,                                                   #min value (binary)
    1,                                                   #max value
    2)                                                   #number of outcomes
event2 = augur.createEvent(
    subbranch, 
    '"What will Jack\'s height be, from 60 to 72 inches, at noon PST on April 1st, 2015?"', 
    31*24*60*5, 
    60,                                                   #scalar event!
    72, 
    2) 
print event1, event2

print "creating a market:",
market = augur.createMarket(
    subbranch,
    '"Market on events %d & %d"' % (event1, event2), 
    1 << 60, 
    10 << 64, 
    (1 << 64) + (1 << 60), 
    [event1, event2])
print market

bought = {}
for addr, key in a_k:
    x = random.randrange(1, 5)
    print "%s is  buying a share of %d:" % (addr, x),
    cost = augur.buyShares(subbranch, market, x, 1, sender=key)
    print "costs %d cashcoins" % cost
    bought[addr] = x

for addr, key in a_k:
    share = bought[addr]
    paid = augur.sellShares(subbranch, market, share, 1, sender=key)
    print "%s got paid %f for selling 1 share of outcome %d" % (addr, paid/gmpy2.mpfr(1 << 64), share)
    
