from ethereum import tester as t

initial_gas = 0

def cash_tests():
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('data_api/cash.se')
    
    c.initiateOwner(111)
    c.setCash(111, 10)
    gas_use(s)
    c.addCash(111,5)
    c.subtractCash(111,4)
    gas_use(s)
    assert(c.balance(111)==11), "Cash value not expected!"
    gas_use(s)
    c.send(111, 10)
    assert(c.balance(111)==21), "Send function broken"
    assert(c.sendFrom(101, 1, 111)==0), "Receiver uninitialized check failed"
    c.initiateOwner(101)
    assert(c.sendFrom(101, 1, 111)==1), "Send from broken"
    assert(c.balance(111)==20), "Send from broken"
    assert(c.balance(101)==1), "Send from broken"
    gas_use(s)
    print "CASH OK"
    
def ether_tests():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('data_api/ether.se')
    assert(c.depositEther(value=5)==5), "Unsuccessful eth deposit"
    assert(c.withdrawEther(111, 500)==0), "Printed money out of thin air..."
    assert(c.withdrawEther(111, 5)==1), "Unsuccessful withdrawal"
    print c.balance(111)
    gas_use(s)
    print "ETHER OK"
    


def gas_use(s):
    global initial_gas
    print "Gas Used:"
    print s.block.gas_used - initial_gas
    initial_gas = s.block.gas_used

    
if __name__ == '__main__':
    cash_tests()
    ether_tests()
