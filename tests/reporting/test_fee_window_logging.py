from ethereum.tools import tester
from utils import captureFilteredLogs, bytesToHexString

def test_fee_wondow_logging(contractsFixture, market, categoricalMarket, scalarMarket, universe):
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())

    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    assert feeWindow.buy(100)

    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)

    assert feeWindow.transfer(tester.a1, 8)

    assert len(logs) == 1
    assert logs[0]['_event_type'] == 'TokensTransferred'
    assert logs[0]['from'] == bytesToHexString(tester.a0)
    assert logs[0]['to'] == bytesToHexString(tester.a1)
    assert logs[0]['token'] == feeWindow.address
    assert logs[0]['universe'] == universe.address
    assert logs[0]['value'] == 8

    assert feeWindow.approve(tester.a2, 12)

    assert feeWindow.transferFrom(tester.a0, tester.a1, 12, sender=tester.k2)

    assert len(logs) == 2
    assert logs[1]['_event_type'] == 'TokensTransferred'
    assert logs[1]['from'] == bytesToHexString(tester.a0)
    assert logs[1]['to'] == bytesToHexString(tester.a1)
    assert logs[1]['token'] == feeWindow.address
    assert logs[1]['universe'] == universe.address
    assert logs[1]['value'] == 12
