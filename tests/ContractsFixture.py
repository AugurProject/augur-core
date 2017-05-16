from ethereum import tester
from binascii import hexlify
from datetime import timedelta
from ethereum import tester
from ethereum.abi import ContractTranslator
from ethereum.tester import ABIContract
import io
import json
import os
import re
import serpent
from utils import bytesToLong

class ContractsFixture:
    # TODO: figure out if these are cached across tests in pytest
    signatures = {}
    compiledCode = {}

    ####
    #### Static Methods
    ####

    @staticmethod
    def ensureCacheDirectoryExists():
        if not os.path.exists('./compilation_cache/'):
            os.makedirs('./compilation_cache/')

    @staticmethod
    def generateSignature(relativeFilePath):
        ContractsFixture.ensureCacheDirectoryExists()
        name = os.path.splitext(os.path.basename(relativeFilePath))[0]
        outputPath = './compilation_cache/' + name + 'Signature'
        lastCompilationTime = os.path.getmtime(outputPath) if os.path.isfile(outputPath) else 0
        if os.path.getmtime(relativeFilePath) > lastCompilationTime:
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
        name = os.path.splitext(os.path.basename(relativeFilePath))[0]
        if name in ContractsFixture.compiledCode:
            return ContractsFixture.compiledCode[name]
        dependencySet = set()
        ContractsFixture.getAllDependencies(relativeFilePath, dependencySet)
        ContractsFixture.ensureCacheDirectoryExists()
        compiledOutputPath = './compilation_cache/' + name
        lastCompilationTime = os.path.getmtime(compiledOutputPath) if os.path.isfile(compiledOutputPath) else 0
        needsRecompile = False
        for path in dependencySet:
            if (os.path.getmtime(path) > lastCompilationTime):
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
            ContractsFixture.compiledCode[name] = compiledCode
            return(compiledCode)

    @staticmethod
    def getAllDependencies(filePath, knownDependencies):
        knownDependencies.add(filePath)
        fileDirectory = os.path.dirname(filePath)
        with open(filePath, 'r') as file:
            fileContents = file.read()
        matches = re.findall("inset\('(.*?)'\)", fileContents)
        for match in matches:
            dependencyPath = os.path.abspath(os.path.join(fileDirectory, match))
            if not dependencyPath in knownDependencies:
                ContractsFixture.getAllDependencies(dependencyPath, knownDependencies)
        matches = re.findall("create\('(.*?)'\)", fileContents)
        for match in matches:
            dependencyPath = os.path.abspath(os.path.join(fileDirectory, match))
            if not dependencyPath in knownDependencies:
                ContractsFixture.getAllDependencies(dependencyPath, knownDependencies)
        return(knownDependencies)

    ####
    #### Class Methods
    ####

    def __init__(self):
        self.state = tester.state()
        self.contracts = {}
        self.state.block.number += 2000000
        self.state.block.timestamp = 1
        tester.gas_limit = long(4.2 * 10**6)
        self.controller = self.upload('../src/controller.se')
        assert self.controller.getOwner() == bytesToLong(tester.a0)
        self.uploadAndAddToController('../src/mutex.se').initialize(self.controller.address)
        assert self.contracts['mutex'].release()

    def uploadAndAddToController(self, relativeFilePath, lookupKey = None):
        lookupKey = lookupKey if lookupKey else os.path.splitext(os.path.basename(relativeFilePath))[0]
        contract = self.upload(relativeFilePath)
        self.controller.setValue(lookupKey.ljust(32, '\x00'), contract.address)
        return(contract)

    def upload(self, relativeFilePath, lookupKey = None):
        lookupKey = lookupKey if lookupKey else os.path.splitext(os.path.basename(relativeFilePath))[0]
        if lookupKey in self.contracts:
            return(self.contracts[lookupKey])
        compiledCode = ContractsFixture.getCompiledCode(relativeFilePath)
        if lookupKey not in ContractsFixture.signatures:
            ContractsFixture.signatures[lookupKey] = ContractsFixture.generateSignature(relativeFilePath)
        signature = ContractsFixture.signatures[lookupKey]
        contractAddress = long(hexlify(self.state.evm(compiledCode)), 16)
        contract = ABIContract(self.state, ContractTranslator(signature), contractAddress)
        self.contracts[lookupKey] = contract
        return(contract)

    def applySignature(self, signatureName, address):
        assert address
        translator = ContractTranslator(ContractsFixture.signatures[signatureName])
        contract = ABIContract(self.state, translator, address)
        return contract

    ####
    #### Bulk Uploaders
    ####

    def ensureBranchDependencies(self):
        self.uploadAndAddToController('../src/trading/topics.se')
        self.uploadAndAddToController('../src/factories/topicsFactory.se')
        self.uploadAndAddToController('../src/reporting/reputationToken.se')
        self.uploadAndAddToController('../src/factories/reputationTokenFactory.se')
        self.uploadAndAddToController('../src/reporting/branch.se')
        self.uploadAndAddToController('../src/factories/branchFactory.se')

    def ensureReportingWindowDependencies(self):
        self.uploadAndAddToController('../src/reporting/registrationToken.se')
        self.uploadAndAddToController('../src/factories/registrationTokenFactory.se')
        self.uploadAndAddToController('../src/reporting/reportingWindow.se')
        self.uploadAndAddToController('../src/factories/reportingWindowFactory.se')

    def ensureShareTokenDependencies(self):
        self.uploadAndAddToController('../src/trading/shareToken.se')
        self.uploadAndAddToController('../src/factories/shareTokenFactory.se')

    def ensureMarketCreationDependencies(self):
        self.ensureReportingWindowDependencies()
        self.ensureShareTokenDependencies()
        self.uploadAndAddToController('../src/reporting/market.se')
        self.uploadAndAddToController('../src/factories/marketFactory.se')
        self.uploadAndAddToController('../src/extensions/marketFeeCalculator.se')
        self.upload('../src/extensions/marketCreation.se')

    def ensureReportingTokenDependencies(self):
        self.uploadAndAddToController('../src/reporting/reportingToken.se')
        self.uploadAndAddToController('../src/factories/reportingTokenFactory.se')

    ####
    #### Helpers
    ####

    def getSeededCash(self):
        cash = self.uploadAndAddToController('../src/trading/cash.se')
        cash.initialize(self.controller.address)
        cash.publicDepositEther(value = 1)
        return cash

    def uploadShareToken(self, controllerAddress = None):
        controllerAddress = controllerAddress if controllerAddress else self.controller.address
        self.ensureShareTokenDependencies()
        shareTokenFactory = self.contracts['shareTokenFactory']
        shareTokenFactory.createShareToken(controllerAddress)
        shareToken = shareTokenFactory.getLastShareToken()
        return self.applySignature('shareToken', shareToken)

    def prepOrders(self):
        orders = self.initializeOrders()
        makeOrder = self.initializeMakeOrder()
        cancelOrder = self.initializeCancelOrder()
        branch = self.createBranch(0, 0)
        cash = self.getSeededCash()
        market = self.createReasonableBinaryMarket(branch, cash)

        return branch, cash, market, orders, makeOrder, cancelOrder

    def initializeOrders(self):
        orders = self.uploadAndAddToController('../src/trading/orders.se')
        orders.initialize(self.controller.address)
        self.controller.addToWhitelist(orders.address)
        return orders

    def initializeCompleteSets(self):
        completeSets = self.uploadAndAddToController('../src/trading/completeSets.se')
        completeSets.initialize(self.controller.address)
        self.controller.addToWhitelist(completeSets.address)
        return completeSets

    def initializeMakeOrder(self):
        makeOrder = self.uploadAndAddToController('../src/trading/makeOrder.se')
        makeOrder.initialize(self.controller.address)
        self.controller.addToWhitelist(makeOrder.address)
        return makeOrder

    def initializeTakeOrder(self):
        takeBidOrder = self.uploadAndAddToController('../src/trading/takeBidOrder.se')
        takeBidOrder.initialize(self.controller.address)
        self.controller.addToWhitelist(takeBidOrder.address)

        takeAskOrder = self.uploadAndAddToController('../src/trading/takeAskOrder.se')
        takeAskOrder.initialize(self.controller.address)
        self.controller.addToWhitelist(takeAskOrder.address)

        takeOrder = self.uploadAndAddToController('../src/trading/takeOrder.se')
        takeOrder.initialize(self.controller.address)
        self.controller.addToWhitelist(takeOrder.address)
        return takeOrder

    def initializeCancelOrder(self):
        cancelOrder = self.uploadAndAddToController('../src/trading/cancelOrder.se')
        cancelOrder.initialize(self.controller.address)
        self.controller.addToWhitelist(cancelOrder.address)
        return cancelOrder

    def createBranch(self, parentBranch, payoutDistributionHash):
        self.ensureBranchDependencies()
        self.contracts['branchFactory'].createBranch(self.controller.address, parentBranch, payoutDistributionHash)
        branchAddress = self.contracts['branchFactory'].getLastBranch()
        return self.applySignature('branch', branchAddress)

    def getReportingToken(self, market, payoutDistribution):
        self.ensureReportingTokenDependencies()
        reportingTokenAddress = market.getReportingToken(payoutDistribution)
        assert reportingTokenAddress
        reportingToken = ABIContract(self.state, ContractTranslator(ContractsFixture.signatures['reportingToken']), reportingTokenAddress)
        return reportingToken

    def getChildBranch(self, parentBranch, market, payoutDistribution):
        payoutDistributionHash = market.derivePayoutDistributionHash(payoutDistribution)
        assert payoutDistributionHash
        childBranchAddress = parentBranch.getChildBranch(payoutDistributionHash)
        assert childBranchAddress
        childBranch = ABIContract(self.state, ContractTranslator(ContractsFixture.signatures['branch']), childBranchAddress)
        return(childBranch)

    def createBinaryMarket(self, branch, endTime, feePerEthInWei, denominationToken, automatedReporterAddress, topic):
        self.ensureMarketCreationDependencies()
        marketCreationFee = self.contracts['marketFeeCalculator'].getValidityBond() + self.contracts['marketFeeCalculator'].getTargetReporterGasCosts()
        marketAddress = self.contracts['marketCreation'].createCategoricalMarket(branch.address, endTime, 2, feePerEthInWei, denominationToken.address, automatedReporterAddress, topic, value = marketCreationFee)
        assert marketAddress
        market = ABIContract(self.state, ContractTranslator(ContractsFixture.signatures['market']), marketAddress)
        return market

    def createReasonableBinaryMarket(self, branch, denominationToken):
        return self.createBinaryMarket(
            branch=branch,
            endTime=long(self.state.block.timestamp + timedelta(days=1).total_seconds()),
            feePerEthInWei=10**16,
            denominationToken=denominationToken,
            automatedReporterAddress=0,
            topic='Sports'.ljust(32, '\x00'))
