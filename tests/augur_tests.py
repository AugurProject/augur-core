#!/usr/bin/python2
from test_utils import *
from collections import defaultdict
import gmpy2
import random

gmpy2.get_context().precision = 256

FILE = '../augur.se'

with timer():
    print title('Starting Tests', dim=False)
    print title('Compiling %s ...' % FILE)
    with timer():
        augur = Contract(FILE, gas=10**7)

    with timer():
        print title('Testing Faucet and Balance')
        for addr, key in addr2key.items():
            print yellow(
                    "Results of calls with address ",
                    pretty_address(addr),
                    ":") 
            result = augur.faucet(sender=key, profiling=True)
            print yellow("\taugur.faucet: ", cyan("Success"))
            print yellow("\t\tgas used: ", cyan(result['gas']))
            result = augur.balance(addr, profiling=True)
            print yellow("\taugur.balance: ",cyan(result['output']/float(1<<64)))
            print yellow("\t\tgas used: ", cyan(result['gas']))

    with timer():
        print title('Testing Send')
        for i, (addr, key) in enumerate(addr2key.items()):
            to = addresses[i-1]
            augur.send(to, 1 << 64, sender=key)
            print yellow(
                    "Sent 1 cashcoin from ",
                    pretty_address(addr),
                    " to ",
                    pretty_address(to))

    with timer():
        print title('Testing CreateSubBranch')
        addr = addresses[1]
        key = addr2key[addr]
        subbranch = augur.createSubbranch('test branch', 100, 1010101, 2**57, sender=key)
        print yellow(
                'Created subbranch ',
                pretty_address(subbranch),
                ' with creator ',
                pretty_address(addr)) 

    with timer():
        print title('Testing CreateEvent')
        addr = addresses[2]
        key = addr2key[addr]
        event1 = augur.createEvent(
            subbranch,                                           #branch 
            '"Will Jack grow at least an inch in March 2015?"',  #description
            5*5*1000,                                            #expiration block
            0,                                                   #min value (binary)
            1,                                                   #max value
            2,                                                   #number of outcomes
            sender=key)
        event2 = augur.createEvent(
            subbranch,
            '''\
"What will Jack's height be, from 60 to 72 inches, 
at noon PST on April 1st, 2015?"''',
            5*5*1000,
            60,                                                   #scalar event!
            72,
            2,
            sender=key)
        print yellow(
                'Created events ',
                pretty_address(event1),
                ' and ',
                pretty_address(event2),
                ' with creator ',
                pretty_address(addr),
        )

    with timer():
        print title('Testing CreateMarket')
        addr = addresses[3]
        key = addr2key[addr]
        market = augur.createMarket(
            subbranch,                                       #branch
            '"Market on events %d & %d"' % (event1, event2), #events
            1 << 60,                                         #alpha
            10 << 70,                                        #fixedpoint initial liquidity
            1 << 58,                                         #trading fee
            [event1, event2],                                #array of events
            sender=key)
        print yellow(
                'Created market ',
                pretty_address(market),
                ' with creator ',
                pretty_address(addr))

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

    bought = defaultdict(lambda : [0]*4)
    shares = [640/(1+12/16.*gmpy2.log(4))]*4
    transaction_nonce = defaultdict(int)
    with timer():
        print title('Testing BuyShares')
        for i in range(50):
            addr = random.choice(addresses)
            key = addr2key[addr]
            outcome = random.randrange(4)
            amt = random.randrange(1, 3)
            expected1 = lslmsr(shares, outcome, amt)
            nonce = trade_pow(subbranch, market, addr, transaction_nonce[addr])
            transaction_nonce[addr] += 1
            expected2 = augur.price(market, outcome + 1)
            cost = augur.buyShares(subbranch, market, outcome + 1, amt << 64, nonce, sender=key)
            shares[outcome] += amt
            print yellow(
                pretty_address(addr),
                " bought ",
                cyan(amt),
                " shares of outcome ",
                cyan(outcome + 1),
                " for ",
                dim_red(cost/float(1 << 64)))
            print yellow("expected cost: ", cyan(float(expected1)))
            print yellow(
                "approximate expected cost per share: ",
                cyan(expected2/float(1 << 64)))
            bought[addr][outcome] += amt

    with timer():
        print title('Testing SellShares')
        while bought:
            addr = random.choice(bought.keys())
            key = addr2key[addr]
            outcome = random.choice([i for i, v in enumerate(bought[addr]) if v])
            amt = random.randrange(1, bought[addr][outcome]+1)
            expected1 = lslmsr(shares, outcome, -amt)
            expected2 = augur.price(market, outcome + 1)
            nonce = trade_pow(subbranch, market, addr, transaction_nonce[addr])
            transaction_nonce[addr] += 1
            paid = augur.sellShares(subbranch, market, outcome + 1, amt << 64, nonce, sender=key)
            shares[outcome] -= amt
            print yellow(
                pretty_address(addr),
                " sold ",
                cyan(amt),
                " shares of outcome ",
                cyan(outcome + 1),
                " for ",
                dim_red(paid/float(1 << 64)))
            print yellow("expected payment: ", cyan(float(expected1)))
            print yellow(
                "approximate expected cost per share: ",
                cyan(expected2/float(1 << 64)))
            bought[addr][outcome] -= amt
            if not any(bought[addr]):
                bought.pop(addr)
