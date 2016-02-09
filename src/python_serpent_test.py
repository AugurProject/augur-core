#!/usr/bin/env python

from ethereum import tester as t
import math
import os

initial_gas = 0

def test_cash():
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('data_api/cash.se')

    assert(c.initiateOwner(111)==1), "Assign owner to id=111"
    assert(c.initiateOwner(111)==0), "Do not re-assign owner of id=111"
    c.setCash(111, 10)
    gas_use(s)
    c.addCash(111,5)
    c.subtractCash(111,4)
    gas_use(s)
    assert(c.balance(111)==11), "Cash value not expected!"
    gas_use(s)
    c.send(111, 10)
    assert(c.send(47, 10)==0), "Receiver check broken"
    assert(c.balance(111)==21), "Send function broken"
    assert(c.sendFrom(101, 1, 111)==0), "Receiver uninitialized check failed"
    c.initiateOwner(101)
    assert(c.sendFrom(101, 1, 111)==1), "Send from broken"
    assert(c.balance(111)==20), "Send from broken"
    assert(c.balance(101)==1), "Send from broken"
    assert(c.setCash(447, 101)==0), "Set cash owner check broken"
    gas_use(s)
    print "CASH OK"

def test_ether():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('data_api/ether.se')
    assert(c.depositEther(value=5)==5), "Unsuccessful eth deposit"
    assert(c.withdrawEther(111, 500)==0), "Printed money out of thin air..."
    assert(c.withdrawEther(111, 5)==1), "Unsuccessful withdrawal"
    gas_use(s)
    print "ETHER OK"

def test_exp():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.setReportHash(1010101, 0, 101, 47, 0)
    assert(c.getReportHash(1010101, 0, 101, 0)==47), "Report hash wrong"
    c.addEvent(1010101, 0, 447)
    assert(c.getEvent(1010101, 0, 0) == 447), "Add/get event broken"
    assert(c.getNumberEvents(1010101, 0)==1), "Num events wrong"
    assert(c.setNumEventsToReportOn(1010101, 0)==-1), "Vote period check issue"
    c.moveEventsToCurrentPeriod(1010101, 1, 2)
    assert(c.getEvent(1010101, 2, 0) == 447), "Move events broken"
    assert(c.sqrt(25*2**64)==5*2**64), "Square root broken"
    print "EXPIRING EVENTS OK"
    gas_use(s)

def test_quicksort():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/quicksort.se')
    array = [1, 40, 2, 30, 44, 33, 22, 12, 22, 43]
    assert(c.quicksort(array) == [1, 2, 12, 22, 22, 30, 33, 40, 43, 44]), "Quicksort broken"
    print "QUICKSORT OK"
    gas_use(s)

def test_insertionsort():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/insertionsort.se')
    array = [1, 40, 2, 30, 44, 33, 22, 12, 22, 43]
    assert(c.insertionSort(array) == [1, 2, 12, 22, 22, 30, 33, 40, 43, 44]), "Insertion sort broken"
    print "INSERTIONSORT OK"
    gas_use(s)
    
def test_log_exp():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('data_api/fxpFunctions.se')
    assert(c.fx_exp(2**64) == 50143449209799256664), "Exp broken"
    assert(c.fx_log(2**64) == 7685), "Log broken"
    print "LOG EXP OK"
    xs = [2**64, 2**80, 2**68, 2**70]
    maximum = max(xs)
    sum = 0
    original_method_sum = 0
    i = 0
    while i < len(xs):
        sum += c.fx_exp(xs[i] - maximum)
        original_method_sum += c.fx_exp(xs[i])
        i += 1
    print maximum + c.fx_log(sum)
    print c.fx_log(original_method_sum)
    gas_use(s)

def test_markets():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initializeMarket(444, [445, 446, 447], 1, 2**57, 1010101, 2)
    c.initialLiquiditySetup(444, 2**55, 1, 2)
    c.setWinningOutcomes(444, [2])
    assert(c.getWinningOutcomes(444)[0] == 2), "Winning outcomes wrong"
    assert(c.addParticipant(444, s.block.coinbase)==0), "Participant adding issue"
    #modifyShares(market, outcome, amount)
    #modifyParticipantShares(branch, marketID, participantNumber, outcome, amount)
    #lsLmsr(marketID)
    #c.getParticipantSharesPurchased(market, participantNumber, outcome)
    # getMarketEvent singular
    assert(c.getParticipantNumber(444, s.block.coinbase)==0), "Participant number issue"
    assert(c.getParticipantID(444, 0)==745948140856946866108753121277737810491401257713), "Participant ID issue"
    assert(c.getMarketEvents(444) == [445,446,447]), "Market events load/save broken"
    print "MARKETS OK"

def test_reporting():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    assert(c.getRepByIndex(1010101, 0) == 47*2**64), "Get rep broken"
    assert(c.getReporterID(1010101, 1)==1010101), "Get reporter ID broken"
    #c.getReputation(address)
    assert(c.repIDToIndex(1010101, 1010101)==1), "Rep ID to index wrong"
    #c.claimInitialRep(parent, newBranch)
    c.addReporter(1010101, 777)
    c.addRep(1010101, 2, 55*2**64)
    c.subtractRep(1010101, 2, 2**64)
    assert(c.getRepByIndex(1010101, 2) == 54*2**64), "Get rep broken upon adding new reporter"
    assert(c.getReporterID(1010101, 2)==777), "Get reporter ID broken upon adding new reporter"
    assert(c.repIDToIndex(1010101, 777)==2), "Rep ID to index wrong upon adding new reporter"
    c.setRep(1010101, 2, 5*2**64)
    assert(c.getRepBalance(1010101, 777) == 5*2**64), "Get rep broken upon set rep"
    c.addDormantRep(1010101, 2, 5)
    c.subtractDormantRep(1010101, 2, 2)
    assert(c.getDormantRepBalance(1010101, 777)==3), "Dormant rep balance broken"
    assert(c.getDormantRepByIndex(1010101, 2)==3), "Dormant rep by index broken"
    gas_use(s)
    c.setSaleDistribution([4,44,444,4444,44444], [0, 1, 2, 3, 4], 1010101)
    assert(c.getRepBalance(1010101, 4444)==3), "Rep Balance fetch broken w/ initial distrib."
    assert(c.getReporterID(1010101, 6)==4444), "Sale distrib. reporter ID wrong"
    print "REPORTING OK"

def test_create_event():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    event_binary = c.createEvent(1010101, "new event", 555, 1, 2, 2)
    event_categorical = c.createEvent(1010101, "new event", 555, 1, 5, 5)
    event_scalar = c.createEvent(1010101, "new event", 555, 1, 200, 2)
    assert(event_binary>2**64 or event_binary <-2**64), "binary Event creation broken"
    assert(event_categorical>2**64 or event_categorical <-2**64), "categorical Event creation broken"
    assert(event_scalar>2**64 or event_s <-2**64), "scalar Event creation broken"
    gas_use(s)
    print "EVENT CREATION OK"

def test_create_market():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    # binary
    event1 = c.createEvent(1010101, "new event", 555, 1, 2, 2)
    # scalar
    event2 = c.createEvent(1010101, "new event", 555, 1, 200, 2)
    # categorical
    event3 = c.createEvent(1010101, "new event", 555, 1, 5, 5)
    # scalar
    event4 = c.createEvent(1010101, "new event", 555, -100, 200, 2)
    # binary
    event5 = c.createEvent(1010101, "new event", 557, 1, 2, 2)
    # scalar
    event6 = c.createEvent(1010101, "new event", 557, 1, 25, 2)

    gas_use(s)
    
    ### Single Markets
    # binary market
    gas_use(s)
    bin_market = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    print bin_market
    gas_use(s)
    print c.getSharesPurchased(bin_market, 1)
    print c.getSharesPurchased(bin_market, 2)
    # scalar market
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2], 1) 
    # odd range scalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event4], 1)
    # categorical market
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event3], 1)
    print "1D Done"
    
    ### 2D Markets
    # scalar + scalar market
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2, event4], 1)
    # nonscalar, scalar
    x = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event1, event2], 1)
    assert(c.getMarketNumOutcomes(x)==4), "Market num outcomes wrong"

    # scalar, nonscalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event4, event1], 1)
    # nonscalar, nonscalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event5, event1], 1)
    print "2D Done"
    
    ### 3D Markets
    # scalar, scalar, scalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event5, event2, event6], 1)
    # scalar, nonscalar, scalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2, event3, event4], 1)
    # nonscalar, scalar, scalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event1, event2, event4], 1)
    # nonscalar, nonscalar, scalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event5, event3, event6], 1)
    # scalar, scalar, nonscalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2, event4, event5], 1)
    # scalar, nonscalar, nonscalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2, event1, event3], 1)
    # nonscalar, scalar, nonscalar
    market = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event3, event2, event5], 1)
    assert(c.getMarketNumOutcomes(market)==20), "Market num outcomes wrong"
    gas_use(s)
    # nonscalar, nonscalar, nonscalar
    print c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event1, event5, event3], 1)
    print "3D Done"
    gas_use(s)
    assert(c.getNumMarkets(event2)==9), "Num markets for event wrong"
    assert(c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event1, event5, event3], 1)==-4), "Duplicate market check broken"
    assert(c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event3, event3, event3], 1)==-6), "Duplicate event check broken"
    print "Market Creation OK"

def test_buy_sell_shares():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    # binary
    event1 = c.createEvent(1010101, "new event", 555, 1, 2, 2)
    # scalar
    event2 = c.createEvent(1010101, "new event", 555, 1, 200, 2)
    # categorical
    event3 = c.createEvent(1010101, "new event", 555, 1, 5, 5)
    # scalar
    event4 = c.createEvent(1010101, "new event", 555, -100, 200, 2)
    # binary
    event5 = c.createEvent(1010101, "new event", 557, 1, 2, 2)
    # scalar
    event6 = c.createEvent(1010101, "new event", 557, 1, 25, 2)

    gas_use(s)

    ### Single Markets
    # binary market
    bin_market = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    initialSharesPurchased1 = c.getSharesPurchased(bin_market, 1)
    initialSharesPurchased2 = c.getSharesPurchased(bin_market, 2)
    sharesToTrade = 5*2**64
    c.commitTrade(bin_market, c.makeMarketHash(bin_market, 2, sharesToTrade, 0))
    s.mine(1)
    assert(c.buyShares(1010101, bin_market, 2, sharesToTrade, 0)==1), "Buy shares issue"
    assert(c.getSharesPurchased(bin_market, 1) - initialSharesPurchased1 == 0), "Share storage issue"
    print "shares traded:", (c.getSharesPurchased(bin_market, 2) - initialSharesPurchased2) / 2**64
    assert(c.getSharesPurchased(bin_market, 2) - initialSharesPurchased2 == sharesToTrade), "Share storage issue"
    c.commitTrade(bin_market, c.makeMarketHash(bin_market, 2, sharesToTrade, 0))
    s.mine(1)
    assert(c.sellShares(1010101, bin_market, 2, sharesToTrade, 0)==1), "Sell shares issue"
    assert(c.getSharesPurchased(bin_market, 1) - initialSharesPurchased1 == 0), "Share storage issue"
    assert(c.getSharesPurchased(bin_market, 2) - initialSharesPurchased2 == 0), "Share storage issue"

    # scalar market
    a = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2], 1)
    bal = c.balance(s.block.coinbase)
    c.commitTrade(a, c.makeMarketHash(a, 1, 15*2**64, 0))
    s.mine(1)
    # should cost ~200/share
    c.buyShares(1010101, a, 1, 15*2**64,0)
    bal_after = c.balance(s.block.coinbase)
    assert((bal-bal_after) <= 3015*2**64 and (bal-bal_after) >= 2980*2**64), "Scalar buy off"
    c.commitTrade(a, c.makeMarketHash(a, 2, 12*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.buyShares(1010101, a, 2, 12*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < 20*2**64), "Scalar buy off"
    c.commitTrade(a, c.makeMarketHash(a, 1, 15*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    print c.sellShares(1010101, a, 1, 15*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after <= -590*2**64), "Scalar sell off"
    assert(c.price(a, 1) < 2**64), "Scalar sell off"
    assert(c.price(a, 2) > 198*2**64), "Scalar sell off"

    # odd range scalar
    b = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event4], 1)
    bal = c.balance(s.block.coinbase)
    c.commitTrade(b, c.makeMarketHash(b, 1, 15*2**64, 0))
    s.mine(1)
    c.buyShares(1010101, b, 1, 15*2**64, 0)
    bal_after = c.balance(s.block.coinbase)
    print bal - bal_after
    assert((bal-bal_after) <= 4550*2**64 and (bal-bal_after) >= 4500*2**64), "Scalar buy off"
    c.commitTrade(b, c.makeMarketHash(b, 2, 12*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.buyShares(1010101, b, 2, 12*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < 20*2**64), "Scalar buy off"
    c.commitTrade(b, c.makeMarketHash(b, 1, 15*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.sellShares(1010101, b, 1, 15*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after <= -890*2**64), "Scalar sell off"
    assert(c.price(b, 2) > 298*2**64), "Scalar sell off"
    assert(c.price(b, 1) < 2**64), "Scalar sell off"
    c.commitTrade(b, c.makeMarketHash(b, 1, 10*2**64, 0))
    s.mine(1)
    assert(c.buyShares(1010101, b, 1, 10*2**64, 0)==1), "Buy back not working"

    # categorical market
    d = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event3], 1)
    bal = c.balance(s.block.coinbase)
    c.commitTrade(d, c.makeMarketHash(d, 1, 15*2**64, 0))
    s.mine(1)
    assert(c.price(d, 5)==c.price(d, 4)==c.price(d, 3)==c.price(d, 2)==c.price(d, 1)), "Pricing off for categorical"
    c.buyShares(1010101, d, 1, 15*2**64,0)
    bal_after = c.balance(s.block.coinbase)
    print c.price(d, 1)
    print c.price(d, 2)
    print c.price(d, 3)
    print c.price(d, 4)
    print c.price(d, 5)
    # .44 cost on avg
    # resume here
    print bal-bal_after
    assert((bal-bal_after) <= .47*15*2**64 and (bal-bal_after) >= .44*15*2**64), "Categorical buy off"
    assert(c.price(d, 1) > .68*2**64 and c.price(d, 1) < .69*2**64), "Categorical buy off"
    c.commitTrade(d, c.makeMarketHash(d, 3, 12*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.buyShares(1010101, d, 3, 12*2**64, 0)
    assert(c.price(d, 2) == c.price(d, 4) == c.price(d, 5)), "Categorical prices off"
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < .22*12*2**64 and bal-bal_after >.20*12*2**64), "Categorical buy off"
    # Sell
    c.commitTrade(d, c.makeMarketHash(d, 1, 15*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.sellShares(1010101, d, 1, 15*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    print bal-bal_after
    # 28 cents on avg / share
    assert(bal-bal_after < -4*2**64 and bal-bal_after > -5*2**64), "Categorical sell off"
    assert(c.price(d, 1) > .12*2**64 and c.price(d, 1) < .14*2**64), "Categorical sell off"
    print "1D Done"
    
    ### 2D Markets
    # scalar + scalar market
    c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2, event4], 1)
    # nonscalar, scalar
    c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event1, event2], 1)
    # scalar, nonscalar
    e = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event4, event1], 1)
    bal = c.balance(s.block.coinbase)
    c.commitTrade(e, c.makeMarketHash(e, 1, 15*2**64, 0))
    s.mine(1)
    assert(c.getCumScale(e)==300), "Cumulative scale wrong"
    assert(c.price(e, 1) == c.price(e, 2) == c.price(e, 4) == c.price(e, 3)), "Scalar prices off"
    c.buyShares(1010101, e, 1, 15*2**64,0)
    bal_after = c.balance(s.block.coinbase)
    assert((bal-bal_after) <= 4550*2**64 and (bal-bal_after) >= 4500*2**64), "Scalar buy off"
    c.commitTrade(e, c.makeMarketHash(e, 3, 14*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.buyShares(1010101, e, 3, 14*2**64, 0)
    gas_use(s)
    print c.price(e, 1)
    print c.price(e, 2)
    print c.price(e, 3)
    print c.price(e, 4)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < 20*2**64), "Scalar buy off"
    c.commitTrade(e, c.makeMarketHash(e, 1, 15*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.sellShares(1010101, e, 1, 15*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < -300*2**64 and bal-bal_after > -320*2**64), "Scalar sell off"
    # nonscalar, nonscalar
    c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event5, event1], 1)
    print "2D Done"
    
    ### 3D Markets
    # scalar, scalar, scalar
    f = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event4, event2, event6], 1)
    bal = c.balance(s.block.coinbase)
    assert(c.getCumScale(f) == 523), "3d cumscale wrong"
    c.commitTrade(f, c.makeMarketHash(f, 8, 2*2**64, 0))
    s.mine(1)
    c.buyShares(1010101, f, 8, 2*2**64,0)
    bal_after = c.balance(s.block.coinbase)
    print bal - bal_after
    assert(c.price(f,1)==c.price(f,2)==c.price(f,3)==c.price(f,4)==c.price(f,5)==c.price(f,6)==c.price(f,7)), "3d pricing broken"
    assert(c.price(f,8)>=522*2**64 and c.price(f,8) <= 524*2**64), "3d pricing broken"
    assert((bal-bal_after) <= 1055*2**64 and (bal-bal_after) >= 1005*2**64), "3d buy off"
    c.commitTrade(f, c.makeMarketHash(f, 2, 1*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.buyShares(1010101, f, 2, 1*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < 20*2**64), "3d buy off"
    c.commitTrade(f, c.makeMarketHash(f, 8, 1*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.sellShares(1010101, f, 8, 1*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < 20*2**64), "3d sell off"
    # scalar, nonscalar, scalar
    h = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2, event3, event4], 1)
    bal = c.balance(s.block.coinbase)
    assert(c.getMarketNumOutcomes(h) == 20), "3d number outcomes wrong"
    c.commitTrade(h, c.makeMarketHash(h, 15, 15*2**64, 0))
    s.mine(1)
    assert(c.getCumScale(h) == 499), "3d cumscale wrong"
    c.buyShares(1010101, h, 15, 15*2**64,0)
    bal_after = c.balance(s.block.coinbase)
    print bal - bal_after
    assert((bal-bal_after) <= 7600*2**64 and (bal-bal_after) >= 7500*2**64), "3d buy off"
    c.commitTrade(h, c.makeMarketHash(h, 2, 12*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.buyShares(1010101, h, 2, 12*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < 20*2**64), "3d buy off"
    c.commitTrade(h, c.makeMarketHash(h, 15, 12*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.sellShares(1010101, h, 15, 12*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < 20*2**64), "3d sell off"
    # nonscalar, scalar, scalar
    c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event1, event2, event4], 1)
    # nonscalar, nonscalar, scalar
    c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event5, event3, event6], 1)
    # scalar, scalar, nonscalar
    c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2, event4, event5], 1)
    # scalar, nonscalar, nonscalar
    c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event2, event1, event3], 1)
    # nonscalar, scalar, nonscalar
    g = market = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event3, event2, event5], 1)
    bal = c.balance(s.block.coinbase)
    assert(c.getMarketNumOutcomes(g) == 20), "3d number outcomes wrong"
    c.commitTrade(g, c.makeMarketHash(g, 8, 15*2**64, 0))
    s.mine(1)
    assert(c.getCumScale(g) == 199), "3d cumscale wrong"
    c.buyShares(1010101, g, 8, 15*2**64,0)
    bal_after = c.balance(s.block.coinbase)
    print bal - bal_after
    assert((bal-bal_after) <= 3010*2**64 and (bal-bal_after) >= 2960*2**64), "3d buy off"
    c.commitTrade(g, c.makeMarketHash(g, 2, 12*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.buyShares(1010101, g, 2, 12*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < 20*2**64), "3d buy off"
    c.commitTrade(g, c.makeMarketHash(g, 2, 12*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.sellShares(1010101, g, 2, 12*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < 20*2**64), "3d sell off"
    # nonscalar, nonscalar, nonscalar
    i = c.createMarket(1010101, "new market 2", 2**58, 100*2**64, 368934881474191032, [event1, event5, event3], 1)
    bal = c.balance(s.block.coinbase)
    assert(c.getMarketNumOutcomes(i) == 20), "3d number outcomes wrong"
    c.commitTrade(i, c.makeMarketHash(i, 20, 15*2**64, 0))
    s.mine(1)
    assert(c.getCumScale(i) == 1), "3d cumscale wrong"
    c.buyShares(1010101, i, 20, 15*2**64,0)
    bal_after = c.balance(s.block.coinbase)
    print bal - bal_after
    assert((bal-bal_after) <= .13*15*2**64 and (bal-bal_after) >= .12*15*2**64), "3d buy off"
    c.commitTrade(i, c.makeMarketHash(i, 2, 12*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.buyShares(1010101, i, 2, 12*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < .12*12*2**64), "3d buy off"
    c.commitTrade(i, c.makeMarketHash(i, 20, 11*2**64, 0))
    s.mine(1)
    bal = c.balance(s.block.coinbase)
    gas_use(s)
    c.sellShares(1010101, i, 20, 11*2**64, 0)
    gas_use(s)
    bal_after = c.balance(s.block.coinbase)
    assert(bal-bal_after < -1.2*2**64 and bal-bal_after > -1.5*2**64), "3d sell off"
    print "3D Done"
    print "BUY AND SELL OK"

def test_transfer_shares():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    # binary
    event1 = c.createEvent(1010101, "new event", 555, 1, 2, 2)

    ### Single Markets
    # binary market
    bin_market = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    c.commitTrade(bin_market, c.makeMarketHash(bin_market, 1, 15*2**64, 0))
    s.mine(1)
    c.buyShares(1010101, bin_market, 1, 15*2**64,0)
    # -1: invalid outcome or you haven't traded in this market (or market doesn't exist)
    assert(c.transferShares(1010101, bin_market, 1, 15*2**64, 444)==15*2**64), "Transfer shares fail"
    assert(c.transferShares(1010101, bin_market, 1, 15*2**64, 444)==-2), "Check for not having shares fail"
    assert(c.transferShares(1010101, 222, 1, 15*2**64, 444)==-1), "Check for invalid market fail"
    print "Transfer shares OK"

def test_create_branch():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    b = c.createSubbranch("new branch", 100, 1010101, 2**55, 0)
    assert(b<-3 or b>3), "Branch creation fail"
    assert(c.createSubbranch("new branch", 100, 1010101, 2**55, 0)==-2), "Branch already exist fail"
    assert(c.createSubbranch("new branch", 100, 10101, 2**55, 0)==-1), "Branch doesn't exist check fail"
    assert(c.getParentPeriod(b)==c.getVotePeriod(1010101)), "Parent period saving broken"
    event1 = c.createEvent(b, "new event", 555, 1, 2, 2)
    print hex(event1)
    bin_market = c.createMarket(b, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    print hex(bin_market)
    print "Test branch OK"

def test_send_rep():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    assert(c.sendReputation(1010101, s.block.coinbase, 444)==444), "Send rep failure"
    assert(c.sendReputation(1010101, 1010101, 444)==444), "Send rep failure"
    assert(c.sendReputation(1010101, 999, 444)==-2), "Send rep to nonexistant receiver check failure"
    assert(c.sendReputation(1010101, s.block.coinbase, 1000000*2**64)==0), "Send rep user doesn't have check failure"
    assert(c.convertToDormantRep(1010101, 500*2**64)==0), "Allowed converting a bunch of rep to dormant that user didn't have"
    assert(c.convertToDormantRep(1010101, 444)==444), "Dormant rep conversion unsuccessful"
    assert(c.convertToActiveRep(1010101, 500*2**64)==0), "Allowed converting a bunch of rep to active that user didn't have"
    assert(c.convertToActiveRep(1010101, 400)==400), "Active rep conversion unsuccessful"
    assert(c.sendDormantRep(1010101, s.block.coinbase, 444)==0), "Send dormant rep user didn't have check failure"
    assert(c.sendDormantRep(1010101, s.block.coinbase, 10)==10), "Send dormant rep user failure"
    assert(c.sendDormantRep(1010101, 999, 10)==-2), "Send dormant rep to nonexistant receiver check failure"
    assert(c.getDormantRepBalance(1010101, s.block.coinbase)==44), "Dormant rep balance off"
    assert(c.getRepBalance(1010101, s.block.coinbase)==866996971464348925464), "Rep balance off"
    print "Test send rep OK"

def test_make_reports():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    assert(c.submitReportHash(1010101, 3232, -1, 222, 0)==-2), "Nonexistant event check broken"
    event1 = c.createEvent(1010101, "new event", 5, 1, 2, 2)
    bin_market = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    s.mine(105)
    gas_use(s)
    c.incrementPeriod(1010101)
    report_hash = c.makeHash(0, 2**64, event1)
    gas_use(s)
    print c.submitReportHash(1010101, report_hash, 0, event1, 0)
    assert(c.submitReportHash(1010101, report_hash, 0, event1, 0)==1), "Report hash submission failed"
    gas_use(s)
    s.mine(55)
    gas_use(s)
    assert(c.submitReport(1010101, 0, 0, 0, 2**64, event1, 2**64)==1), "Report submission failed"
    gas_use(s)
    print c.getUncaughtOutcome(event1)
    gas_use(s)
    print "Test make reports OK"

def test_close_market():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    event1 = c.createEvent(1010101, "new event", 5, 1, 2, 2)
    bin_market = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    event2 = c.createEvent(1010101, "new eventt", 5, 1, 2, 2)
    bin_market2 = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event2], 1)
    event3 = c.createEvent(1010101, "new eventtt", 5, 1, 2, 2)
    bin_market3 = c.createMarket(1010101, "new markett", 2**58, 100*2**64, 184467440737095516, [event3], 1)
    event4 = c.createEvent(1010101, "new eevent", 5, 1, 2, 2)
    bin_market4 = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event4], 1)
    # categorical
    event5 = c.createEvent(1010101, "new event", 555, 1, 5, 5)
    # scalar
    event6 = c.createEvent(1010101, "new event", 555, -100, 200, 2)
    market5 = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event1, event5, event6], 1)
    c.commitTrade(bin_market3, c.makeMarketHash(bin_market3, 2, 5000*2**64, 0))
    c.commitTrade(bin_market2, c.makeMarketHash(bin_market2, 2, 10*2**64, 0))
    s.mine(1)
    c.buyShares(1010101, bin_market3, 2, 5000*2**64, 0)
    c.buyShares(1010101, bin_market2, 2, 10*2**64, 0)
    s.mine(105)
    c.incrementPeriod(1010101)
    report_hash = c.makeHash(0, 2**64, event1)
    report_hash2 = c.makeHash(0, 2*2**64, event2)
    report_hash3 = c.makeHash(0, 2*2**64, event3)
    report_hash4 = c.makeHash(0, 3*2**63, event4)
    assert(c.submitReportHash(1010101, report_hash, 0, event1, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(1010101, report_hash2, 0, event2, 1)==1), "Report hash submission failed"
    assert(c.submitReportHash(1010101, report_hash3, 0, event3, 2)==-5), "Report hash .99 check failed"
    assert(c.submitReportHash(1010101, report_hash4, 0, event4, 3)==1), "Report hash submission failed"
    s.mine(55)
    assert(c.submitReport(1010101, 0, 1, 0, 2*2**64, event2, 2**64)==1), "Report submission failed"
    assert(c.submitReport(1010101, 0, 3, 0, 3*2**63, event4, 2**64)==1), "Report submission failed"
    assert(c.closeMarket(1010101, bin_market)==0), "Not expired check [and not early resolve due to not enough reports submitted check] broken"
    assert(c.submitReport(1010101, 0, 0, 0, 2**64, event1, 2**64)==1), "Report submission failed"
    s.mine(60)
    c.incrementPeriod(1010101)
    c.setUncaughtOutcome(event1, 0)
    c.setOutcome(event1, 0)
    assert(c.closeMarket(1010101, bin_market)==-2), "No outcome on market yet"
    assert(c.closeMarket(1010101, bin_market3)==-7), ".99 market issue"
    c.setUncaughtOutcome(event1, 3*2**63)
    c.setOutcome(event1, 3*2**63)
    assert(c.closeMarket(1010101, bin_market)==0), "Already resolved indeterminate market check fail"
    assert(c.closeMarket(1010101, bin_market4)==-4), ".5 once, pushback and retry failure"
    orig = c.balance(s.block.coinbase)
    assert(c.balance(bin_market2)>=108*2**64)
    assert(c.balance(event2)==42*2**64)
    assert(c.closeMarket(1010101, bin_market2)==1), "Close market failure"
    new = c.balance(s.block.coinbase)
    # get 1/2 of liquidity (50) + 42 for event bond
    assert((new - orig)>=90*2**64 and (new - orig)<=95*2**65), "Liquidity and event bond not returned properly"
    assert(c.balance(bin_market2)==10*2**64), "liquidity not returned properly, should only be winning shares remaining"
    assert(c.balance(event2)==0)
    # ensure proceeds returned properly
    assert(c.claimProceeds(1010101, bin_market2)==1)
    newNew = c.balance(s.block.coinbase)
    assert((newNew - new)==10*2**64), "Didn't get 10 back from selling winning shares"
    assert(c.balance(bin_market2)==0), "Payouts not done successfully"
    print "Test close market OK"

def test_consensus():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    event1 = c.createEvent(1010101, "new event", 5, 1, 2, 2)
    bin_market = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    event2 = c.createEvent(1010101, "new eventt", 5, 1, 2, 2)
    bin_market2 = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event2], 1)
    s.mine(105)
    c.incrementPeriod(1010101)
    report_hash = c.makeHash(0, 2**64, event1)
    report_hash2 = c.makeHash(0, 2*2**64, event2)
    assert(c.submitReportHash(1010101, report_hash, 0, event1, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(1010101, report_hash2, 0, event2, 1)==1), "Report hash submission failed"
    s.mine(55)
    assert(c.submitReport(1010101, 0, 0, 0, 2**64, event1, 2**64)==1), "Report submission failed"
    assert(c.submitReport(1010101, 0, 1, 0, 2*2**64, event2, 2**64)==1), "Report submission failed"
    s.mine(60)
    c.incrementPeriod(1010101)
    assert(c.penalizeWrong(1010101, event1)==-3)
    branch = 1010101
    period = 0
    assert(c.getBeforeRep(branch, period)==c.getAfterRep(branch, period)==c.getRepBalance(branch, s.block.coinbase)==47*2**64)
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==47*2**64)
    assert(c.getTotalRepReported(branch)==47*2**64)
    
    assert(c.penalizeNotEnoughReports(1010101)==1)
    
    # assumes user lost no rep after penalizing
    assert(c.getBeforeRep(branch, period)==c.getAfterRep(branch, period)==c.getRepBalance(branch, s.block.coinbase)==47*2**64)
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.getTotalRep(branch)==47*2**64)
    assert(c.getTotalRepReported(branch)==47*2**64)
    # need to resolve event first
    assert(c.closeMarket(1010101, bin_market)==1)
    assert(c.closeMarket(1010101, bin_market2)==1)
    
    assert(c.getBeforeRep(branch, period)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch)==c.getTotalRepReported(branch))
    assert(c.getAfterRep(branch, period) < int(47.1*2**64) and c.getAfterRep(branch, period) > int(46.9*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, event1)==1)
    assert(c.getBeforeRep(branch, period)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch)==c.getTotalRepReported(branch))
    assert(c.getAfterRep(branch, period) < int(47.1*2**64) and c.getAfterRep(branch, period) > int(46.9*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, event2)==1)
    assert(c.getBeforeRep(branch, period)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch)==c.getTotalRepReported(branch))
    assert(c.getAfterRep(branch, period) < int(47.1*2**64) and c.getAfterRep(branch, period) > int(46.9*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    s.mine(55)
    assert(c.collectFees(1010101)==1)
    assert(c.getBeforeRep(branch, period)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch)==c.getTotalRepReported(branch))
    assert(c.getAfterRep(branch, period) < int(47.1*2**64) and c.getAfterRep(branch, period) > int(46.9*2**64))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    print "Test consensus OK"

def test_slashrep():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    event1 = c.createEvent(1010101, "new event", 5, 1, 2, 2)
    bin_market = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    event2 = c.createEvent(1010101, "new eventt", 5, 1, 2, 2)
    bin_market2 = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event2], 1)
    s.mine(105)
    c.incrementPeriod(1010101)
    report_hash = c.makeHash(0, 2**64, event1)
    report_hash2 = c.makeHash(0, 2*2**64, event2)
    assert(c.submitReportHash(1010101, report_hash, 0, event1, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(1010101, report_hash2, 0, event2, 1)==1), "Report hash submission failed"
    c.slashRep(1010101, 0, 2**64, s.block.coinbase, event1)
    s.mine(55)
    assert(c.submitReport(1010101, 0, 0, 0, 2**64, event1, 2**64)==1), "Report submission failed"
    assert(c.submitReport(1010101, 0, 1, 0, 2*2**64, event2, 2**64)==1), "Report submission failed"
    s.mine(60)
    c.incrementPeriod(1010101)
    assert(c.penalizeWrong(1010101, event1)==-3)
    branch = 1010101
    period = 0
    assert(c.getBeforeRep(branch, period)==c.getAfterRep(branch, period)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==c.getTotalRepReported(branch))
    
    assert(c.penalizeNotEnoughReports(1010101)==1)
    
    # assumes user lost no rep after penalizing
    assert(c.getBeforeRep(branch, period)==c.getAfterRep(branch, period)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getRepBalance(branch, branch)==0)
    assert(c.getTotalRep(branch)==c.getTotalRepReported(branch))
    # need to resolve event first
    assert(c.closeMarket(1010101, bin_market)==1)
    assert(c.closeMarket(1010101, bin_market2)==1)

    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, event1)==1)
    assert(c.getBeforeRep(branch, period)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch)==c.getTotalRepReported(branch))
    print c.getAfterRep(branch, period)
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    assert(c.penalizeWrong(1010101, event2)==1)
    assert(c.getBeforeRep(branch, period)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch)==c.getTotalRepReported(branch))
    print c.getAfterRep(branch, period)
    print c.repBalance(branch, s.block.coinbase)
    print c.repBalance(branch, branch)
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    s.mine(55)
    assert(c.collectFees(1010101)==1)
    assert(c.getBeforeRep(branch, period)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch)==c.getTotalRepReported(branch))
    assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
    print "OK"

def test_catchup():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    c.initiateOwner(1010101)
    c.reputationFaucet(1010101)
    s.mine(400)
    c.incrementPeriod(1010101)
    c.incrementPeriod(1010101)
    c.incrementPeriod(1010101)
    c.incrementPeriod(1010101)
    assert(c.penalizationCatchup(1010101)==1)
    assert(c.getRepBalance(1010101, s.block.coinbase)==702267546886122664673)
    event1 = c.createEvent(1010101, "new event", 405, 1, 2, 2)
    bin_market = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event1], 1)
    event2 = c.createEvent(1010101, "new eventt", 405, 1, 2, 2)
    bin_market2 = c.createMarket(1010101, "new market", 2**58, 100*2**64, 184467440737095516, [event2], 1)
    s.mine(105)
    c.incrementPeriod(1010101)
    # in vote period 4 now
    assert(c.penalizeNotEnoughReports(1010101)==1)
    assert(c.penalizeWrong(1010101, 444444)==1)
    report_hash = c.makeHash(0, 2**64, event1)
    report_hash2 = c.makeHash(0, 2*2**64, event2)
    assert(c.submitReportHash(1010101, report_hash, 4, event1, 0)==1), "Report hash submission failed"
    assert(c.submitReportHash(1010101, report_hash2, 4, event2, 1)==1), "Report hash submission failed"
    s.mine(55)
    assert(c.submitReport(1010101, 4, 0, 0, 2**64, event1, 2**64)==1), "Report submission failed"
    assert(c.submitReport(1010101, 4, 1, 0, 2*2**64, event2, 2**64)==1), "Report submission failed"
    s.mine(60)
    c.incrementPeriod(1010101)
    assert(c.penalizeWrong(1010101, event1)==-3)
    branch = 1010101
    period = 4
    assert(c.getBeforeRep(branch, period)==c.getAfterRep(branch, period)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getRepBalance(branch, branch)==164729424578226261279)
    assert(c.getTotalRep(branch)==866996971464348925952)
    assert(c.getTotalRepReported(branch, period)==702267546886122664673)
    
    assert(c.penalizeNotEnoughReports(1010101)==1)
    
    # assumes user lost no rep after penalizing
    assert(c.getBeforeRep(branch, period)==c.getAfterRep(branch, period)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getRepBalance(branch, branch)==164729424578226261279)
    assert(c.getTotalRep(branch)==866996971464348925952)
    assert(c.getTotalRepReported(branch, period)==702267546886122664673)
    
    # need to resolve event first
    assert(c.closeMarket(1010101, bin_market)==1)
    assert(c.closeMarket(1010101, bin_market2)==1)
    
    assert(c.getBeforeRep(branch, period)==c.getAfterRep(branch, period)==c.getRepBalance(branch, s.block.coinbase))
    assert(c.getRepBalance(branch, branch)==164729424578226261279)
    assert(c.getTotalRep(branch)==866996971464348925952)
    print c.penalizeWrong(1010101, event1)
    print c.getReport(branch, period, event1)

    print c.getBeforeRep(branch, period)
    print c.getAfterRep(branch, period)
    print c.getRepBalance(branch, s.block.coinbase)
    print c.getRepBalance(branch, branch)
    print c.getTotalRep(branch)
    assert(c.penalizeWrong(1010101, event2)==1)
    print c.getBeforeRep(branch, period)
    print c.getAfterRep(branch, period)
    print c.getRepBalance(branch, s.block.coinbase)
    print c.getRepBalance(branch, branch)
    print c.getTotalRep(branch)
    s.mine(55)
    assert(c.collectFees(1010101)==1)
    print c.getBeforeRep(branch, period)
    print c.getAfterRep(branch, period)
    print c.getRepBalance(branch, s.block.coinbase)
    print c.getRepBalance(branch, branch)
    print c.getTotalRep(branch)
    

def gas_use(s):
    global initial_gas
    print "Gas Used:"
    print s.block.gas_used - initial_gas
    initial_gas = s.block.gas_used

if __name__ == '__main__':
    src = os.path.join(os.getenv('HOME', '/home/ubuntu'), 'workspace', 'src')
    os.system('python mk_test_file.py \'' + os.path.join(src, 'functions') + '\' \'' + os.path.join(src, 'data_api') + '\' \'' + os.path.join(src, 'functions') + '\'')
    # data/api tests
    #test_cash()
    #test_ether()
    #test_quicksort()
    #test_insertionsort()
    #test_log_exp()
    #test_exp()
    #test_markets()
    #test_reporting()

    # function tests
    #test_create_event()
    #test_create_market()
    #test_buy_sell_shares()
    #test_transfer_shares()
    #test_create_branch()
    #test_send_rep()
    #test_make_reports()
    #test_close_market()
    #test_consensus()
    test_catchup()
    #test_slashrep()
    print "DONE TESTING"