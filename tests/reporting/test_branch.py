from ethereum.tools import tester
from utils import longToHexString

def test_branch_creation(contractsFixture):
    branch = contractsFixture.createBranch(3, 5)
    reputationToken = contractsFixture.applySignature('ReputationToken', branch.getReputationToken())

    assert branch.getParentBranch() == 3
    assert branch.getParentPayoutDistributionHash() == 5
    assert branch.getForkingMarket() == 0
    assert branch.getForkEndTime() == 0
    assert reputationToken.getBranch() == branch.address
    assert reputationToken.getTopMigrationDestination() == longToHexString(0)
