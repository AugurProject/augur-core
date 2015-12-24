from ethereum import tester as t
import math

initial_gas = 0

def test_cash():
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
    
'''def test_exp():
    global initial_gas
    initial_gas = 0
    t.gas_limit = 100000000
    s = t.state()
    c = s.abi_contract('data_api/expiringEvents.se')
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
    gas_use(s)'''

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

def gas_use(s):
    global initial_gas
    print "Gas Used:"
    print s.block.gas_used - initial_gas
    initial_gas = s.block.gas_used


if __name__ == '__main__':
    test_cash()
    test_ether()
    test_quicksort()
    test_insertionsort()
    test_log_exp()
    #exp_tests()
    #markets_tests()
    #reporting_tests()
    #faucet_tests()
    #create_branch_tests()
    #send_rep_tests()
    #create_event_tests()
    #create_market_tests()
    #buy_sell_shares_tests()
    #transfer_shares_tests()
    #close_market_tests()
    #make_report_tests()
    #consensus_tests()
    #p2p_wager_tests()