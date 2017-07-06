class BidOrderCoveredWithTokens:
    def __init__(market, outcome, maker, tokens_offered, shares_desired):
        self.market = market
        self.outcome = outcome
        self.maker = maker
        self.tokens_offered = tokens_offered
        self.shares_desired = shares_desired

class BidOrderCoveredWithShares:
    def __init__(market, outcome, maker, tokens_offered, shares_desired):
        self.market = market
        self.outcome = outcome
        self.maker = maker
        self.tokens_offered = tokens_offered
        self.shares_desired = shares_desired

def make_share_covered_bid(market, outcome, tokens_offered, shares_desired):
    maker = msg.sender

    # escrow shares
    for outcome in range(0, market.getNumOutcomes()):
        if outcome == order.outcome:
            continue
        market.getShare(outcome).transferFrom(maker, market, shares_desired)

    # create the order and add it to the book
    order = BidOrderCoveredWithShares(market, outcome, maker, tokens_offered, shares_desired)
    orders.add(order)

def make_token_covered_bid(market, outcome, tokens_offered, shares_desired):
    maker = msg.sender

    # escrow tokens
    market.getToken().transferFrom(maker, market, tokens_offered)

    # create the order and add it to the book
    order = BidOrderCoveredWithTokens(market, outcome, maker, tokens_offered, shares_desired)
    orders.add(order)

def take_share_covered_bid_with_shares(order)
    maker = order.maker
    taker = msg.sender

    # destroy complete sets
    market.getShare(order.outcome).burn(taker, order.shares_desired)
    for outcome in range(0, market.getNumOutcomes()):
        if outcome == order.outcome:
            continue
        market.getShare(outcome).burn(market, order.shares_desired)

    # divide up the proceeds of the sale
    taker_portion = order.tokens_offered
    maker_portion = order.shares_desired - taker_portion
    market.getToken().transferFrom(market, maker, maker_portion)
    market.getToken().transferFrom(market, taker, taker_portion)

    orders.remove(order)

def take_share_covered_bid_with_tokens(order):
    order.maker
    taker = msg.sender

    # send shares from escrow to taker and tokens from taker to maker
    for outcome in range(0, market.getNumOutcomes()):
        if outcome == order.outcome:
            continue
        market.getShare(outcome).transferFrom(market, taker, order.shares_desired)
    market.getToken().transferFrom(taker, maker, order.tokens_offered)

    orders.remove(order)

def take_token_covered_bid_with_shares(order):
    order.maker
    taker = msg.sender

    # send tokens from escrow to taker and shares from taker to maker
    market.getShare(order.outcome).transferFrom(taker, maker, order.shares_desired)
    market.getToken().transferFrom(market, taker, order.tokens_offered)

    orders.remove(order)

def take_token_covered_bid_with_tokens(order):
    order.maker
    taker = msg.sender

    # taker funds the rest required to create the complete sets
    tokens_required_to_cover = order.shares_desired - order.tokens_offered
    market.getToken().transferFrom(taker, market, tokens_required_to_cover)

    # destribute the shares to appropriate parties
    market.getShare(order.outcome).mint(maker, order.shares_desired)
    for outcome in range(0, market.getNumOutcomes()):
        if outcome == order.outcome:
            continue
        market.getShare(outcome).mint(taker, order.shares_desired)

    orders.remove(order)


# Range: [40,60]
# User wants to go long at 45
# ETH provided: 5 * 10^18
# Shares Received: 20 * 10^18
# Maker portion of complete set costs: 5/20
# Taker portion of complete set costs: 15/20
