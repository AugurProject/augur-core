from pytest import mark

ONE = 10 ** 18

@mark.parametrize('numIndeterminate, targetIndeterminatePerHundred, previousBond, expectedValue', [
    # No change
    (1, 1, ONE, ONE),
    (5, 5, ONE, ONE),
    (1, 1, 5 * ONE, 5 * ONE),

    # Maximum Decrease
    (0, 1, 2 * ONE, ONE),
    (0, 99, 2 * ONE, ONE),
    (0, 1, 10 * ONE, 5 * ONE),

    # Maximum Increase
    (100, 1, ONE, 2 * ONE - 1), # Small rounding errors
    (100, 0, ONE, 2 * ONE),
    (100, 99, ONE, 2 * ONE),
    (100, 1, 10 * ONE, 20 * ONE - 10), # Small rounding errors

    # Decrease
    (1, 10, 10 * ONE, 5.5 * ONE),
    (2, 10, 10 * ONE, 6 * ONE),
    (4, 10, 10 * ONE, 7 * ONE),
    (8, 10, 10 * ONE, 9 * ONE),
    (9, 10, 10 * ONE, 9.5 * ONE),

    # Increase
    (51, 50, 10 * ONE, 10.2 * ONE),
    (55, 50, 10 * ONE, 11 * ONE),
    (60, 50, 10 * ONE, 12 * ONE),
    (80, 50, 10 * ONE, 16 * ONE),
    (90, 50, 10 * ONE, 18 * ONE),
])
def test_validity_bond_calculation(numIndeterminate, targetIndeterminatePerHundred, previousBond, expectedValue, contractsFixture):
    feeCalculator = contractsFixture.contracts["MarketFeeCalculator"]
    targetIndeterminate = targetIndeterminatePerHundred * 10 ** 18 / 100
    newBond = feeCalculator.calculateValidityBond(numIndeterminate, 100, targetIndeterminate, previousBond)
    assert newBond == expectedValue

def test_getTargetReporterGasCosts(contractsFixture):
    pass

def test_getReportingFeeInAttoethPerEth(contractsFixture):
    pass
