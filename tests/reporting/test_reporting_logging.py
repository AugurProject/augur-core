from ethereum.tools import tester
from utils import captureFilteredLogs, bytesToHexString, AssertLog
from reporting_utils import proceedToNextRound

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

def test_fee_token_transfer(contractsFixture, universe):
    feeWindow = contractsFixture.applySignature('FeeWindow', universe.getOrCreateCurrentFeeWindow())

    feeToken = contractsFixture.applySignature("FeeToken", feeWindow.getFeeToken())

    feeTokenTransferLog = {
        'from': bytesToHexString(tester.a0),
        'to': bytesToHexString(tester.a1),
        'token': feeToken.address,
        'universe': universe.address,
        'tokenType': 4,
        'value': 0,
    }
    with AssertLog(contractsFixture, "TokensTransferred", feeTokenTransferLog):
        assert feeToken.transfer(tester.a1, 0)

def test_crowdsourcer_transfer(contractsFixture, market, universe):
    proceedToNextRound(contractsFixture, market)
    proceedToNextRound(contractsFixture, market)
    proceedToNextRound(contractsFixture, market)

    crowdsourcer = contractsFixture.applySignature("DisputeCrowdsourcer", market.getWinningReportingParticipant())

    crowdsourcerTokenTransferLog = {
        'from': bytesToHexString(tester.a0),
        'to': bytesToHexString(tester.a1),
        'token': crowdsourcer.address,
        'universe': universe.address,
        'tokenType': 2,
        'value': 0,
    }
    with AssertLog(contractsFixture, "TokensTransferred", crowdsourcerTokenTransferLog):
        assert crowdsourcer.transfer(tester.a1, 0)