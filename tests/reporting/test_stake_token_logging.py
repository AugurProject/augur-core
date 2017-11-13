from ethereum.tools import tester
from utils import captureFilteredLogs, bytesToHexString

def test_stake_token_logging(contractsFixture, market, universe):
    stakeToken = contractsFixture.getOrCreateStakeToken(market, [10**18,0])
    reportingWindow = contractsFixture.applySignature('ReportingWindow', universe.getOrCreateNextReportingWindow())

    # Fast forward to one second after the next reporting window
    contractsFixture.chain.head_state.timestamp = reportingWindow.getStartTime() + 1

    stakeToken.buy(100)

    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)

    assert stakeToken.transfer(tester.a1, 8)

    assert len(logs) == 1
    assert logs[0]['_event_type'] == 'TokensTransferred'
    assert logs[0]['from'] == bytesToHexString(tester.a0)
    assert logs[0]['to'] == bytesToHexString(tester.a1)
    assert logs[0]['token'] == stakeToken.address
    assert logs[0]['universe'] == universe.address
    assert logs[0]['value'] == 8

    assert stakeToken.approve(tester.a2, 12)

    assert stakeToken.transferFrom(tester.a0, tester.a1, 12, sender=tester.k2)

    assert len(logs) == 2
    assert logs[1]['_event_type'] == 'TokensTransferred'
    assert logs[1]['from'] == bytesToHexString(tester.a0)
    assert logs[1]['to'] == bytesToHexString(tester.a1)
    assert logs[1]['token'] == stakeToken.address
    assert logs[1]['universe'] == universe.address
    assert logs[1]['value'] == 12
