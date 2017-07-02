from ethereum import tester
import os
import serpent

library = """
def bar():
    return(1: uint256)
"""

code = """
data fruits[]
def foo(fruits: arr):
    save(self.fruits[0], fruits, items = len(fruits))

def bar():
    return(load(self.fruits[0], items = 2): arr)
"""

with open("garbage.se", "w") as file:
    file.write(library)

try:
    state = tester.state()
    state.block.number += 2000000
    contract = state.abi_contract(code)
    contract.foo([3,5])
    print contract.bar()
finally:
    os.remove("garbage.se")
