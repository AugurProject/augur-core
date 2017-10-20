#!/usr/bin/env python

from ethereum.tools import tester
from ethereum.tools.tester import TransactionFailed
from pytest import raises
from utils import fix, bytesToHexString

def test_decrease_trading_fee_success(market):
    originalFee = market.getMarketCreatorSettlementFeeDivisor()
    assert market.getOwner() == bytesToHexString(tester.a0)
    newFeeInput = (10 ** 18 / originalFee) - 10 ** 15

    assert market.decreaseMarketCreatorSettlementFeeInAttoethPerEth(newFeeInput, sender = tester.k0)
    newFee = market.getMarketCreatorSettlementFeeDivisor()

    assert newFee == 10 ** 18 / newFeeInput

def test_decrease_trading_fee_failure(market):
    originalFee = market.getMarketCreatorSettlementFeeDivisor()

    with raises(TransactionFailed):
        market.decreaseMarketCreatorSettlementFeeInAttoethPerEth(0, sender = tester.k1)
    with raises(TransactionFailed):
        newFeeInput = 2 * 10 ** 18 / originalFee
        market.decreaseMarketCreatorSettlementFeeInAttoethPerEth(newFeeInput)
