import os
import serpent
from ethereum.tools import tester as tester
from ethereum.abi import ContractTranslator
from ethereum.tools.tester import ABIContract
from ethereum import utils as u
from ethereum.config import config_metropolis, Env

config_metropolis['BLOCK_GAS_LIMIT'] = 2**60

library = """
def bar():
    return(1: uint256)
"""

code = """
event Foo(bar: str)
def foo(fruits: str):
    log(type=Foo, fruits)
"""

with open("garbage.se", "w") as file:
    file.write(library)

try:
    chain = tester.Chain(env=Env(config=config_metropolis))
    chain.block.number += 2000000
    contract = chain.contract(code, language="serpent")
    contract.foo("hello goodbye")
finally:
    os.remove("garbage.se")
