import random
from ethereum import tester as t
t.gas_limit = 4100000
s = t.state()
d = s.abi_contract('test.se')
c = s.abi_contract('repContract.se')
amounts = [int(random.random()*x*10**20) for x in range(1, 11)]
remaining = 11000000*10**20 - sum(amounts)
amounts[0] += remaining
accounts = [d.getSender(sender=eval('t.k'+str(x))) for x in range(10)]
c.setSaleDistribution(accounts, amounts)
assert(c.getSeeded())
assert(c.getDecimals()==20)
assert(c.totalSupply()==11000000*10**20)
for x in range(10):
	assert(c.balanceOf(accounts[x])==amounts[x])
for x in range(5):
	assert(c.approve(accounts[x+5], amounts[x], sender=eval('t.k'+str(x))))
	assert(c.allowance(accounts[x], accounts[x+5]) == amounts[x])
	assert(c.transferFrom(accounts[x], accounts[x+5], amounts[x], sender=eval('t.k'+str(x+5))))
	assert(c.balanceOf(accounts[x])==0)
	assert(c.balanceOf(accounts[x+5])==(amounts[x]+amounts[x+5]))
for x in range(5, 10):
	assert(c.transfer(0, (amounts[x]+amounts[x-5]), sender=eval('t.k'+str(x))))
assert(c.balanceOf(0)==11000000*10**20)