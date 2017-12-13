from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, EtherDelta, TokenDelta

def test_market_escape_hatch_all_fees(localFixture, controller, market, reputationToken):
    # We can't call the Market escape hatch when things are alright
    with raises(TransactionFailed):
        market.withdrawInEmergency()

    # Emergency Stop
    assert controller.emergencyStop()

    # Now we can call the market escape hatch and get back all the fees paid in creation
    with EtherDelta(localFixture.chain.head_state.get_balance(market.address), market.getOwner(), localFixture.chain, "ETH balance was not given to the market owner"):
        with TokenDelta(reputationToken, reputationToken.balanceOf(market.address), market.getOwner(), "REP balance was not given to the market owner"):
            assert market.withdrawInEmergency()

def test_market_escape_hatch_partial_fees(localFixture, market, reputationToken, feeWindow, constants, controller):
    # We'll skip to Limited reporting and make a report
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    stakeToken = localFixture.getOrCreateStakeToken(market, [0, market.getNumTicks()], False)
    MarketEtherDelta = constants.DEFAULT_VALIDITY_BOND() - localFixture.chain.head_state.get_balance(market.address)
    with EtherDelta(MarketEtherDelta, market.address, localFixture.chain, "First reporter gas fee was not given to first reporter"):
        with TokenDelta(reputationToken, -reputationToken.balanceOf(market.address), market.address, "REP balance was not given to the first reporter"):
            stakeToken.buy(0, sender=tester.k1)

    # Emergency Stop
    assert controller.emergencyStop()

    # We will only get back the validity bond since our REP bond and first reporter bond were forfeit already
    with EtherDelta(constants.DEFAULT_VALIDITY_BOND(), market.getOwner(), localFixture.chain, "Remaining ETH balance was not given to the market owner"):
        with TokenDelta(reputationToken, 0, market.getOwner(), "REP balance was somehow given to the market owner"):
            assert market.withdrawInEmergency()

def test_stake_token_escape_hatch(localFixture, market, feeWindow, reputationToken, cash, controller):
    # We'll skip to Limited reporting
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    # We'll give some testers some REP
    for testAccount in [tester.a1, tester.a2, tester.a3, tester.a4]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    # Now we'll make various reports
    stakeToken1 = localFixture.getOrCreateStakeToken(market, [0, market.getNumTicks()], False)
    stakeToken1.buy(0, sender=tester.k1)
    stake = reputationToken.balanceOf(stakeToken1.address)

    stakeToken2 = localFixture.getOrCreateStakeToken(market, [1, market.getNumTicks()-1], False)
    stakeToken2.buy(stake, sender=tester.k2)

    stakeToken3 = localFixture.getOrCreateStakeToken(market, [2, market.getNumTicks()-2], False)
    stakeToken3.buy(stake, sender=tester.k3)

    stakeToken4 = localFixture.getOrCreateStakeToken(market, [3, market.getNumTicks()-3], False)
    stakeToken4.buy(stake, sender=tester.k4)

    # We can't call the escape hatch on a stake token until the system has been stopped
    with raises(TransactionFailed):
        stakeToken1.withdrawInEmergency(sender=tester.k1)

    # Emergency Stop
    assert controller.emergencyStop()

    fees = cash.balanceOf(feeWindow.address) / 4
    stakeTokens = [stakeToken1, stakeToken2, stakeToken3, stakeToken4]

    # We can redeem any tokens purchased
    for i in range(1,4):
        with TokenDelta(reputationToken, stake, localFixture.testerAddress[i], "REP was not given back to Stake token holder"):
            assert stakeTokens[i-1].withdrawInEmergency(sender=localFixture.testerKey[i])

def test_dispute_bond_token_escape_hatch(localFixture, feeWindow, controller, reputationToken, market, constants, cash):
    # We'll skip to Designated reporting and make a report
    localFixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)

    stakeToken = localFixture.getOrCreateStakeToken(market, [0, market.getNumTicks()], False)
    designatedStake = constants.DEFAULT_DESIGNATED_REPORT_STAKE()
    assert stakeToken.buy(designatedStake)

    assert market.getReportingState() == constants.DESIGNATED_DISPUTE()

    reputationToken.transfer(tester.a1, 1 * 10**6 * 10**18)

    # Now we'll put up a dispute bond on the report
    assert market.disputeDesignatedReport([1, market.getNumTicks()-1], 1, False, sender=tester.k1)
    disputeBond = localFixture.applySignature("DisputeBond", market.getDesignatedReporterDisputeBond())

    # We cannot call the escape hatch on the dispute bond until the system is stopped
    with raises(TransactionFailed):
        disputeBond.withdrawInEmergency(sender=tester.k1)

    # Emergency Stop
    assert controller.emergencyStop()

    bondAmount = constants.DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()

    # We will get back the REP used to purchase the BOND
    with TokenDelta(reputationToken, bondAmount, tester.a1, "REP balance was somehow given to the market owner"):
        assert disputeBond.withdrawInEmergency(sender=tester.k1)

def test_participation_token_escape_hatch(localFixture, feeWindow, controller, reputationToken, market, constants, cash, categoricalMarket, scalarMarket):
    # We'll do a designated report on each market
    localFixture.contracts["Time"].setTimestamp(market.getEndTime() + 1)

    stakeToken = localFixture.getOrCreateStakeToken(market, [0, market.getNumTicks()], False)
    designatedStake = constants.DEFAULT_DESIGNATED_REPORT_STAKE()
    assert stakeToken.buy(designatedStake)

    categoricalStakeToken = localFixture.getOrCreateStakeToken(categoricalMarket, [0, 0, categoricalMarket.getNumTicks()], False)
    assert categoricalStakeToken.buy(designatedStake)

    scalarStakeToken = localFixture.getOrCreateStakeToken(scalarMarket, [0, scalarMarket.getNumTicks()], False)
    assert scalarStakeToken.buy(designatedStake)

    # Skip past the dispute phase and finalize the markets
    localFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    # We'll give some testers some REP
    for testAccount in [tester.a1, tester.a2, tester.a3, tester.a4]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    # Now we'll purchase some participation tokens
    feeWindow = localFixture.applySignature("FeeWindow", feeWindow.getFeeWindow())

    # We'll purchase stake in this amount to make the math clean
    stake = constants.DEFAULT_DESIGNATED_REPORT_STAKE()

    feeWindow.buy(stake, sender=tester.k1)
    feeWindow.buy(stake, sender=tester.k2)
    feeWindow.buy(stake, sender=tester.k3)
    feeWindow.buy(stake, sender=tester.k4)

    # We can't call the escape hatch on an participation token until the system has been stopped
    with raises(TransactionFailed):
        feeWindow.withdrawInEmergency(sender=tester.k1)

    # Emergency Stop
    assert controller.emergencyStop()

    fees = cash.balanceOf(feeWindow.address) / 7

    # We can redeem any tokens purchased
    for i in range(1,4):
        with TokenDelta(reputationToken, stake, localFixture.testerAddress[i], "REP was not given back to Stake token holder"):
            assert feeWindow.withdrawInEmergency(sender=localFixture.testerKey[i])

@fixture(scope="module")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    fixture.contracts['universe'] = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    fixture.contracts['market'] = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    fixture.contracts['cash'] = ABIContract(fixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
    fixture.contracts['categoricalMarket'] = ABIContract(fixture.chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)
    fixture.contracts['scalarMarket'] = ABIContract(fixture.chain, kitchenSinkSnapshot['scalarMarket'].translator, kitchenSinkSnapshot['scalarMarket'].address)
    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def controller(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['Controller']

@fixture
def universe(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['universe']

@fixture
def market(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['market']

@fixture
def cash(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['cash']

@fixture
def reputationToken(localFixture, kitchenSinkSnapshot, universe):
    return localFixture.applySignature("ReputationToken", universe.getReputationToken())

@fixture
def feeWindow(localFixture, kitchenSinkSnapshot, market):
    return localFixture.applySignature("FeeWindow", market.getFeeWindow())

@fixture
def constants(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['Constants']

@fixture
def categoricalMarket(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['categoricalMarket']

@fixture
def scalarMarket(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['scalarMarket']
