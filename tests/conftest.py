from binascii import hexlify
from datetime import timedelta
from ethereum.state import State
from ethereum.tools import tester
from ethereum.tools.tester import Chain
from ethereum.abi import ContractTranslator
from ethereum.tools.tester import ABIContract
from ethereum.config import config_metropolis, Env
from ethereum import utils
from ethereum import vm
import ethereum
from io import open as io_open
from json import dump as json_dump, load as json_load, dumps as json_dumps
from os import path, walk, makedirs, listdir, remove as remove_file
import pytest
from re import findall
from solc import compile_standard
from utils import bytesToHexString, bytesToLong, longToHexString, stringToBytes, garbageBytes20, garbageBytes32, twentyZeros, thirtyTwoZeros
from copy import deepcopy

# Make TXs free.
ethereum.opcodes.GCONTRACTBYTE = 0
ethereum.opcodes.GTXDATAZERO = 0
ethereum.opcodes.GTXDATANONZERO = 0

# Monkeypatch to bypass the contract size limit
def monkey_post_spurious_dragon_hardfork():
    return False

original_create_contract = ethereum.messages.create_contract

def new_create_contract(ext, msg):
    old_post_spurious_dragon_hardfork_check = ext.post_spurious_dragon_hardfork
    ext.post_spurious_dragon_hardfork = monkey_post_spurious_dragon_hardfork
    res, gas, dat = original_create_contract(ext, msg)
    ext.post_spurious_dragon_hardfork = old_post_spurious_dragon_hardfork_check
    return res, gas, dat

ethereum.messages.create_contract = new_create_contract

# used to resolve relative paths
BASE_PATH = path.dirname(path.abspath(__file__))
def resolveRelativePath(relativeFilePath):
    return path.abspath(path.join(BASE_PATH, relativeFilePath))
COMPILATION_CACHE = resolveRelativePath('./compilation_cache')

class bcolors:
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

CONTRACT_SIZE_LIMIT = 24576.0
CONTRACT_SIZE_WARN_LEVEL = CONTRACT_SIZE_LIMIT * 0.75

def pytest_addoption(parser):
    parser.addoption("--cover", action="store_true", help="Use the coverage enabled contracts. Meant to be used with the tools/generateCoverageReport.js script")

def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers",
        "cover: use coverage contracts")

class ContractsFixture:
    signatures = {}
    compiledCode = {}

    ####
    #### Static Methods
    ####

    @staticmethod
    def ensureCacheDirectoryExists():
        if not path.exists(COMPILATION_CACHE):
            makedirs(COMPILATION_CACHE)

    def generateSignature(self, relativeFilePath):
        ContractsFixture.ensureCacheDirectoryExists()
        filename = path.basename(relativeFilePath)
        name = path.splitext(filename)[0]
        outputPath = path.join(COMPILATION_CACHE,  name + 'Signature')
        lastCompilationTime = path.getmtime(outputPath) if path.isfile(outputPath) else 0
        if path.getmtime(relativeFilePath) > lastCompilationTime:
            print('generating signature for ' + name)
            extension = path.splitext(filename)[1]
            signature = None
            if extension == '.sol':
                signature = self.compileSolidity(relativeFilePath)['abi']
            else:
                raise
            with open(outputPath, mode='w') as file:
                json_dump(signature, file)
        else:
            pass#print('using cached signature for ' + name)
        with open(outputPath, 'r') as file:
            signature = json_load(file)
        return(signature)

    def getCompiledCode(self, relativeFilePath):
        filename = path.basename(relativeFilePath)
        name = path.splitext(filename)[0]
        if name in ContractsFixture.compiledCode:
            return ContractsFixture.compiledCode[name]
        dependencySet = set()
        self.getAllDependencies(relativeFilePath, dependencySet)
        ContractsFixture.ensureCacheDirectoryExists()
        compiledOutputPath = path.join(COMPILATION_CACHE, name)
        lastCompilationTime = path.getmtime(compiledOutputPath) if path.isfile(compiledOutputPath) else 0
        needsRecompile = False
        for dependencyPath in dependencySet:
            if (path.getmtime(dependencyPath) > lastCompilationTime):
                needsRecompile = True
                break
        if (needsRecompile):
            print('compiling ' + name + '...')
            extension = path.splitext(filename)[1]
            compiledCode = None
            if extension == '.sol':
                compiledCode = bytearray.fromhex(self.compileSolidity(relativeFilePath)['evm']['bytecode']['object'])
            else:
                raise
            with io_open(compiledOutputPath, mode='wb') as file:
                file.write(compiledCode)
        else:
            pass#print('using cached compilation for ' + name)
        with io_open(compiledOutputPath, mode='rb') as file:
            compiledCode = file.read()
            contractSize = len(compiledCode)
            if (contractSize >= CONTRACT_SIZE_LIMIT):
                print('%sContract %s is OVER the size limit by %d bytes%s' % (bcolors.FAIL, name, contractSize - CONTRACT_SIZE_LIMIT, bcolors.ENDC))
            elif (contractSize >= CONTRACT_SIZE_WARN_LEVEL):
                print('%sContract %s is under size limit by only %d bytes%s' % (bcolors.WARN, name, CONTRACT_SIZE_LIMIT - contractSize, bcolors.ENDC))
            elif (contractSize > 0):
                pass#print('Size: %i' % contractSize)
            ContractsFixture.compiledCode[name] = compiledCode
            return(compiledCode)

    def compileSolidity(self, relativeFilePath):
        absoluteFilePath = resolveRelativePath(relativeFilePath)
        filename = path.basename(relativeFilePath)
        contractName = path.splitext(filename)[0]
        print absoluteFilePath
        compilerParameter = {
            'language': 'Solidity',
            'sources': {
                absoluteFilePath: {
                    'urls': [ absoluteFilePath ]
                }
            },
            'settings': {
                # TODO: Remove 'remappings' line below and update 'sources' line above
                'remappings': [ '=%s/' % resolveRelativePath(self.relativeContractsPath), 'TEST=%s/' % resolveRelativePath(self.relativeTestContractsPath) ],
                'optimizer': {
                    'enabled': True,
                    'runs': 500
                },
                'outputSelection': {
                    "*": {
                        '*': [ 'metadata', 'evm.bytecode', 'evm.sourceMap', 'abi' ]
                    }
                }
            }
        }
        return compile_standard(compilerParameter, allow_paths=resolveRelativePath("../"))['contracts'][absoluteFilePath][contractName]

    def getAllDependencies(self, filePath, knownDependencies):
        knownDependencies.add(filePath)
        fileDirectory = path.dirname(filePath)
        with open(filePath, 'r') as file:
            fileContents = file.read()
        matches = findall("inset\('(.*?)'\)", fileContents)
        for match in matches:
            dependencyPath = path.abspath(path.join(fileDirectory, match))
            if not dependencyPath in knownDependencies:
                self.getAllDependencies(dependencyPath, knownDependencies)
        matches = findall("create\('(.*?)'\)", fileContents)
        for match in matches:
            dependencyPath = path.abspath(path.join(fileDirectory, match))
            if not dependencyPath in knownDependencies:
                self.getAllDependencies(dependencyPath, knownDependencies)
        matches = findall("import ['\"](.*?)['\"]", fileContents)
        for match in matches:
            dependencyPath = path.join(BASE_PATH, self.relativeContractsPath, match)
            if "TEST" in dependencyPath:
                dependencyPath = path.join(BASE_PATH, self.relativeTestContractsPath, match).replace("TEST/", "")
            if not path.isfile(dependencyPath):
                raise Exception("Could not resolve dependency file path: %s" % dependencyPath)
            if not dependencyPath in knownDependencies:
                self.getAllDependencies(dependencyPath, knownDependencies)
        return(knownDependencies)

    ####
    #### Class Methods
    ####

    def __init__(self):
        tester.GASPRICE = 0
        tester.STARTGAS = long(6.7 * 10**7)
        config_metropolis['GASLIMIT_ADJMAX_FACTOR'] = .000000000001
        config_metropolis['GENESIS_GAS_LIMIT'] = 2**60
        config_metropolis['MIN_GAS_LIMIT'] = 2**60
        config_metropolis['BLOCK_GAS_LIMIT'] = 2**60

        for a in range(10):
            tester.base_alloc[getattr(tester, 'a%i' % a)] = {'balance': 10**24}

        self.chain = Chain(env=Env(config=config_metropolis))
        self.contracts = {}
        self.testerAddress = self.generateTesterMap('a')
        self.testerKey = self.generateTesterMap('k')
        self.testerAddressToKey = dict(zip(self.testerAddress.values(), self.testerKey.values()))
        if path.isfile('./allFiredEvents'):
            remove_file('./allFiredEvents')
        self.relativeContractsPath = '../source/contracts'
        self.relativeTestContractsPath = 'solidity_test_helpers'
        self.coverageMode = pytest.config.option.cover
        if self.coverageMode:
            self.chain.head_state.log_listeners.append(self.writeLogToFile)
            self.relativeContractsPath = '../coverageEnv/contracts'
            self.relativeTestContractsPath = '../coverageEnv/solidity_test_helpers'


    def writeLogToFile(self, message):
        with open('./allFiredEvents', 'a') as logsFile:
            logsFile.write(json_dumps(message.to_dict()) + '\n')

    def distributeRep(self, universe):
        # Get the reputation token for this universe and migrate legacy REP to it
        reputationToken = self.applySignature('ReputationToken', universe.getReputationToken())
        reputationToken.migrateBalancesFromLegacyRep([tester.a0])

    def generateTesterMap(self, ch):
        testers = {}
        for i in range(0,9):
            testers[i] = getattr(tester, ch + "%d" % i)
        return testers

    def uploadAndAddToController(self, relativeFilePath, lookupKey = None, signatureKey = None, constructorArgs=[]):
        lookupKey = lookupKey if lookupKey else path.splitext(path.basename(relativeFilePath))[0]
        contract = self.upload(relativeFilePath, lookupKey, signatureKey, constructorArgs)
        if not contract: return None
        self.contracts['Controller'].registerContract(lookupKey.ljust(32, '\x00'), contract.address, garbageBytes20, garbageBytes32)
        return(contract)

    def upload(self, relativeFilePath, lookupKey = None, signatureKey = None, constructorArgs=[]):
        resolvedPath = resolveRelativePath(relativeFilePath)
        if self.coverageMode:
            resolvedPath = resolvedPath.replace("tests", "coverageEnv").replace("source/", "coverageEnv/")
        lookupKey = lookupKey if lookupKey else path.splitext(path.basename(resolvedPath))[0]
        signatureKey = signatureKey if signatureKey else lookupKey
        if lookupKey in self.contracts:
            return(self.contracts[lookupKey])
        compiledCode = self.getCompiledCode(resolvedPath)
        # abstract contracts have a 0-length array for bytecode
        if len(compiledCode) == 0:
            if ("libraries" in relativeFilePath or lookupKey.startswith("I") or lookupKey.startswith("Base")):
                pass#print "Skipping upload of " + lookupKey + " because it had no bytecode (likely a abstract class/interface)."
            else:
                raise Exception("Contract: " + lookupKey + " has no bytecode, but this is not expected. It probably doesn't implement all its abstract methods")
            return None
        if signatureKey not in ContractsFixture.signatures:
            ContractsFixture.signatures[signatureKey] = self.generateSignature(resolvedPath)
        signature = ContractsFixture.signatures[signatureKey]
        contractTranslator = ContractTranslator(signature)
        if len(constructorArgs) > 0:
            compiledCode += contractTranslator.encode_constructor_arguments(constructorArgs)
        contractAddress = bytesToHexString(self.chain.contract(compiledCode, language='evm'))
        contract = ABIContract(self.chain, contractTranslator, contractAddress)
        self.contracts[lookupKey] = contract
        return(contract)

    def applySignature(self, signatureName, address):
        assert address
        if type(address) is long:
            address = longToHexString(address)
        translator = ContractTranslator(ContractsFixture.signatures[signatureName])
        contract = ABIContract(self.chain, translator, address)
        return contract

    def createSnapshot(self):
        self.chain.tx(sender=tester.k0, to=tester.a1, value=0)
        self.chain.mine(1)
        contractsCopy = {}
        for contractName in self.contracts:
            contractsCopy[contractName] = dict(translator = self.contracts[contractName].translator, address = self.contracts[contractName].address)
        return  { 'state': self.chain.head_state.to_snapshot(), 'contracts': contractsCopy }

    def resetToSnapshot(self, snapshot):
        if not 'state' in snapshot: raise "snapshot is missing 'state'"
        if not 'contracts' in snapshot: raise "snapshot is missing 'contracts'"
        self.chain = Chain(genesis=snapshot['state'], env=Env(config=config_metropolis))
        if self.coverageMode:
            self.chain.head_state.log_listeners.append(self.writeLogToFile)
        self.contracts = {}
        for contractName in snapshot['contracts']:
            contract = snapshot['contracts'][contractName]
            self.contracts[contractName] = ABIContract(self.chain, contract['translator'], contract['address'])

    ####
    #### Bulk Operations
    ####

    def uploadAllContracts(self):
        for directory, _, filenames in walk(resolveRelativePath(self.relativeContractsPath)):
            # skip the legacy reputation directory since it is unnecessary and we don't support uploads of contracts with constructors yet
            if 'legacy_reputation' in directory: continue
            for filename in filenames:
                name = path.splitext(filename)[0]
                extension = path.splitext(filename)[1]
                if extension != '.sol': continue
                if name == 'controller': continue
                if name == 'Augur': continue
                if name == 'Time': continue # In testing and development we swap the Time library for a ControlledTime version which lets us manage block timestamp
                contractsToDelegate = ['Orders', 'TradingEscapeHatch', 'Cash']
                if name in contractsToDelegate:
                    delegationTargetName = "".join([name, "Target"])
                    self.uploadAndAddToController(path.join(directory, filename), delegationTargetName, name)
                    self.uploadAndAddToController("../source/contracts/libraries/Delegator.sol", name, "delegator", constructorArgs=[self.contracts['Controller'].address, delegationTargetName.ljust(32, '\x00')])
                    self.contracts[name] = self.applySignature(name, self.contracts[name].address)
                elif name == "TimeControlled":
                    self.uploadAndAddToController(path.join(directory, filename), lookupKey = "Time", signatureKey = "TimeControlled")
                elif name == "Trade":
                    self.uploadAndAddToController("solidity_test_helpers/TestTrade.sol", lookupKey = "Trade", signatureKey = "Trade")
                else:
                    self.uploadAndAddToController(path.join(directory, filename))

    def uploadAllMockContracts(self):
        for directory, _, filenames in walk(resolveRelativePath(self.relativeTestContractsPath)):
            for filename in filenames:
                name = path.splitext(filename)[0]
                extension = path.splitext(filename)[1]
                if extension != '.sol': continue
                if not name.startswith('Mock'): continue
                if 'Factory' in name:
                    self.upload(path.join(directory, filename))
                else:
                    self.uploadAndAddToController(path.join(directory, filename))


    def whitelistTradingContracts(self):
        for filename in listdir(resolveRelativePath('../source/contracts/trading')):
            name = path.splitext(filename)[0]
            extension = path.splitext(filename)[1]
            if extension != '.sol': continue
            if name == "ShareToken": continue
            if not name in self.contracts: continue
            self.contracts['Controller'].addToWhitelist(self.contracts[name].address)

    def initializeAllContracts(self):
        contractsToInitialize = ['CompleteSets','CreateOrder','FillOrder','CancelOrder','Trade','ClaimTradingProceeds','OrdersFetcher', 'Time']
        for contractName in contractsToInitialize:
            if getattr(self.contracts[contractName], "setController", None):
                self.contracts[contractName].setController(self.contracts['Controller'].address)
            elif getattr(self.contracts[contractName], "initialize", None):
                self.contracts[contractName].initialize(self.contracts['Controller'].address)
            else:
                raise "contract has neither 'initialize' nor 'setController' method on it."

    ####
    #### Helpers
    ####

    def getSeededCash(self):
        cash = self.contracts['Cash']
        cash.depositEther(value = 1, sender = tester.k9)
        return cash

    def approveCentralAuthority(self):
        authority = self.contracts['Augur']
        contractsToApprove = ['Cash']
        testersGivingApproval = [getattr(tester, 'k%i' % x) for x in range(0,10)]
        for testerKey in testersGivingApproval:
            for contractName in contractsToApprove:
                self.contracts[contractName].approve(authority.address, 2**254, sender=testerKey)

    def uploadAugur(self):
        # We have to upload Augur first so it can log when contracts are added to the registry
        augur = self.upload("../source/contracts/Augur.sol")
        self.contracts["Augur"].setController(self.contracts['Controller'].address)
        self.contracts['Controller'].registerContract("Augur".ljust(32, '\x00'), augur.address, garbageBytes20, garbageBytes32)
        return augur

    def uploadShareToken(self, controllerAddress = None):
        controllerAddress = controllerAddress if controllerAddress else self.contracts['Controller'].address
        self.ensureShareTokenDependencies()
        shareTokenFactory = self.contracts['ShareTokenFactory']
        shareToken = shareTokenFactory.createShareToken(controllerAddress)
        return self.applySignature('shareToken', shareToken)

    def createUniverse(self):
        universeAddress = self.contracts['Augur'].createGenesisUniverse()
        universe = self.applySignature('Universe', universeAddress)
        assert universe.getTypeName() == stringToBytes('Universe')
        return universe

    def getShareToken(self, market, outcome):
        shareTokenAddress = market.getShareToken(outcome)
        assert shareTokenAddress
        shareToken = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['ShareToken']), shareTokenAddress)
        return shareToken

    def getOrCreateChildUniverse(self, parentUniverse, market, payoutDistribution):
        assert payoutDistributionHash
        childUniverseAddress = parentUniverse.getOrCreateChildUniverse(payoutDistribution, False)
        assert childUniverseAddress
        childUniverse = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['Universe']), childUniverseAddress)
        return childUniverse

    def createBinaryMarket(self, universe, endTime, feePerEthInWei, denominationToken, designatedReporterAddress, sender=tester.k0, topic="", description="description", extraInfo=""):
        marketCreationFee = universe.getOrCacheMarketCreationCost()
        marketAddress = universe.createBinaryMarket(endTime, feePerEthInWei, denominationToken.address, designatedReporterAddress, topic, description, extraInfo, value = marketCreationFee, sender=sender)
        assert marketAddress
        market = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['Market']), marketAddress)
        return market

    def createCategoricalMarket(self, universe, numOutcomes, endTime, feePerEthInWei, denominationToken, designatedReporterAddress, sender=tester.k0, topic="", description="description", extraInfo=""):
        marketCreationFee = universe.getOrCacheMarketCreationCost()
        outcomes = [" "] * numOutcomes
        marketAddress = universe.createCategoricalMarket(endTime, feePerEthInWei, denominationToken.address, designatedReporterAddress, outcomes, topic, description, extraInfo, value = marketCreationFee, sender=sender)
        assert marketAddress
        market = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['Market']), marketAddress)
        return market

    def createScalarMarket(self, universe, endTime, feePerEthInWei, denominationToken, maxPrice, minPrice, numTicks, designatedReporterAddress, sender=tester.k0, description="description", extraInfo=""):
        marketCreationFee = universe.getOrCacheMarketCreationCost()
        marketAddress = universe.createScalarMarket(endTime, feePerEthInWei, denominationToken.address, designatedReporterAddress, minPrice, maxPrice, numTicks, "", description, extraInfo, value = marketCreationFee, sender=sender)
        assert marketAddress
        market = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['Market']), marketAddress)
        return market

    def createReasonableBinaryMarket(self, universe, denominationToken, sender=tester.k0, topic="", description="description", extraInfo=""):
        return self.createBinaryMarket(
            universe = universe,
            endTime = long(self.contracts["Time"].getTimestamp() + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = denominationToken,
            designatedReporterAddress = tester.a0,
            sender = sender,
            topic= topic,
            description= description,
            extraInfo= extraInfo)

    def createReasonableCategoricalMarket(self, universe, numOutcomes, denominationToken, sender=tester.k0):
        return self.createCategoricalMarket(
            universe = universe,
            numOutcomes = numOutcomes,
            endTime = long(self.contracts["Time"].getTimestamp() + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = denominationToken,
            designatedReporterAddress = tester.a0,
            sender = sender)

    def createReasonableScalarMarket(self, universe, maxPrice, minPrice, numTicks, denominationToken, sender=tester.k0):
        return self.createScalarMarket(
            universe = universe,
            endTime = long(self.contracts["Time"].getTimestamp() + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = denominationToken,
            maxPrice= maxPrice,
            minPrice= minPrice,
            numTicks= numTicks,
            designatedReporterAddress = tester.a0,
            sender = sender)

@pytest.fixture(scope="session")
def fixture():
    return ContractsFixture()

@pytest.fixture(scope="session")
def baseSnapshot(fixture):
    return fixture.createSnapshot()

@pytest.fixture(scope="session")
def controllerSnapshot(fixture, baseSnapshot):
    fixture.resetToSnapshot(baseSnapshot)
    controller = fixture.upload('solidity_test_helpers/TestController.sol', lookupKey="Controller")
    assert fixture.contracts['Controller'].owner() == bytesToHexString(tester.a0)
    return fixture.createSnapshot()

@pytest.fixture(scope="session")
def augurInitializedSnapshot(fixture, controllerSnapshot):
    fixture.resetToSnapshot(controllerSnapshot)
    fixture.uploadAugur()
    fixture.uploadAllContracts()
    fixture.initializeAllContracts()
    fixture.whitelistTradingContracts()
    fixture.approveCentralAuthority()
    return fixture.createSnapshot()

@pytest.fixture(scope="session")
def augurInitializedWithMocksSnapshot(fixture, augurInitializedSnapshot):
    fixture.uploadAndAddToController("solidity_test_helpers/Constants.sol")
    fixture.uploadAllMockContracts()
    controller = fixture.contracts['Controller']
    mockAugur = fixture.contracts['MockAugur']
    controller.registerContract(stringToBytes('Augur'), mockAugur.address, twentyZeros, thirtyTwoZeros)
    return fixture.createSnapshot()

@pytest.fixture(scope="session")
def kitchenSinkSnapshot(fixture, augurInitializedSnapshot):
    fixture.resetToSnapshot(augurInitializedSnapshot)
    # TODO: remove assignments to the fixture as they don't get rolled back, so can bleed across tests.  We should be accessing things via `fixture.contracts[...]`
    legacyReputationToken = fixture.contracts['LegacyReputationToken']
    legacyReputationToken.faucet(11 * 10**6 * 10**18)
    universe = fixture.createUniverse()
    cash = fixture.getSeededCash()
    augur = fixture.contracts['Augur']
    fixture.distributeRep(universe)
    binaryMarket = fixture.createReasonableBinaryMarket(universe, cash)
    startingGas = fixture.chain.head_state.gas_used
    categoricalMarket = fixture.createReasonableCategoricalMarket(universe, 3, cash)
    print 'Gas Used: %s' % (fixture.chain.head_state.gas_used - startingGas)
    scalarMarket = fixture.createReasonableScalarMarket(universe, 30, -10, 400000, cash)
    fixture.uploadAndAddToController("solidity_test_helpers/Constants.sol")
    snapshot = fixture.createSnapshot()
    snapshot['universe'] = universe
    snapshot['cash'] = cash
    snapshot['augur'] = augur
    snapshot['binaryMarket'] = binaryMarket
    snapshot['categoricalMarket'] = categoricalMarket
    snapshot['scalarMarket'] = scalarMarket
    return snapshot

@pytest.fixture
def kitchenSinkFixture(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    return fixture

@pytest.fixture
def universe(kitchenSinkFixture, kitchenSinkSnapshot):
    return ABIContract(kitchenSinkFixture.chain, kitchenSinkSnapshot['universe'].translator, kitchenSinkSnapshot['universe'].address)

@pytest.fixture
def cash(kitchenSinkFixture, kitchenSinkSnapshot):
    return ABIContract(kitchenSinkFixture.chain, kitchenSinkSnapshot['cash'].translator, kitchenSinkSnapshot['cash'].address)

@pytest.fixture
def augur(kitchenSinkFixture, kitchenSinkSnapshot):
    return ABIContract(kitchenSinkFixture.chain, kitchenSinkSnapshot['augur'].translator, kitchenSinkSnapshot['augur'].address)

@pytest.fixture
def market(kitchenSinkFixture, kitchenSinkSnapshot):
    return ABIContract(kitchenSinkFixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)

@pytest.fixture
def binaryMarket(kitchenSinkFixture, kitchenSinkSnapshot):
    return ABIContract(kitchenSinkFixture.chain, kitchenSinkSnapshot['binaryMarket'].translator, kitchenSinkSnapshot['binaryMarket'].address)

@pytest.fixture
def categoricalMarket(kitchenSinkFixture, kitchenSinkSnapshot):
    return ABIContract(kitchenSinkFixture.chain, kitchenSinkSnapshot['categoricalMarket'].translator, kitchenSinkSnapshot['categoricalMarket'].address)

@pytest.fixture
def scalarMarket(kitchenSinkFixture, kitchenSinkSnapshot):
    return ABIContract(kitchenSinkFixture.chain, kitchenSinkSnapshot['scalarMarket'].translator, kitchenSinkSnapshot['scalarMarket'].address)

# TODO: globally replace this with `fixture` and `kitchenSinkSnapshot` as appropriate then delete this
@pytest.fixture(scope="session")
def sessionFixture(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    return fixture

@pytest.fixture
def contractsFixture(fixture, kitchenSinkSnapshot):
    fixture.resetToSnapshot(kitchenSinkSnapshot)
    return fixture

@pytest.fixture
def augurInitializedFixture(fixture, augurInitializedSnapshot):
    fixture.resetToSnapshot(augurInitializedSnapshot)
    return fixture
