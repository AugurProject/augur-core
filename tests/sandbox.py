from ethereum import tester
import os
import serpent

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
    state = tester.state()
    state.block.number += 2000000
    contract = state.abi_contract(code)
    contract.foo("hello goodbye")
finally:
    os.remove("garbage.se")
