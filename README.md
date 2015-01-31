augur-serpent
-------------

### To do:
	# test / fixup redeem close market and consensus in augur.se
	# optimize consensus.se (martin will help w/ this too!)
	# Implement Version 0.2 (eta - feb?)

### UI features:
	# featured markets
	# filters to organize markets by volume, category, number of traders, trading fee, initial liquidity
	# api voting
	# search engine for contract data / markets
	# chat in UI
	# social media integrations

### Version 0.5 
	# pay fee to just get a report / consensus
	 # e.g. real world event consensus
	# need to add audits
	# https://blog.ethereum.org/2015/01/28/p-epsilon-attack/

### Version 0.4 (Awesome fun stuff):
	# make code updatable + work with etherex
	# how do we scale / what if a ton of events, markets, etc.
	# stablecoin
	# reward whoever does redeem and close market according to gas cost
	# vpm
	# zeroing of array values
	# 4th Cumulant in consensus.se
	# hash first frontrunning prevention mechanism
	# high fees to check event outcome

### Version 0.3 (The Voting Upgrade):
	# make sure this follows paul's whitepaper well
	# may need a ballot max size b/c cost so need a systematic way to do voting (e.g. vote on first xxx events, then next set are another ballot)
	# randomized voter selection? - first x events expiring vote on in one ballot - random selection, then another ballot
	# fast voting cycle first few days to get the 60% problem away from a branch, e.g. what if not enough people vote
		# add a branch initial rbcr rapid period to start w/
	# 60% of votes -- need to get the cycle length parameters right
	# rapid rbcr anytime to vote i'm alive if <60% of people vote after a few cycles or something
	# max number of owners in a branch of rep.

### Version 0.2 (Markets Upgrades):
	# add support for categorical and multidimensional events
	# salt hash vote mechanism


















