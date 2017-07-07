from ethereum import tester

def test_branch_creation(contractsFixture):
    branch = contractsFixture.createBranch(3, 5)
    reputationToken = contractsFixture.applySignature('reputationToken', branch.getReputationToken())

    assert(branch.getParentBranch() == 3)
    assert(branch.getParentPayoutDistributionHash() == 5)
    assert(branch.getForkingMarket() == 0)
    assert(branch.getForkEndTime() == 0)
    assert(reputationToken.getBranch() == branch.address)
    assert(reputationToken.getTopMigrationDestination() == 0)
