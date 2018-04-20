from ethereum.tools import tester
from utils import AssertLog, bytesToHexString

def test_fee_window_logging(contractsFixture, market, categoricalMarket, scalarMarket, universe):
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())

    contractsFixture.contracts["Time"].setTimestamp(feeWindow.getStartTime() + 1)

    assert feeWindow.buy(100)

    tokensTransferredLog = {
        'from': bytesToHexString(tester.a0),
        'to': bytesToHexString(tester.a1),
        'token': feeWindow.address,
        'universe': universe.address,
        'tokenType': 3,
        'value': 8
    }
    with AssertLog(contractsFixture, "TokensTransferred", tokensTransferredLog):
        assert feeWindow.transfer(tester.a1, 8)

    assert feeWindow.approve(tester.a2, 12)

    tokensTransferredLog = {
        'from': bytesToHexString(tester.a0),
        'to': bytesToHexString(tester.a1),
        'token': feeWindow.address,
        'universe': universe.address,
        'tokenType': 3,
        'value': 12
    }
    with AssertLog(contractsFixture, "TokensTransferred", tokensTransferredLog):
        assert feeWindow.transferFrom(tester.a0, tester.a1, 12, sender=tester.k2)
