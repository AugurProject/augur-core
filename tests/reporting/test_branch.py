from utils import longToHexString, stringToBytes

def test_branch_creation(contractsFixture):
    branch = contractsFixture.createBranch(3, "5")
    reputationToken = contractsFixture.applySignature('ReputationToken', branch.getReputationToken())

    assert branch.getParentBranch() == longToHexString(3)
    assert branch.getParentPayoutDistributionHash() == stringToBytes("5")
    assert branch.getForkingMarket() == longToHexString(0)
    assert branch.getForkEndTime() == 0
    assert reputationToken.getBranch() == branch.address
    assert reputationToken.getTopMigrationDestination() == longToHexString(0)
