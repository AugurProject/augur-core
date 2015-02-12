augur-serpent
-------------

### To do:
	# MVP
		# trading fees for markets
		# voting period fixes / when can / can't vote / when things up for voting
		# redeem (multiple tx stuff from consensus)
		# update api
		# accuracy of exp needs to be within .1%
	# Implement Version 0.3
	# support https://github.com/ethereum/cpp-ethereum/wiki/MetaCoin-API
	# and https://github.com/ethereum/cpp-ethereum/wiki/Exchange-API possibly
	# slice(x, start, end)
	shrink
	string stuff
	# To hash an arbitrary number of bytes, use chars syntax. Example: x = sha256([0xf1fc122bc7f5d74df2b9441a42a1469500000000000000000000000000000000], chars=16) - returns the sha256 of the first 16 bytes. Note: padding with trailing zeroes, otherwise the first 16 bytes will be zeroes, and the sha256 of it will be computed instead of the desired.
	# The person who improperly revealed their secret could lose a safety deposit, and the tattle-tail would get part of the deposit. w/ collusion

### Version 0.5 (More fun features - May):
	# need to add audits
	# special cfds + public good funding + poss. futarchy
	# decentralized exchange (etherex and chow) -- chow exchange needs a way to prevent two people from claiming an order, sending bitcoin, then being screwed unless altruism (suggest a claim tx w/ possible small ether bond and during that time no one else can claim the exchange tx - but if you wait too long you lose the bond + it becomes open again, something like that)
	# make code updatable + work with etherex
	# https://blog.ethereum.org/2015/01/28/p-epsilon-attack/
	# stablecoin
	# could have multiple people add liquidity to the market :o

### Version 0.4 (Awesome fun stuff - April):
	# make sure this follows paul's whitepaper well	
	# reward whoever does redeem and close market according to gas cost
	# zeroing of array values
	# hash first frontrunning prevention mechanism
	# salt hash vote mechanism
	# high fees to check event outcome - doesn't solve freeloader problem :/

### Version 0.3 (The Voting Upgrade - March):
	# randomized voter selection? - first x events expiring vote on in one ballot - random selection, then another ballot
	# fast voting cycle first few days to get the 60% problem away from a branch, e.g. what if not enough people vote
	# 60% of votes -- need to get the cycle length parameters right
	# rapid rbcr anytime to vote i'm alive if <60% of people vote after a few cycles or something
	# max number of owners in a branch of rep.

	collusion (solved by zack proposal)
	p + epsilon (req. a 51% atk)
	free rider (solved by vss)