#!/usr/bin/python2
import time
import random
from pyethereum import tester as t
from cStringIO import StringIO
from collections import defaultdict
import sys
import types
import gmpy2
gmpy2.get_context().precision = 256

t.gas_limit = 10**7

FILE = "augur.se"
VERBOSE = True

class ContractWrapper(object):
    def __init__(self, verbose, contract):
        self._contract = contract
        self.verbose = verbose

    def __getattr__(self, name, default=None):
        obj = getattr(self._contract, name, default)
        if not self.verbose and isinstance(obj, types.FunctionType):
            def wrapper(*args, **kwds):
                old = sys.stdout
                sys.stdout = StringIO()
                result = obj(*args, **kwds)
                sys.stdout = old
                return result
            return wrapper
        return obj

def colorize(color, *strings):
    chunk_end = '\033[0m'
    return color + (chunk_end+color).join(strings) + chunk_end

def green(*strings):
    return colorize('\033[1;32m', *strings)

def red(*strings):
    return colorize('\033[1;31m', *strings)

def yellow(*strings):
    return colorize('\033[1;33m', *strings)

def cyan(*strings):
    return colorize('\033[1;36m', *strings)

def dim_red(*strings):
    return colorize('\033[0;31m', *strings)

def title(string):
    return dim_red(string.center(80, '#'))

print red(' Starting Tests '.center(80, '#'))
print title(" Compiling %s ... " % FILE)
start = time.time()
s = t.state()
augur = ContractWrapper(VERBOSE, s.abi_contract(FILE, gas=10**8))
print yellow("Done compiling in %f seconds.") % (time.time() - start)
s.mine()
balances = []
a_k = zip(t.accounts, t.keys)
s.mine(1)
print title(' Testing Faucet and Balance ')
for addr, key in a_k:
    print yellow("Results of calls with address ", green("%s:")) % addr
    augur.faucet(sender=key)
    print yellow("\taugur.faucet: ", cyan("Success"))
    print yellow("\taugur.balance: ",cyan("%d")) % augur.balance(addr)

print title(' Testing Send ')
for i, (addr, key) in reversed(list(enumerate(a_k))):
    to = t.accounts[i-1]
    augur.send(to, 1 << 64, sender=key)
    print yellow("Sent 1 cashcoin from ", green("%s "), "to ", green("%s")) % (addr, to)

print title(' Testing MakeSubBranch ')
subbranch = augur.createSubbranch('"test branch"', 100, 1010101)
print yellow('Created subbranch ', cyan('%s '), 'with address ', green(t.a0)) % subbranch

print title(' Testing CreateEvent ')
event1 = augur.createEvent(
    subbranch,                                           #branch 
    '"Will Jack grow at least san inch in March 2015?"', #description
    5*5,                                                 #expiration block
    0,                                                   #min value (binary)
    1,                                                   #max value
    2)                                                   #number of outcomes
event2 = augur.createEvent(
    subbranch,
    '"What will Jack\'s height be, from 60 to 72 inches, at noon PST on April 1st, 2015?"',
    5*5,
    60,                                                   #scalar event!
    72,
    2)
print yellow('Created events ', cyan('%d '), 'and ', cyan('%d '), 'with address ', green('%s')) % \
(event1, event2, t.a0) 

print title(" Testing CreateMarket ")
market = augur.createMarket(
    subbranch,
    '"Market on events %d & %d"' % (event1, event2),
    1 << 60,
    10 << 70,
    1 << 58,
    [event1, event2])
print yellow("Created market ", cyan("%d "), 'with address ', green('%s')) % (market, t.a0)

def lslmsr(q_, i, a):
    assert q_[i] + a >= 0
    q = q_[:]
    alpha = 1/16.
    scale = 12
    Bq1 = alpha*scale*sum(q)
    C1 = Bq1*gmpy2.log(sum(gmpy2.exp(q_i/Bq1) for q_i in q))
    q[i] += a
    Bq2 = alpha*scale*sum(q)
    C2 = Bq2*gmpy2.log(sum(gmpy2.exp(q_i/Bq2) for q_i in q))

    if a > 0:
        return (C2 - C1)*1.015625
    else:
        return (C1 - C2)*0.984375

print title(' Testing BuyShares ')
bought = defaultdict(lambda : [0]*4)
shares = [640/(1+12/16.*gmpy2.log(4))]*4
for i in range(50):
    addr, key = random.choice(a_k)
    outcome = random.randrange(4)
    amt = random.randrange(1,3)
    expected1 = lslmsr(shares, outcome, amt)
    expected2 = augur.price(market, outcome + 1)
    cost = augur.buyShares(subbranch, market, outcome + 1, amt << 64, sender=key)
    shares[outcome] += amt
    print yellow(green("%s "), "bought ", cyan("%d "), "shares of outcome ", cyan("%d "), "for ", red("%f")) % (addr, amt, outcome + 1, cost/gmpy2.mpfr(1 << 64))
    print yellow("expected cost: ", cyan("%f")) % expected1
    print yellow("approximate expected cost per share: ", cyan("%f")) % (expected2 / gmpy2.mpfr(1 << 64))
    bought[addr][outcome] += amt

s.mine()
print title(' Testing SellShares ')
while bought:
    addr = random.choice(bought.keys())
    outcome = random.choice([i for i, v in enumerate(bought[addr]) if v])
    amt = random.randrange(1, bought[addr][outcome]+1)
    expected1 = lslmsr(shares, outcome, -amt)
    expected2 = augur.price(market, outcome + 1)
    paid = augur.sellShares(subbranch, market, outcome + 1, amt << 64, sender=key)
    shares[outcome] -= amt
    print yellow(green("%s "), "sold ", cyan("%d "), "shares of outcome ", cyan("%d "), "for ", red("%f")) % (addr, amt, outcome + 1, cost/gmpy2.mpfr(1 << 64))
    print yellow("expected payment: ", cyan("%f")) % expected1
    print yellow("approximate expected cost per share: ", cyan("%f")) % (expected2 / gmpy2.mpfr(1 << 64))
    bought[addr][outcome] -= amt
    if not any(bought[addr]):
        bought.pop(addr)
