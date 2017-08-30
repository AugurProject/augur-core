from ethereum.tools import tester

def test_legacyRep(contractsFixture):
    legacyRep = contractsFixture.contracts['LegacyRepContract']
    amounts = [1, 3, 7, 11, 13, 17]
    accounts = [tester.a0, tester.a1, tester.a2, tester.a3, tester.a4, tester.a5]
    legacyRep.setSaleDistribution(accounts, amounts)
    legacyRep.setSaleDistribution([tester.a6], [11 * 10**6 * 10**18 - sum(amounts)])
    contractsFixture.chain.head_state.timestamp += 15000
    assert legacyRep.getSeeded()
    assert legacyRep.decimals() == 18
    assert legacyRep.totalSupply() == 11 * 10**6 * 10**18

    for x in range(6):
        assert legacyRep.balanceOf(accounts[x]) == amounts[x]
    assert legacyRep.balanceOf(tester.a6) == 11 * 10**6 * 10**18 - sum(amounts)

    assert legacyRep.approve(tester.a0, 17, sender = tester.k5)
    assert legacyRep.allowance(tester.a5, tester.a0) == 17
    assert legacyRep.transferFrom(tester.a5, tester.a1, 17, sender = tester.k0)
    assert legacyRep.balanceOf(tester.a5) == 0
    assert legacyRep.balanceOf(tester.a1) == 20
    assert legacyRep.totalSupply() == 11 * 10**6 * 10**18

    assert legacyRep.transfer(tester.a3, 7, sender = tester.k2)
    assert legacyRep.balanceOf(tester.a3) == 18
    assert legacyRep.balanceOf(tester.a2) == 0
