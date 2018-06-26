from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import captureFilteredLogs, bytesToHexString, AssertLog
from pytest import raises
from reporting_utils import proceedToNextRound

def test_redeploy_and_migration(contractsFixture, universe):
    # Pull escape hatch

    # Do a new deploy with the new Rep Token contract

    # Create genesis universe

    # Show new REP not frozen, just 0 supply

    # Migrate REP to the new REP token

    # Show supply increased in new and decreased in old
