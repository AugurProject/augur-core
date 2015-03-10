augur-serpent
-------------

### To do:
	- market needs liquidity to be cash amount, not num of shares
	- need a price function for ls-lmsr
	- min max categorical events - so max-min/numOutcomes is interval between outcome
	- implement categorical in consensus fun + augur.se.
	- what if a scalar has a .5 actual value outcome
	  - I suggest the .5 outcome be something like 2^256
	- for final .5 outcomes take shares bought and divide the money up amongst them equally (should be .50 each)
	  - if a .5 in a market with multiple dimensions it still pays out (just mult. prices by .5)
	- Disputed: If any of a Market’s Decisions attain ‘Disputed’ status, the Market attains the Disputed status. No one can buy or sell until the Dispute is resolved (i suggest a disputed outcome is a weird value returned from consensus)
	- if no agreement on any outcome <65% or whatever confidence (failure to achieve certainty), then do over next voting period (i guess have consensus push them all into next voting period and not report outcomes besides 0), if that fails then it goes to audit vote (where people "vote" with their cash) (every 6 mo. disputed decisions have this happen)- this confidence is *of the rep reported* - perhaps use a "times voted" thing for this
	- With these three conditions: [1] Stalled Branch, [2] Decision-Author’s signature, [3] Market-Author’s signature, one can move a Market’s Decisions to a new Branch (use ecVerify serpent function)
	- 20k gas storage issue

### Bugs:
	- not allowing me to make a subbranch w/ same desc. but a parent which is a different subbranch (I h5ave a suspicion the *only* thing getting hashed is the description and not the other metadata, causing this issue)

### Scalability optimizations (hopefully these become an issue!:
	- http://lightning.network/lightning-network.pdf
	- sidechains
	- randomized voter selection? - first x events expiring vote on in one ballot - random selection, then another ballot (V presentation on a similar strat.)
	- ethereum rng:
	  - probability 0 1 ... 100
	  - prob = probability*2^32
	  - if(sha(block.prevhash+block.coinbase+block.timestamp+nonce) mod 2^32<prob):
	   	you got picked / won the rng!
	- max number of owners in a branch of rep. issues w/ sending rep etc
	- zeroing of array values (e.g. people in the rep index after they have 0 rep left)
	- consensus bond mechanism cheaper
	- possibly enable people to choose their own resolution scripts

### Version 0.5 (More fun features - May and Beyond):
	- audit fee
	- need to add audits
	- Audited: If a Market remained in a Disputed state and became audited, the Market would enter this state. Shares can be sold (redeemed) but the payoff formula is slightly more complicated (see Appendix III). Buying is also disabled (for simplicity and consistency).
	- two wave svd before audits?
	- e.g. if it falls within the certainty threshold, then it goes to wave 2 of svd else it goes to an audit  
	- special cfds + public good funding + poss. futarchy
	- make code updatable + work with etherex & chow (bitsquare, coineffine other decentralized exchanges as well)
	- stablecoin
	- VPM
	- allow people to set market base currencies
	- separate Branches might compete over different parameter-families, it may be advantageous for the blockchain itself to impose “Reasonable Bounds” on possible choices for parameters. Branches themselves may impose “Reasonable Bounds” on Market-specific parameters, (content-tags, trading/audit fees).

### Version 0.4 (Awesome fun stuff - April):
	- go over stuff in close and redeem txs
	- make sure we're not printing money anywhere on accident (e.g. event payouts and trading fees)
	  - reward whoever does close market according to gas cost (pay gas fee in cashcoin to miner)
	- hash first frontrunning prevention mechanism or pow
	- p+e fix?
	- how did V propose we support mult. currencies?
	- limit orders
	
### Version 0.3 (The Voting Upgrade - March):
	- salt hash vote mechanism
	  - blocknumber mod period is residual
   	  - if residual is <period/2 submit hash of (msg.sender, Rnum, Votes[]) for that reporter
      - if >period/2 submit Rnum and Votes[] for reporter
   	  - check in consensus if they match, if not, no vote ballot (allow people to change votes and hash up until lock in residual change)
	  - anti cheat provide p and randomNum mechanism steal deposit (will need to support snarks eventually)