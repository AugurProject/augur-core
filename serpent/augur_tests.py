#!/usr/bin/python2
import time
import random
from pyethereum import tester as t
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


print "making a subbranch!"
subbranch = augur.makeSubBranch('"test branch"', 100, 1010101)
print '>>', subbranch
print "creating an event!"
event = augur.createEvent(subbranch, '"will jack grow at least six inches in 2014?"', 1000, 0,1, 2)
print '>>', event
print "creating a market!"
market = augur.createMarket(subbranch, '"Market on event %d"' % event, 1 << 60, 10 << 64, (1 << 64) + (1 << 60), [event])
print '>>', market
bought = {}
for addr, key in a_k:
    x = random.randrange(1, 3)
    print "%s is  buying a share of %d" % (addr, x)
    myid = augur.buyShares(subbranch, market, x, 1, sender=key)
    print '>>', myid
    bought[addr] = (x, myid)

for addr, key in a_k:
    share, myid = bought[addr]
    paid = augur.sellShares(subbranch, market, share, 1, myid, sender=key)
    print "%s got paid %f for selling 1 share of outcome %d" % (addr, paid/float(2**64), share)
    
