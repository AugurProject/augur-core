from ethereum import tester
from ethereum.abi import ContractTranslator
from ethereum.tester import ABIContract
import json
import os
import serpent

controllerCode = """
data addresses[]
def add(key, address):
    self.addresses[key] = address
def lookup(key):
    return(self.addresses[key])
"""

libraryCode = """
data controller
data key
data apple
data banana
data cherry
data durian
data eggplant
data fruit

def init():
    self.apple = 5

def setNumber(apple, banana, cherry, durian, eggplant, fruit):
    self.apple = apple
    self.banana = banana
    self.cherry = cherry
    self.durian = durian
    self.eggplant = eggplant
    self.fruit = fruit

def getApple():
    return(self.apple)
def getBanana():
    return(self.banana)
def getCherry():
    return(self.cherry)
def getDurian():
    return(self.durian)
def getEggplant():
    return(self.eggplant)
def getFruit():
    return(self.fruit)
"""

factoryCode = """
extern delegateExtern: [setup:[int256,int256]:_]
data lastLibrary
def createLibrary(controller):
    library = create('garbage.se')
    library.setup(controller, 'library')
    # workaround for https://github.com/ethereum/serpent/issues/119
    self.lastLibrary = library
    return(library)
def getLastLibrary():
    return(self.lastLibrary)
"""

delegateCode = """
extern controllerExtern: [lookup:[int256]:address]
data controller
data key
def any():
    if (self.controller and self.key):
        ~mstore(0, self.controller.lookup(self.key))
        ~calldatacopy(32, 0, ~calldatasize())
        if not ~delegatecall(msg.gas - 10000, ~mload(0), 32, ~calldatasize(), 0, 32):
            ~invalid()
        ~return(0, 32)
def setup(controller, key):
    self.controller = controller
    self.key = key
"""

with open("garbage.se", "w") as file:
    file.write(delegateCode)

try:
    state = tester.state()
    state.block.number += 2000000

    controller = state.abi_contract(controllerCode)
    library = state.abi_contract(libraryCode)
    controller.add('library'.ljust(32, '\x00'), library.address)
    print(serpent.mk_signature(factoryCode))
    factory = state.abi_contract(factoryCode)

    startingGasUsed = state.block.gas_used
    factory.createLibrary(controller.address)
    delegateAddress = factory.getLastLibrary()
    print("Creation Gas Used: " + str(state.block.gas_used - startingGasUsed))

    delegate = ABIContract(state, library.translator, delegateAddress)

    print("Starting Apple: " + str(delegate.getApple()))
    delegate.setNumber(1, 3, 5, 7, 11, 13)
    print("Apple: " + str(delegate.getApple()))
    print("Banana: " + str(delegate.getBanana()))
    print("Cherry: " + str(delegate.getCherry()))
    print("Durian: " + str(delegate.getDurian()))
    print("Eggplant: " + str(delegate.getEggplant()))
    print("Fruit: " + str(delegate.getFruit()))
finally:
    os.remove("garbage.se")
