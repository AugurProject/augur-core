from utils import longToHexString, stringToBytes

def test_universe_creation(contractsFixture):
    universe = contractsFixture.createUniverse(3, "5")
    reputationToken = contractsFixture.applySignature('ReputationToken', universe.getReputationToken())

    assert universe.getParentUniverse() == longToHexString(3)
    assert universe.getParentPayoutDistributionHash() == stringToBytes("5")
    assert universe.getForkingMarket() == longToHexString(0)
    assert universe.getForkEndTime() == 0
    assert reputationToken.getUniverse() == universe.address
    assert reputationToken.getTopMigrationDestination() == longToHexString(0)
