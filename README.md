augur-serpent
-------------

### To do:
	# min max categorical events - so max-min/numOutcomes is interval between outcome
	# implement categorical in consensus fun + augur.se.

### Scalability optimizations (hopefully these become an issue!):
	# randomized voter selection? - first x events expiring vote on in one ballot - random selection, then another ballot (V presentation on a similar strat.)
	# ethereum rng:
	  probability 0 1 ... 100
	  prob = probability*2^32
	  if(sha(block.prevhash+block.coinbase+block.timestamp+nonce) mod 2^32<prob):
	   	you got picked / won the rng!
	# max number of owners in a branch of rep. issues w/ sending rep etc
	# zeroing of array values
	# consensus bond mechanism cheaper
	# possibly enable people to choose their own resolution scripts

### Version 0.5 (More fun features - May and Beyond):
	# need to add audits
	# special cfds + public good funding + poss. futarchy
	# make code updatable + work with etherex & chow (bitsquare, coineffine other decentralized exchanges as well)
	# stablecoin
	# make sure this follows paul's whitepaper well	
	# VPM

### Version 0.4 (Awesome fun stuff - April):
	# go over stuff in close and redeem txs
	# make sure we're not printing money anywhere on accident (e.g. event payouts and trading fees)
		# reward whoever does close market according to gas cost (pay gas fee in cashcoin to miner)
	# hash first frontrunning prevention mechanism
	# p+e fix?

### Version 0.3 (The Voting Upgrade - March):
	# fast voting cycle first few days to get the <60% problem away from a branch
	# rapid rbcr *anytime* to vote i'm alive if <60% of people vote after a few cycles
	# salt hash vote mechanism
   		blocknumber mod period is residual
   		if residual is <period/2 submit hash of (msg.sender, Rnum, Votes[]) for that reporter
   		if >period/2 submit Rnum and Votes[] for reporter
   		check in consensus if they match, if not, no vote ballot (allow people to change votes and hash up until lock in residual change)
	   	anti cheat provide p and randomNum mechanism steal deposit (will need to support snarks eventually)

	if your minimum rep reported isn't enough, you get behind
	the next voting period comes up and you still haven't solved the last one
	now the problem is no one is allowed to vote on the old period anymore so it'll never get enough rep reported
	and if you get far enough behind, any events that get pushed up due to a small voting period can't be voted on either
	I think a solution to this is to simply notice when a branch is stalled in this case (not enough rep reported at the point people can no longer vote in that period) and then move all those events up to the next voting period

	when the next voting period clock starts we don't want anyone to submit a vote not counted because some events got pushed up from the last vote period due to either not enough reporters or not enough events

	# what if people get behind on voting (e.g the redeem tx isn't called <1 period after it can be called) 
	# voteperiod is an optional parameter only used in the scenario that we get behind on voting periods
	# so people will need to vote on periods that are upcoming even if our currentVotePeriod is a bit behind, but what if an event then gets pushed into one of these periods that can't be voted on anymore..., perhaps don't allow voting if upcoming even if behind, but then we have a problem because can't vote on pushed up events


	so you can't vote anymore on the next period, so instead the events get pushed up to next vote period provided stuff has expired, currentVotePeriod is incremented, and people try to vote again (if we're still so behind, checkQuorem again, etc.)