augur-serpent
-------------

### To do:
	# MVP
   		see if current block.num/period is greater than the last period, if so we're in the start of a new period
   		check mul and div parens
	# min/max to fixed poss.

### Version 0.5 (More fun features - May and Beyond):
	# need to add audits
	# special cfds + public good funding + poss. futarchy
	# make code updatable + work with etherex & chow (bitsquare, coineffine other decentralized exchanges as well)
	# stablecoin
	# make sure this follows paul's whitepaper well	
	# zeroing of array values
	# consensus bond mechanism cheaper
	# VPM

### Version 0.4 (Awesome fun stuff - April):
	# go over stuff in close and redeem txs
	# make sure we're not printing money anywhere on accident (e.g. event payouts and trading fees)
		# reward whoever does close market according to gas cost (pay gas fee in cashcoin to miner)
	# hash first frontrunning prevention mechanism
	# salt hash vote mechanism
   		blocknumber mod period is residual
   		if residual is <period/2 submit hash of (msg.sender, Rnum, Votes[]) for that reporter
   		if >period/2 submit Rnum and Votes[] for reporter
   		check in consensus if they match, if not, no vote ballot (allow people to change votes and hash up until lock in residual change)
   		anti cheat provide p and randomNum mechanism steal deposit (will need to support snarks eventually)
	# p+e fix?

### Version 0.3 (The Voting Upgrade - March):
	# randomized voter selection? - first x events expiring vote on in one ballot - random selection, then another ballot
	# fast voting cycle first few days to get the <60% problem away from a branch
	# e.g. what if not enough people vote
	# or what if people get behind on voting
	# rapid rbcr anytime to vote i'm alive if <60% of people vote after a few cycles or something
	# max number of owners in a branch of rep. issues w/ sending rep etc