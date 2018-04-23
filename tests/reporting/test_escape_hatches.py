from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, EtherDelta, TokenDelta, AssertLog
from reporting_utils import proceedToNextRound

def test_market_escape_hatch_all_fees(localFixture, controller, market, reputationToken):
    # We can't call the Market escape hatch when things are alright
    with raises(TransactionFailed):
        market.withdrawInEmergency()

    # Emergency Stop
    escapeHatchChangedLog = {
        "isOn": True,
    }
    with AssertLog(localFixture, "EscapeHatchChanged", escapeHatchChangedLog):
        assert controller.emergencyStop()

    # Now we can call the market escape hatch and get back all the fees paid in creation
    with EtherDelta(localFixture.chain.head_state.get_balance(market.address), market.getOwner(), localFixture.chain, "ETH balance was not given to the market owner"):
        with TokenDelta(reputationToken, reputationToken.balanceOf(market.address), market.getOwner(), "REP balance was not given to the market owner"):
            assert market.withdrawInEmergency()

    escapeHatchChangedLog = {
        "isOn": False,
    }
    with AssertLog(localFixture, "EscapeHatchChanged", escapeHatchChangedLog):
        assert controller.release()

def test_market_escape_hatch_partial_fees(localFixture, market, reputationToken, constants, controller):
    reputationToken.transfer(tester.a1, 1 * 10**6 * 10**18)

    proceedToNextRound(localFixture, market, contributor = tester.k1)

    # Emergency Stop
    assert controller.emergencyStop()

    # We will only get back the validity bond since our REP bond and first reporter bond were forfeit already
    with EtherDelta(constants.DEFAULT_VALIDITY_BOND(), market.getOwner(), localFixture.chain, "Remaining ETH balance was not given to the market owner"):
        with TokenDelta(reputationToken, 0, market.getOwner(), "REP balance was somehow given to the market owner"):
            assert market.withdrawInEmergency()

def test_participation_token_escape_hatch(localFixture, universe, reputationToken, cash, controller):
    feeWindow = localFixture.applySignature("FeeWindow", universe.getCurrentFeeWindow())

    # Now we'll purchase some participation tokens
    amount = 100
    feeWindow.buy(amount)

    # We can't call the escape hatch on a participation token until the system has been stopped
    with raises(TransactionFailed):
        feeWindow.withdrawInEmergency()

    # Emergency Stop
    assert controller.emergencyStop()

    # We can redeem any participation tokens purchased
    with TokenDelta(reputationToken, amount, tester.a0, "REP was not given back"):
        assert feeWindow.withdrawInEmergency()

def test_reporting_participant_escape_hatch(localFixture, controller, reputationToken, market, constants, cash):
    # Initial Reporting
    proceedToNextRound(localFixture, market)
    # Crowdsourcer 1
    proceedToNextRound(localFixture, market)
    # Crowdsourcer 2
    proceedToNextRound(localFixture, market)

    initialReporter = localFixture.applySignature("InitialReporter", market.getReportingParticipant(0))
    crowdsourcer1 = localFixture.applySignature("DisputeCrowdsourcer", market.getReportingParticipant(1))
    crowdsourcer2 = localFixture.applySignature("DisputeCrowdsourcer", market.getReportingParticipant(2))

    # We cannot call the escape hatches yet
    with raises(TransactionFailed):
        initialReporter.withdrawInEmergency()

    with raises(TransactionFailed):
        crowdsourcer1.withdrawInEmergency()

    with raises(TransactionFailed):
        crowdsourcer2.withdrawInEmergency()

    # Emergency Stop
    assert controller.emergencyStop()

    # We can now call the escape hatch
    with TokenDelta(reputationToken, reputationToken.balanceOf(initialReporter.address), tester.a0, "REP was not given back"):
        assert initialReporter.withdrawInEmergency()

    with TokenDelta(reputationToken, reputationToken.balanceOf(crowdsourcer1.address), tester.a0, "REP was not given back"):
        assert crowdsourcer1.withdrawInEmergency()

    with TokenDelta(reputationToken, reputationToken.balanceOf(crowdsourcer2.address), tester.a0, "REP was not given back"):
        assert crowdsourcer2.withdrawInEmergency()


@fixture(scope="module")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    fixture.contracts['universe'] = ABIContract(fixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)
    fixture.contracts['market'] = ABIContract(fixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)
    fixture.contracts['cash'] = ABIContract(fixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)
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
def constants(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['Constants']
