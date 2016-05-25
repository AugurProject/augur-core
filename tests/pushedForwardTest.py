os.system('rm functions/output.se')
os.system('python mk_test_file.py \'' + os.path.join(src, 'functions') + '\' \'' + os.path.join(src, 'data_api') + '\' \'' + os.path.join(src, 'functions') + '\'')
global initial_gas
initial_gas = 0
t.gas_limit = 100000000
s = t.state()
c = s.abi_contract('functions/output.se')
c.initiateOwner(1010101)
c.reputationFaucet(1010101)
blocktime = s.block.timestamp
event1 = c.createEvent(1010101, "new event", blocktime+10000, 2**64, 2*2**64, 2, "www.roflcopter.com")
bin_market = c.createMarket(1010101, "new market", 184467440737095516, [event1], 1, 2, 3, 0, "yayaya", value=10**19)
event2 = c.createEvent(1010101, "new eventa", blocktime+10000, 2**64, 2*2**64, 2, "www.roflcopter.coms")
bin_market2 = c.createMarket(1010101, "new vmarket", 184467440737095516, [event2], 1, 2, 3, 0, "yayayam", value=10**19)
c.buyCompleteSets(bin_market, 2**65)
c.buyCompleteSets(bin_market2, 2**65)
c.pushMarketForward(1010101, bin_market)
c.pushMarketForward(1010101, bin_market2)
s.mine(1)
periodLength = c.getPeriodLength(1010101)
i = c.getVotePeriod(1010101)
while i < int((s.block.timestamp+1)/c.getPeriodLength(1010101)):
    c.incrementPeriod(1010101)
    i += 1
while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
    time.sleep(c.getPeriodLength(1010101)/2)
    s.mine(1)
report_hash = c.makeHash(0, 2**64, event1, s.block.coinbase)
report_hash2 = c.makeHash(0, 2**63, event2, s.block.coinbase)
c.penalizeWrong(1010101, 0)
assert(c.submitReportHash(event1, report_hash)==1), "Report hash submission failed"
assert(c.submitReportHash(event2, report_hash2)==1), "Report hash submission failed"
while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
    time.sleep(int(periodLength/2))
    s.mine(1)
assert(c.submitReport(event1, 0, 2**64, 2**64)==1), "Report submission failed"
assert(c.submitReport(event2, 0, 2**63, 2**64)==1), "Report submission failed"
while(s.block.timestamp%c.getPeriodLength(1010101) > c.getPeriodLength(1010101)/2):
    time.sleep(c.getPeriodLength(1010101)/2)
    s.mine(1)
c.incrementPeriod(1010101)
branch = 1010101
period = int((blocktime+1)/c.getPeriodLength(1010101))
assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getAfterRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==47*2**64)
assert(c.getRepBalance(branch, branch)==0)
assert(c.getTotalRep(branch)==47*2**64)
gas_use(s)
# get events in periods both old and new here
assert(c.closeMarket(1010101, bin_market)==1)
# get events in periods both old and new here again and make sure proper
# for event 1 of actual outcome current exp should still exist, original shouldn't in that period
# for event 2 it should have a rejected period and be rejected, original period should still exist, current was the one it was rejected in and expiration should be same as orig. expiration again
assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*2**64) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*2**64))
assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
gas_use(s)
assert(c.penalizeWrong(1010101, event1)==1)
print "Penalize wrong gas cost"
gas_use(s)
assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*2**64) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*2**64))
assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
while(s.block.timestamp%c.getPeriodLength(1010101) <= periodLength/2):
    time.sleep(int(periodLength/2))
    s.mine(1)
assert(c.collectFees(1010101)==1)
assert(c.getBeforeRep(branch, period, s.block.coinbase)==c.getRepBalance(branch, s.block.coinbase)==c.getTotalRep(branch))
assert(c.getAfterRep(branch, period, s.block.coinbase) < int(47.1*2**64) and c.getAfterRep(branch, period, s.block.coinbase) > int(46.9*2**64))
assert(c.getRepBalance(branch, branch)==0), "Branch magically gained rep..."
print "Test consensus OK"