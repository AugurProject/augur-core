from ethereum.tools import tester
from utils import captureFilteredLogs, bytesToHexString

def test_decimals(contractsFixture, universe):
    reputationTokenFactory = contractsFixture.contracts['ReputationTokenFactory']
    assert reputationTokenFactory
    reputationTokenAddress = reputationTokenFactory.createReputationToken(contractsFixture.contracts['Controller'].address, universe.address)
    reputationToken = contractsFixture.applySignature('ReputationToken', reputationTokenAddress)

    assert reputationToken.decimals() == 18

def test_reputation_token_logging(contractsFixture, universe):
    reputationToken = contractsFixture.applySignature("ReputationToken", universe.getReputationToken())

    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)

    assert reputationToken.transfer(tester.a1, 8)

    assert len(logs) == 1
    assert logs[0]['_event_type'] == 'TokensTransferred'
    assert logs[0]['from'] == bytesToHexString(tester.a0)
    assert logs[0]['to'] == bytesToHexString(tester.a1)
    assert logs[0]['token'] == reputationToken.address
    assert logs[0]['universe'] == universe.address
    assert logs[0]['value'] == 8

    assert reputationToken.approve(tester.a2, 12)

    assert reputationToken.transferFrom(tester.a0, tester.a1, 12, sender=tester.k2)

    assert len(logs) == 2
    assert logs[1]['_event_type'] == 'TokensTransferred'
    assert logs[1]['from'] == bytesToHexString(tester.a0)
    assert logs[1]['to'] == bytesToHexString(tester.a1)
    assert logs[1]['token'] == reputationToken.address
    assert logs[1]['universe'] == universe.address
    assert logs[1]['value'] == 12
