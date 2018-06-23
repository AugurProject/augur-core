from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, raises
from utils import longTo32Bytes, PrintGasUsed, fix
from constants import BID, ASK, YES, NO
from datetime import timedelta

def test_fill_order_with_tokens(localFixture, zeroX, market, cash, controller):
    expirationTimestampInSec = controller.getTimestamp() + 1
    orderAddresses = [tester.a0, market.address]
    orderValues = [YES, BID, 10, 1000, expirationTimestampInSec, 42]

    # TODO get order v,r,s
    v = 0
    r = longTo32Bytes(0)
    s = longTo32Bytes(0)

    fillAmount = 5

    assert zeroX.fillOrder(
          orderAddresses,
          orderValues,
          fillAmount,
          v,
          r,
          s,
          sender = tester.k1)

    # TODO assert account 0 cash
    # TODO assert account 0 shares
    # TODO assert account 1 cash
    # TODO assert account 1 cash

    orderHash = zeroX.getOrderHash(orderAddresses, orderValues)
    # TODO assert zeroX.getUnavailableAmount(orderHash) == fillAmount

def test_cancel_order(localFixture, zeroX, market, cash, controller):
    expirationTimestampInSec = controller.getTimestamp() + 1
    orderAddresses = [tester.a0, market.address]
    orderValues = [YES, BID, 10, 1000, expirationTimestampInSec, 42]

    cancelAmount = 5

    assert zeroX.cancelOrder(
          orderAddresses,
          orderValues,
          cancelAmount)

    orderHash = zeroX.getOrderHash(orderAddresses, orderValues)
    assert zeroX.getUnavailableAmount(orderHash) == cancelAmount

def test_deposit_and_withdraw(localFixture, zeroX, cash):
    assert cash.depositEther(value = 10)
    assert cash.approve(zeroX.address, 10)
    assert zeroX.deposit(cash.address, 9)

    assert zeroX.getTokenBalance(cash.address, tester.a0) == 9
    assert cash.balanceOf(tester.a0) == 1

    with raises(TransactionFailed):
        zeroX.withdraw(cash.address, 10)

    assert zeroX.withdraw(cash.address, 8)

    assert zeroX.getTokenBalance(cash.address, tester.a0) == 1
    assert cash.balanceOf(tester.a0) == 9


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    augur = fixture.contracts["Augur"]
    kitchenSinkSnapshot['zeroX'] = fixture.upload('solidity_test_helpers/ZeroX/ZeroXPoC.sol', "zeroX", constructorArgs=[augur.address])
    market = ABIContract(fixture.chain, kitchenSinkSnapshot['yesNoMarket'].translator, kitchenSinkSnapshot['yesNoMarket'].address)

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def zeroX(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['zeroX'].translator, kitchenSinkSnapshot['zeroX'].address)

@fixture
def market(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['yesNoMarket'].translator, kitchenSinkSnapshot['yesNoMarket'].address)

@fixture
def cash(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)

@fixture
def controller(localFixture, kitchenSinkSnapshot):
    return localFixture.contracts['Controller']
