augur-serpent
-------------

### To do (Paul update):
	# market needs liquidity cash changes
	# need a price function for tradeshares function
	# min max categorical events - so max-min/numOutcomes is interval between outcome
	# implement categorical in consensus fun + augur.se.
	# what if a scalar has a .5 actual value outcome
		# I suggest the null outcome be either scalarmin-1 or max+1
	# what happens if a .5 disputed outcome in general?
	# Disputed: If any of a Market’s Decisions attain ‘Disputed’ status, the Market attains the Disputed status. No one can buy or sell until the Dispute is resolved (i suggest a disputed outcome is a 0 returned from consensus)
	# if no agreement on any outcome <65% or whatever confidence, then do over next voting period (i guess have consensus return a 0), if that fails then it goes to audit vote (where people "vote" with their cash) - this confidence is *of the rep reported*
	# for final .5 outcomes take shares bought and divide the money up amongst them equally (should be .50 each)
	# With these three conditions: [1] Stalled Branch, [2] Decision-Author’s signature, [3] Market-Author’s signature, one can move a Market’s Decisions to a new Branch
	# what if we have 3-4 cycles in a row of 10 events getting pushed back --- market would already be closed even though events up to be decided on for a while yet never decided --- technically this is a stalled branch and market should be open no? -- yes
	# catch parameter
	# could do .5 outcomes where if a .5 in a market with multiple dimensions it still pays out
	# One failure to achieve certainty could be a simple confusion (and should not go directly to audit) - perhaps vote again on it
	# a certain .5 outcome shouldn't be voted on again though

### Scalability optimizations (hopefully these become an issue!:
	# http://lightning.network/lightning-network.pdf 
	# sidechains 
	# randomized voter selection? - first x events expiring vote on in one ballot - random selection, then another ballot (V presentation on a similar strat.)
	# ethereum rng:
	  probability 0 1 ... 100
	  prob = probability*2^32
	  if(sha(block.prevhash+block.coinbase+block.timestamp+nonce) mod 2^32<prob):
	   	you got picked / won the rng!
	# max number of owners in a branch of rep. issues w/ sending rep etc
	# zeroing of array values (e.g. people in the rep index after they have 0 rep left)
	# consensus bond mechanism cheaper
	# possibly enable people to choose their own resolution scripts

### Version 0.5 (More fun features - May and Beyond):
	# audit fee
	# need to add audits
	# Audited: If a Market remained in a Disputed state and became audited, the Market would enter this state. Shares can be sold (redeemed) but the payoff formula is slightly more complicated (see Appendix III). Buying is also disabled (for simplicity and consistency).
	# two wave svd before audits?
	# e.g. if it falls within the certainty threshold, then it goes to wave 2 of svd else it goes to an audit  
	# special cfds + public good funding + poss. futarchy
	# make code updatable + work with etherex & chow (bitsquare, coineffine other decentralized exchanges as well)
	# stablecoin
	# VPM
	# allow people to set market base currencies
	# separate Branches might compete over different parameter-families, it may be advantageous for the blockchain itself to impose “Reasonable Bounds” on possible choices for parameters. Branches themselves may impose “Reasonable Bounds” on Market-specific parameters, (b, content-tags, trading/audit fees).	

### Version 0.4 (Awesome fun stuff - April):
	# go over stuff in close and redeem txs
	# make sure we're not printing money anywhere on accident (e.g. event payouts and trading fees)
		# reward whoever does close market according to gas cost (pay gas fee in cashcoin to miner)
	# hash first frontrunning prevention mechanism or pow
	# p+e fix?
	# how did V propose we support mult. currencies?
	# limit orders
	
### Version 0.3 (The Voting Upgrade - March):
	# salt hash vote mechanism
   		blocknumber mod period is residual
   	    if residual is <period/2 submit hash of (msg.sender, Rnum, Votes[]) for that reporter
   		if >period/2 submit Rnum and Votes[] for reporter
   		check in consensus if they match, if not, no vote ballot (allow people to change votes and hash up until lock in residual change)
	   	anti cheat provide p and randomNum mechanism steal deposit (will need to support snarks eventually)

### Bugs:
	# not allowing me to make a subbranch w/ same desc. but a parent which is a different subbranch (I have a suspicion the *only* thing getting hashed is the description and not the other metadata, causing this issue)