#!/usr/bin/env node

import * as binascii from "binascii";
import * as path from "path";
import * as EthjsAbi from "ethjs-abi";
import * as EthjsContract from "ethjs-contract";
import * as EthjsQuery from "ethjs-query";
// TODO: Update TS type definition for ContractBlockchainData to allow for empty object (e.g. upload() & uploadAndAddToController())?
import { ContractBlockchainData, ContractReceipt } from "contract-deployment";
import { generateTestAccounts, padAndHexlify } from "./HelperFunctions";
import { parseAbiIntoMethods } from './AbiParser';


export class ContractDeployer {
    private ethjsQuery: EthjsQuery;
    private ethjsContract: EthjsContract;
    private compiledContracts;
    private contracts;
    private signatures;
    private bytecodes;
    private utils;
    private constants;
    private gasAmount;
    private testAccountSecretKeys;
    private testAccounts;
    private controller;
    private universe;
    private cash;
    private binaryMarket;
    private categoricalMarket;
    private scalarMarket;

    public constructor(ethjsQuery: EthjsQuery, contractJson: string, gasAmount: number, secretKeys: string[]) {
        this.ethjsQuery = ethjsQuery;
        this.ethjsContract = new EthjsContract(ethjsQuery);
        this.compiledContracts = JSON.parse(contractJson);
        this.signatures = [];
        this.bytecodes = [];
        this.contracts = [];
        this.gasAmount = gasAmount;
        this.testAccountSecretKeys = secretKeys;
    }

    public async deploy(): Promise<boolean> {
        this.testAccounts = await generateTestAccounts(this.testAccountSecretKeys);

        this.controller = await this.upload("../source/contracts/Controller.sol");
        const ownerAddress = (await this.controller.owner())[0];
        if (ownerAddress.toLowerCase() !== this.testAccounts[0].address) {
            throw new Error("Controller owner does not equal from address");
        }
        await this.uploadAllContracts();
        await this.whitelistTradingContracts();
        await this.initializeAllContracts();
        await this.approveCentralAuthority();
        this.universe = await this.createGenesisUniverse();
        this.cash = await this.getSeededCash();
        // this.utils = await this.upload("../tests/solidity_test_helpers/Utils.sol");
        this.binaryMarket = await this.createReasonableBinaryMarket(this.universe, this.cash);
        // this.categoricalMarket = this.createReasonableCategoricalMarket(this.universe, 3, this.cash);
        // this.scalarMarket = this.createReasonableScalarMarket(this.universe, 40, this.cash);
        // this.constants = await this.upload("../tests/solidity_test_helpers/Constants.sol");

        return true;
    }

    // Helper functions

    public async parseBlockTimestamp(blockTimestamp): Promise<Date> {
        const timestampHex = "0x" + JSON.stringify(blockTimestamp).replace(/\"/g, "");
        const timestampInt = parseInt(timestampHex, 16) * 1000;
        return new Date(timestampInt);
    }

    // Getters
    public getEthjsQuery() {
        return this.ethjsQuery;
    }

    public getSignatures() {
        return this.signatures;
    }

    public getCompiledContracts() {
        return this.compiledContracts;
    }

    public getContracts() {
        return this.contracts;
    }

    public getTestAccounts() {
        return this.testAccounts;
    }

    public getController() {
        return this.controller;
    }

    public getUniverse() {
        return this.universe;
    }

    public getCash() {
        return this.cash;
    }

    public getBinaryMarket() {
        return this.binaryMarket;
    }

    private async uploadAndAddDelegatedToController(contractFileName: string, contractName: string): Promise<ContractBlockchainData|undefined> {
        const delegationTargetName = contractName + "Target";
        const hexlifiedDelegationTargetName = "0x" + binascii.hexlify(delegationTargetName);
        const delegatorConstructorArgs = [this.controller.address, hexlifiedDelegationTargetName];

        await this.uploadAndAddToController(contractFileName, delegationTargetName, contractName);
        return await this.uploadAndAddToController("../source/contracts/libraries/Delegator.sol", contractName, "Delegator", delegatorConstructorArgs);
    }

    private async uploadAndAddToController(relativeFilePath: string, lookupKey: string = "", signatureKey: string = "", constructorArgs: any = []): Promise<ContractBlockchainData|undefined> {
        lookupKey = (lookupKey === "") ? path.basename(relativeFilePath).split(".")[0] : lookupKey;
        const contract = await this.upload(relativeFilePath, lookupKey, signatureKey, constructorArgs);
        if (typeof contract === "undefined") {
            return undefined;
        }
        // TODO: Add padding to hexlifiedLookupKey to make it the right length?  It seems to work without padding.
        const hexlifiedLookupKey = "0x" + binascii.hexlify(lookupKey);
        await this.controller.setValue(hexlifiedLookupKey, contract.address);

        return contract;
    }

    private async upload(relativeFilePath: string, lookupKey: string = "", signatureKey: string = "", constructorArgs: string[] = []): Promise<ContractBlockchainData|undefined> {
        lookupKey = (lookupKey === "") ? path.basename(relativeFilePath).split(".")[0] : lookupKey;
        signatureKey = (signatureKey === "") ? lookupKey : signatureKey;
        if (this.contracts[lookupKey]) {
            return(this.contracts[lookupKey]);
        }
        relativeFilePath = relativeFilePath.replace("../source/contracts/", "");
        const bytecode = this.compiledContracts[relativeFilePath][signatureKey].evm.bytecode.object;
        // abstract contracts have a 0-length array for bytecode
        if (bytecode.length === 0) {
            return undefined;
        }
        if (!this.signatures[signatureKey]) {
            this.signatures[signatureKey] = this.compiledContracts[relativeFilePath][signatureKey].abi;
            this.bytecodes[signatureKey] = bytecode;
        }
        const signature = this.signatures[signatureKey];
        const contractBuilder = this.ethjsContract(signature, bytecode, { from: this.testAccounts[0].address, gas: this.gasAmount });
        let receiptAddress: string;
        if (constructorArgs.length > 0) {
            receiptAddress = await contractBuilder.new(constructorArgs[0], constructorArgs[1]);
        } else {
            receiptAddress = await contractBuilder.new();
        }
        const receipt: ContractReceipt = await this.ethjsQuery.getTransactionReceipt(receiptAddress);
        this.contracts[lookupKey] = await contractBuilder.at(receipt.contractAddress);

        return this.contracts[lookupKey];
    }

    public async applySignature(signatureName: string, address: string): Promise<ContractBlockchainData> {
        if (!address) {
            throw new Error ("Address not set.");
        }
        // TODO: Add format check of address
        // if () {
        //    address = await padAndHexlify(address, 40);
        // }

        const signature = this.signatures[signatureName];
        const bytecode = this.bytecodes[signatureName];
        const contractBuilder = this.ethjsContract(signature, bytecode, { from: this.testAccounts[0].address, gas: this.gasAmount });
        const contract = await contractBuilder.at(address);
        return contract;
    }

    private async uploadAllContracts(): Promise<boolean> {
        const contractsToDelegate = {"Orders": true, "TradingEscapeHatch": true};

        let uploadedContractPromises: Promise<ContractBlockchainData|undefined>[] = [];
        for (let contractFileName in this.compiledContracts) {
            if (contractFileName === "Controller.sol" || contractFileName === "libraries/Delegator.sol") {
                continue;
            }

            for (let contractName in this.compiledContracts[contractFileName]) {
                // Filter out interface contracts, as they do not need to be deployed
                if (this.compiledContracts[contractFileName][contractName].evm.bytecode.object === "") {
                    continue;
                }
                if (contractsToDelegate[contractName] === true) {
                    uploadedContractPromises.push(this.uploadAndAddDelegatedToController(contractFileName, contractName));
                    // this.contracts[contractName] = this.applySignature(contractName, this.contracts[contractName].address)
                } else {
                    uploadedContractPromises.push(this.uploadAndAddToController(contractFileName));
                }
            }
        }

        await Promise.all(uploadedContractPromises);

        return true;
    }

    private async whitelistTradingContracts(): Promise<boolean> {
        for (let contractFileName in this.compiledContracts) {
            if (contractFileName.indexOf("trading/") > -1) {
                const contractName = path.basename(contractFileName, ".sol");
                if (!this.contracts[contractName]) continue;
                this.controller.addToWhitelist(this.contracts[contractName].address);
            }
        }

        return true;
    }

    private async initializeAllContracts(): Promise<boolean> {
        const contractsToInitialize = ["Augur","Cash","CompleteSets","CreateOrder","FillOrder","CancelOrder","Trade","ClaimProceeds","OrdersFetcher"];
        for (let contractName of contractsToInitialize) {
            if (this.contracts[contractName]["setController"]) {
                this.contracts[contractName].setController(this.controller.address);
            } else if (this.contracts[contractName]["initialize"]) {
                this.contracts[contractName].initialize(this.controller.address);
            } else {
                throw new Error("Contract " + contractName + " has neither \"initialize\" nor \"setController\" method on it.");
            }
        }

        return true;
    }

    private async getSeededCash(): Promise<ContractBlockchainData> {
        const cash = this.contracts['Cash'];
        cash.depositEther({ value: 1, from: this.testAccounts[9].address });
//        cash.depositEther({ value: 9200000000000000001, from: this.testAccounts[1].address });
        return cash;
    }

    private async approveCentralAuthority(): Promise<boolean> {
        const authority = this.contracts["Augur"];
        const contractsToApprove = ["Cash"];
        for (let testAccount in this.testAccounts) {
            for (let contractName of contractsToApprove) {
                this.contracts[contractName].approve(authority.address, 2 ** 256, { from: this.testAccounts[testAccount].address });
            }
        }

        return true;
    }

    private async createGenesisUniverse(): Promise<ContractBlockchainData> {
        const delegatorBuilder = this.ethjsContract(this.signatures["Delegator"], this.bytecodes["Delegator"], { from: this.testAccounts[0].address, gas: this.gasAmount });
        const universeBuilder = this.ethjsContract(this.signatures["Universe"], this.bytecodes["Universe"], { from: this.testAccounts[0].address, gas: this.gasAmount });
        const receiptAddress = await delegatorBuilder.new(this.controller.address, `0x${binascii.hexlify("Universe")}`);
        const receipt = await this.ethjsQuery.getTransactionReceipt(receiptAddress);
        const universe = await universeBuilder.at(receipt.contractAddress);
        await universe.initialize("0x0000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000000");
        return universe;
    }

    public async getReportingToken(market, payoutDistribution): Promise<ContractBlockchainData> {
        const reportingTokenAddress = market.getReportingToken(payoutDistribution);
        if (!reportingTokenAddress) {
            throw new Error();
        }
        const signature = this.signatures["ReportingToken"];
        const bytecode = this.bytecodes["ReportingToken"];
        const contractBuilder = this.ethjsContract(signature, bytecode, { from: this.testAccounts[0].address, gas: this.gasAmount });
        const reportingToken = await contractBuilder.at(reportingTokenAddress);

        return reportingToken;
    }

    public async getReceiptLogs(transactionHash: string, signatureKey: string) {
        const transactionReceipt = await this.ethjsQuery.getTransactionReceipt(transactionHash);
        const contractCreationAbi = this.signatures["MarketCreation"];
        const decoder = EthjsAbi.logDecoder(this.signatures["MarketCreation"]);
        return decoder(transactionReceipt.logs);
    }

    public async getContractFromAddress(address: string, signatureKey: string, fromAddress: string, gasAmount: number): Promise<ContractBlockchainData> {
        const signature = this.signatures[signatureKey];
        const bytecode = this.bytecodes[signatureKey];
        const contractBuilder = await this.ethjsContract(signature, bytecode, { from: fromAddress, gas: gasAmount });
        const market = await contractBuilder.at(address);
        return market;
    }

    private async createBinaryMarket(universe, endTime: number, feePerEthInWei: number, denominationToken, designatedReporterAddress, numTicks: number): Promise<ContractBlockchainData> {
        return await this.createCategoricalMarket(universe, 2, endTime, feePerEthInWei, denominationToken, designatedReporterAddress, numTicks);
    }

    private async createCategoricalMarket(universe, numOutcomes, endTime, feePerEthInWei, denominationToken, designatedReporterAddress, numTicks): Promise<ContractBlockchainData> {
        const myUniverse = await parseAbiIntoMethods(this.ethjsQuery, this.signatures["Universe"], { to: universe.address, from: this.testAccounts[0].address, gas: "0x5b8d80" });
        const marketFeeCalculator = await parseAbiIntoMethods(this.ethjsQuery, this.signatures["MarketFeeCalculator"], { to: this.contracts["MarketFeeCalculator"].address });
        await myUniverse.getCurrentReportingWindow.bind({ gas: 3*10**6 })();
        const reportingWindowAddress = await myUniverse.getCurrentReportingWindow.bind({ constant: true })();

        // console.log(reportingWindowAddress);

        // const factory = await parseAbiIntoMethods(this.ethjsQuery, this.signatures["FruitFactory"], { to: this.contracts["FruitFactory"].address, from: this.testAccounts[0].address, gas: "0x5b8d80" });
        // const fruitAddress = await factory.createFruit.bind({ to: this.contracts["FruitFactory"].address, from: this.testAccounts[0].address, gas: "0x5b8d80", constant: true })();
        // await factory.createFruit();
        // console.log("Fruit address: " + fruitAddress);

        // FIXME: the following two functions are not constant, so we can't call them and get a return value
        const validityBond = await marketFeeCalculator.getValidityBond.bind({ constant: true })(reportingWindowAddress);
        const targetReporterGasCosts = await marketFeeCalculator.getTargetReporterGasCosts.bind({ constant: true })(reportingWindowAddress);
        const marketCreationFee = await validityBond.add(targetReporterGasCosts);
        // const transactionHash = await this.contracts["MarketCreation"].createMarket(universe.address, endTime, numOutcomes, feePerEthInWei, denominationToken.address, numTicks, designatedReporterAddress, { value: marketCreationFee, startgas: 6.7 * 10 ** 6 });
        const marketCreation = await parseAbiIntoMethods(this.ethjsQuery, this.signatures["MarketCreation"], { to: this.contracts["MarketCreation"].address, from: this.testAccounts[0].address, gas: "0x5b8d80" });
        // console.log("!!!!!!!!!!!!!!");
        // console.log(universe.address);
        // console.log(endTime);
        // console.log( numOutcomes);
        // console.log(feePerEthInWei);
        // console.log(denominationToken.address);
        // console.log(numTicks);
        // console.log(designatedReporterAddress);
        // console.log("!!!!!!!!!!!!!!");

        const marketAddress = await marketCreation.createMarket.bind({ to: this.contracts["MarketCreation"].address, from: this.testAccounts[0].address, gas: "0x5b8d80", value: marketCreationFee, constant: true })(universe.address, endTime, numOutcomes, feePerEthInWei, denominationToken.address, numTicks, designatedReporterAddress);
        await marketCreation.createMarket(universe.address, endTime, numOutcomes, feePerEthInWei, denominationToken.address, numTicks, designatedReporterAddress);

console.log(marketAddress);
        return marketAddress;
    }

    private async createScalarMarket(universe, endTime, feePerEthInWei, denominationToken, numTicks, designatedReporterAddress): Promise<ContractBlockchainData> {
        const reportingWindowAddress = universe.getCurrentReportingWindow();
        const marketCreationFee = this.contracts['MarketFeeCalculator'].getValidityBond(reportingWindowAddress) + this.contracts['MarketFeeCalculator'].getTargetReporterGasCosts(reportingWindowAddress);
        const marketAddress = this.contracts['MarketCreation'].createMarket(universe.address, endTime, 2, feePerEthInWei, denominationToken.address, numTicks, designatedReporterAddress, {value: marketCreationFee});
        if (!marketAddress) {
            throw new Error("Unable to create new market.");
        }
        const signature = this.signatures["Market"];
        const bytecode = this.bytecodes["Market"];
        const contractBuilder = this.ethjsContract(signature, bytecode, { from: this.testAccounts[0].address, gas: this.gasAmount });
        const market = await contractBuilder.at(marketAddress);
        return market;
    }

    private async createReasonableBinaryMarket(universe, denominationToken): Promise<ContractBlockchainData> {
        const block = await this.ethjsQuery.getBlockByNumber(0, true);
        const blockDateTime = await this.parseBlockTimestamp(block.timestamp);
        const blockDateTimePlusDay = new Date();
        blockDateTimePlusDay.setDate(blockDateTime.getDate() + 1);
        return await this.createBinaryMarket(universe, blockDateTimePlusDay.getTime()/1000, 10 ** 16, denominationToken, this.testAccounts[0].address, 10 ** 18);
    }

    private async createReasonableCategoricalMarket(universe, numOutcomes, denominationToken): Promise<ContractBlockchainData> {
        const block = await this.ethjsQuery.getBlockByNumber(0, true);
        const blockDateTime = await this.parseBlockTimestamp(block.timestamp);
        const blockDateTimePlusDay = new Date();
        blockDateTimePlusDay.setDate(blockDateTime.getDate() + 1);
        return this.createCategoricalMarket(universe, numOutcomes, blockDateTimePlusDay.getTime()/1000, 10 ** 16, denominationToken, this.testAccounts[0].address, 3 * 10 ** 17);
    }

    private async createReasonableScalarMarket(universe, priceRange, denominationToken): Promise<ContractBlockchainData> {
        const block = await this.ethjsQuery.getBlockByNumber(0, true);
        const blockDateTime = await this.parseBlockTimestamp(block.timestamp);
        const blockDateTimePlusDay = new Date();
        blockDateTimePlusDay.setDate(blockDateTime.getDate() + 1);
        return this.createScalarMarket(universe, blockDateTimePlusDay.getTime()/1000, 10 ** 16, denominationToken, 40 * 10 ** 18, this.testAccounts[0].address);
    }
}
