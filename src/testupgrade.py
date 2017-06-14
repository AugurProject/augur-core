from ethereum import tester
from ethereum.tester import ABIContract
import serpent
import os

factoryCode = """
def createLibrary(controller):
    library = create('garbage.se')
    return(library: address)
"""

delegateCode = """
def any():
    ~return(0, 32)
"""

with open("garbage.se", "w") as file:
    file.write(delegateCode)

try:
    state = tester.state()
    state.state.block_number += 2000000
    print serpent.mk_signature(factoryCode)
finally:
    os.remove("garbage.se")