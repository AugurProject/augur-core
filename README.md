augur-serpent
-------------

### To do:
	# test / fixup redeem close market and consensus in augur.se
	# optimize consensus.se (martin & alan)
	# Implement Version 0.2 (eta - feb?)
	# abi_contract to js for calling js functions

### Version 0.4 (Awesome fun stuff):
	# clean api interface
	# secure multiparty computation to prevent attack vitalik brought up
		zack [4:42 PM] 
		Faster alternative to SMPC:
		Say there are 100 votecoin holders in a jury.
		Each voter makes their encrypted vote, then they collect all the encrypted votes onto one big page.
		Each voter make sure that their own vote is on the page.
		Each voter signs the page. 
		Each voter then creates an un-signed transaction that reveals their vote.
		It would be impossible for a voter to prove how he voted (unless all 100 voted the same way). So the attacker wont know who to reward. (edited)
	# record number of shares bought in USD at conversion rate of bitcoin in the UI to give accurate probabilities
	# or just use seigniorage shares
	# make code updatable 
	# how do we scale / what if a ton of events, markets, etc.
	# featured markets
	# seigniorage coin
	# zeroing of array values
	# api voting
	# blockchain explorer to get / examine data or make rpc api calls to the contract to get it
			# local contract calls don't cost gas - # ui functions
	# search engine for contract data / events
	# 4th Cumulant in consensus.se
	# hash first frontrunning prevention mechanism
	# high fees to check event outcome

### Version 0.3 (The Voting Upgrade):
	# make sure this follows paul's whitepaper well
	# reward whoever does redeem and close market according to cost
	# may need a ballot max size b/c cost so need a systematic way to do voting (e.g. vote on first xxx events, then next set are another ballot)
	# randomized voter selection? - first x events expiring vote on in one ballot - random selection, then another ballot
	# fast voting cycle first few days to get the 60% problem away from a branch, e.g. what if not enough people vote
		# add a branch initial rbcr rapid period to start w/
	# 60% of votes -- need to get the cycle length parameters right
	# rapid rbcr anytime to vote i'm alive if <60% of people vote after a few cycles or something
	# profit msr
	# max number of owners in a branch of rep.
	# people should choose markets based on lower trading fee, more liquidity, and most volume

### Version 0.2 (Markets Upgrades):
	# add support for categorical and multidimensional events
	# order by the dimensions
	# allow settable trading fees
	so categorical would just be a list of events, 1 dimension, states = numevents+1
	multidimensional binary is just 1, event, 2, event, states = 2^k
	can also have multidimensional w/ scalars
	or a multidimensional with a binary and a scalar
	multidimensional categorical
	# salt hash vote mechanism
	# fix strings
	# .5 outcome needs to pay back money, and whoever provided liquidity gets 0 back

### AMSR:
	# events exhaustive partition - 1 has to happen (can actually add a new event while market is running - can't delete events)
	# specify probabilities & how much money they're willing to lose (can increase $ want to lose, ability to change priors on events - separate vector of probabilities and market maker can just change them -- changes prior, not the actual market price) -- change prior during event.
	# market maker if he sets bad odds people will arbitrage it and make him lose his money.
	# market prices will equilibrate as well if there are two separate markets on the same thing.
	# market makers make a ton of money
	# ways to make money in system are:
		# creating events, creating markets, reporting on their outcomes, holding rep due to market profit

	Distance function:
	# l1 (a function of the number of shares you purchase in the market)

	Utility function:
	# ln(x)

	Liquidity function:
	f(s) = .924*sqrt(s+132.3) - sqrt(132.3)

	Profit function:
	variable for g(s) profit cut should be adjustable from .25 - 5%
	early stage parameter 1.10
	g(s) = .01s

	# event probabilities from pricing would be price per share - (excess fee / share)
