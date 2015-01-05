augur-serpent
-------------

### To do:
	# Optimize consensus.se contract
	# 4th Cumulant in consensus.se

### Version 0.4:
	# make code updatable 
	# seigniorage coin
	# api voting
	# blockchain explorer to get / examine data or make rpc api calls to the contract to get it
			# local contract calls don't cost gas
	# search engine for contract data / events
	# p2p 1-1 parimutuel betting

### Version 0.3:
	# make sure this follows paul's whitepaper well
	# reward whoever does redeem and close market according to cost
	# how do we scale / what if a ton of events, markets, etc.
	# api voting option
	# may need a ballot max size b/c cost so need a systematic way to do voting (e.g. vote on first xxx events, then next set are another ballot)
	# randomized voter selection? - first x events expiring vote on in one ballot - random selection, then another ballot
	# fast voting cycle first few days to get the 60% problem away from a branch, e.g. what if not enough people vote
	# 60% of votes -- need to get the cycle length parameters right
	# rapid rbcr anytime to vote i'm alive if <60% of people vote after a few cycles or something
	# profit msr

### Version 0.2:
	# add support for categorical and scalar and multidimensional events
	# Scalar event where people update what type of share they bought using a thing
	# in an array where index is their scalar x and value
	# is the share updated number of shares bought
	# zeroing of array values
	# make sure events voting periods are properly setup
	# make sure eventsexpdates currentindex -1 is the stuff we actually vote on in redeem tx
	# ui functions
	# hash first frontrunning prevention mechanism
	# salt hash vote mechanism
	# add a branch initial rbcr rapid period to start w/
	# should make an API function for this (make ballot)
	# can't determine vote scenario
	#0th reporter funny business or change numReporters to currentRepIndex

### To do:
	# inset bug