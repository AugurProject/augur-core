#!/usr/bin/env python

# CONSIDER: We may want to add a helper method to the fixture in conftest.py since acquiring reputation is likely to be a pretty common operation.  It probably would be easiest to make it so`tester.k9` starts out with all of the REP in `__init__` of that fixture and then when someone needs REP, we can just transfer from them.

# CONSIDER: We may also want to move the bond-related constants to their own contract under tests/solidity_test_helpers if they will be used in other test files.

# CONSIDER: Break up test_dispute_bond_tokens() into more functions

from ethereum.tools import tester
from pytest import raises, fixture, mark, lazy_fixture
from utils import bytesToLong, bytesToHexString, fix

REP_TOTAL = 11 * 10**6 # Total number of REP tokens in existence
REP_DIVISOR = 10**18 # Amount by which a single REP token can be divided

AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT = 11 * 10**20
LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**21
ALL_REPORTERS_DISPUTE_BOND_AMOUNT = 11 * 10**22

MARKET_TYPE_CATEGORICAL = 0
MARKET_TYPE_SCALAR = 1

CATEGORICAL_OUTCOME_A = [3, 0, 0]
CATEGORICAL_OUTCOME_B = [0, 3, 0]
CATEGORICAL_OUTCOME_C = [0, 0, 3]

SCALAR_OUTCOME_A = [30*10**18, 10*10**18]
SCALAR_OUTCOME_B = [10*10**18, 30*10**18]
SCALAR_OUTCOME_C = [20*10**18, 20*10**18]

def printTestAccountBalances(reputationToken, showRepFractions):
    divisor = REP_DIVISOR
    if (showRepFractions):
        divisor = 1
    for accountNum in xrange(0, 10):
        print "a" + str(accountNum) + ": " + bytesToHexString(getattr(tester, 'a' + str(accountNum))) + " | " + str(reputationToken.balanceOf(getattr(tester, 'a' + str(accountNum))) / divisor)
    print ""

def printReportingTokenBalances(reputationToken, reportingTokenA, reportingTokenB, reportingTokenC, showRepFractions):
    divisor = REP_DIVISOR
    if (showRepFractions):
        divisor = 1
    print "----- REPORTING TOKEN BALANCES -----"
    print str(reputationToken.balanceOf(reportingTokenA.address) / divisor)
    print str(reputationToken.balanceOf(reportingTokenB.address) / divisor)
    print str(reputationToken.balanceOf(reportingTokenC.address) /divisor) + "\n"

def printDisputeBondTokenBalances(reputationToken, automatedReporterDisputeBondToken, limitedReportersDisputeBondToken, allReportersDisputeBondToken, showRepFractions):
    divisor = REP_DIVISOR
    if (showRepFractions):
        divisor = 1
    print "----- DISPUTE BOND TOKEN BALANCES -----"
    if (automatedReporterDisputeBondToken):
        print "automatedReporterDisputeBondToken balance: " + str(reputationToken.balanceOf(automatedReporterDisputeBondToken.address) / divisor)
    if (limitedReportersDisputeBondToken):
        print "limitedReportersDisputeBondToken balance: " + str(reputationToken.balanceOf(limitedReportersDisputeBondToken.address) / divisor)
    if (allReportersDisputeBondToken):
        print "allReportersDisputeBondToken balance: " + str(reputationToken.balanceOf(allReportersDisputeBondToken.address) / divisor)
    print ""

# Put 1 million REP tokens in tester.a0-tester.a8 and the remainder in tester.a9
def initializeTestAccountBalances(reputationToken):
    print "Initializing test account balances"
    originalAccountBalance = 1 * 10**6 * REP_DIVISOR
    numOfTesterAccounts = 10
    for accountNum in xrange(0, numOfTesterAccounts-1):
        reputationToken.transfer(getattr(tester, 'a' + str(accountNum)), originalAccountBalance)
    reputationToken.transfer(tester.a9, (REP_TOTAL * REP_DIVISOR) - ((numOfTesterAccounts-1) * originalAccountBalance))
    print ""

def buyRegistrationTokens(disputeStakes, registrationToken, reputationToken):
    print "Buying registration tokens"
    for row in disputeStakes:
        accountBalance = reputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
        registrationToken.register(sender=getattr(tester, 'k' + str(row[0])))
        assert registrationToken.balanceOf(getattr(tester, 'a' + str(row[0]))) == 1
        assert reputationToken.balanceOf(getattr(tester, 'a' + str(row[0]))) == accountBalance - (1 * REP_DIVISOR)
    print ""

def buyReportingTokens(marketType, disputeStakes, reputationToken, reportingTokenA, reportingTokenB, reportingTokenC):
    print "Buying reporting tokens"
    for row in disputeStakes:
        accountBalance = reputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
        if (marketType == MARKET_TYPE_CATEGORICAL):
            if (row[1] == CATEGORICAL_OUTCOME_A):
                reportingToken = reportingTokenA
            elif (row[1] == CATEGORICAL_OUTCOME_B):
                reportingToken = reportingTokenB
            elif (row[1] == CATEGORICAL_OUTCOME_C):
                reportingToken = reportingTokenC
        elif (marketType == MARKET_TYPE_SCALAR):
            if (row[1] == SCALAR_OUTCOME_A):
                reportingToken = reportingTokenA
            elif (row[1] == SCALAR_OUTCOME_B):
                reportingToken = reportingTokenB
            elif (row[1] == SCALAR_OUTCOME_C):
                reportingToken = reportingTokenC
        reportingToken.buy(row[2], sender=getattr(tester, 'k' + str(row[0])))
        assert reportingToken.balanceOf(getattr(tester, 'a' + str(row[0]))) == row[2]
        assert reputationToken.balanceOf(getattr(tester, 'a' + str(row[0]))) == accountBalance - row[2]
    print ""

def calculateTotalLosingDisputeBondTokens(automatedReporterDisputeBondToken, limitedReportersDisputeBondToken, tentativeWinningPayoutDistributionHash):
    totalLosingDisputeBondTokens = 0
    if (automatedReporterDisputeBondToken and automatedReporterDisputeBondToken.getDisputedPayoutDistributionHash() == tentativeWinningPayoutDistributionHash):
        totalLosingDisputeBondTokens += AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT
    if (limitedReportersDisputeBondToken and limitedReportersDisputeBondToken.getDisputedPayoutDistributionHash() == tentativeWinningPayoutDistributionHash):
        totalLosingDisputeBondTokens += LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT
    return totalLosingDisputeBondTokens

@mark.parametrize('marketType,automatedReporterAccountNum,automatedReporterOutcome,automatedReporterDisputerAccountNum,automatedReporterDisputeStakes,limitedReportersDisputerAccountNum,limitedReportersDisputeStakes,allReportersDisputerAccountNum,allReportersDisputeStakes,expectedAccountBalances', [
    # CONSIDER: Create test cases where:
    # - There is no automated reporting (just limited reporters & all reporters)
    # - There is a tie between 2 outcomes

    # ----- Start categorical market test cases -----
    # Test case where there is an automated reporter & no disputes
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, None, [], None, [], None, [], [[0, None, 1000000 * REP_DIVISOR], [1, None, 1000000 * REP_DIVISOR]]),

    # Test cases where automated reporter is disputed
    # No losing tokens; bond holder was incorrect (bond holder gets nothing back, correct token holders get bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[2, CATEGORICAL_OUTCOME_A, 105 * REP_DIVISOR]], None, [], None, [], [[0,  None, 1000000 * REP_DIVISOR], [1, None, 998900 * REP_DIVISOR], [2, None, 1001099 * REP_DIVISOR]]),
    # Some losing tokens; some winning tokens; bond holder was incorrect (bond holder gets nothing, winning token holders get bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 105 * REP_DIVISOR], [1, CATEGORICAL_OUTCOME_B, 100 * REP_DIVISOR], [2, CATEGORICAL_OUTCOME_C, 100 * REP_DIVISOR]], None, [], None, [], [[0, None, 1001299000000000000000000], [1, None, 998799000000000000000000], [2, None, 999899000000000000000000]]),
    # Small amount of losing tokens; some winning tokens; bond holder was correct (bond holder gets less than 2x, winning token holders get no bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 100 * REP_DIVISOR], [1, CATEGORICAL_OUTCOME_B, 105 * REP_DIVISOR], [2, CATEGORICAL_OUTCOME_C, 100 * REP_DIVISOR]], None, [], None, [], [[0, None, 999899000000000000000000], [1, None, 1000199000000000000000000], [2, None, 999899000000000000000000]]),
    # Large amount of losing tokens; some winning tokens; bond holder was correct (bond holder gets 2x, winning token holders get bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 2500 * REP_DIVISOR], [1, CATEGORICAL_OUTCOME_B, 1500 * REP_DIVISOR], [2, CATEGORICAL_OUTCOME_B, 1500 * REP_DIVISOR], [3, CATEGORICAL_OUTCOME_C, 1500 * REP_DIVISOR]], None, [], None, [], [[0, None, 997499000000000000000000], [1, None, 1002549000000000000000000], [2, None, 1001449000000000000000000], [3, None, 998499000000000000000000]]),
    # No losing tokens; bond holder was right (bond holder gets 1x back, winning tokens get no bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[1, CATEGORICAL_OUTCOME_B, 200 * REP_DIVISOR], [2, CATEGORICAL_OUTCOME_B, 100 * REP_DIVISOR]], None, [], None, [], [[0,  None, 1000000 * REP_DIVISOR], [1, None, 999999 * REP_DIVISOR], [2, None, 999999 * REP_DIVISOR]]),

    # Test cases where automated reporter & limited reporters are disputed
    # No losing tokens; bond holder was incorrect (bond holder gets nothing back, correct token holders get bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 105 * REP_DIVISOR]], 2, [[3, CATEGORICAL_OUTCOME_A, 150 * REP_DIVISOR]], None, [], [[0, None, 1004981352941176470588235], [1, None, 998900000000000000000000], [2, None, 989000000000000000000000], [3, None, 1007116647058823529411765]]),
    # Some losing tokens; some winning tokens; bond holders were incorrect (bond holders get nothing, winning token holders get bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 105 * REP_DIVISOR], [1, CATEGORICAL_OUTCOME_B, 100 * REP_DIVISOR], [2, CATEGORICAL_OUTCOME_C, 100 * REP_DIVISOR]], 2, [[3, CATEGORICAL_OUTCOME_A, 150 * REP_DIVISOR]], None, [], [[0, None, 1005063705882352941176470], [1, None, 998799000000000000000000], [2, None, 988899000000000000000000], [3, None, 1007234294117647058823530]]),
    # Small amount of losing tokens; some winning tokens; bond holders were correct (bond holders get less than 2x, winning token holders get no bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 105 * REP_DIVISOR], [1, CATEGORICAL_OUTCOME_B, 100 * REP_DIVISOR], [2, CATEGORICAL_OUTCOME_C, 100 * REP_DIVISOR]], 2, [[3, CATEGORICAL_OUTCOME_B, 150 * REP_DIVISOR]], None, [], [[0, None, 999894000000000000000000], [1, None, 1000204000000000000000000], [2, None, 999899000000000000000000], [3, None, 999999000000000000000000]]),
    # Large amount of losing tokens; some winning tokens; bond holders were correct (bond holders get 2x, winning token holders get bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 25000 * REP_DIVISOR], [1, CATEGORICAL_OUTCOME_B, 105 * REP_DIVISOR], [2, CATEGORICAL_OUTCOME_C, 100 * REP_DIVISOR]], 1, [[3, CATEGORICAL_OUTCOME_B, 25000 * REP_DIVISOR]], None, [], [[0, None, 974999000000000000000000], [1, None, 1012153371639115714001194], [2, None, 999899000000000000000000], [3, None, 1012944628360884285998806]]),
    # No losing tokens; first bond holder was right (first bond holder get 1x back, winning tokens get no bonus)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[2, CATEGORICAL_OUTCOME_B, 105 * REP_DIVISOR]], 0, [[3, CATEGORICAL_OUTCOME_B, 150 * REP_DIVISOR]], None, [], [[0, None, 989000000000000000000000], [1, None, 1000000000000000000000000], [2, None, 1004528411764705882352941], [3, None, 1006469588235294117647059]]),

    # Test cases where automated reporter, limited reporters, & all reporters are disputed.  (Users should always end up with roughly the same amount of REP they started with, since there is no REP redistribution in the event of a fork)
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 105 * REP_DIVISOR]], 2, [[3, CATEGORICAL_OUTCOME_A, 150 * REP_DIVISOR]], 1, [[0, CATEGORICAL_OUTCOME_A], [1, CATEGORICAL_OUTCOME_B], [2, CATEGORICAL_OUTCOME_B], [3, CATEGORICAL_OUTCOME_A], [4, CATEGORICAL_OUTCOME_A]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [0, CATEGORICAL_OUTCOME_A, 999999000000000000000000], [1, CATEGORICAL_OUTCOME_A, 0], [2, CATEGORICAL_OUTCOME_A, 0], [3, CATEGORICAL_OUTCOME_A, 999999000000000000000000], [4, CATEGORICAL_OUTCOME_A, 1000000000000000000000000], [0, CATEGORICAL_OUTCOME_B, 0], [1, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [2, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [3, CATEGORICAL_OUTCOME_B, 0], [4, CATEGORICAL_OUTCOME_B, 0], [0, CATEGORICAL_OUTCOME_C, 0], [1, CATEGORICAL_OUTCOME_C, 0], [2, CATEGORICAL_OUTCOME_C, 0], [3, CATEGORICAL_OUTCOME_C, 0], [4, CATEGORICAL_OUTCOME_C, 0]]),
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 105 * REP_DIVISOR], [1, CATEGORICAL_OUTCOME_B, 100 * REP_DIVISOR]], 2, [[3, CATEGORICAL_OUTCOME_A, 150 * REP_DIVISOR]], 4, [[0, CATEGORICAL_OUTCOME_A], [1, CATEGORICAL_OUTCOME_B], [2, CATEGORICAL_OUTCOME_B], [3, CATEGORICAL_OUTCOME_A], [4, CATEGORICAL_OUTCOME_B], [5, CATEGORICAL_OUTCOME_A], [6, CATEGORICAL_OUTCOME_A]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [5, None, 0], [6, None, 0], [0, CATEGORICAL_OUTCOME_A, 999999000000000000000000], [1, CATEGORICAL_OUTCOME_A, 0], [2, CATEGORICAL_OUTCOME_A, 0], [3, CATEGORICAL_OUTCOME_A, 999999000000000000000000], [4, CATEGORICAL_OUTCOME_A, 0], [5, CATEGORICAL_OUTCOME_A, 1000000000000000000000000], [6, CATEGORICAL_OUTCOME_A, 1000000000000000000000000], [0, CATEGORICAL_OUTCOME_B, 0], [1, CATEGORICAL_OUTCOME_B, 999999000000000000000000], [2, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [3, CATEGORICAL_OUTCOME_B, 0], [4, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [5, CATEGORICAL_OUTCOME_B, 0], [6, CATEGORICAL_OUTCOME_B, 0], [0, CATEGORICAL_OUTCOME_C, 0], [1, CATEGORICAL_OUTCOME_C, 0], [2, CATEGORICAL_OUTCOME_C, 0], [3, CATEGORICAL_OUTCOME_C, 0], [4, CATEGORICAL_OUTCOME_C, 0], [5, CATEGORICAL_OUTCOME_C, 0], [6, CATEGORICAL_OUTCOME_C, 0]]),
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 105 * REP_DIVISOR], [1, CATEGORICAL_OUTCOME_B, 100 * REP_DIVISOR], [2, CATEGORICAL_OUTCOME_C, 100 * REP_DIVISOR]], 2, [[3, CATEGORICAL_OUTCOME_B, 150 * REP_DIVISOR]], 4, [[0, CATEGORICAL_OUTCOME_A], [1, CATEGORICAL_OUTCOME_B], [2, CATEGORICAL_OUTCOME_C], [3, CATEGORICAL_OUTCOME_B], [4, CATEGORICAL_OUTCOME_A], [5, CATEGORICAL_OUTCOME_B], [6, CATEGORICAL_OUTCOME_B]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [5, None, 0], [6, None, 0], [0, CATEGORICAL_OUTCOME_A, 999999000000000000000000], [1, CATEGORICAL_OUTCOME_A, 0], [2, CATEGORICAL_OUTCOME_A, 0], [3, CATEGORICAL_OUTCOME_A, 0], [4, CATEGORICAL_OUTCOME_A, 1000000000000000000000000], [5, CATEGORICAL_OUTCOME_A, 0], [6, CATEGORICAL_OUTCOME_A, 0], [0, CATEGORICAL_OUTCOME_B, 0], [1, CATEGORICAL_OUTCOME_B, 999999000000000000000000], [2, CATEGORICAL_OUTCOME_B, 0], [3, CATEGORICAL_OUTCOME_B, 999999000000000000000000], [4, CATEGORICAL_OUTCOME_B, 0], [5, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [6, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [0, CATEGORICAL_OUTCOME_C, 0], [1, CATEGORICAL_OUTCOME_C, 0], [2, CATEGORICAL_OUTCOME_C, 999999000000000000000000], [3, CATEGORICAL_OUTCOME_C, 0], [4, CATEGORICAL_OUTCOME_C, 0], [5, CATEGORICAL_OUTCOME_C, 0], [6, CATEGORICAL_OUTCOME_C, 0]]),
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[0, CATEGORICAL_OUTCOME_A, 150000 * REP_DIVISOR], [1, CATEGORICAL_OUTCOME_B, 100000 * REP_DIVISOR]], 2, [[2, CATEGORICAL_OUTCOME_B, 200000 * REP_DIVISOR], [3, CATEGORICAL_OUTCOME_A, 100000 * REP_DIVISOR]], 4, [[0, CATEGORICAL_OUTCOME_A], [1, CATEGORICAL_OUTCOME_B], [2, CATEGORICAL_OUTCOME_B], [3, CATEGORICAL_OUTCOME_A], [4, CATEGORICAL_OUTCOME_B], [5, CATEGORICAL_OUTCOME_B], [6, CATEGORICAL_OUTCOME_B]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [5, None, 0], [6, None, 0], [0, CATEGORICAL_OUTCOME_A, 999999000000000000000000], [1, CATEGORICAL_OUTCOME_A, 0], [2, CATEGORICAL_OUTCOME_A, 0], [3, CATEGORICAL_OUTCOME_A, 999999000000000000000000], [4, CATEGORICAL_OUTCOME_A, 0], [5, CATEGORICAL_OUTCOME_A, 0], [6, CATEGORICAL_OUTCOME_A, 0], [0, CATEGORICAL_OUTCOME_B, 0], [1, CATEGORICAL_OUTCOME_B, 999999000000000000000000], [2, CATEGORICAL_OUTCOME_B, 999999000000000000000000], [3, CATEGORICAL_OUTCOME_B, 0], [4, CATEGORICAL_OUTCOME_B, 890000000000000000000000], [5, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [6, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [0, CATEGORICAL_OUTCOME_C, 0], [1, CATEGORICAL_OUTCOME_C, 0], [2, CATEGORICAL_OUTCOME_C, 0], [3, CATEGORICAL_OUTCOME_C, 0], [4, CATEGORICAL_OUTCOME_C, 0], [5, CATEGORICAL_OUTCOME_C, 0], [6, CATEGORICAL_OUTCOME_C, 0]]),
    (MARKET_TYPE_CATEGORICAL, 0, CATEGORICAL_OUTCOME_A, 1, [[2, CATEGORICAL_OUTCOME_B, 105 * REP_DIVISOR]], 0, [[3, CATEGORICAL_OUTCOME_B, 150 * REP_DIVISOR]], 4, [[0, CATEGORICAL_OUTCOME_A], [1, CATEGORICAL_OUTCOME_B], [2, CATEGORICAL_OUTCOME_B], [3, CATEGORICAL_OUTCOME_B], [4, CATEGORICAL_OUTCOME_A], [5, CATEGORICAL_OUTCOME_B], [6, CATEGORICAL_OUTCOME_B]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [5, None, 0], [6, None, 0], [0, CATEGORICAL_OUTCOME_A, 1000000000000000000000000], [1, CATEGORICAL_OUTCOME_A, 0], [2, CATEGORICAL_OUTCOME_A, 0], [3, CATEGORICAL_OUTCOME_A, 0], [4, CATEGORICAL_OUTCOME_A, 1000000000000000000000000], [5, CATEGORICAL_OUTCOME_A, 0], [6, CATEGORICAL_OUTCOME_A, 0], [0, CATEGORICAL_OUTCOME_B, 0], [1, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [2, CATEGORICAL_OUTCOME_B, 999999000000000000000000], [3, CATEGORICAL_OUTCOME_B, 999999000000000000000000], [4, CATEGORICAL_OUTCOME_B, 0], [5, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [6, CATEGORICAL_OUTCOME_B, 1000000000000000000000000], [0, CATEGORICAL_OUTCOME_C, 0], [1, CATEGORICAL_OUTCOME_C, 0], [2, CATEGORICAL_OUTCOME_C, 0], [3, CATEGORICAL_OUTCOME_C, 0], [4, CATEGORICAL_OUTCOME_C, 0], [5, CATEGORICAL_OUTCOME_C, 0], [6, CATEGORICAL_OUTCOME_C, 0]]),
    # ----- End categorical market test cases -----

    # ----- Start scalar market test cases -----
    # Test case where there is an automated reporter & no disputes
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, None, [], None, [], None, [], [[0, None, 1000000 * REP_DIVISOR], [1, None, 1000000 * REP_DIVISOR]]),

    # Test cases where automated reporter is disputed
    # No losing tokens; bond holder was incorrect (bond holder gets nothing back, correct token holders get bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[2, SCALAR_OUTCOME_A, 105 * REP_DIVISOR]], None, [], None, [], [[0,  None, 1000000 * REP_DIVISOR], [1, None, 998900 * REP_DIVISOR], [2, None, 1001099 * REP_DIVISOR]]),
    # Some losing tokens; some winning tokens; bond holder was incorrect (bond holder gets nothing, winning token holders get bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 105 * REP_DIVISOR], [1, SCALAR_OUTCOME_B, 100 * REP_DIVISOR], [2, SCALAR_OUTCOME_C, 100 * REP_DIVISOR]], None, [], None, [], [[0, None, 1001299000000000000000000], [1, None, 998799000000000000000000], [2, None, 999899000000000000000000]]),
    # Small amount of losing tokens; some winning tokens; bond holder was correct (bond holder gets less than 2x, winning token holders get no bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 100 * REP_DIVISOR], [1, SCALAR_OUTCOME_B, 105 * REP_DIVISOR], [2, SCALAR_OUTCOME_C, 100 * REP_DIVISOR]], None, [], None, [], [[0, None, 999899000000000000000000], [1, None, 1000199000000000000000000], [2, None, 999899000000000000000000]]),
    # Large amount of losing tokens; some winning tokens; bond holder was correct (bond holder gets 2x, winning token holders get bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 2500 * REP_DIVISOR], [1, SCALAR_OUTCOME_B, 1500 * REP_DIVISOR], [2, SCALAR_OUTCOME_B, 1500 * REP_DIVISOR], [3, SCALAR_OUTCOME_C, 1500 * REP_DIVISOR]], None, [], None, [], [[0, None, 997499000000000000000000], [1, None, 1002549000000000000000000], [2, None, 1001449000000000000000000], [3, None, 998499000000000000000000]]),
    # No losing tokens; bond holder was right (bond holder gets 1x back, winning tokens get no bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[1, SCALAR_OUTCOME_B, 200 * REP_DIVISOR], [2, SCALAR_OUTCOME_B, 100 * REP_DIVISOR]], None, [], None, [], [[0,  None, 1000000 * REP_DIVISOR], [1, None, 999999 * REP_DIVISOR], [2, None, 999999 * REP_DIVISOR]]),

    # Test cases where automated reporter & limited reporters are disputed
    # No losing tokens; bond holder was incorrect (bond holder gets nothing back, correct token holders get bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 105 * REP_DIVISOR]], 2, [[3, SCALAR_OUTCOME_A, 150 * REP_DIVISOR]], None, [], [[0, None, 1004981352941176470588235], [1, None, 998900000000000000000000], [2, None, 989000000000000000000000], [3, None, 1007116647058823529411765]]),
    # Some losing tokens; some winning tokens; bond holders were incorrect (bond holders get nothing, winning token holders get bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 105 * REP_DIVISOR], [1, SCALAR_OUTCOME_B, 100 * REP_DIVISOR], [2, SCALAR_OUTCOME_C, 100 * REP_DIVISOR]], 2, [[3, SCALAR_OUTCOME_A, 150 * REP_DIVISOR]], None, [], [[0, None, 1005063705882352941176470], [1, None, 998799000000000000000000], [2, None, 988899000000000000000000], [3, None, 1007234294117647058823530]]),
    # Small amount of losing tokens; some winning tokens; bond holders were correct (bond holders get less than 2x, winning token holders get no bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 105 * REP_DIVISOR], [1, SCALAR_OUTCOME_B, 100 * REP_DIVISOR], [2, SCALAR_OUTCOME_C, 100 * REP_DIVISOR]], 2, [[3, SCALAR_OUTCOME_B, 150 * REP_DIVISOR]], None, [], [[0, None, 999894000000000000000000], [1, None, 1000204000000000000000000], [2, None, 999899000000000000000000], [3, None, 999999000000000000000000]]),
    # Large amount of losing tokens; some winning tokens; bond holders were correct (bond holders get 2x, winning token holders get bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 25000 * REP_DIVISOR], [1, SCALAR_OUTCOME_B, 105 * REP_DIVISOR], [2, SCALAR_OUTCOME_C, 100 * REP_DIVISOR]], 1, [[3, SCALAR_OUTCOME_B, 25000 * REP_DIVISOR]], None, [], [[0, None, 974999000000000000000000], [1, None, 1012153371639115714001194], [2, None, 999899000000000000000000], [3, None, 1012944628360884285998806]]),
    # No losing tokens; first bond holder was right (first bond holder get 1x back, winning tokens get no bonus)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[2, SCALAR_OUTCOME_B, 105 * REP_DIVISOR]], 0, [[3, SCALAR_OUTCOME_B, 150 * REP_DIVISOR]], None, [], [[0, None, 989000000000000000000000], [1, None, 1000000000000000000000000], [2, None, 1004528411764705882352941], [3, None, 1006469588235294117647059]]),

    # Test cases where automated reporter, limited reporters, & all reporters are disputed.  (Users should always end up with roughly the same amount of REP they started with, since there is no REP redistribution in the event of a fork)
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 105 * REP_DIVISOR]], 2, [[3, SCALAR_OUTCOME_A, 150 * REP_DIVISOR]], 1, [[0, SCALAR_OUTCOME_A], [1, SCALAR_OUTCOME_B], [2, SCALAR_OUTCOME_B], [3, SCALAR_OUTCOME_A], [4, SCALAR_OUTCOME_A]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [0, SCALAR_OUTCOME_A, 999999000000000000000000], [1, SCALAR_OUTCOME_A, 0], [2, SCALAR_OUTCOME_A, 0], [3, SCALAR_OUTCOME_A, 999999000000000000000000], [4, SCALAR_OUTCOME_A, 1000000000000000000000000], [0, SCALAR_OUTCOME_B, 0], [1, SCALAR_OUTCOME_B, 1000000000000000000000000], [2, SCALAR_OUTCOME_B, 1000000000000000000000000], [3, SCALAR_OUTCOME_B, 0], [4, SCALAR_OUTCOME_B, 0], [0, SCALAR_OUTCOME_C, 0], [1, SCALAR_OUTCOME_C, 0], [2, SCALAR_OUTCOME_C, 0], [3, SCALAR_OUTCOME_C, 0], [4, SCALAR_OUTCOME_C, 0]]),
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 105 * REP_DIVISOR], [1, SCALAR_OUTCOME_B, 100 * REP_DIVISOR]], 2, [[3, SCALAR_OUTCOME_A, 150 * REP_DIVISOR]], 4, [[0, SCALAR_OUTCOME_A], [1, SCALAR_OUTCOME_B], [2, SCALAR_OUTCOME_B], [3, SCALAR_OUTCOME_A], [4, SCALAR_OUTCOME_B], [5, SCALAR_OUTCOME_A], [6, SCALAR_OUTCOME_A]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [5, None, 0], [6, None, 0], [0, SCALAR_OUTCOME_A, 999999000000000000000000], [1, SCALAR_OUTCOME_A, 0], [2, SCALAR_OUTCOME_A, 0], [3, SCALAR_OUTCOME_A, 999999000000000000000000], [4, SCALAR_OUTCOME_A, 0], [5, SCALAR_OUTCOME_A, 1000000000000000000000000], [6, SCALAR_OUTCOME_A, 1000000000000000000000000], [0, SCALAR_OUTCOME_B, 0], [1, SCALAR_OUTCOME_B, 999999000000000000000000], [2, SCALAR_OUTCOME_B, 1000000000000000000000000], [3, SCALAR_OUTCOME_B, 0], [4, SCALAR_OUTCOME_B, 1000000000000000000000000], [5, SCALAR_OUTCOME_B, 0], [6, SCALAR_OUTCOME_B, 0], [0, SCALAR_OUTCOME_C, 0], [1, SCALAR_OUTCOME_C, 0], [2, SCALAR_OUTCOME_C, 0], [3, SCALAR_OUTCOME_C, 0], [4, SCALAR_OUTCOME_C, 0], [5, SCALAR_OUTCOME_C, 0], [6, SCALAR_OUTCOME_C, 0]]),
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 105 * REP_DIVISOR], [1, SCALAR_OUTCOME_B, 100 * REP_DIVISOR], [2, SCALAR_OUTCOME_C, 100 * REP_DIVISOR]], 2, [[3, SCALAR_OUTCOME_B, 150 * REP_DIVISOR]], 4, [[0, SCALAR_OUTCOME_A], [1, SCALAR_OUTCOME_B], [2, SCALAR_OUTCOME_C], [3, SCALAR_OUTCOME_B], [4, SCALAR_OUTCOME_A], [5, SCALAR_OUTCOME_B], [6, SCALAR_OUTCOME_B]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [5, None, 0], [6, None, 0], [0, SCALAR_OUTCOME_A, 999999000000000000000000], [1, SCALAR_OUTCOME_A, 0], [2, SCALAR_OUTCOME_A, 0], [3, SCALAR_OUTCOME_A, 0], [4, SCALAR_OUTCOME_A, 1000000000000000000000000], [5, SCALAR_OUTCOME_A, 0], [6, SCALAR_OUTCOME_A, 0], [0, SCALAR_OUTCOME_B, 0], [1, SCALAR_OUTCOME_B, 999999000000000000000000], [2, SCALAR_OUTCOME_B, 0], [3, SCALAR_OUTCOME_B, 999999000000000000000000], [4, SCALAR_OUTCOME_B, 0], [5, SCALAR_OUTCOME_B, 1000000000000000000000000], [6, SCALAR_OUTCOME_B, 1000000000000000000000000], [0, SCALAR_OUTCOME_C, 0], [1, SCALAR_OUTCOME_C, 0], [2, SCALAR_OUTCOME_C, 999999000000000000000000], [3, SCALAR_OUTCOME_C, 0], [4, SCALAR_OUTCOME_C, 0], [5, SCALAR_OUTCOME_C, 0], [6, SCALAR_OUTCOME_C, 0]]),
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[0, SCALAR_OUTCOME_A, 150000 * REP_DIVISOR], [1, SCALAR_OUTCOME_B, 100000 * REP_DIVISOR]], 2, [[2, SCALAR_OUTCOME_B, 200000 * REP_DIVISOR], [3, SCALAR_OUTCOME_A, 100000 * REP_DIVISOR]], 4, [[0, SCALAR_OUTCOME_A], [1, SCALAR_OUTCOME_B], [2, SCALAR_OUTCOME_B], [3, SCALAR_OUTCOME_A], [4, SCALAR_OUTCOME_B], [5, SCALAR_OUTCOME_B], [6, SCALAR_OUTCOME_B]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [5, None, 0], [6, None, 0], [0, SCALAR_OUTCOME_A, 999999000000000000000000], [1, SCALAR_OUTCOME_A, 0], [2, SCALAR_OUTCOME_A, 0], [3, SCALAR_OUTCOME_A, 999999000000000000000000], [4, SCALAR_OUTCOME_A, 0], [5, SCALAR_OUTCOME_A, 0], [6, SCALAR_OUTCOME_A, 0], [0, SCALAR_OUTCOME_B, 0], [1, SCALAR_OUTCOME_B, 999999000000000000000000], [2, SCALAR_OUTCOME_B, 999999000000000000000000], [3, SCALAR_OUTCOME_B, 0], [4, SCALAR_OUTCOME_B, 890000000000000000000000], [5, SCALAR_OUTCOME_B, 1000000000000000000000000], [6, SCALAR_OUTCOME_B, 1000000000000000000000000], [0, SCALAR_OUTCOME_C, 0], [1, SCALAR_OUTCOME_C, 0], [2, SCALAR_OUTCOME_C, 0], [3, SCALAR_OUTCOME_C, 0], [4, SCALAR_OUTCOME_C, 0], [5, SCALAR_OUTCOME_C, 0], [6, SCALAR_OUTCOME_C, 0]]),
    (MARKET_TYPE_SCALAR, 0, SCALAR_OUTCOME_A, 1, [[2, SCALAR_OUTCOME_B, 105 * REP_DIVISOR]], 0, [[3, SCALAR_OUTCOME_B, 150 * REP_DIVISOR]], 4, [[0, SCALAR_OUTCOME_A], [1, SCALAR_OUTCOME_B], [2, SCALAR_OUTCOME_B], [3, SCALAR_OUTCOME_B], [4, SCALAR_OUTCOME_A], [5, SCALAR_OUTCOME_B], [6, SCALAR_OUTCOME_B]], [[0, None, 0], [1, None, 0], [2, None, 0], [3, None, 0], [4, None, 0], [5, None, 0], [6, None, 0], [0, SCALAR_OUTCOME_A, 1000000000000000000000000], [1, SCALAR_OUTCOME_A, 0], [2, SCALAR_OUTCOME_A, 0], [3, SCALAR_OUTCOME_A, 0], [4, SCALAR_OUTCOME_A, 1000000000000000000000000], [5, SCALAR_OUTCOME_A, 0], [6, SCALAR_OUTCOME_A, 0], [0, SCALAR_OUTCOME_B, 0], [1, SCALAR_OUTCOME_B, 1000000000000000000000000], [2, SCALAR_OUTCOME_B, 999999000000000000000000], [3, SCALAR_OUTCOME_B, 999999000000000000000000], [4, SCALAR_OUTCOME_B, 0], [5, SCALAR_OUTCOME_B, 1000000000000000000000000], [6, SCALAR_OUTCOME_B, 1000000000000000000000000], [0, SCALAR_OUTCOME_C, 0], [1, SCALAR_OUTCOME_C, 0], [2, SCALAR_OUTCOME_C, 0], [3, SCALAR_OUTCOME_C, 0], [4, SCALAR_OUTCOME_C, 0], [5, SCALAR_OUTCOME_C, 0], [6, SCALAR_OUTCOME_C, 0]]),
    # ----- End scalar market test cases -----
])
def test_dispute_bond_tokens(marketType, automatedReporterAccountNum, automatedReporterOutcome, automatedReporterDisputerAccountNum, automatedReporterDisputeStakes, limitedReportersDisputerAccountNum, limitedReportersDisputeStakes, allReportersDisputerAccountNum, allReportersDisputeStakes, expectedAccountBalances, contractsFixture):
    branch = contractsFixture.branch
    if (marketType == MARKET_TYPE_CATEGORICAL):
        market = contractsFixture.categoricalMarket
        OUTCOME_A = CATEGORICAL_OUTCOME_A
        OUTCOME_B = CATEGORICAL_OUTCOME_B
        OUTCOME_C = CATEGORICAL_OUTCOME_C
    elif (marketType == MARKET_TYPE_SCALAR):
        market = contractsFixture.scalarMarket
        OUTCOME_A = SCALAR_OUTCOME_A
        OUTCOME_B = SCALAR_OUTCOME_B
        OUTCOME_C = SCALAR_OUTCOME_C
    reportingTokenA = contractsFixture.getReportingToken(market, OUTCOME_A)
    reportingTokenB = contractsFixture.getReportingToken(market, OUTCOME_B)
    reportingTokenC = contractsFixture.getReportingToken(market, OUTCOME_C)
    reportingWindow = contractsFixture.applySignature('ReportingWindow', market.getReportingWindow())

    automatedReporterDisputeBondToken = None
    limitedReportersDisputeBondToken = None
    allReportersDisputeBondToken = None

    # Seed legacy REP contract with 11 million reputation tokens
    legacyRepContract = contractsFixture.contracts['LegacyRepContract']
    legacyRepContract.faucet(long(REP_TOTAL * REP_DIVISOR))

    # Get the reputation token for this branch and migrate legacy REP to it
    reputationToken = contractsFixture.applySignature('ReputationToken', branch.getReputationToken())
    legacyRepContract.approve(reputationToken.address, REP_TOTAL * REP_DIVISOR)
    reputationToken.migrateFromLegacyRepContract()

    initializeTestAccountBalances(reputationToken)

    # Fast forward to one second after the next reporting window
    contractsFixture.chain.head_state.timestamp = market.getEndTime() + 1

    # Perform automated report (if there is one)
    if (len(automatedReporterOutcome) > 0):
        market.automatedReport(automatedReporterOutcome, sender=getattr(tester, 'k' + str(automatedReporterAccountNum)))

        # If someone disputes the automated reporter outcome
        if (automatedReporterDisputerAccountNum != None):
            # Fast forward to one second after dispute start time
            contractsFixture.chain.head_state.timestamp = market.getAutomatedReportDueTimestamp() + 1

            print "a" + str(automatedReporterDisputerAccountNum) + " is disputing automated reporter outcome"

            # Dispute the automated reporter outcome
            disputerAccountBalance = reputationToken.balanceOf(getattr(tester, 'a' + str(automatedReporterDisputerAccountNum)))
            market.disputeAutomatedReport(sender=getattr(tester, 'k' + str(automatedReporterDisputerAccountNum)))
            automatedReporterDisputeBondToken = contractsFixture.applySignature('DisputeBondToken', market.getAutomatedReporterDisputeBondToken())
            assert automatedReporterDisputeBondToken.getMarket() == market.address

            # Ensure correct bond amount was sent to dispute bond token
            assert reputationToken.balanceOf(getattr(tester, 'a' + str(automatedReporterDisputerAccountNum))) == disputerAccountBalance - AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT
            assert reputationToken.balanceOf(automatedReporterDisputeBondToken.address) == AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT
            assert automatedReporterDisputeBondToken.getBondRemainingToBePaidOut() == AUTOMATED_REPORTER_DISPUTE_BOND_AMOUNT * 2

            # CONSIDER: Are these asserts required when disputing automated reporter
            # outcome like they are when disputing limited/all rerporters outcomes?
            # assert not reportingWindow.isContainerForMarket(market.address)
            # assert branch.isContainerForMarket(market.address)
            # reportingWindow = contractsFixture.applySignature('ReportingWindow', market.getReportingWindow())
            # assert reportingWindow.isContainerForMarket(market.address)

            # Buy registration tokens
            registrationToken = contractsFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())
            buyRegistrationTokens(automatedReporterDisputeStakes, registrationToken, reputationToken)

            # Fast forward to reporting start time
            contractsFixture.chain.head_state.timestamp = reportingWindow.getReportingStartTime() + 1

            # Have test accounts report on the outcome
            buyReportingTokens(marketType, automatedReporterDisputeStakes, reputationToken, reportingTokenA, reportingTokenB, reportingTokenC)

            # Fast forward to one second after dispute end time
            contractsFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    if (limitedReportersDisputerAccountNum != None):
        # Fast forward to one second after dispute start time
        contractsFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

        print "a" + str(automatedReporterDisputerAccountNum) + " is disputing limited reporters outcome"

        # Dispute the limited reporters result
        disputerAccountBalance = reputationToken.balanceOf(getattr(tester, 'a' + str(limitedReportersDisputerAccountNum)))
        market.disputeLimitedReporters(sender=getattr(tester, 'k' + str(limitedReportersDisputerAccountNum)))
        limitedReportersDisputeBondToken = contractsFixture.applySignature('DisputeBondToken', market.getLimitedReportersDisputeBondToken())
        assert limitedReportersDisputeBondToken.getMarket() == market.address

        # Ensure correct bond amount was sent to dispute bond token
        assert reputationToken.balanceOf(getattr(tester, 'a' + str(limitedReportersDisputerAccountNum))) == disputerAccountBalance - LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT
        assert reputationToken.balanceOf(limitedReportersDisputeBondToken.address) == LIMITED_REPORTERS_DISPUTE_BOND_AMOUNT

        assert not reportingWindow.isContainerForMarket(market.address)
        assert branch.isContainerForMarket(market.address)
        reportingWindow = contractsFixture.applySignature('ReportingWindow', market.getReportingWindow())
        assert reportingWindow.isContainerForMarket(market.address)

        # Buy registration tokens
        registrationToken = contractsFixture.applySignature('RegistrationToken', reportingWindow.getRegistrationToken())
        buyRegistrationTokens(limitedReportersDisputeStakes, registrationToken, reputationToken)

        # Fast forward to reporting start time
        contractsFixture.chain.head_state.timestamp = reportingWindow.getReportingStartTime() + 1

        # Have test accounts report on the outcome
        buyReportingTokens(marketType, limitedReportersDisputeStakes, reputationToken, reportingTokenA, reportingTokenB, reportingTokenC)

        # Fast forward to one second after dispute end time
        contractsFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    if (allReportersDisputerAccountNum != None):
        # Fast forward to one second after dispute start time
        contractsFixture.chain.head_state.timestamp = reportingWindow.getDisputeStartTime() + 1

        # Have test account dispute the limited reporting result
        print "a" + str(automatedReporterDisputerAccountNum) + " is disputing all reporters outcome (and forking)"

        # Dispute the all reporters result
        disputerAccountBalance = reputationToken.balanceOf(getattr(tester, 'a' + str(allReportersDisputerAccountNum)))
        market.disputeAllReporters(sender=getattr(tester, 'k' + str(allReportersDisputerAccountNum)))
        allReportersDisputeBondToken = contractsFixture.applySignature('DisputeBondToken', market.getAllReportersDisputeBondToken())
        assert allReportersDisputeBondToken.getMarket() == market.address

        # Ensure correct bond amount was sent to dispute bond token
        assert reputationToken.balanceOf(getattr(tester, 'a' + str(allReportersDisputerAccountNum))) == disputerAccountBalance - ALL_REPORTERS_DISPUTE_BOND_AMOUNT
        assert reputationToken.balanceOf(allReportersDisputeBondToken.address) == ALL_REPORTERS_DISPUTE_BOND_AMOUNT

        assert not reportingWindow.isContainerForMarket(market.address)
        assert branch.isContainerForMarket(market.address)
        reportingWindow = contractsFixture.applySignature('ReportingWindow', market.getReportingWindow())
        assert reportingWindow.isContainerForMarket(market.address)

        aBranch = contractsFixture.getOrCreateChildBranch(branch, market, OUTCOME_A)
        aBranchReputationToken = contractsFixture.applySignature('ReputationToken', aBranch.getReputationToken())
        assert aBranch.address != branch.address
        bBranch = contractsFixture.getOrCreateChildBranch(branch, market, OUTCOME_B)
        bBranchReputationToken = contractsFixture.applySignature('ReputationToken', bBranch.getReputationToken())
        assert bBranch.address != branch.address
        cBranch = contractsFixture.getOrCreateChildBranch(branch, market, OUTCOME_C)
        cBranchReputationToken = contractsFixture.applySignature('ReputationToken', cBranch.getReputationToken())
        assert bBranch.address != branch.address
        assert aBranch.address != bBranch.address
        assert aBranch.address != cBranch.address
        assert bBranch.address != cBranch.address

        # Participate in the fork by moving REP
        for row in allReportersDisputeStakes:
            if (row[1] == OUTCOME_A):
                destinationBranchReputationToken = aBranchReputationToken
            elif (row[1] == OUTCOME_B):
                destinationBranchReputationToken = bBranchReputationToken
            elif (row[1] == OUTCOME_C):
                destinationBranchReputationToken = cBranchReputationToken
            accountBalance = reputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
            reputationToken.migrateOut(destinationBranchReputationToken.address, getattr(tester, 'a' + str(row[0])), reputationToken.balanceOf(getattr(tester, 'a' + str(row[0]))), sender=getattr(tester, 'k' + str(row[0])))
            assert not reputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
            assert destinationBranchReputationToken.balanceOf(getattr(tester, 'a' + str(row[0]))) == accountBalance

        # Fast forward to one second after dispute end time
        contractsFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    if (automatedReporterDisputerAccountNum == None and limitedReportersDisputerAccountNum == None and allReportersDisputerAccountNum == None):
        contractsFixture.chain.head_state.timestamp = reportingWindow.getDisputeEndTime() + 1

    tentativeWinningReportingTokenAddress = market.getReportingTokenOrZeroByPayoutDistributionHash(market.getTentativeWinningPayoutDistributionHash())
    tentativeWinningReportingTokenBalance = reputationToken.balanceOf(tentativeWinningReportingTokenAddress)

    totalLosingDisputeBondTokens = calculateTotalLosingDisputeBondTokens(automatedReporterDisputeBondToken, limitedReportersDisputeBondToken, market.getTentativeWinningPayoutDistributionHash())

    # Finalize market (i.e., transfer losing dispute bond tokens to winning reporting token)
    print "\nFinalizing market\n"
    market.tryFinalize()
    assert market.getReportingState() == contractsFixture.constants.FINALIZED()
    if (allReportersDisputerAccountNum):
        print "Original branch test accounts"
        printTestAccountBalances(reputationToken, False)
        print "A branch test accounts"
        printTestAccountBalances(aBranchReputationToken, False)
        print "B branch test accounts"
        printTestAccountBalances(bBranchReputationToken, False)
        print "C branch test accounts"
        printTestAccountBalances(cBranchReputationToken, False)
    else:
        printTestAccountBalances(reputationToken, False)

    printReportingTokenBalances(reputationToken, reportingTokenA, reportingTokenB, reportingTokenC, False)
    printDisputeBondTokenBalances(reputationToken, automatedReporterDisputeBondToken, limitedReportersDisputeBondToken, allReportersDisputeBondToken, False)

    # Verify that losing dispute bonds went to the winning reporting token
    if (allReportersDisputerAccountNum == None):
        winningReportingToken = contractsFixture.applySignature('ReportingToken', market.getFinalWinningReportingToken())
        winningReportingTokenBalance = reputationToken.balanceOf(winningReportingToken.address)

        if (automatedReporterDisputeBondToken and automatedReporterDisputeBondToken.getDisputedPayoutDistributionHash() == market.getTentativeWinningPayoutDistributionHash()):
            assert reputationToken.balanceOf(automatedReporterDisputeBondToken.address) == 0
        if (limitedReportersDisputeBondToken and limitedReportersDisputeBondToken.getDisputedPayoutDistributionHash() == market.getTentativeWinningPayoutDistributionHash()):
            assert reputationToken.balanceOf(limitedReportersDisputeBondToken.address) == 0
        assert winningReportingTokenBalance == tentativeWinningReportingTokenBalance + totalLosingDisputeBondTokens

        print "-------------------------------------------------------"
        print "Winning reporting token balance before market finalization: " + str(tentativeWinningReportingTokenBalance / REP_DIVISOR)
        print "Total losing dispute bond tokens: " + str(totalLosingDisputeBondTokens / REP_DIVISOR)
        print "Winning reporting token balance after market finalization: " + str(winningReportingTokenBalance / REP_DIVISOR) + "\n"

    if (automatedReporterDisputerAccountNum != None or limitedReportersDisputerAccountNum != None):
        # Migrate losing reporting tokens (if no fork occurred)
        if (allReportersDisputerAccountNum == None):
            winningReportingTokenBalanceBeforeMigration = reputationToken.balanceOf(winningReportingToken.address)

            # Calculate total losing reporting tokens
            totalLosingReportingTokens = 0
            if (market.getFinalPayoutDistributionHash() == reportingTokenA.getPayoutDistributionHash()):
                totalLosingReportingTokens += reputationToken.balanceOf(reportingTokenB.address)
                totalLosingReportingTokens += reputationToken.balanceOf(reportingTokenC.address)
            elif (market.getFinalPayoutDistributionHash() == reportingTokenB.getPayoutDistributionHash()):
                totalLosingReportingTokens += reputationToken.balanceOf(reportingTokenA.address)
                totalLosingReportingTokens += reputationToken.balanceOf(reportingTokenC.address)
            elif (market.getFinalPayoutDistributionHash() == reportingTokenC.getPayoutDistributionHash()):
                totalLosingReportingTokens += reputationToken.balanceOf(reportingTokenA.address)
                totalLosingReportingTokens += reputationToken.balanceOf(reportingTokenB.address)

            amountSentToAutomatedReporterDisputeBondToken = 0
            amountSentToLimitedReportersDisputeBondToken = 0
            amountSentToAllReportersDisputeBondToken = 0
            # Calculate how many losing tokens should be sent to each winning dispute bond token
            if (automatedReporterDisputeBondToken and automatedReporterDisputeBondToken.getDisputedPayoutDistributionHash() != market.getFinalPayoutDistributionHash()):
                automatedReporterDisputeBondTokenBalanceBeforeMigration = reputationToken.balanceOf(automatedReporterDisputeBondToken.address)
                amountNeeded = automatedReporterDisputeBondToken.getBondRemainingToBePaidOut() - automatedReporterDisputeBondTokenBalanceBeforeMigration
                amountSentToAutomatedReporterDisputeBondToken = min(amountNeeded, totalLosingReportingTokens)
            if (limitedReportersDisputeBondToken and limitedReportersDisputeBondToken.getDisputedPayoutDistributionHash() != market.getFinalPayoutDistributionHash()):
                limitedReportersDisputeBondTokenBalanceBeforeMigration = reputationToken.balanceOf(limitedReportersDisputeBondToken.address)
                amountNeeded = limitedReportersDisputeBondToken.getBondRemainingToBePaidOut() - limitedReportersDisputeBondTokenBalanceBeforeMigration
                amountSentToLimitedReportersDisputeBondToken = min(amountNeeded, totalLosingReportingTokens - amountSentToAutomatedReporterDisputeBondToken)
            if (allReportersDisputeBondToken and allReportersDisputeBondToken.getDisputedPayoutDistributionHash() != market.getFinalPayoutDistributionHash()):
                allReportersDisputeBondTokenBalanceBeforeMigration = reputationToken.balanceOf(allReportersDisputeBondToken.address)
                amountNeeded = allReportersDisputeBondToken.getBondRemainingToBePaidOut() - allReportersDisputeBondTokenBalanceBeforeMigration
                amountSentToAllReportersDisputeBondToken = min(amountNeeded, totalLosingReportingTokens - amountSentToLimitedReportersDisputeBondToken - amountSentToAutomatedReporterDisputeBondToken)
            # Calculate remaining losing tokens to be sent to winning reporting token
            amountSentToWinningReportingToken = totalLosingReportingTokens - amountSentToAllReportersDisputeBondToken - amountSentToLimitedReportersDisputeBondToken - amountSentToAutomatedReporterDisputeBondToken

            print "Migrating losing reporting tokens"
            if (market.getFinalPayoutDistributionHash() == reportingTokenA.getPayoutDistributionHash()):
                reportingTokenB.migrateLosingTokens()
                assert reputationToken.balanceOf(reportingTokenB.address) == 0
                reportingTokenC.migrateLosingTokens()
                assert reputationToken.balanceOf(reportingTokenC.address) == 0
            elif (market.getFinalPayoutDistributionHash() == reportingTokenB.getPayoutDistributionHash()):
                reportingTokenA.migrateLosingTokens()
                assert reputationToken.balanceOf(reportingTokenA.address) == 0
                reportingTokenC.migrateLosingTokens()
                assert reputationToken.balanceOf(reportingTokenC.address) == 0
            elif (market.getFinalPayoutDistributionHash() == reportingTokenC.getPayoutDistributionHash()):
                reportingTokenA.migrateLosingTokens()
                assert reputationToken.balanceOf(reportingTokenA.address) == 0
                reportingTokenB.migrateLosingTokens()
                assert reputationToken.balanceOf(reportingTokenB.address) == 0

            if (automatedReporterDisputeBondToken and automatedReporterDisputeBondToken.getDisputedPayoutDistributionHash() != market.getFinalPayoutDistributionHash()):
                assert reputationToken.balanceOf(automatedReporterDisputeBondToken.address) == automatedReporterDisputeBondTokenBalanceBeforeMigration + amountSentToAutomatedReporterDisputeBondToken
            if (limitedReportersDisputeBondToken and limitedReportersDisputeBondToken.getDisputedPayoutDistributionHash() != market.getFinalPayoutDistributionHash()):
                assert reputationToken.balanceOf(limitedReportersDisputeBondToken.address) == limitedReportersDisputeBondTokenBalanceBeforeMigration + amountSentToLimitedReportersDisputeBondToken
            if (allReportersDisputeBondToken and allReportersDisputeBondToken.getDisputedPayoutDistributionHash() != market.getFinalPayoutDistributionHash()):
                assert reputationToken.balanceOf(allReportersDisputeBondToken.address) == allReportersDisputeBondTokenBalanceBeforeMigration + amountSentToAllReportersDisputeBondToken
            assert reputationToken.balanceOf(winningReportingToken.address) == winningReportingTokenBalanceBeforeMigration + amountSentToWinningReportingToken

            winningReportingTokenBalance = reputationToken.balanceOf(winningReportingToken.address)

            print "Total losing reporting tokens: " + str(totalLosingReportingTokens)
            print "Amount sent to automated reporter dispute bond token: " + str(amountSentToAutomatedReporterDisputeBondToken)
            print "Amount sent to limited reporters dispute bond token: " + str(amountSentToLimitedReportersDisputeBondToken)
            print "Amount sent to all reporters dispute bond token: " + str(amountSentToAllReportersDisputeBondToken)
            print "Amount sent to winning reporting token: : " + str(amountSentToWinningReportingToken)
            print "Winning reporting token balance before migration: " + str(winningReportingTokenBalanceBeforeMigration / REP_DIVISOR)
            print "Winning reporting token balance after migration: " + str(winningReportingTokenBalance / REP_DIVISOR) + "\n"
            printDisputeBondTokenBalances(reputationToken, automatedReporterDisputeBondToken, limitedReportersDisputeBondToken, allReportersDisputeBondToken, False)

        # Redeem winning/forked reporting tokens
        # TODO: Break this section into separate function
        if (allReportersDisputerAccountNum):
            # Reputation staked on a particular outcome must be redeemed only on the branch for that outcome.
            # Reputation held in a dispute bond against a particular outcome must be redeemed on a branch other than the disputed outcome.
            migrators = {}
            for row in allReportersDisputeStakes:
                migrators[row[0]] = row[1]

            print 'Migrators array:'
            print str(migrators) + "\n"

            for row in automatedReporterDisputeStakes:
                destinationReputationToken = None
                if (migrators[row[0]] and migrators[row[0]] == OUTCOME_A):
                    print "Redeeming forked reporting tokens for tester.a" + str(row[0]) + " on branch A"
                    reportingToken = reportingTokenA
                    destinationReputationToken = aBranchReputationToken
                if (migrators[row[0]] and migrators[row[0]] == OUTCOME_B):
                    print "Redeeming forked reporting tokens for tester.a" + str(row[0]) + " on branch B"
                    reportingToken = reportingTokenB
                    destinationReputationToken = bBranchReputationToken
                if (migrators[row[0]] and migrators[row[0]] == OUTCOME_C):
                    print "Redeeming forked reporting tokens for tester.a" + str(row[0]) + " on branch C"
                    reportingToken = reportingTokenC
                    destinationReputationToken = cBranchReputationToken
                if (destinationReputationToken):
                    accountBalanceBeforeRedemption = destinationReputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
                    expectedWinnings = reputationToken.balanceOf(reportingToken.address) * row[2] / reportingToken.totalSupply()
                    print "accountBalanceBeforeRedemption: " + str(accountBalanceBeforeRedemption)
                    print "expectedWinnings: " + str(expectedWinnings)
                    reportingToken.redeemForkedTokens(sender=getattr(tester, 'k' + str(row[0])))
                    assert destinationReputationToken.balanceOf(getattr(tester, 'a' + str(row[0]))) == accountBalanceBeforeRedemption + expectedWinnings
                    print "Transferred " + str(expectedWinnings) + " to account a" + str(row[0]) + "\n"

            for row in limitedReportersDisputeStakes:
                destinationReputationToken = None
                print row
                if (migrators[row[0]] and migrators[row[0]] == OUTCOME_A):
                    print "Redeeming forked reporting tokens for tester.a" + str(row[0]) + " on branch A"
                    reportingToken = reportingTokenA
                    destinationReputationToken = aBranchReputationToken
                if (migrators[row[0]] and migrators[row[0]] == OUTCOME_B):
                    print "Redeeming forked reporting tokens for tester.a" + str(row[0]) + " on branch B"
                    reportingToken = reportingTokenB
                    destinationReputationToken = bBranchReputationToken
                if (migrators[row[0]] and migrators[row[0]] == OUTCOME_C):
                    print "Redeeming forked reporting tokens for tester.a" + str(row[0]) + " on branch C"
                    reportingToken = reportingTokenC
                    destinationReputationToken = cBranchReputationToken
                if (destinationReputationToken):
                    accountBalanceBeforeRedemption = destinationReputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
                    expectedWinnings = reputationToken.balanceOf(reportingToken.address) * row[2] / reportingToken.totalSupply()
                    print "accountBalanceBeforeRedemption: " + str(accountBalanceBeforeRedemption)
                    print "expectedWinnings: " + str(expectedWinnings)
                    reportingToken.redeemForkedTokens(sender=getattr(tester, 'k' + str(row[0])))
                    assert destinationReputationToken.balanceOf(getattr(tester, 'a' + str(row[0]))) == accountBalanceBeforeRedemption + expectedWinnings
                    print "Transferred " + str(expectedWinnings) + " to account a" + str(row[0]) + "\n"

            print "Original branch test accounts"
            printTestAccountBalances(reputationToken, False)
            print "A branch test accounts"
            printTestAccountBalances(aBranchReputationToken, False)
            print "B branch test accounts"
            printTestAccountBalances(bBranchReputationToken, False)
            print "C branch test accounts"
            printTestAccountBalances(cBranchReputationToken, False)
        else:
            # Calculate total reporting tokens staked on winning outcome
            totalStakedOnWinningOutcome = 0
            winningOutcomeStakes = {}
            for row in automatedReporterDisputeStakes:
                if (market.derivePayoutDistributionHash(row[1]) == winningReportingToken.getPayoutDistributionHash()):
                    totalStakedOnWinningOutcome += row[2]
                    if (row[0] in winningOutcomeStakes):
                        winningOutcomeStakes[row[0]] += row[2]
                    else:
                        winningOutcomeStakes.update({row[0]: row[2]})
            for row in limitedReportersDisputeStakes:
                if (market.derivePayoutDistributionHash(row[1]) == winningReportingToken.getPayoutDistributionHash()):
                    totalStakedOnWinningOutcome += row[2]
                    if (row[0] in winningOutcomeStakes):
                        winningOutcomeStakes[row[0]] += row[2]
                    else:
                        winningOutcomeStakes.update({row[0]: row[2]})

            print "Total reporting tokens staked on winning outcome: " + str(totalStakedOnWinningOutcome)
            print winningOutcomeStakes
            print ""

            print "Redeeming winning reporting tokens"
            for key in winningOutcomeStakes:
                accountBalanceBeforeRedemption = reputationToken.balanceOf(getattr(tester, 'a' + str(key)))
                expectedWinnings = reputationToken.balanceOf(winningReportingToken.address) * winningOutcomeStakes[key] / winningReportingToken.totalSupply()
                winningReportingToken.redeemWinningTokens(sender=getattr(tester, 'k' + str(key)))
                assert reputationToken.balanceOf(getattr(tester, 'a' + str(key))) == accountBalanceBeforeRedemption + expectedWinnings
                print "Transferred " + str(expectedWinnings) + " to account a" + str(key)
            printTestAccountBalances(reputationToken, False)

        contractsFixture.chain.head_state.timestamp = reportingWindow.getEndTime() + 1

        # Have correct dispute bond holders withdraw from dispute token
        # TODO: Break this section out into separate function
        if (allReportersDisputerAccountNum == None):
            if (automatedReporterDisputeBondToken and market.getFinalPayoutDistributionHash() != automatedReporterDisputeBondToken.getDisputedPayoutDistributionHash()):
                print "Withdrawing automated reporter dispute bond tokens"
                accountBalanceBeforeWithdrawl = reputationToken.balanceOf(automatedReporterDisputeBondToken.getBondHolder())
                disputeBondTokenBalanceBeforeWithdrawl = reputationToken.balanceOf(automatedReporterDisputeBondToken.address)
                automatedReporterDisputeBondToken.withdraw(sender=getattr(tester, 'k' + str(automatedReporterDisputerAccountNum)))
                assert reputationToken.balanceOf(automatedReporterDisputeBondToken.address) == 0
                assert reputationToken.balanceOf(automatedReporterDisputeBondToken.getBondHolder()) == accountBalanceBeforeWithdrawl + disputeBondTokenBalanceBeforeWithdrawl
            if (limitedReportersDisputeBondToken and market.getFinalPayoutDistributionHash() != limitedReportersDisputeBondToken.getDisputedPayoutDistributionHash()):
                print "Withdrawing limited reporters dispute bond tokens"
                accountBalanceBeforeWithdrawl = reputationToken.balanceOf(limitedReportersDisputeBondToken.getBondHolder())
                disputeBondTokenBalanceBeforeWithdrawl = reputationToken.balanceOf(limitedReportersDisputeBondToken.address)
                limitedReportersDisputeBondToken.withdraw(sender=getattr(tester, 'k' + str(limitedReportersDisputerAccountNum)))
                assert reputationToken.balanceOf(limitedReportersDisputeBondToken.address) == 0
                assert reputationToken.balanceOf(limitedReportersDisputeBondToken.getBondHolder()) == accountBalanceBeforeWithdrawl + disputeBondTokenBalanceBeforeWithdrawl
        else:
            # Withdraw dispute bond tokens to the branch the disputers migrated to
            print "All reporters dispute stakes:"
            for row in allReportersDisputeStakes:
                disputeAccountNum = None
                disputeBondToken = None
                print str(row) + "\n"
                if (row[0] == automatedReporterDisputerAccountNum):
                    disputeAccountNum = automatedReporterDisputerAccountNum
                    disputeBondToken = automatedReporterDisputeBondToken
                    disputeBondTokenBalanceBeforeWithdrawl = reputationToken.balanceOf(disputeBondToken.address)
                    destinationBranch = None
                    destinationBranchReputationToken = None
                    #print "disputedPayoutDistributionHash:" + str(disputeBondToken.getDisputedPayoutDistributionHash())
                    #print "market.derivePayoutDistributionHash(row[1]): " + str(market.derivePayoutDistributionHash(row[1]))
                    if (disputeBondToken.getDisputedPayoutDistributionHash() != market.derivePayoutDistributionHash(row[1])):
                        if (row[1] == OUTCOME_A):
                            destinationBranch = aBranch
                            destinationBranchReputationToken = aBranchReputationToken
                            print "Withdrawing automated reporter dispute bond tokens for a" + str(row[0]) + " to branch A"
                        elif (row[1] == OUTCOME_B):
                            destinationBranch = bBranch
                            destinationBranchReputationToken = bBranchReputationToken
                            print "Withdrawing automated reporter dispute bond tokens for a" + str(row[0]) + " to branch B"
                        elif (row[1] == OUTCOME_C):
                            destinationBranch = cBranch
                            destinationBranchReputationToken = cBranchReputationToken
                            print "Withdrawing automated reporter dispute bond tokens for a" + str(row[0]) + " to branch C"
                        if (destinationBranch and destinationBranchReputationToken):
                            accountBalanceBeforeWithdrawl = destinationBranchReputationToken.balanceOf(disputeBondToken.getBondHolder())
                            disputeBondToken.withdrawToBranch(destinationBranch.address, sender=getattr(tester, 'k' + str(disputeAccountNum)))
                            assert reputationToken.balanceOf(disputeBondToken.address) == 0
                            assert destinationBranchReputationToken.balanceOf(disputeBondToken.getBondHolder()) == accountBalanceBeforeWithdrawl + disputeBondTokenBalanceBeforeWithdrawl
                            printTestAccountBalances(destinationBranchReputationToken, True)
                if (row[0] == limitedReportersDisputerAccountNum):
                    disputeAccountNum = limitedReportersDisputerAccountNum
                    disputeBondToken = limitedReportersDisputeBondToken
                    disputeBondTokenBalanceBeforeWithdrawl = reputationToken.balanceOf(disputeBondToken.address)
                    destinationBranch = None
                    destinationBranchReputationToken = None
                    #print "disputedPayoutDistributionHash:" + str(disputeBondToken.getDisputedPayoutDistributionHash())
                    #print "market.derivePayoutDistributionHash(row[1]): " + str(market.derivePayoutDistributionHash(row[1]))
                    if (disputeBondToken.getDisputedPayoutDistributionHash() != market.derivePayoutDistributionHash(row[1])):
                        if (row[1] == OUTCOME_A):
                            destinationBranch = aBranch
                            destinationBranchReputationToken = aBranchReputationToken
                            print "Withdrawing limited reporters dispute bond tokens for a" + str(row[0]) + " to branch A"
                        elif (row[1] == OUTCOME_B):
                            destinationBranch = bBranch
                            destinationBranchReputationToken = bBranchReputationToken
                            print "Withdrawing limited reporters dispute bond tokens for a" + str(row[0]) + " to branch B"
                        elif (row[1] == OUTCOME_C):
                            destinationBranch = cBranch
                            destinationBranchReputationToken = cBranchReputationToken
                            print "Withdrawing limited reporters dispute bond tokens for a" + str(row[0]) + " to branch C"
                        if (destinationBranch and destinationBranchReputationToken):
                            accountBalanceBeforeWithdrawl = destinationBranchReputationToken.balanceOf(disputeBondToken.getBondHolder())
                            disputeBondToken.withdrawToBranch(destinationBranch.address, sender=getattr(tester, 'k' + str(disputeAccountNum)))
                            assert reputationToken.balanceOf(disputeBondToken.address) == 0
                            assert destinationBranchReputationToken.balanceOf(disputeBondToken.getBondHolder()) == accountBalanceBeforeWithdrawl + disputeBondTokenBalanceBeforeWithdrawl
                            printTestAccountBalances(destinationBranchReputationToken, True)
                if (row[0] == allReportersDisputerAccountNum):
                    disputeAccountNum = allReportersDisputerAccountNum
                    disputeBondToken = allReportersDisputeBondToken
                    disputeBondTokenBalanceBeforeWithdrawl = reputationToken.balanceOf(disputeBondToken.address)
                    destinationBranch = None
                    destinationBranchReputationToken = None
                    #print "disputedPayoutDistributionHash:" + str(disputeBondToken.getDisputedPayoutDistributionHash())
                    #print "market.derivePayoutDistributionHash(row[1]): " + str(market.derivePayoutDistributionHash(row[1]))
                    if (disputeBondToken.getDisputedPayoutDistributionHash() != market.derivePayoutDistributionHash(row[1])):
                        if (row[1] == OUTCOME_A):
                            destinationBranch = aBranch
                            destinationBranchReputationToken = aBranchReputationToken
                            print "Withdrawing all reporters dispute bond tokens for a" + str(row[0]) + " to branch A"
                        elif (row[1] == OUTCOME_B):
                            destinationBranch = bBranch
                            destinationBranchReputationToken = bBranchReputationToken
                            print "Withdrawing all reporters dispute bond tokens for a" + str(row[0]) + " to branch B"
                        elif (row[1] == OUTCOME_C):
                            destinationBranch = cBranch
                            destinationBranchReputationToken = cBranchReputationToken
                            print "Withdrawing all reporters dispute bond tokens for a" + str(row[0]) + " to branch C"
                        if (destinationBranch and destinationBranchReputationToken):
                            accountBalanceBeforeWithdrawl = destinationBranchReputationToken.balanceOf(disputeBondToken.getBondHolder())
                            disputeBondToken.withdrawToBranch(destinationBranch.address, sender=getattr(tester, 'k' + str(disputeAccountNum)))
                            assert reputationToken.balanceOf(disputeBondToken.address) == 0
                            assert destinationBranchReputationToken.balanceOf(disputeBondToken.getBondHolder()) == accountBalanceBeforeWithdrawl + disputeBondTokenBalanceBeforeWithdrawl
                            printTestAccountBalances(destinationBranchReputationToken, True)

    print "Final test account balances"
    if (allReportersDisputerAccountNum):
        print "Original branch test accounts"
        printTestAccountBalances(reputationToken, True)
        print "A branch test accounts"
        printTestAccountBalances(aBranchReputationToken, True)
        print "B branch test accounts"
        printTestAccountBalances(bBranchReputationToken, True)
        print "C branch test accounts"
        printTestAccountBalances(cBranchReputationToken, True)
    else:
        printTestAccountBalances(reputationToken, True)

    for row in expectedAccountBalances:
        if (row[1] == OUTCOME_A):
            assert row[2] == aBranchReputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
        elif (row[1] == OUTCOME_B):
            assert row[2] == bBranchReputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
        elif (row[1] == OUTCOME_C):
            assert row[2] == cBranchReputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
        elif (row[1] == None):
            assert row[2] == reputationToken.balanceOf(getattr(tester, 'a' + str(row[0])))
