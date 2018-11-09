from ethereum.tools import tester
from ethereum.tools.tester import ABIContract, TransactionFailed
from pytest import fixture, raises
from utils import longTo32Bytes, PrintGasUsed, fix, stringToBytes, bytesToHexString
from constants import BID, ASK, YES, NO
from datetime import timedelta
from ethereum.utils import ecsign, sha3, normalize_key, int_to_32bytearray, bytearray_to_bytestr, zpad

gemIlk = longTo32Bytes(42)
ethIlk = longTo32Bytes(43)
ONE = 10**27

def test_mdai(localFixture, dai, token, vat, pit, drip, cat, vow, flipper, flopper, flapper, gemJoin, daiJoin, ethJoin, daiMove):
    # get some tokens and "dai"
    assert token.faucet(10000)
    assert dai.faucet(10000)

    # Put some of our tokens into the system
    token.approve(gemJoin.address, 1000)
    bytesUserAddress = vat.getBytesAddress(tester.a0)
    gemJoin.join(bytesUserAddress, 1000)
    assert vat.getGemBalance(gemIlk, bytesUserAddress) == 1000 * ONE

    # also add some eth
    ethJoin.join(tester.a0, value=10000)

    # Lets get some dai by first opening a CDP using our token as collateral

    # Before we actually get the dai lets configure the Pit for our token and initialize the Vat for it
    vat.init(gemIlk)

    #spot: the maximum amount of Dai drawn per unit collateral
    pit.file(gemIlk, "spot", 10 * ONE)
    # line: the maximum total Dai drawn
    pit.file(gemIlk, "line", 10000000 * ONE)
    # Line: the maximum total Dai drawn across all ilks
    pit.file(gemIlk, "Line", 1000000000 * ONE)

    # Now we can actually get the dai
    tokensProvided = 10
    daiReceived = 100
    pit.frob(gemIlk, tokensProvided, daiReceived)
    assert vat.getDaiBalance(bytesUserAddress) == 100 * ONE

    # If we adjust the spot rate such that it will trigger liquidation we can call the cat.bite method to initiate that
    pit.file(gemIlk, "spot", 9 * ONE)
    cat.bite(gemIlk, bytesUserAddress)

    # We can see some tokens were removed from the user balance in accordance with the new spot rate
    assert vat.getGemBalance(gemIlk, bytesUserAddress) == 990 * ONE
    catBytesAddress = vat.getBytesAddress(cat.address)
    assert vat.getGemBalance(gemIlk, catBytesAddress) == 10 * ONE

    # Lets configure some of the liquidation params
    cat.fileData(gemIlk, "chop", ONE)

    # Maximum auction
    cat.fileData(gemIlk, "lump", 10)

    # We can kick off an auction now for some seized funds
    cat.flip(0, 10)

    # Now lets bid on the gems that have been put up for auction
    daiMove.hope(flipper.address)
    flipper.tend(1, 1, 1)

    assert vat.getDaiBalance(bytesUserAddress) == 99 * ONE

    # Move time to the end of the auction and get our tokens
    localFixture.chain.head_state.timestamp += flipper.tau() + 1
    flipper.deal(1)
    assert vat.getGemBalance(gemIlk, bytesUserAddress) == 991 * ONE


@fixture(scope="session")
def localSnapshot(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    augur = fixture.contracts["Augur"]
    dai = kitchenSinkSnapshot['dai'] = fixture.upload('solidity_test_helpers/mcdai/Dai.sol', "dai")
    token = kitchenSinkSnapshot['token'] = fixture.upload('solidity_test_helpers/StandardTokenHelper.sol', "token")
    vat = kitchenSinkSnapshot['vat'] = fixture.upload('solidity_test_helpers/mcdai/Vat.sol', "vat")
    pit = kitchenSinkSnapshot['pit'] = fixture.upload('solidity_test_helpers/mcdai/Pit.sol', "pit", constructorArgs=[vat.address])
    drip = kitchenSinkSnapshot['drip'] = fixture.upload('solidity_test_helpers/mcdai/Drip.sol', "drip", constructorArgs=[vat.address])
    cat = kitchenSinkSnapshot['cat'] = fixture.upload('solidity_test_helpers/mcdai/Cat.sol', "cat", constructorArgs=[vat.address])
    vow = kitchenSinkSnapshot['vow'] = fixture.upload('solidity_test_helpers/mcdai/Vow.sol', "vow")
    gemJoin = kitchenSinkSnapshot['gemJoin'] = fixture.upload('solidity_test_helpers/mcdai/GemJoin.sol', "gemJoin", constructorArgs=[vat.address, gemIlk, token.address])
    daiJoin = kitchenSinkSnapshot['daiJoin'] = fixture.upload('solidity_test_helpers/mcdai/DaiJoin.sol', "daiJoin", constructorArgs=[vat.address, dai.address])
    ethJoin = kitchenSinkSnapshot['ethJoin'] = fixture.upload('solidity_test_helpers/mcdai/ETHJoin.sol', "ethJoin", constructorArgs=[vat.address, ethIlk])
    daiMove = kitchenSinkSnapshot['daiMove'] = fixture.upload('solidity_test_helpers/mcdai/DaiMove.sol', "daiMove", constructorArgs=[vat.address])
    gemMove = kitchenSinkSnapshot['gemMove'] = fixture.upload('solidity_test_helpers/mcdai/GemMove.sol', "gemMove", constructorArgs=[vat.address, gemIlk])
    flipper = kitchenSinkSnapshot['flipper'] = fixture.upload('solidity_test_helpers/mcdai/Flipper.sol', "flipper", constructorArgs=[daiMove.address, gemMove.address])
    flopper = kitchenSinkSnapshot['flopper'] = fixture.upload('solidity_test_helpers/mcdai/Flopper.sol', "flopper", constructorArgs=[daiMove.address, gemMove.address])
    flapper = kitchenSinkSnapshot['flapper'] = fixture.upload('solidity_test_helpers/mcdai/Flapper.sol', "flapper", constructorArgs=[daiMove.address, gemMove.address])

    vat.rely(gemJoin.address)
    vat.rely(daiJoin.address)
    vat.rely(ethJoin.address)
    vat.rely(drip.address)
    vat.rely(pit.address)
    vat.rely(cat.address)
    vat.rely(vow.address)
    vat.rely(gemMove.address)
    vat.rely(daiMove.address)

    vow.file("flap", flapper.address)
    vow.file("flop", flopper.address)
    vow.file("vat", vat.address)
    vow.rely(cat.address)

    cat.file(gemIlk, "flip", flipper.address)
    cat.file(gemIlk, "pit", pit.address)
    cat.file(gemIlk, "vow", vow.address)

    drip.fileContract("vow", vat.getBytesAddress(vow.address))

    return fixture.createSnapshot()

@fixture
def localFixture(fixture, localSnapshot):
    fixture.resetToSnapshot(localSnapshot)
    return fixture

@fixture
def dai(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['dai'].translator, kitchenSinkSnapshot['dai'].address)

@fixture
def token(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['token'].translator, kitchenSinkSnapshot['token'].address)

@fixture
def vat(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['vat'].translator, kitchenSinkSnapshot['vat'].address)

@fixture
def pit(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['pit'].translator, kitchenSinkSnapshot['pit'].address)

@fixture
def drip(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['drip'].translator, kitchenSinkSnapshot['drip'].address)

@fixture
def cat(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['cat'].translator, kitchenSinkSnapshot['cat'].address)

@fixture
def vow(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['vow'].translator, kitchenSinkSnapshot['vow'].address)

@fixture
def flipper(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['flipper'].translator, kitchenSinkSnapshot['flipper'].address)

@fixture
def flopper(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['flopper'].translator, kitchenSinkSnapshot['flopper'].address)

@fixture
def flapper(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['flapper'].translator, kitchenSinkSnapshot['flapper'].address)

@fixture
def gemJoin(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['gemJoin'].translator, kitchenSinkSnapshot['gemJoin'].address)

@fixture
def daiJoin(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['daiJoin'].translator, kitchenSinkSnapshot['daiJoin'].address)

@fixture
def ethJoin(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['ethJoin'].translator, kitchenSinkSnapshot['ethJoin'].address)

@fixture
def gemMove(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['gemMove'].translator, kitchenSinkSnapshot['gemMove'].address)

@fixture
def daiMove(localFixture, kitchenSinkSnapshot):
    return ABIContract(localFixture.chain, kitchenSinkSnapshot['daiMove'].translator, kitchenSinkSnapshot['daiMove'].address)
