from ethereum import tester
import os
import serpent

library = """
def bar():
    return(1: uint256)
"""

code = """
def foo():
    return(create('garbage.se'))
"""

with open("garbage.se", "w") as file:
    file.write(library)

try:
    state = tester.state()
    state.block.number += 2000000
    contract = state.abi_contract(code)
    print contract.foo()
finally:
    os.remove("garbage.se")
