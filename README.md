augur-serpent
-------------

### To do:
	# MVP
		# voting period fixes / when can / can't vote / when things up for voting
        if blockNum / periodLength is say 5 and eventsExpDates[5]
        the current vote period should be on things from eventsExpDates 4
        then once blockNum / periodLength is say 6 and eventsExpDates[6]
       	votePeriod 4 should close and the currentVotePeriod should be from
   		eventsExpDates 5 (anyone can call the consensus function for voteperiod 4 at this point)
	# min/max to fixed poss.
	# do winningOutcomes stuff

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
	# p+e fix?

### Version 0.3 (The Voting Upgrade - March):
	# randomized voter selection? - first x events expiring vote on in one ballot - random selection, then another ballot
	# fast voting cycle first few days to get the <60% problem away from a branch, e.g. what if not enough people vote
	# rapid rbcr anytime to vote i'm alive if <60% of people vote after a few cycles or something
	# max number of owners in a branch of rep. issues w/ sending rep etc

