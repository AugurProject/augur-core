from ethereum.tools import tester
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
    chain = tester.chain()
    chain.block.number += 2000000
    contract = chain.contract(code, language="serpent")
    contract.foo("hello goodbye")
finally:
    os.remove("garbage.se")
