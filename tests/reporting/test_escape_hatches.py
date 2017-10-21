from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, mark, raises
from utils import longTo32Bytes, captureFilteredLogs, ETHDelta, TokenDelta

def test_market_escape_hatch_all_fees(localFixture, controller, market, reputationToken, utils):
    # We can't call the Market escape hatch when things are alright
    with raises(TransactionFailed):
        market.withdrawInEmergency()
    
    # Emergency Stop
    assert controller.emergencyStop()

    # Now we can call the market escape hatch and get back all the fees paid in creation
    with ETHDelta(utils.getETHBalance(market.address), market.getOwner(), utils, "ETH balance was not given to the market owner"):
        with TokenDelta(reputationToken, reputationToken.balanceOf(market.address), market.getOwner(), "REP balance was not given to the market owner"):
            assert market.withdrawInEmergency()

def test_market_escape_hatch_partial_fees(localFixture, market, reputationToken, utils, reportingWindow, constants, controller):
    # We'll skip to Limited reporting and make a report
    localFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1

    stakeToken = localFixture.getStakeToken(market, [0, market.getNumTicks()], False)
    ethDelta = constants.DEFAULT_VALIDITY_BOND() - utils.getETHBalance(market.address)
    with ETHDelta(ethDelta, market.address, utils, "First reporter gas fee was not given to first reporter"):
        with TokenDelta(reputationToken, -reputationToken.balanceOf(market.address), market.address, "REP balance was not given to the first reporter"):
            stakeToken.buy(0, sender=tester.k1)

    # Emergency Stop
    assert controller.emergencyStop()

    # We will only get back the validity bond since our REP bond and first reporter bond were forfeit already
    with ETHDelta(constants.DEFAULT_VALIDITY_BOND(), market.getOwner(), utils, "Remaining ETH balance was not given to the market owner"):
        with TokenDelta(reputationToken, 0, market.getOwner(), "REP balance was somehow given to the market owner"):
            assert market.withdrawInEmergency()

def test_stake_token_escape_hatch(localFixture, market, reportingWindow, reputationToken, cash, controller, utils):
    # We'll skip to Limited reporting
    localFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1

    # We'll give some testers some REP
    for testAccount in [tester.a1, tester.a2, tester.a3, tester.a4]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    # Now we'll make various reports
    stakeToken1 = localFixture.getStakeToken(market, [0, market.getNumTicks()], False)
    stakeToken1.buy(0, sender=tester.k1)
    stake = reputationToken.balanceOf(stakeToken1.address)

    stakeToken2 = localFixture.getStakeToken(market, [1, market.getNumTicks()-1], False)
    stakeToken2.buy(stake, sender=tester.k2)

    stakeToken3 = localFixture.getStakeToken(market, [2, market.getNumTicks()-2], False)
    stakeToken3.buy(stake, sender=tester.k3)

    stakeToken4 = localFixture.getStakeToken(market, [3, market.getNumTicks()-3], False)
    stakeToken4.buy(stake, sender=tester.k4)

    # We can't call the escape hatch on a stake token until the system has been stopped
    with raises(TransactionFailed):
        stakeToken1.withdrawInEmergency(sender=tester.k1)

    # Emergency Stop
    assert controller.emergencyStop()

    fees = cash.balanceOf(reportingWindow.address) / 4
    stakeTokens = [stakeToken1, stakeToken2, stakeToken3, stakeToken4]

    # We can redeem any tokens purchased and get back fees as though the token was the winning outcome
    for i in range(1,4):
        with ETHDelta(fees, localFixture.testerAddress[i], utils, "Fees were not correctly given during Stake Token escape hatch"):
            with TokenDelta(reputationToken, stake, localFixture.testerAddress[i], "REP was not given back to Stake token holder"):
                assert stakeTokens[i-1].withdrawInEmergency(sender=localFixture.testerKey[i])

def test_dispute_bond_token_escape_hatch(localFixture, reportingWindow, controller, reputationToken, market, utils, constants, cash):
    # We'll skip to Designated reporting and make a report
    localFixture.chain.head_state.timestamp = market.getEndTime() + 1

    stakeToken = localFixture.getStakeToken(market, [0, market.getNumTicks()], False)
    designatedStake = constants.DEFAULT_DESIGNATED_REPORT_STAKE()
    assert stakeToken.buy(designatedStake)

    assert market.getReportingState() == constants.DESIGNATED_DISPUTE()

    reputationToken.transfer(tester.a1, 1 * 10**6 * 10**18)

    # Now we'll put up a dispute bond on the report
    assert market.disputeDesignatedReport([1, market.getNumTicks()-1], 1, False, sender=tester.k1)
    disputeBond = localFixture.applySignature("DisputeBondToken", market.getDesignatedReporterDisputeBondToken())

    # We cannot call the escape hatch on the dispute bond until the system is stopped
    with raises(TransactionFailed):
        disputeBond.withdrawInEmergency(sender=tester.k1)

    # Emergency Stop
    assert controller.emergencyStop()

    bondAmount = constants.DESIGNATED_REPORTER_DISPUTE_BOND_AMOUNT()
    fees = cash.balanceOf(reportingWindow.address) * bondAmount / reportingWindow.getTotalStake()

    # We will get back the REP used to purchase the BOND as well as fees from the reporting window
    with ETHDelta(fees, tester.a1, utils, "Remaining ETH balance was not given to the market owner"):
        with TokenDelta(reputationToken, bondAmount, tester.a1, "REP balance was somehow given to the market owner"):
            assert disputeBond.withdrawInEmergency(sender=tester.k1)

def test_attendance_token_escape_hatch(localFixture, reportingWindow, controller, reputationToken, market, utils, constants, cash, categoricalMarket, scalarMarket):
    # We'll do a designated report on each market
    localFixture.chain.head_state.timestamp = market.getEndTime() + 1

    stakeToken = localFixture.getStakeToken(market, [0, market.getNumTicks()], False)
    designatedStake = constants.DEFAULT_DESIGNATED_REPORT_STAKE()
    assert stakeToken.buy(designatedStake)

    categoricalStakeToken = localFixture.getStakeToken(categoricalMarket, [0, 0, categoricalMarket.getNumTicks()], False)
    assert categoricalStakeToken.buy(designatedStake)

    scalarStakeToken = localFixture.getStakeToken(scalarMarket, [0, scalarMarket.getNumTicks()], False)
    assert scalarStakeToken.buy(designatedStake)

    # Skip past the dispute phase and finalize the markets
    localFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1
    assert market.tryFinalize()
    assert categoricalMarket.tryFinalize()
    assert scalarMarket.tryFinalize()

    # We'll give some testers some REP
    for testAccount in [tester.a1, tester.a2, tester.a3, tester.a4]:
        reputationToken.transfer(testAccount, 1 * 10**6 * 10**18)

    # Now we'll purchase some attendance tokens
    attendanceToken = localFixture.applySignature("ReportingAttendanceToken", reportingWindow.getReportingAttendanceToken())

    # We'll purchase stake in this amount to make the math clean
    stake = constants.DEFAULT_DESIGNATED_REPORT_STAKE()

    attendanceToken.buy(stake, sender=tester.k1)
    attendanceToken.buy(stake, sender=tester.k2)
    attendanceToken.buy(stake, sender=tester.k3)
    attendanceToken.buy(stake, sender=tester.k4)

    # We can't call the escape hatch on an attendance token until the system has been stopped
    with raises(TransactionFailed):
        attendanceToken.withdrawInEmergency(sender=tester.k1)

    # Emergency Stop
    assert controller.emergencyStop()

    fees = cash.balanceOf(reportingWindow.address) / 7

    # We can redeem any tokens purchased and get back fees as normal
    for i in range(1,4):
        with ETHDelta(fees, localFixture.testerAddress[i], utils, "Fees were not correctly given during Stake Token escape hatch"):
            with TokenDelta(reputationToken, stake, localFixture.testerAddress[i], "REP was not given back to Stake token holder"):
                assert attendanceToken.withdrawInEmergency(sender=localFixture.testerKey[i])

@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
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
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)

@fixture
def market(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)

@fixture
def cash(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)

@fixture
def reputationToken(localFixture, kitchenSinkSnapshot, universe):
    return localFixture.applySignature("ReputationToken", universe.getReputationToken())

@fixture
def reportingWindow(localFixture, kitchenSinkSnapshot, market):
    return localFixture.applySignature("ReportingWindow", market.getReportingWindow())

@fixture
def utils(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['Utils']

@fixture
def constants(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['Constants']

@fixture
def categoricalMarket(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)

@fixture
def scalarMarket(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['scalarMarket'].translator, kitchenSinkSnapshot['scalarMarket'].address)
