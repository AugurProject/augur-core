from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, raises
from utils import longTo32Bytes, PrintGasUsed, fix
from constants import BID, ASK, YES, NO
from datetime import timedelta
from ethereum.utils import ecsign, sha3, normalize_key, int_to_32bytearray, bytearray_to_bytestr, zpad


def test_fill_order_with_tokens(localFixture, zeroX, market, cash, controller):
    expirationTimestampInSec = controller.getTimestamp() + 1
    orderAddresses = [tester.a0, market.address]
    orderValues = [YES, BID, 10, 1000, expirationTimestampInSec, 42]

    orderHash = zeroX.getOrderHash(orderAddresses, orderValues)
    v, r, s = createOrder(orderHash)

    fillAmount = 5

    # Fail with no Cash deposited
    with raises(TransactionFailed):
        zeroX.fillOrder(
            orderAddresses,
            orderValues,
            fillAmount,
            v,
            r,
            s,
            sender = tester.k1)

    assert cash.depositEther(value = 5000)
    assert cash.approve(zeroX.address, 5000)
    assert zeroX.deposit(cash.address, 5000)

    assert cash.depositEther(value = 45000, sender=tester.k1)
    assert cash.approve(zeroX.address, 45000, sender=tester.k1)
    assert zeroX.deposit(cash.address, 45000, sender=tester.k1)

    with PrintGasUsed(localFixture, "FILL_0X"):
        assert zeroX.fillOrder(
            orderAddresses,
            orderValues,
            fillAmount,
            v,
            r,
            s,
            sender = tester.k1)

    yesShareAddress = market.getShareToken(YES)
    noShareAddress = market.getShareToken(NO)
    assert zeroX.getTokenBalance(cash.address, tester.a0) == 0
    assert zeroX.getTokenBalance(yesShareAddress, tester.a0) == fillAmount
    assert zeroX.getTokenBalance(cash.address, tester.a1) == 0
    assert zeroX.getTokenBalance(noShareAddress, tester.a1) == fillAmount
    assert zeroX.getUnavailableAmount(orderHash) == fillAmount

def test_fill_order_with_shares(localFixture, zeroX, market, cash, controller):
    expirationTimestampInSec = controller.getTimestamp() + 1
    orderAddresses = [tester.a0, market.address]
    orderValues = [YES, ASK, 10, 1000, expirationTimestampInSec, 42]

    orderHash = zeroX.getOrderHash(orderAddresses, orderValues)
    v, r, s = createOrder(orderHash)

    fillAmount = 5

    # Fail with no shares deposited
    with raises(TransactionFailed):
        zeroX.fillOrder(
            orderAddresses,
            orderValues,
            fillAmount,
            v,
            r,
            s,
            sender = tester.k1)

    yesShareAddress = market.getShareToken(YES)
    noShareAddress = market.getShareToken(NO)
    invalidShareAddress = market.getShareToken(0)
    yesShareToken = localFixture.applySignature('ShareToken', yesShareAddress)
    noShareToken = localFixture.applySignature('ShareToken', noShareAddress)
    invalidShareToken = localFixture.applySignature('ShareToken', invalidShareAddress)
    completeSets = localFixture.contracts['CompleteSets']
    assert completeSets.publicBuyCompleteSets(market.address, fix(20), value=fix('20', market.getNumTicks()))
    assert noShareToken.transfer(tester.a1, 10)
    assert invalidShareToken.transfer(tester.a1, 10)

    assert yesShareToken.approve(zeroX.address, 10)
    assert zeroX.deposit(yesShareAddress, 10)

    assert noShareToken.approve(zeroX.address, 10, sender=tester.k1)
    assert zeroX.deposit(noShareAddress, 10, sender=tester.k1)
    assert invalidShareToken.approve(zeroX.address, 10, sender=tester.k1)
    assert zeroX.deposit(invalidShareAddress, 10, sender=tester.k1)

    with PrintGasUsed(localFixture, "FILL_0X"):
        assert zeroX.fillOrder(
            orderAddresses,
            orderValues,
            fillAmount,
            v,
            r,
            s,
            sender = tester.k1)

    yesShareAddress = market.getShareToken(YES)
    noShareAddress = market.getShareToken(NO)
    assert zeroX.getTokenBalance(cash.address, tester.a0) == 4900
    assert zeroX.getTokenBalance(yesShareAddress, tester.a0) == 5
    assert zeroX.getTokenBalance(cash.address, tester.a1) == 44100
    assert zeroX.getTokenBalance(noShareAddress, tester.a1) == 5
    assert zeroX.getUnavailableAmount(orderHash) == fillAmount

def test_maker_sell_shares_for_tokens(localFixture, zeroX, market, cash, controller):
    expirationTimestampInSec = controller.getTimestamp() + 1
    orderAddresses = [tester.a0, market.address]
    orderValues = [YES, ASK, 10, 1000, expirationTimestampInSec, 42]

    orderHash = zeroX.getOrderHash(orderAddresses, orderValues)
    v, r, s = createOrder(orderHash)

    fillAmount = 5

    # Fail with no shares deposited
    with raises(TransactionFailed):
        zeroX.fillOrder(
            orderAddresses,
            orderValues,
            fillAmount,
            v,
            r,
            s,
            sender = tester.k1)

    yesShareAddress = market.getShareToken(YES)
    noShareAddress = market.getShareToken(NO)
    yesShareToken = localFixture.applySignature('ShareToken', yesShareAddress)
    completeSets = localFixture.contracts['CompleteSets']
    assert completeSets.publicBuyCompleteSets(market.address, fix(20), value=fix('20', market.getNumTicks()))

    assert yesShareToken.approve(zeroX.address, 10)
    assert zeroX.deposit(yesShareAddress, 10)

    assert cash.depositEther(value = 5000, sender=tester.k1)
    assert cash.approve(zeroX.address, 5000, sender=tester.k1)
    assert zeroX.deposit(cash.address, 5000, sender=tester.k1)

    with PrintGasUsed(localFixture, "FILL_0X"):
        assert zeroX.fillOrder(
            orderAddresses,
            orderValues,
            fillAmount,
            v,
            r,
            s,
            sender = tester.k1)

    yesShareAddress = market.getShareToken(YES)
    assert zeroX.getTokenBalance(cash.address, tester.a0) == 5000
    assert zeroX.getTokenBalance(yesShareAddress, tester.a0) == 5
    assert zeroX.getTokenBalance(cash.address, tester.a1) == 0
    assert zeroX.getTokenBalance(yesShareAddress, tester.a1) == 5
    assert zeroX.getUnavailableAmount(orderHash) == fillAmount

def test_maker_buy_shares_for_tokens(localFixture, zeroX, market, cash, controller):
    # TODO
    pass

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

def createOrder(orderHash, key=tester.k0):
    key = normalize_key(key)
    v, r, s = ecsign(sha3("\x19Ethereum Signed Message:\n32" + orderHash), key)
    return v, zpad(bytearray_to_bytestr(int_to_32bytearray(r)), 32), zpad(bytearray_to_bytestr(int_to_32bytearray(s)), 32)
