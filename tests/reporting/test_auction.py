from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed, ABIContract
from pytest import fixture, raises
from utils import TokenDelta, EtherDelta, AssertLog
from reporting_utils import generateFees

def test_bootstrap(localFixture, universe, reputationToken, auction, time, cash):
    # Lets confirm the auction is in the dormant state initially and also in bootstrap mode
    assert auction.getRoundType() == 0
    assert auction.bootstrapMode()
    assert not auction.isActive()

    # If we move time forward to the next auction start time we can see that the auction is now active.
    startTime = auction.getAuctionStartTime()
    assert time.setTimestamp(startTime)
    assert auction.getRoundType() == 2
    assert auction.bootstrapMode()
    assert auction.isActive()

    # We can get the price of ETH in REP
    assert auction.getRepSalePriceInAttoEth() == auction.initialRepSalePrice()

    # However since we're in bootstrap mode we cannot yet sell REP for ETH.
    with raises(TransactionFailed):
        auction.getEthSalePriceInAttoRep()

    # If we move time forward but stay in the auction the sale price of the REP will drop accordingly. We'll move forward an hour and confirm the price is 1/24th less
    repSalePrice = auction.initialRepSalePrice() * 23 / 24
    assert time.incrementTimestamp(60 * 60)
    assert auction.getRepSalePriceInAttoEth() == repSalePrice

    # Before we do any trading lets confirm the contract balances are as expected
    repAuctionToken = localFixture.applySignature("AuctionToken", auction.repAuctionToken())
    assert auction.initialAttoRepBalance() == reputationToken.balanceOf(repAuctionToken.address)
    assert auction.initialAttoRepBalance() == 11 * 10 ** 6 * 10 ** 18 / 400
    assert localFixture.chain.head_state.get_balance(auction.address) == 0

    # We can purchase some of the REP now. We'll send some extra ETH to confirm it just gets returned too
    repAmount = 10 ** 18
    cost = repAmount * repSalePrice / 10 ** 18
    with TokenDelta(cash, cost, auction.address, "ETH was not transfered to auction correctly"):
        with TokenDelta(repAuctionToken, cost, tester.a0, "REP auction token was not transferred to the user correctly"):
            assert auction.tradeEthForRep(repAmount, value=cost + 20)

    # Lets purchase the remaining REP in the auction
    repAmount = auction.getCurrentAttoRepBalance()
    cost = repAmount * repSalePrice / 10 ** 18
    with TokenDelta(cash, cost, auction.address, "ETH was not transfered to auction correctly"):
        with TokenDelta(repAuctionToken, cost, tester.a0, "REP auction token was not transferred to the user correctly"):
            assert auction.tradeEthForRep(repAmount, value=cost)

    # If we try to purchase any more the transaction will fail
    with raises(TransactionFailed):
        auction.tradeEthForRep(repAmount, value=cost)

    # Lets end this auction then move time to the next auction
    endTime = auction.getAuctionEndTime()
    assert time.setTimestamp(endTime + 1)

    assert auction.getRoundType() == 3
    assert auction.bootstrapMode()
    assert not auction.isActive()

    # Now we can redeem the tokens we received for the amount of REP we purchased
    expectedREP = reputationToken.balanceOf(repAuctionToken.address)
    with TokenDelta(reputationToken, expectedREP, tester.a0, "REP was not distributed correctly from auction token redemption"):
        repAuctionToken.redeem()

    startTime = auction.getAuctionStartTime()
    assert time.setTimestamp(startTime)

    # We can see that the ETH and REP auctions are active
    assert auction.getRoundType() == 6
    assert auction.isActive()

    assert auction.getRepSalePriceInAttoEth() == auction.initialRepSalePrice()
    assert auction.getEthSalePriceInAttoRep() == auction.initialEthSalePrice()

    assert not auction.bootstrapMode()

    ethAuctionToken = localFixture.applySignature("AuctionToken", auction.ethAuctionToken())
    ethSalePrice = auction.initialEthSalePrice()
    ethAmount = 10 ** 18
    cost = ethAmount * ethSalePrice / 10 ** 18
    with TokenDelta(ethAuctionToken, cost, tester.a0, "ETH auction token was not transferred to the user correctly"):
        with TokenDelta(reputationToken, cost, auction.address, "REP was not transferred to the auction correctly"):
            assert auction.tradeRepForEth(ethAmount)

    endTime = auction.getAuctionEndTime()
    assert time.setTimestamp(endTime + 1)

    # We can redeem the eth auction tokens for ETH. Since the auction ended with no other bids we get all the ETH
    with EtherDelta(cash.balanceOf(ethAuctionToken.address), tester.a0, localFixture.chain, "ETH redemption from eth auction token did not work correctly"):
        assert ethAuctionToken.redeem()

def test_reporting_fee_from_auction(localFixture, universe, auction, reputationToken, time, cash):
    # We'll quickly do the bootstrap auction and seed it with some ETH
    startTime = auction.getAuctionStartTime()
    assert time.setTimestamp(startTime)

    # Buy 5000 REP
    repSalePrice = auction.getRepSalePriceInAttoEth()
    repAuctionToken = localFixture.applySignature("AuctionToken", auction.repAuctionToken())
    repAmount = 5000 * 10 ** 18
    cost = repAmount * repSalePrice / 10 ** 18
    with TokenDelta(cash, cost, auction.address, "ETH was not transfered to auction correctly"):
        with TokenDelta(repAuctionToken, cost, tester.a0, "REP was not transferred to the user correctly"):
            assert auction.tradeEthForRep(repAmount, value=cost)

    # Now we'll go to the first real auction, which will be a reported auction, meaning the result affects the reported REP price
    endTime = auction.getAuctionEndTime()
    assert time.setTimestamp(endTime + 1)

    # Now we can redeem the tokens we received for the amount of REP we purchased
    expectedREP = reputationToken.balanceOf(repAuctionToken.address)
    with TokenDelta(reputationToken, expectedREP, tester.a0, "REP was not distributed correctly from auction token redemption"):
        repAuctionToken.redeem()

    startTime = auction.getAuctionStartTime()
    assert time.setTimestamp(startTime)

    # Initially the REP price of the auction will simply be what was provided as the constant initialized value
    assert auction.getRepPriceInAttoEth() == auction.manualRepPriceInAttoEth()
    repSalePrice = auction.getRepSalePriceInAttoEth()
    repAuctionToken = localFixture.applySignature("AuctionToken", auction.repAuctionToken())
    ethAuctionToken = localFixture.applySignature("AuctionToken", auction.ethAuctionToken())

    # Purchasing REP or ETH will update the current auctions derived price, though until the auction ends it will be very innacurate so we dont bother checking here. We'll purchase 1/4 of the available supply of each at the initial price
    repAmount = auction.getCurrentAttoRepBalance() / 4
    cost = repAmount * repSalePrice / 10 ** 18
    assert auction.tradeEthForRep(repAmount, value=cost)

    ethSalePrice = auction.getEthSalePriceInAttoRep()
    ethAmount = auction.getCurrentAttoEthBalance() / 4
    cost = ethAmount * ethSalePrice / 10 ** 18
    assert auction.tradeRepForEth(ethAmount)

    # We'll let some time pass and buy the rest of the REP and ETH and the halfpoint prices
    assert time.incrementTimestamp(12 * 60 * 60)

    newRepSalePrice = auction.getRepSalePriceInAttoEth()
    repAmount = auction.getCurrentAttoRepBalance()
    cost = repAmount * newRepSalePrice / 10 ** 18
    assert auction.tradeEthForRep(repAmount, value=cost)

    # Now we'll purchase 2 ETH
    newEthSalePrice = auction.getEthSalePriceInAttoRep()
    ethAmount = auction.getCurrentAttoEthBalance()
    cost = ethAmount * newEthSalePrice / 10 ** 18
    assert auction.tradeRepForEth(ethAmount)

    # We can observe that the recorded lower bound weighs this purchase more since more ETH was purchased
    lowerBoundRepPrice = auction.initialAttoEthBalance() * 10**18 / ethAuctionToken.maxSupply()
    upperBoundRepPrice = repAuctionToken.maxSupply() * 10**18 / auction.initialAttoRepBalance()
    derivedRepPrice = (lowerBoundRepPrice + upperBoundRepPrice) / 2
    assert auction.getDerivedRepPriceInAttoEth() == derivedRepPrice

    # Lets turn on auction price reporting and move time so that this auction is considered over
    assert localFixture.contracts["Controller"].toggleFeedSource(True)
    assert time.setTimestamp(auction.getAuctionEndTime() + 1)

    # We can see now that the auction will use the derived rep price when we request the price of rep for reporting fee purposes
    assert auction.getRepPriceInAttoEth() == derivedRepPrice

    # If we move time forward to the next auction we can confirm the price is still the derived price
    assert time.setTimestamp(auction.getAuctionStartTime())
    assert auction.getRepPriceInAttoEth() == derivedRepPrice

    # Lets purchase REP and ETH in this auction and confirm that it does not change the reported rep price, but is recorded for use internally to set auction pricing
    repSalePrice = auction.getRepSalePriceInAttoEth()

    # Note that the repSalePrice now starts at 4 x the previous auctions derived price
    assert auction.initialRepSalePrice() == 4 * derivedRepPrice

    repAmount = auction.getCurrentAttoRepBalance()
    cost = repAmount * repSalePrice / 10 ** 18
    assert auction.tradeEthForRep(repAmount, value=cost)

    # Now we'll purchase 1 ETH
    ethSalePrice = auction.getEthSalePriceInAttoRep()

    # Note that the ethSalePrice is now 4 x the previous auctions derived price in terms of ETH
    assert auction.initialEthSalePrice() == 4 * 10**36 / derivedRepPrice

    ethAmount = auction.getCurrentAttoEthBalance()
    cost = ethAmount * ethSalePrice / 10 ** 18
    assert auction.tradeRepForEth(ethAmount)

    # And as before the recorded REP price is the mean of the two bounds
    repAuctionToken = localFixture.applySignature("AuctionToken", auction.repAuctionToken())
    ethAuctionToken = localFixture.applySignature("AuctionToken", auction.ethAuctionToken())
    lowerBoundRepPrice = auction.initialAttoEthBalance() * 10**18 / ethAuctionToken.maxSupply()
    upperBoundRepPrice = repAuctionToken.maxSupply() * 10**18 / auction.initialAttoRepBalance()
    newDerivedRepPrice = (lowerBoundRepPrice + upperBoundRepPrice) / 2
    assert auction.getDerivedRepPriceInAttoEth() == newDerivedRepPrice

    # Now lets go to the dormant state and confirm that the reported rep price is still the previous recorded auctions derived REP price
    assert time.setTimestamp(auction.getAuctionEndTime() + 1)
    assert auction.getRepPriceInAttoEth() == derivedRepPrice

    # In the next auction we will see the newly derived REP price used as the basis for auction pricing but NOT used as the reported rep price for fees
    assert time.setTimestamp(auction.getAuctionStartTime())
    assert auction.initializeNewAuction()
    assert auction.getRepPriceInAttoEth() == derivedRepPrice
    assert auction.lastRepPrice() == newDerivedRepPrice
    assert auction.initialRepSalePrice() == 4 * newDerivedRepPrice
    assert auction.initialEthSalePrice() == 4 * 10**36 / newDerivedRepPrice

def test_buyback_from_reporting_fees(localFixture, universe, auction, reputationToken, time, market, cash):
    # We'll quickly do the bootstrap auction and seed it with some ETH
    startTime = auction.getAuctionStartTime()
    assert time.setTimestamp(startTime)

    # Buy 5000 REP
    repSalePrice = auction.getRepSalePriceInAttoEth()
    repAmount = 5000 * 10 ** 18
    cost = repAmount * repSalePrice / 10 ** 18
    assert auction.tradeEthForRep(repAmount, value=cost)

    # Now we'll go to the first real auction
    endTime = auction.getAuctionEndTime()
    assert time.setTimestamp(endTime + 1)

    startTime = auction.getAuctionStartTime()
    assert time.setTimestamp(startTime)

    # Generate some fees
    generateFees(localFixture, universe, market)
    feesGenerated = auction.feeBalance()

    # Now we'll sell some REP and we can see that the fees that were collected were used and that the REP provided was burned
    ethSalePrice = auction.getEthSalePriceInAttoRep()
    ethAmount = feesGenerated / 2
    cost = ethAmount * ethSalePrice / 10 ** 18
    totalRepSupply = reputationToken.totalSupply()
    assert auction.tradeRepForEth(ethAmount)

    assert totalRepSupply - reputationToken.totalSupply() == cost
    assert auction.feeBalance() == feesGenerated / 2

    # If we now sell some REP again but do so by selling more than could be covered by remaining fees only a proportional amount of REP is actually burned
    ethAmount = feesGenerated
    cost = ethAmount * ethSalePrice / 10 ** 18
    totalRepSupply = reputationToken.totalSupply()
    assert auction.tradeRepForEth(ethAmount)

    assert totalRepSupply - reputationToken.totalSupply() == cost / 2
    assert auction.feeBalance() == 0

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    universe = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)

    # Distribute REP
    reputationToken = fixture.applySignature('ReputationToken', universe.getReputationToken())
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def universe(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)

@fixture
def time(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts["Time"]
