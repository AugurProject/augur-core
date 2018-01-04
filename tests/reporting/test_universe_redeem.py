from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises, mark
from utils import longToHexString, EtherDelta, TokenDelta, PrintGasUsed
from reporting_utils import generateFees, proceedToNextRound, proceedToFork, finalizeFork, getExpectedFees

def test_redeem_participation_tokens(kitchenSinkFixture, universe, market, cash):
    reputationToken = kitchenSinkFixture.applySignature("ReputationToken", universe.getReputationToken())

    # proceed to the next round and buy some more fee window tokens
    proceedToNextRound(kitchenSinkFixture, market, doGenerateFees = True)

    feeWindow = kitchenSinkFixture.applySignature('FeeWindow', market.getFeeWindow())

    # We'll make the window active then purchase some participation tokens
    kitchenSinkFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)
    feeWindowAmount = 100

    # Distribute REP
    for testAccount in [tester.a1, tester.a2, tester.a3]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    assert feeWindow.buy(feeWindowAmount, sender=tester.k1)
    assert feeWindow.buy(feeWindowAmount, sender=tester.k2)
    assert feeWindow.buy(feeWindowAmount, sender=tester.k3)

    # proceed to the next round and buy some more fee window tokens
    proceedToNextRound(kitchenSinkFixture, market, doGenerateFees = True)

    newFeeWindow = kitchenSinkFixture.applySignature('FeeWindow', market.getFeeWindow())

    assert newFeeWindow.buy(feeWindowAmount, sender=tester.k1)
    assert newFeeWindow.buy(feeWindowAmount, sender=tester.k2)
    assert newFeeWindow.buy(feeWindowAmount, sender=tester.k3)

    # Now end the window
    kitchenSinkFixture.contracts["Time"].setTimestamp(newFeeWindow.getEndTime() + 1)

    reporterFees = 1000 * market.getNumTicks() / universe.getOrCacheReportingFeeDivisor()
    totalStake = feeWindow.getTotalFeeStake() + newFeeWindow.getTotalFeeStake()
    assert cash.balanceOf(feeWindow.address) == reporterFees
    assert cash.balanceOf(newFeeWindow.address) == reporterFees

    expectedParticipationFees = reporterFees * feeWindowAmount * 2 / totalStake

    # Cashing out Participation tokens will awards fees proportional to the total winning stake in the window
    with TokenDelta(reputationToken, feeWindowAmount * 2, tester.a3, "Redeeming participation tokens didn't refund REP"):
        with TokenDelta(feeWindow, -feeWindowAmount, tester.a3, "Redeeming participation tokens didn't decrease participation token balance correctly"):
            with EtherDelta(expectedParticipationFees, tester.a3, kitchenSinkFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
                with PrintGasUsed(kitchenSinkFixture, "Universe Redeem:", 0):
                    assert universe.redeemStake([], [feeWindow.address, newFeeWindow.address], sender = tester.k3)

    with TokenDelta(reputationToken, feeWindowAmount * 2, tester.a1, "Redeeming participation tokens didn't refund REP"):
        with TokenDelta(feeWindow, -feeWindowAmount, tester.a1, "Redeeming participation tokens didn't decrease participation token balance correctly"):
            with EtherDelta(expectedParticipationFees, tester.a1, kitchenSinkFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
                assert universe.redeemStake([], [feeWindow.address, newFeeWindow.address], sender = tester.k1)

    with TokenDelta(reputationToken, feeWindowAmount * 2, tester.a2, "Redeeming participation tokens didn't refund REP"):
        with TokenDelta(feeWindow, -feeWindowAmount, tester.a2, "Redeeming participation tokens didn't decrease participation token balance correctly"):
            with EtherDelta(expectedParticipationFees, tester.a2, kitchenSinkFixture.chain, "Redeeming participation tokens didn't increase ETH correctly"):
                assert universe.redeemStake([], [feeWindow.address, newFeeWindow.address], sender = tester.k2)

def test_redeem_reporting_participants(kitchenSinkFixture, market, categoricalMarket, scalarMarket, universe, cash):
    reputationToken = kitchenSinkFixture.applySignature("ReputationToken", universe.getReputationToken())
    constants = kitchenSinkFixture.contracts["Constants"]

    # Initial Report
    proceedToNextRound(kitchenSinkFixture, market, doGenerateFees = True)
    # Initial Report Losing
    proceedToNextRound(kitchenSinkFixture, market, doGenerateFees = True)
    # Initial Report Winning
    proceedToNextRound(kitchenSinkFixture, market, doGenerateFees = True)
    # Initial Report Losing
    proceedToNextRound(kitchenSinkFixture, market, doGenerateFees = True)
    # Initial Report Winning
    proceedToNextRound(kitchenSinkFixture, market, doGenerateFees = True)

    # Get the winning reporting participants
    initialReporter = kitchenSinkFixture.applySignature('InitialReporter', market.getReportingParticipant(0))
    winningDisputeCrowdsourcer1 = kitchenSinkFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(2))
    winningDisputeCrowdsourcer2 = kitchenSinkFixture.applySignature('DisputeCrowdsourcer', market.getReportingParticipant(4))

    # Fast forward time until the new fee window is over and we can redeem
    feeWindow = kitchenSinkFixture.applySignature("FeeWindow", market.getFeeWindow())
    kitchenSinkFixture.contracts["Time"].setTimestamp(feeWindow.getEndTime() + 1)
    assert market.finalize()

    expectedFees = getExpectedFees(kitchenSinkFixture, cash, winningDisputeCrowdsourcer1, 4)
    expectedFees += getExpectedFees(kitchenSinkFixture, cash, winningDisputeCrowdsourcer2, 2)
    expectedFees += getExpectedFees(kitchenSinkFixture, cash, initialReporter, 5)
    expectedRep = long(winningDisputeCrowdsourcer2.getStake() + winningDisputeCrowdsourcer1.getStake())
    expectedRep = long(expectedRep + expectedRep / 2)
    expectedRep += long(initialReporter.getStake() + initialReporter.getStake() / 2)
    expectedGasBond = 2 * constants.GAS_TO_REPORT() * constants.DEFAULT_REPORTING_GAS_PRICE()
    with TokenDelta(reputationToken, expectedRep, tester.a0, "Redeeming didn't refund REP"):
        with PrintGasUsed(kitchenSinkFixture, "Universe Redeem:", 0):
            assert universe.redeemStake([initialReporter.address, winningDisputeCrowdsourcer1.address, winningDisputeCrowdsourcer2.address], [])

