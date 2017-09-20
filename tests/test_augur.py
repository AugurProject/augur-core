#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises


def test_augur_central_authority_for_cash(contractsFixture):
    # In testing we automatically provide the augur central authority contract with approval to transfer on behalf of the tester accounts
    cash = contractsFixture.cash
    testers = [(getattr(tester, 'k%i' % x), getattr(tester, 'a%i' % x)) for x in range(0,10)]
    # We will prove this by having testers dust some of their Cash through a trusted request to the Augur contract
    for (testerKey, testerAddress) in testers:
        assert cash.depositEther(sender=testerKey, value=100)
        originalTesterBalance = cash.balanceOf(testerAddress)
        originalVoidBalance = cash.balanceOf(0)
        assert contractsFixture.augur.trustedTransfer(cash.address, testerAddress, 0, 40)
        assert cash.balanceOf(testerAddress) == originalTesterBalance - 40
        assert cash.balanceOf(0) == originalVoidBalance + 40
