from ethereum import tester
from ContractsFixture import ContractsFixture

def test_branch_creation():
    fixture = ContractsFixture()

    branch = fixture.createBranch(3, 5)
    reputationToken = fixture.applySignature('reputationToken', branch.getReputationToken())

    assert(branch.getParentBranch() == 3)
    assert(branch.getParentPayoutDistributionHash() == 5)
    assert(branch.getForkingMarket() == 0)
    assert(branch.getForkEndTime() == 0)
    assert(reputationToken.getBranch() == branch.address)
    assert(reputationToken.getTopMigrationDestination() == 0)
