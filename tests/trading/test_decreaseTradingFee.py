#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import fix, bytesToHexString

def test_decrease_trading_fee_success(contractsFixture):
    market = contractsFixture.binaryMarket
    originalFee = market.feePerEthInAttoeth()
    assert market.creator() == bytesToHexString(tester.a0)
    newFee = originalFee -1

    assert market.decreaseMarketCreatorSettlementFeeInAttoethPerEth(newFee, sender = tester.k0)
    newFee = market.feePerEthInAttoeth()

    assert newFee == newFee

def test_decrease_trading_fee_failure(contractsFixture):
    market = contractsFixture.binaryMarket
    originalFee = market.feePerEthInAttoeth()

    with raises(TransactionFailed):
        market.decreaseMarketCreatorSettlementFeeInAttoethPerEth(0, sender = tester.k1)
    with raises(TransactionFailed):
        market.decreaseMarketCreatorSettlementFeeInAttoethPerEth(originalFee * 2)
