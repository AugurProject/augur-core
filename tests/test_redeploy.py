from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import captureFilteredLogs, bytesToHexString, AssertLog, TokenDelta
from pytest import raises, fixture
from reporting_utils import proceedToNextRound

def test_redeploy_and_migration(contractsFixture, universe, controller):
    # Pull escape hatch
    assert controller.emergencyStop()
    oldRepTokenAddress = universe.getReputationToken()
    oldRepToken = contractsFixture.applySignature('ReputationToken', oldRepTokenAddress)

    # Do a new deploy with the new Rep Token contract
    contractsFixture.contracts = {}
    newController = contractsFixture.upload('solidity_test_helpers/TestController.sol', lookupKey="Controller")
    contractsFixture.uploadAugur()
    contractsFixture.uploadAllContracts(legacyRepForRedeployTest=oldRepTokenAddress)
    contractsFixture.initializeAllContracts()
    contractsFixture.whitelistTradingContracts()
    contractsFixture.approveCentralAuthority()

    # Create genesis universe
    newUniverseAddress = contractsFixture.contracts['Augur'].createGenesisUniverse()
    newUniverse = contractsFixture.applySignature('Universe', newUniverseAddress)

    # The new REP is not frozen, just 0 supply
    newRepTokenAddress = newUniverse.getReputationToken()
    newRepToken = contractsFixture.applySignature('NewReputationToken', newRepTokenAddress)
    assert newRepToken.totalSupply() == 0
    assert newRepToken.transfer(tester.a1, 0)

    # Migrate REP to the new REP token
    repBalance = oldRepToken.balanceOf(tester.a0)
    oldRepToken.approve(newRepToken.address, repBalance)

    with TokenDelta(oldRepToken, -repBalance, tester.a0, "Old Rep Token balance not decreased"):
        with TokenDelta(newRepToken, repBalance, tester.a0, "New Rep Token balance not increased"):
            newRepToken.migrateFromLegacyReputationToken()

    # Create a market just to confirm that REP function works
    cash = contractsFixture.getSeededCash()
    yesNoMarket = contractsFixture.createReasonableYesNoMarket(newUniverse, cash)


@fixture
def controller(contractsFixture, kitchenSinkSnapshot):
    return contractsFixture.contracts['Controller']
