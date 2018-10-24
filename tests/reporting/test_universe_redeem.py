from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import fixture, raises, mark
from utils import longToHexString, EtherDelta, TokenDelta, PrintGasUsed
from reporting_utils import proceedToNextRound, proceedToFork, finalizeFork

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

    # Fast forward time until the new dispute window is over and we can redeem
    disputeWindow = kitchenSinkFixture.applySignature("DisputeWindow", market.getDisputeWindow())
    kitchenSinkFixture.contracts["Time"].setTimestamp(disputeWindow.getEndTime() + 1)
    assert market.finalize()

    expectedRep = winningDisputeCrowdsourcer2.getStake() + winningDisputeCrowdsourcer1.getStake() + initialReporter.getStake()
    expectedRep = expectedRep + expectedRep * 2 / 5
    expectedRep -= 1 # Rounding error
    with TokenDelta(reputationToken, expectedRep, tester.a0, "Redeeming didn't refund REP"):
        with PrintGasUsed(kitchenSinkFixture, "Universe Redeem:", 0):
            assert universe.redeemStake([initialReporter.address, winningDisputeCrowdsourcer1.address, winningDisputeCrowdsourcer2.address])
