augur-serpent
-------------

### To do:
- min/max fxp? & 1,2 or 2^64 and 2*2^64 - should probably support fxp
- need to support categorical outcomes in consensus --- dunno if we do atm
- #def moveEvent(event, newBranch, authorSignature):
- check that msg.sender is one of our function contracts
- make data EXTERNs updatable

### Bugs:
- what if a scalar has a .5 actual value outcome
  - I suggest the .5 outcome be something like 2^256
  - scalar .5 outcomes just don't work at all atm either
  - jack idea for this
- for scalar events, how do you distinguish a 0 numerical response from a no-response (usually 0)?
  - idea: store answer/no-answer for each reporter separate from the report values

### Redeem/consensus optimizations:
- we will ultimately want to combine the redeem functions with their consensus counterparts! (it is inefficient to have two function calls for each step)
- store iterations/components as contract data, instead of inside the loading vector

### Scalability optimizations (hopefully these become an issue!) ... Curse you gas issues (too soon):
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
- lazy evaluation
- metadata off chain
- events

### Once eth supports it:
- reward whoever does close market according to gas cost (pay gas fee in cashcoin to miner)
- work with etherex & chow (bitsquare, coineffine, mercuryex other decentralized exchanges as well)

### Version 0.5 (More fun features - May and Beyond):
- if no agreement on any outcome <65% confidence (failure to achieve certainty) this confidence is *of the rep reported* (consensus needs to take this as a param), then do over next voting period
  - have consensus push all into next voting period (this is currently known as disputed)
    - perhaps use a "times voted" thing for this
    - Disputed: If any of a Market’s Decisions attain ‘Disputed’ status, the Market attains the Disputed status. No one can buy or sell until the Dispute is resolved (i suggest a disputed outcome is a weird value returned from consensus or perhaps a simple 0)
- Audited: If a Market remained in a Disputed state and became audited (after 2 failures to achieve consensus), the Market would enter this state. Shares can be sold (redeemed) but the payoff formula is slightly more complicated (see Appendix III). Buying is also disabled (for simplicity and consistency).
  - audit vote (where people "vote" with their cash) (every 6 mo. disputed decisions have this happen)
  - audits have a fee
- two wave svd before audits?
  - e.g. if it falls within the certainty threshold, then it goes to wave 2 of svd else it goes to next period (disputed), if that fails, audit
- public good funding + poss. futarchy
- allow people to set market base currencies - is this what V meant by mult. currency support
- With these conditions: [1] Stalled Branch, [2] Decision-Author’s signature, one can move an event to a new Branch (use ecVerify serpent function)

### Version 0.4 (Awesome fun stuff - April):
- go over stuff in closeMarket tx
- make sure we're not printing money anywhere on accident (e.g. event payouts and trading fees)
- limit orders in UI if price > or < a number and maximum amount of money (or shares?) you're willing to spend for buy, max shares to sell for sell - but what about real on chain limit orders?
- Stop loss orders
- update eventsExpDates so you can update & it not lose events from whatever your branch's last voting periods was, should just moveEventsToCurrentPeriod upon update perhaps have 2 vars in a contract for old addr and new, call old and get its events then move to new contract
- consider implications of updating data/api contracts & data migration ^
- make sure UI checks _current vote period_ not the one in branch but the actual one we _should_ be voting on even if we're behind, so if behind by 10 UI should still be asking people to vote on the what the current period should be 
