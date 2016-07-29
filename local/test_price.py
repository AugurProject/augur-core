def test_price():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('functions/output.se')
    gas_use(s)
    c.initiateOwner(1010101)
    event = c.createEvent(1010101, "new event", 2051633, 1, 2, 2)
    gas_use(s)
    market = c.createMarket(1010101, "new market", 0x205bc01a36e2eb2, 0x62eaac4c29e39f5c8a, 0x51eb851eb851eb8, [event], 1)
    print "event:", event
    print "market:", market
    cost = c.lsLmsr(market)
    print "cost:", cost
    price1 = c.price(market, 1)
    price2 = c.price(market, 2)
    print "prices:", price1, price2
    simulatedBuy = c.getSimulatedBuy(market, 1, 2)
    print "simulatedBuy:", simulatedBuy
    simulatedSell = c.getSimulatedSell(market, 1, 2)
    print "simulatedSell:", simulatedSell
    assert(cost == 922337203685477579054)
    assert(price1 == 9324563974794018816)
    assert(price2 == 9324563974794018816)
    print "PRICE OK"