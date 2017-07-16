from binascii import hexlify
from datetime import timedelta
from ethereum.tools import tester as tester
from ethereum.abi import ContractTranslator
from ethereum.tools.tester import ABIContract
from ethereum import utils as u
from ethereum.config import config_metropolis, Env
import io
import json
from os import path, walk, makedirs, listdir
from pytest import fixture
import re
import serpent
from utils import bytesToLong

tester.GASPRICE = 0

config_metropolis['BLOCK_GAS_LIMIT'] = 2**60

# used to resolve relative paths
BASE_PATH = path.dirname(path.abspath(__file__))
def resolveRelativePath(relativeFilePath):
    return path.abspath(path.join(BASE_PATH, relativeFilePath))
COMPILATION_CACHE = resolveRelativePath('./compilation_cache')

class NewContractsFixture:
    # TODO: figure out how to disable logging events to stdout (they are super noisy)
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
        NewContractsFixture.ensureCacheDirectoryExists()
        name = path.splitext(path.basename(relativeFilePath))[0]
        outputPath = path.join(COMPILATION_CACHE,  name + 'Signature')
        lastCompilationTime = path.getmtime(outputPath) if path.isfile(outputPath) else 0
        if path.getmtime(relativeFilePath) > lastCompilationTime:
            print('generating signature for ' + name)
            signature = serpent.mk_full_signature(relativeFilePath)
            with open(outputPath, mode='w') as file:
                json.dump(signature, file)
        else:
            print('using cached signature for ' + name)
        with open(outputPath, 'r') as file:
            signature = json.load(file)
        return(signature)

    @staticmethod
    def getCompiledCode(relativeFilePath):
        name = path.splitext(path.basename(relativeFilePath))[0]
        if name in NewContractsFixture.compiledCode:
            return NewContractsFixture.compiledCode[name]
        dependencySet = set()
        NewContractsFixture.getAllDependencies(relativeFilePath, dependencySet)
        NewContractsFixture.ensureCacheDirectoryExists()
        compiledOutputPath = path.join(COMPILATION_CACHE, name)
        lastCompilationTime = path.getmtime(compiledOutputPath) if path.isfile(compiledOutputPath) else 0
        needsRecompile = False
        for dependencyPath in dependencySet:
            if (path.getmtime(dependencyPath) > lastCompilationTime):
                needsRecompile = True
                break
        if (needsRecompile):
            print('compiling ' + name + '...')
            compiledCode = serpent.compile(relativeFilePath)
            with io.open(compiledOutputPath, mode='wb') as file:
                file.write(compiledCode)
        else:
            print('using cached compilation for ' + name)
        with io.open(compiledOutputPath, mode='rb') as file:
            compiledCode = file.read()
            NewContractsFixture.compiledCode[name] = compiledCode
            return(compiledCode)

    @staticmethod
    def getAllDependencies(filePath, knownDependencies):
        knownDependencies.add(filePath)
        fileDirectory = path.dirname(filePath)
        with open(filePath, 'r') as file:
            fileContents = file.read()
        matches = re.findall("inset\('(.*?)'\)", fileContents)
        for match in matches:
            dependencyPath = path.abspath(path.join(fileDirectory, match))
            if not dependencyPath in knownDependencies:
                NewContractsFixture.getAllDependencies(dependencyPath, knownDependencies)
        matches = re.findall("create\('(.*?)'\)", fileContents)
        for match in matches:
            dependencyPath = path.abspath(path.join(fileDirectory, match))
            if not dependencyPath in knownDependencies:
                NewContractsFixture.getAllDependencies(dependencyPath, knownDependencies)
        return(knownDependencies)

    ####
    #### Class Methods
    ####

    def __init__(self):
        self.chain = tester.Chain(env=Env(config=config_metropolis))
        self.contracts = {}
      	self.controller = self.upload('../src/controller.se')
        assert self.controller.getOwner() == bytesToLong(tester.a0)
        self.uploadAllContracts()
        self.whitelistTradingContracts()
        self.initializeAllContracts()
        self.branch = self.createBranch(0, 0)
        self.cash = self.getSeededCash()
        self.binaryMarket = self.createReasonableBinaryMarket(self.branch, self.cash)
        self.categoricalMarket = self.createReasonableCategoricalMarket(self.branch, 3, self.cash)
        self.scalarMarket = self.createReasonableScalarMarket(self.branch, -10 * 10**18, 30 * 10**18, self.cash)
        self.chain.mine(1)
        self.originalHead = self.chain.head_state
        self.originalBlock = self.chain.block
        self.snapshot = self.chain.snapshot()

    def uploadAndAddToController(self, relativeFilePath, lookupKey = None):
        lookupKey = lookupKey if lookupKey else path.splitext(path.basename(relativeFilePath))[0]
        contract = self.upload(relativeFilePath, lookupKey)
        self.controller.setValue(lookupKey.ljust(32, '\x00'), contract.address)
        return(contract)

    def upload(self, relativeFilePath, lookupKey = None):
        resolvedPath = resolveRelativePath(relativeFilePath)
        lookupKey = lookupKey if lookupKey else path.splitext(path.basename(resolvedPath))[0]
        if lookupKey in self.contracts:
            return(self.contracts[lookupKey])
        compiledCode = NewContractsFixture.getCompiledCode(resolvedPath)
        if lookupKey not in NewContractsFixture.signatures:
            NewContractsFixture.signatures[lookupKey] = NewContractsFixture.generateSignature(resolvedPath)
        signature = NewContractsFixture.signatures[lookupKey]
        print lookupKey
        contractAddress = long(hexlify(self.chain.contract(compiledCode, startgas=long(6.7 * 10**6))), 16)
        contract = ABIContract(self.chain, ContractTranslator(signature), contractAddress)
        self.contracts[lookupKey] = contract
	return(contract)

    def applySignature(self, signatureName, address):
        assert address
        translator = ContractTranslator(NewContractsFixture.signatures[signatureName])
        contract = ABIContract(self.chain, translator, address)
        return contract

    def resetSnapshot(self):
        self.chain.block = self.originalBlock
        self.chain.head_state = self.originalHead
        self.chain.revert(self.snapshot)

    ####
    #### Bulk Operations
    ####

    def uploadAllContracts(self):
        for directory, _, filenames in walk(resolveRelativePath('../src')):
            for filename in filenames:
                name = path.splitext(filename)[0]
                extension = path.splitext(filename)[1]
                if extension != '.se': continue
                if name == 'controller': continue
                self.uploadAndAddToController(path.join(directory, filename))

    def whitelistTradingContracts(self):
        for filename in listdir(resolveRelativePath('../src/trading')):
            name = path.splitext(filename)[0]
            self.controller.addToWhitelist(self.contracts[name].address)

    def initializeAllContracts(self):
        self.contracts['mutex'].initialize(self.controller.address)
        self.contracts['cash'].initialize(self.controller.address)
        self.contracts['orders'].initialize(self.controller.address)
        self.contracts['completeSets'].initialize(self.controller.address)
        self.contracts['makeOrder'].initialize(self.controller.address)
        self.contracts['takeBidOrder'].initialize(self.controller.address)
        self.contracts['takeAskOrder'].initialize(self.controller.address)
        self.contracts['takeOrder'].initialize(self.controller.address)
        self.contracts['cancelOrder'].initialize(self.controller.address)
        self.contracts['trade'].initialize(self.controller.address)
        self.contracts['claimProceeds'].initialize(self.controller.address)
        self.contracts['tradingEscapeHatch'].initialize(self.controller.address)

    ####
    #### Helpers
    ####

    def getSeededCash(self):
        cash = self.contracts['cash']
        cash.publicDepositEther(value = 1, sender = tester.k9)
        return cash

    def uploadShareToken(self, controllerAddress = None):
        controllerAddress = controllerAddress if controllerAddress else self.controller.address
        self.ensureShareTokenDependencies()
        shareTokenFactory = self.contracts['shareTokenFactory']
        shareTokenFactory.createShareToken(controllerAddress)
        shareToken = shareTokenFactory.getLastShareToken()
        return self.applySignature('shareToken', shareToken)

    def createBranch(self, parentBranch, payoutDistributionHash):
        self.contracts['branchFactory'].createBranch(self.controller.address, parentBranch, payoutDistributionHash)
        branchAddress = self.contracts['branchFactory'].getLastBranch()
        return self.applySignature('branch', branchAddress)

    def getReportingToken(self, market, payoutDistribution):
        reportingTokenAddress = market.getReportingToken(payoutDistribution)
        assert reportingTokenAddress
        reportingToken = ABIContract(self.chain, ContractTranslator(NewContractsFixture.signatures['reportingToken']), reportingTokenAddress)
        return reportingToken

    def getChildBranch(self, parentBranch, market, payoutDistribution):
        payoutDistributionHash = market.derivePayoutDistributionHash(payoutDistribution)
        assert payoutDistributionHash
        childBranchAddress = parentBranch.getChildBranch(payoutDistributionHash)
        assert childBranchAddress
        childBranch = ABIContract(self.chain, ContractTranslator(NewContractsFixture.signatures['branch']), childBranchAddress)
        return(childBranch)

    def createBinaryMarket(self, branch, endTime, feePerEthInWei, denominationToken, automatedReporterAddress, topic):
        return self.createCategoricalMarket(branch, 2, endTime, feePerEthInWei, denominationToken, automatedReporterAddress, topic)

    def createCategoricalMarket(self, branch, numOutcomes, endTime, feePerEthInWei, denominationToken, automatedReporterAddress, topic):
        marketCreationFee = self.contracts['marketFeeCalculator'].getValidityBond() + self.contracts['marketFeeCalculator'].getTargetReporterGasCosts()
        marketAddress = self.contracts['marketCreation'].createCategoricalMarket(branch.address, endTime, numOutcomes, feePerEthInWei, denominationToken.address, automatedReporterAddress, topic, value = marketCreationFee)
        assert marketAddress
        market = ABIContract(self.chain, ContractTranslator(NewContractsFixture.signatures['market']), marketAddress)
        return market

    def createScalarMarket(self, branch, endTime, feePerEthInWei, denominationToken, minDisplayPrice, maxDisplayPrice, automatedReporterAddress, topic):
        marketCreationFee = self.contracts['marketFeeCalculator'].getValidityBond() + self.contracts['marketFeeCalculator'].getTargetReporterGasCosts()
        marketAddress = self.contracts['marketCreation'].createScalarMarket(branch.address, endTime, feePerEthInWei, denominationToken.address, minDisplayPrice, maxDisplayPrice, automatedReporterAddress, topic, value = marketCreationFee)
        assert marketAddress
        market = ABIContract(self.chain, ContractTranslator(NewContractsFixture.signatures['market']), marketAddress)
        return market

    def createReasonableBinaryMarket(self, branch, denominationToken):
        return self.createBinaryMarket(
            branch = branch,
            endTime = long(self.chain.head_state.timestamp + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = denominationToken,
            automatedReporterAddress = tester.a0,
            topic = 'Sports'.ljust(32, '\x00'))

    def createReasonableCategoricalMarket(self, branch, numOutcomes, denominationToken):
        return self.createCategoricalMarket(
            branch = branch,
            numOutcomes = numOutcomes,
            endTime = long(self.chain.head_state.timestamp + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = denominationToken,
            automatedReporterAddress = tester.a0,
            topic = 'Sports'.ljust(32, '\x00'))

    def createReasonableScalarMarket(self, branch, minDisplayPrice, maxDisplayPrice, denominationToken):
        return self.createScalarMarket(
            branch = branch,
            endTime = long(self.chain.head_state.timestamp + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = denominationToken,
            minDisplayPrice = minDisplayPrice,
            maxDisplayPrice = maxDisplayPrice,
            automatedReporterAddress = tester.a0,
            topic = 'Sports'.ljust(32, '\x00'))

@fixture(scope="session")
def sessionFixture():
    return NewContractsFixture()

@fixture
def contractsFixture(sessionFixture):
    sessionFixture.resetSnapshot()
    return sessionFixture
