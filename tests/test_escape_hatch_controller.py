from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import captureFilteredLogs, bytesToHexString, AssertLog, TokenDelta
from pytest import raises, fixture

def test_escape_hatch_controller(contractsFixture, universe, controller):
    escapeHatchController = contractsFixture.upload('../source/contracts/external/EscapeHatchController.sol')
    assert escapeHatchController.setController(controller.address)
    assert escapeHatchController.controller() == controller.address
    assert escapeHatchController.getOwner() == bytesToHexString(tester.a0)

    # transfer ownership of controller to the escape hatch controller
    assert controller.transferOwnership(escapeHatchController.address)
    assert controller.owner() == escapeHatchController.address

    # Pull escape hatch
    assert escapeHatchController.emergencyStop()
    assert controller.stopped()


@fixture
def controller(contractsFixture, kitchenSinkSnapshot):
    return contractsFixture.contracts['Controller']
