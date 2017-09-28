class BidOrderCoveredWithTokens:
    def __init__(market, outcome, creator, tokens_offered, shares_desired):
        self.market = market
        self.outcome = outcome
        self.creator = creator
        self.tokens_offered = tokens_offered
        self.shares_desired = shares_desired

class BidOrderCoveredWithShares:
    def __init__(market, outcome, creator, tokens_offered, shares_desired):
        self.market = market
        self.outcome = outcome
        self.creator = creator
        self.tokens_offered = tokens_offered
        self.shares_desired = shares_desired

def create_share_covered_bid(market, outcome, tokens_offered, shares_desired):
    creator = msg.sender

    # escrow shares
    for outcome in range(0, market.getNumOutcomes()):
        if outcome == order.outcome:
            continue
        market.getShare(outcome).transferFrom(creator, market, shares_desired)

    # create the order and add it to the book
    order = BidOrderCoveredWithShares(market, outcome, creator, tokens_offered, shares_desired)
    orders.add(order)

def create_token_covered_bid(market, outcome, tokens_offered, shares_desired):
    creator = msg.sender

    # escrow tokens
    market.getToken().transferFrom(creator, market, tokens_offered)

    # create the order and add it to the book
    order = BidOrderCoveredWithTokens(market, outcome, creator, tokens_offered, shares_desired)
    orders.add(order)

def fill_share_covered_bid_with_shares(order)
    creator = order.creator
    filler = msg.sender

    # destroy complete sets
    market.getShare(order.outcome).burn(filler, order.shares_desired)
    for outcome in range(0, market.getNumOutcomes()):
        if outcome == order.outcome:
            continue
        market.getShare(outcome).burn(market, order.shares_desired)

    # divide up the proceeds of the sale
    filler_portion = order.tokens_offered
    creator_portion = order.shares_desired - filler_portion
    market.getToken().transferFrom(market, creator, creator_portion)
    market.getToken().transferFrom(market, filler, filler_portion)

    orders.remove(order)

def fill_share_covered_bid_with_tokens(order):
    order.creator
    filler = msg.sender

    # send shares from escrow to filler and tokens from filler to creator
    for outcome in range(0, market.getNumOutcomes()):
        if outcome == order.outcome:
            continue
        market.getShare(outcome).transferFrom(market, filler, order.shares_desired)
    market.getToken().transferFrom(filler, creator, order.tokens_offered)

    orders.remove(order)

def fill_token_covered_bid_with_shares(order):
    order.creator
    filler = msg.sender

    # send tokens from escrow to filler and shares from filler to creator
    market.getShare(order.outcome).transferFrom(filler, creator, order.shares_desired)
    market.getToken().transferFrom(market, filler, order.tokens_offered)

    orders.remove(order)

def fill_token_covered_bid_with_tokens(order):
    order.creator
    filler = msg.sender

    # filler funds the rest required to create the complete sets
    tokens_required_to_cover = order.shares_desired - order.tokens_offered
    market.getToken().transferFrom(filler, market, tokens_required_to_cover)

    # destribute the shares to appropriate parties
    market.getShare(order.outcome).mint(creator, order.shares_desired)
    for outcome in range(0, market.getNumOutcomes()):
        if outcome == order.outcome:
            continue
        market.getShare(outcome).mint(filler, order.shares_desired)

    orders.remove(order)


# Range: [40,60]
# User wants to go long at 45
# ETH provided: 5 * 10^18
# Shares Received: 20 * 10^18
# Maker portion of complete set costs: 5/20
# Filler portion of complete set costs: 15/20
