augur-serpent
-------------

### To do:
	# min max categorical events - so max-min/numOutcomes is interval between outcome
	# implement categorical in consensus fun + augur.se.
	# don't need reprequired
	# what if a scalar has a .5 actual value outcome
		# I suggest the null outcome be either scalarmin-1 or max+1
	# what happens if a .5 disputed outcome in general?
	# Disputed: If any of a Market’s Decisions attain ‘Disputed’ status, the Market attains the Disputed status. No one can buy or sell until the Dispute is resolved
	# Audited: If a Market remained in a Disputed state and became audited, the Market would enter this state. Shares can be sold (redeemed) but the payoff formula is slightly more complicated (see Appendix III). Buying is also disabled (for simplicity and consistency).  
	# if no agreement on any outcome <65% or whatever confidence, then do over next voting period, if that fails then it goes to audit vote (where people "vote" with their cash) - this confidence is *of the rep reported*
	# VoteCoins cannot be simultaneously spent (transferred) and used to vote (need to fix this)
	# refund left over initial liquidity in market - half to market creator, other half to voters
	# *unless* it's a scaled decision, refund all initial liquidity left overto market creator
	# rest of money available in market + the additional trading fees divy up amongst reporters and market creator
	# for final .5 outcomes take shares bought and divide the money up amongst them equally (should be .50 each)
			# ) Shares themselves can be ‘traded’ for efficiency or (optionally) even to offload tradinginfrastructure
		to third parties. Instead of selling for CashCoin, transferring CashCoin, and
		then re-buying (a cost of 2 trading fees and 3 transaction fees, and substantial delay and
		price risk), a ‘transfer’ function can simply move shares among keypairs in one
		transaction. However, to remain incentive-compatible, this function would need to
		require an explicit payment to the Market of 2 trading fees.
	# With these three conditions: [1] Stalled Branch, [2] Decision-Author’s signature, [3] Market-Author’s signature, one can move a Market’s Decisions to a new Branch


It may be desirable to impose serious prerequisites for Branching. The option to Branch may require an automatic trigger, for example, that there be >500 upcoming Decisions.  Requiring high λ and Λ parameters would also discourage the creation of frivolous Branches (as these would need to reliably support many Decisions in order to operate effectively).
limit order
front running pow


does it matter if we have mult. decisions for a dimension vs just one event w/ multiple outcome

catch parameter

could do .5 outcomes where if a .5 in a market with multiple dimensions it still pays out 

two wave svd before audits?
e.g. if it falls within the certainty threshold, then it goes to wave 2 of svd
else it goes to an audit

One failure to achieve certainty could be a simple confusion (and should not go directly to audit) - perhaps vote again on it

a certain .5 outcome shouldn't be voted on again though

separate Branches might compete over different parameter-families, it may be advantageous for the blockchain itself to impose “Reasonable Bounds” on possible choices for parameters. Branches themselves may impose “Reasonable Bounds” on Market-specific parameters, (b, content-tags, trading/audit fees).


min future decisions at stake - 200 - else branch stalls (do same thing we do if min ballot/event size isn't met, push events into next voting period and hopefully more people will create decisions so it can actually be vote on, else repeat)

audit fee

### Scalability optimizations (hopefully these become an issue!):
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
	# salt hash vote mechanism
   		blocknumber mod period is residual
   	    if residual is <period/2 submit hash of (msg.sender, Rnum, Votes[]) for that reporter
   		if >period/2 submit Rnum and Votes[] for reporter
   		check in consensus if they match, if not, no vote ballot (allow people to change votes and hash up until lock in residual change)
	   	anti cheat provide p and randomNum mechanism steal deposit (will need to support snarks eventually)

	is there *supposed* to be a min rep reported? i don't think so

	if your minimum rep reported isn't enough, you get behind
	the next voting period comes up and you still haven't solved the last one
	now the problem is no one is allowed to vote on the old period anymore so it'll never get enough rep reported
	and if you get far enough behind, any events that get pushed up due to a small voting period can't be voted on either
	I think a solution to this is to simply notice when a branch is stalled in this case (not enough rep reported at the point people can no longer vote in that period) and then move all those events up to the next voting period (and possibly allow an alive vote consensus call to be made)

	when the next voting period clock starts we don't want anyone to submit a vote not counted because some events got pushed up from the last vote period due to either not enough reporters or not enough events

	# what if people get behind on voting (e.g the redeem tx isn't called <1 period after it can be called) 
	# voteperiod is an optional parameter only used in the scenario that we get behind on voting periods
	# so people will need to vote on periods that are upcoming even if our currentVotePeriod is a bit behind, but what if an event then gets pushed into one of these periods that can't be voted on anymore..., perhaps don't allow voting if upcoming even if behind, but then we have a problem because can't vote on pushed up events


	so you can't vote anymore on the next period, so instead the events get pushed up to next vote period provided stuff has expired, currentVotePeriod is incremented, and people try to vote again (if we're still so behind, checkQuorem again, etc.)

	what if we have 3-4 cycles in a row of 10 events getting pushed back --- market would already be closed even though events up to be decided on for a while yet never decided --- technically this is a stalled branch and market should be open no?
