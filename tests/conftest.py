from binascii import hexlify
from datetime import timedelta
from ethereum.tools import tester
from ethereum.abi import ContractTranslator
from ethereum.tools.tester import ABIContract
from ethereum.config import config_metropolis, Env
from io import open as io_open
from json import dump as json_dump, load as json_load
from os import path, walk, makedirs, listdir
from pytest import fixture
from re import findall
from solc import compile_standard
from utils import bytesToHexString, bytesToLong, longToHexString
from copy import deepcopy

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

    @staticmethod
    def generateSignature(relativeFilePath):
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
                signature = ContractsFixture.compileSolidity(relativeFilePath)['abi']
            else:
                raise
            with open(outputPath, mode='w') as file:
                json_dump(signature, file)
        else:
            print('using cached signature for ' + name)
        with open(outputPath, 'r') as file:
            signature = json_load(file)
        return(signature)

    @staticmethod
    def getCompiledCode(relativeFilePath):
        filename = path.basename(relativeFilePath)
        name = path.splitext(filename)[0]
        if name in ContractsFixture.compiledCode:
            return ContractsFixture.compiledCode[name]
        dependencySet = set()
        ContractsFixture.getAllDependencies(relativeFilePath, dependencySet)
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
                compiledCode = bytearray.fromhex(ContractsFixture.compileSolidity(relativeFilePath)['evm']['bytecode']['object'])
            else:
                raise
            with io_open(compiledOutputPath, mode='wb') as file:
                file.write(compiledCode)
        else:
            print('using cached compilation for ' + name)
        with io_open(compiledOutputPath, mode='rb') as file:
            compiledCode = file.read()
            contractSize = len(compiledCode)
            if (contractSize >= CONTRACT_SIZE_LIMIT):
                print('%sContract %s is OVER the size limit by %d bytes%s' % (bcolors.FAIL, name, contractSize - CONTRACT_SIZE_LIMIT, bcolors.ENDC))
            elif (contractSize >= CONTRACT_SIZE_WARN_LEVEL):
                print('%sContract %s is under size limit by only %d bytes%s' % (bcolors.WARN, name, CONTRACT_SIZE_LIMIT - contractSize, bcolors.ENDC))
            elif (contractSize > 0):
                print('Size: %i' % contractSize)
            ContractsFixture.compiledCode[name] = compiledCode
            return(compiledCode)

    @staticmethod
    def compileSolidity(relativeFilePath):
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
                'remappings': [ '=%s/' % resolveRelativePath("../source/contracts") ],
                'optimizer': {
                    'enabled': True,
                    'runs': 500
                },
                'outputSelection': {
                    '*': [ 'metadata', 'evm.bytecode', 'evm.sourceMap' ]
                }
            }
        }
        return compile_standard(compilerParameter, allow_paths=resolveRelativePath("../"))['contracts'][absoluteFilePath][contractName]

    @staticmethod
    def getAllDependencies(filePath, knownDependencies):
        knownDependencies.add(filePath)
        fileDirectory = path.dirname(filePath)
        with open(filePath, 'r') as file:
            fileContents = file.read()
        matches = findall("inset\('(.*?)'\)", fileContents)
        for match in matches:
            dependencyPath = path.abspath(path.join(fileDirectory, match))
            if not dependencyPath in knownDependencies:
                ContractsFixture.getAllDependencies(dependencyPath, knownDependencies)
        matches = findall("create\('(.*?)'\)", fileContents)
        for match in matches:
            dependencyPath = path.abspath(path.join(fileDirectory, match))
            if not dependencyPath in knownDependencies:
                ContractsFixture.getAllDependencies(dependencyPath, knownDependencies)
        matches = findall("import ['\"](.*?)['\"]", fileContents)
        for match in matches:
            dependencyPath = path.join(BASE_PATH, '..', 'source/contracts', match)
            if not dependencyPath in knownDependencies:
                ContractsFixture.getAllDependencies(dependencyPath, knownDependencies)
        return(knownDependencies)

    ####
    #### Class Methods
    ####

    def __init__(self):
        tester.GASPRICE = 0
        config_metropolis['GASLIMIT_ADJMAX_FACTOR'] = .000000000001
        config_metropolis['GENESIS_GAS_LIMIT'] = 2**60
        config_metropolis['MIN_GAS_LIMIT'] = 2**60
        config_metropolis['BLOCK_GAS_LIMIT'] = 2**60

        for a in range(10):
            tester.base_alloc[getattr(tester, 'a%i' % a)] = {'balance': 10**24}

        self.chain = tester.Chain(env=Env(config=config_metropolis))
        self.contracts = {}
        self.controller = self.upload('../source/contracts/Controller.sol')
        assert self.controller.owner() == bytesToHexString(tester.a0)
        self.uploadAllContracts()
        self.whitelistTradingContracts()
        self.initializeAllContracts()
        self.approveCentralAuthority()
        self.universe = self.createUniverse(0, "")
        self.cash = self.getSeededCash()
        self.augur = self.contracts['Augur']
        self.utils = self.upload("solidity_test_helpers/Utils.sol")
        self.distributeRep()
        self.binaryMarket = self.createReasonableBinaryMarket(self.universe, self.cash)
        startingGas = self.chain.head_state.gas_used
        self.categoricalMarket = self.createReasonableCategoricalMarket(self.universe, 3, self.cash)
        print 'Gas Used: %s' % (self.chain.head_state.gas_used - startingGas)
        self.scalarMarket = self.createReasonableScalarMarket(self.universe, 40, self.cash)
        self.constants = self.uploadAndAddToController("solidity_test_helpers/Constants.sol")
        self.chain.mine(1)
        self.originalContracts = deepcopy(self.contracts)
        self.captured = self.createSnapshot()
        self.testerAddress = self.generateTesterMap('a')
        self.testerKey = self.generateTesterMap('k')

    def distributeRep(self):
        legacyRepContract = self.contracts['LegacyRepContract']
        legacyRepContract.faucet(11 * 10**6 * 10**18)
        universe = self.universe

        # Get the reputation token for this universe and migrate legacy REP to it
        reputationToken = self.applySignature('ReputationToken', universe.getReputationToken())
        legacyRepContract.approve(reputationToken.address, 11 * 10**6 * 10**18)
        reputationToken.migrateFromLegacyRepContract()

    def generateTesterMap(self, ch):
        testers = {}
        for i in range(0,9):
            testers[i] = getattr(tester, ch + "%d" % i)
        return testers

    def uploadAndAddToController(self, relativeFilePath, lookupKey = None, signatureKey = None, constructorArgs=[]):
        lookupKey = lookupKey if lookupKey else path.splitext(path.basename(relativeFilePath))[0]
        contract = self.upload(relativeFilePath, lookupKey, signatureKey, constructorArgs)
        if not contract: return None
        self.controller.setValue(lookupKey.ljust(32, '\x00'), contract.address)
        return(contract)

    def upload(self, relativeFilePath, lookupKey = None, signatureKey = None, constructorArgs=[]):
        resolvedPath = resolveRelativePath(relativeFilePath)
        lookupKey = lookupKey if lookupKey else path.splitext(path.basename(resolvedPath))[0]
        signatureKey = signatureKey if signatureKey else lookupKey
        if lookupKey in self.contracts:
            return(self.contracts[lookupKey])
        compiledCode = ContractsFixture.getCompiledCode(resolvedPath)
        # abstract contracts have a 0-length array for bytecode
        if len(compiledCode) == 0:
            print "Skipping upload of " + lookupKey + " because it had no bytecode (likely a abstract class/interface)."
            return None
        if signatureKey not in ContractsFixture.signatures:
            ContractsFixture.signatures[signatureKey] = ContractsFixture.generateSignature(resolvedPath)
        signature = ContractsFixture.signatures[signatureKey]
        contractTranslator = ContractTranslator(signature)
        if len(constructorArgs) > 0:
            compiledCode += contractTranslator.encode_constructor_arguments(constructorArgs)
        contractAddress = bytesToHexString(self.chain.contract(compiledCode, language='evm', startgas=long(6.7 * 10**6)))
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

    def resetSnapshot(self):
        self.resetToSnapshot(self.captured)

    def createSnapshot(self):
        return  { 'block': self.chain.block, 'head_state': self.chain.head_state, 'snapshot': self.chain.snapshot(), 'contracts': deepcopy(self.contracts) }

    def resetToSnapshot(self, captured):
        if len(captured) < 4:
            raise "captured snapshot doesn't have all parameters in dictionary, need to call createSnapshot"
        self.chain.block = captured['block']
        self.chain.head_state = captured['head_state']
        self.chain.revert(captured['snapshot'])
        self.contracts = deepcopy(captured['contracts'])

    ####
    #### Bulk Operations
    ####

    def uploadAllContracts(self):
        for directory, _, filenames in walk(resolveRelativePath('../source/contracts')):
            # skip the legacy reputation directory since it is unnecessary and we don't support uploads of contracts with constructors yet
            if 'legacy_reputation' in directory: continue
            for filename in filenames:
                name = path.splitext(filename)[0]
                extension = path.splitext(filename)[1]
                if extension != '.sol': continue
                if name == 'controller': continue
                contractsToDelegate = ['Orders', 'TradingEscapeHatch']
                if name in contractsToDelegate:
                    delegationTargetName = "".join([name, "Target"])
                    self.uploadAndAddToController(path.join(directory, filename), delegationTargetName, name)
                    self.uploadAndAddToController("../source/contracts/libraries/Delegator.sol", name, "delegator", constructorArgs=[self.controller.address, delegationTargetName.ljust(32, '\x00')])
                    self.contracts[name] = self.applySignature(name, self.contracts[name].address)
                else:
                    self.uploadAndAddToController(path.join(directory, filename))

    def whitelistTradingContracts(self):
        for filename in listdir(resolveRelativePath('../source/contracts/trading')):
            name = path.splitext(filename)[0]
            extension = path.splitext(filename)[1]
            if extension != '.sol': continue
            if not name in self.contracts: continue
            self.controller.addToWhitelist(self.contracts[name].address)

    def initializeAllContracts(self):
        contractsToInitialize = ['Augur','Cash','CompleteSets','CreateOrder','FillOrder','CancelOrder','Trade','ClaimProceeds','OrdersFetcher']
        for contractName in contractsToInitialize:
            if getattr(self.contracts[contractName], "setController", None):
                self.contracts[contractName].setController(self.controller.address)
            elif getattr(self.contracts[contractName], "initialize", None):
                self.contracts[contractName].initialize(self.controller.address)
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

    def uploadShareToken(self, controllerAddress = None):
        controllerAddress = controllerAddress if controllerAddress else self.controller.address
        self.ensureShareTokenDependencies()
        shareTokenFactory = self.contracts['ShareTokenFactory']
        shareToken = shareTokenFactory.createShareToken(controllerAddress)
        return self.applySignature('shareToken', shareToken)

    def createUniverse(self, parentUniverse, payoutDistributionHash):
        universeAddress = self.contracts['UniverseFactory'].createUniverse(self.controller.address, parentUniverse, payoutDistributionHash)
        universe = self.applySignature('Universe', universeAddress)
        return universe

    def getReportingToken(self, market, payoutDistribution):
        reportingTokenAddress = market.getReportingToken(payoutDistribution)
        assert reportingTokenAddress
        reportingToken = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['ReportingToken']), reportingTokenAddress)
        return reportingToken

    def getShareToken(self, market, outcome):
        shareTokenAddress = market.getShareToken(outcome)
        assert shareTokenAddress
        shareToken = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['ShareToken']), shareTokenAddress)
        return shareToken

    def designatedReport(self, market, payoutDistribution, reporterKey):
        reportingToken = self.getReportingToken(market, payoutDistribution)
        designatedReportStake = self.contracts['MarketFeeCalculator'].getDesignatedReportStake(market.getReportingWindow())
        return reportingToken.buy(designatedReportStake, sender=reporterKey)

    def getOrCreateChildUniverse(self, parentUniverse, market, payoutDistribution):
        payoutDistributionHash = market.derivePayoutDistributionHash(payoutDistribution)
        assert payoutDistributionHash
        childUniverseAddress = parentUniverse.getOrCreateChildUniverse(payoutDistributionHash)
        assert childUniverseAddress
        childUniverse = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['Universe']), childUniverseAddress)
        return(childUniverse)

    def createBinaryMarket(self, universe, endTime, feePerEthInWei, denominationToken, designatedReporterAddress, numTicks):
        return self.createCategoricalMarket(universe, 2, endTime, feePerEthInWei, denominationToken, designatedReporterAddress, numTicks)

    def createCategoricalMarket(self, universe, numOutcomes, endTime, feePerEthInWei, denominationToken, designatedReporterAddress, numTicks):
        reportingWindowAddress = universe.getReportingWindowByMarketEndTime(endTime)
        marketCreationFee = self.contracts['MarketFeeCalculator'].getValidityBond(reportingWindowAddress) + self.contracts['MarketFeeCalculator'].getTargetReporterGasCosts(reportingWindowAddress)
        marketAddress = self.contracts['MarketCreation'].createMarket(universe.address, endTime, numOutcomes, feePerEthInWei, denominationToken.address, numTicks, designatedReporterAddress, value = marketCreationFee, startgas=long(6.7 * 10**6))
        assert marketAddress
        market = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['Market']), marketAddress)
        return market

    def createScalarMarket(self, universe, endTime, feePerEthInWei, denominationToken, numTicks, designatedReporterAddress):
        reportingWindowAddress = universe.getReportingWindowByMarketEndTime(endTime)
        marketCreationFee = self.contracts['MarketFeeCalculator'].getValidityBond(reportingWindowAddress) + self.contracts['MarketFeeCalculator'].getTargetReporterGasCosts(reportingWindowAddress)
        marketAddress = self.contracts['MarketCreation'].createMarket(universe.address, endTime, 2, feePerEthInWei, denominationToken.address, numTicks, designatedReporterAddress, value = marketCreationFee)
        assert marketAddress
        market = ABIContract(self.chain, ContractTranslator(ContractsFixture.signatures['Market']), marketAddress)
        return market

    def createReasonableBinaryMarket(self, universe, denominationToken):
        return self.createBinaryMarket(
            universe = universe,
            endTime = long(self.chain.head_state.timestamp + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = denominationToken,
            designatedReporterAddress = tester.a0,
            numTicks = 10 ** 18)

    def createReasonableCategoricalMarket(self, universe, numOutcomes, denominationToken):
        return self.createCategoricalMarket(
            universe = universe,
            numOutcomes = numOutcomes,
            endTime = long(self.chain.head_state.timestamp + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = denominationToken,
            designatedReporterAddress = tester.a0,
            numTicks = 3 * 10 ** 17)

    def createReasonableScalarMarket(self, universe, priceRange, denominationToken):
        return self.createScalarMarket(
            universe = universe,
            endTime = long(self.chain.head_state.timestamp + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = denominationToken,
            numTicks = 40 * 10 ** 18,
            designatedReporterAddress = tester.a0)

@fixture(scope="session")
def sessionFixture():
    return ContractsFixture()

@fixture
def contractsFixture(sessionFixture):
    sessionFixture.resetSnapshot()
    return sessionFixture
