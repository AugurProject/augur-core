from binascii import hexlify
from ethereum import utils as u
from ethereum.abi import ContractTranslator
from ethereum.config import config_metropolis, Env
from ethereum.tools import tester
from ethereum.tools.tester import ABIContract
from json import dumps as json_dumps
from os import remove as os_remove
from solc import compile_standard

config_metropolis['BLOCK_GAS_LIMIT'] = 2**60

library = """
def bar():
    return(1: uint256)
"""

serCode = """
extern solExterns: [apple:[uint8]:_]
def banana(sol):
    return sol.apple(0x123456)
"""

solCode = """
contract Sol {
    event Foo(uint8 msg);
    function apple(uint8 param) returns(uint256) {
        require(param == 0x56);
        Foo(param);
        return param;
    }
}
"""

def compileSolidity(chain):
    result = compile_standard({ 'language': 'Solidity', 'sources': { 'Sol': { 'content': solCode } } })
    bytecode = bytearray.fromhex(result['contracts']['Sol']['Sol']['evm']['bytecode']['object'])
    signature = result['contracts']['Sol']['Sol']['abi']
    contractAddress = long(hexlify(chain.contract(bytecode)), 16)
    contract = ABIContract(chain, ContractTranslator(signature), contractAddress)
    return contract

with open("garbage.se", "w") as file:
    file.write(library)

try:
    chain = tester.Chain(env=Env(config=config_metropolis))
    logs = []
    sol = compileSolidity(chain)
    ser = chain.contract(serCode, language="serpent")
    chain.head_state.log_listeners.append(lambda log: logs.append(sol.translator.listen(log)))
    print ser.banana(sol.address)
    print logs
finally:
    os_remove("garbage.se")
