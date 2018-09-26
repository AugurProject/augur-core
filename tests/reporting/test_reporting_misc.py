from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from utils import captureFilteredLogs, bytesToHexString, AssertLog
from pytest import raises
from reporting_utils import proceedToNextRound

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

def test_malicious_shady_parties(contractsFixture, universe):
    maliciousMarketHaver = contractsFixture.upload('solidity_test_helpers/MaliciousMarketHaver.sol', 'maliciousMarketHaver')

    maliciousMarketHaver.setMarket(universe.address)
    assert not universe.isContainerForShareToken(maliciousMarketHaver.address)

    maliciousMarketHaver.setMarket(0)
    assert not universe.isContainerForReportingParticipant(maliciousMarketHaver.address)
