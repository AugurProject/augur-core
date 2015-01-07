augur-serpent
-------------

### To do:
	# test / fixup redeem close market and consensus in augur.se
	# Implement Version 0.2 (eta - feb?)

### Version 0.4 (Awesome fun stuff):
	# make code updatable 
	# how do we scale / what if a ton of events, markets, etc.
	# featured markets
	# seigniorage coin
	# api voting
	# blockchain explorer to get / examine data or make rpc api calls to the contract to get it
			# local contract calls don't cost gas - # ui functions
	# search engine for contract data / events
	# p2p 1-1 parimutuel betting
	# conditional upon eventhash and its outcome data Events[](branch, expirationDate, outcome)
	# need a function to setup the bet & another function to close it provided event is expired & outcome is determined
	# 4th Cumulant in consensus.se

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

### Version 0.2 (Markets Upgrades):
	# add support for categorical and scalar and multidimensional events
	# Scalar event where people update what type of share they bought using a thing
	# in an array where index is their scalar x and value
	# is the share updated number of shares bought
	# zeroing of array values
	# hash first frontrunning prevention mechanism
	# salt hash vote mechanism
	# should make an API function to make ballot
	# 0th reporter funny business or change numReporters to currentRepIndex
