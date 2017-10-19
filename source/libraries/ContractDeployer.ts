#!/usr/bin/env node

// TODO: Use mapped types for arrays
// TODO: Update TS type definition for ContractBlockchainData to allow for empty object (e.g. upload() & uploadAndAddToController())?
import * as path from "path";
import EthjsAbi = require("ethjs-abi");
import EthjsContract = require("ethjs-contract");
import EthjsQuery = require("ethjs-query");
import { TransactionReceipt } from 'ethjs-shared';
// TODO: Update TS type definition for ContractBlockchainData to allow for empty object (e.g. upload() & uploadAndAddToController())?
import { ContractBlockchainData, ContractReceipt } from "contract-deployment";
import { Contract, parseAbiIntoMethods } from "./AbiParser";
import { generateTestAccounts, padAndHexlify, stringTo32ByteHex, waitForTransactionReceipt } from "./HelperFunctions";
import { CompilerOutputContracts } from "solc";

export class ContractDeployer {
    public readonly ethjsQuery: EthjsQuery;
    public readonly ethjsContract: EthjsContract;
    public readonly compiledContracts: CompilerOutputContracts;
    public readonly gasPrice: number;
    public readonly contracts = {};
    public readonly signatures = {};
    public readonly bytecodes = {};
    public readonly gasAmount = 6*10**6;
    public testAccounts;
    public controller;
    public universe;
    public market;

    public constructor(ethjsQuery: EthjsQuery, compilerOutput: CompilerOutputContracts, gasPrice: number) {
        this.ethjsQuery = ethjsQuery;
        this.ethjsContract = new EthjsContract(ethjsQuery);
        this.gasPrice = gasPrice;
        this.compiledContracts = compilerOutput;
    }

    public async deploy(): Promise<void> {
        this.testAccounts = await this.ethjsQuery.accounts();

        console.log('Uploading controller...');
        await this.uploadController();
        console.log('Uploading contracts...');
        await this.uploadAllContracts();
        console.log('Whitelisting contracts...');
        await this.whitelistTradingContracts();
        console.log('Initializing contracts...');
        await this.initializeAllContracts();
        console.log('Approving central authoritiy...');
        await this.approveCentralAuthority();
        console.log('Creating genesis universe...');
        this.universe = await this.createGenesisUniverse();
        console.log('Creating a reasonable market...');
        this.market = await this.createReasonableMarket(this.universe.address, this.contracts['Cash'].address, 2);
    }

    public async uploadController(): Promise<void> {
        this.controller = await this.upload("Controller.sol");
        const ownerAddress = (await this.controller.owner())[0];
        if (ownerAddress.toLowerCase() !== this.testAccounts[0]) {
            throw new Error("Controller owner does not equal from address");
        }
    }

    public async parseBlockTimestamp(blockTimestamp): Promise<Date> {
        const timestampHex = `0x${JSON.stringify(blockTimestamp).replace(/\"/g, "")}`;
        const timestampInt = parseInt(timestampHex, 16) * 1000;
        return new Date(timestampInt);
    }

    private async uploadAndAddDelegatedToController(contractFileName: string, contractName: string): Promise<ContractBlockchainData|undefined> {
        const delegationTargetName = contractName + "Target";
        const hexlifiedDelegationTargetName = stringTo32ByteHex(delegationTargetName);
        const delegatorConstructorArgs = [this.controller.address, hexlifiedDelegationTargetName];

        await this.uploadAndAddToController(contractFileName, delegationTargetName, contractName);
        return await this.uploadAndAddToController("libraries/Delegator.sol", contractName, "Delegator", delegatorConstructorArgs);
    }

    private async uploadAndAddToController(relativeFilePath: string, lookupKey: string = "", signatureKey: string = "", constructorArgs: any = []): Promise<ContractBlockchainData|undefined> {
        lookupKey = (lookupKey === "") ? path.basename(relativeFilePath).split(".")[0] : lookupKey;
        const contract = await this.upload(relativeFilePath, lookupKey, signatureKey, constructorArgs);
        if (typeof contract === "undefined") {
            return undefined;
        }
        // TODO: Add padding to hexlifiedLookupKey to make it the right length?  It seems to work without padding.
        const hexlifiedLookupKey = stringTo32ByteHex(lookupKey);
        await this.controller.setValue(hexlifiedLookupKey, contract.address);

        return contract;
    }

    private async upload(relativeFilePath: string, lookupKey: string = "", signatureKey: string = "", constructorArgs: string[] = []): Promise<ContractBlockchainData|undefined> {
        lookupKey = (lookupKey === "") ? path.basename(relativeFilePath).split(".")[0] : lookupKey;
        signatureKey = (signatureKey === "") ? lookupKey : signatureKey;
        if (this.contracts[lookupKey]) {
            return(this.contracts[lookupKey]);
        }
        const bytecode = this.compiledContracts[relativeFilePath][signatureKey].evm.bytecode.object;
        // Abstract contracts have a 0-length array for bytecode
        if (bytecode.length === 0) {
            return undefined;
        }
        if (!this.signatures[signatureKey]) {
            this.signatures[signatureKey] = this.compiledContracts[relativeFilePath][signatureKey].abi;
            this.bytecodes[signatureKey] = bytecode;
        }
        const signature = this.signatures[signatureKey];
        const contractBuilder = await this.ethjsContract(signature, bytecode, { from: this.testAccounts[0], gasPrice: this.gasPrice });
        const gasEstimate = await this.ethjsQuery.estimateGas(Object.assign({ from: this.testAccounts[0], data: bytecode }));
        const transactionHash = (constructorArgs.length === 2)
            ? await contractBuilder.new(constructorArgs[0], constructorArgs[1], { gas: gasEstimate })
            : await contractBuilder.new({ gas: gasEstimate });
        const receipt = await waitForTransactionReceipt(this.ethjsQuery, transactionHash, `Uploading ${signatureKey}`);
        this.contracts[lookupKey] = contractBuilder.at(receipt.contractAddress);

        return this.contracts[lookupKey];
    }

    private async uploadAllContracts(): Promise<void> {
        const contractsToDelegate = {"Orders": true, "TradingEscapeHatch": true};

        const promises: Promise<ContractBlockchainData|undefined>[] = [];
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
                    promises.push(this.uploadAndAddDelegatedToController(contractFileName, contractName));
                } else {
                    promises.push(this.uploadAndAddToController(contractFileName));
                }
            }
        }

        await Promise.all(promises);
    }

    private async whitelistContract(contractName: string): Promise<TransactionReceipt> {
        const transactionHash = await this.controller.addToWhitelist(this.contracts[contractName].address);
        return await waitForTransactionReceipt(this.ethjsQuery, transactionHash, `Whitelisting ${contractName}`);
    }

    private async whitelistTradingContracts(): Promise<void> {
        const promises: Array<Promise<TransactionReceipt>> = [];
        for (let contractFileName in this.compiledContracts) {
            if (contractFileName.indexOf("trading/") > -1) {
                const contractName = path.basename(contractFileName, ".sol");
                if (!this.contracts[contractName]) continue;
                promises.push(this.whitelistContract(contractName));
            }
        }

        await Promise.all(promises);
    }

    private async initializeContract(contractName: string): Promise<TransactionReceipt> {
        const transactionHash = await this.contracts[contractName].setController(this.controller.address);
        return await waitForTransactionReceipt(this.ethjsQuery, transactionHash, `Initializing ${contractName}`);
    }

    private async initializeAllContracts(): Promise<void> {
        const contractsToInitialize = ["Augur","Cash","CompleteSets","CreateOrder","FillOrder","CancelOrder","Trade","ClaimProceeds","OrdersFetcher"];
        const promises: Array<Promise<TransactionReceipt>> = [];
        for (let contractName of contractsToInitialize) {
            promises.push(this.initializeContract(contractName));
        }

        await Promise.all(promises);
    }

    private async approveCentralAuthority(): Promise<void> {
        const authority = this.contracts["Augur"];
        const contractsToApprove = ["Cash"];
        const promises: Array<Promise<string>> = [];
        for (let testAccount in this.testAccounts) {
            for (let contractName of contractsToApprove) {
                promises.push(this.contracts[contractName].approve(authority.address, 2 ** 256, { from: this.testAccounts[testAccount] }));
            }
        }

        await Promise.all(promises);
    }

    private async createGenesisUniverse(): Promise<ContractBlockchainData> {
        const delegatorBuilder = this.ethjsContract(this.signatures["Delegator"], this.bytecodes["Delegator"], { from: this.testAccounts[0], gasPrice: this.gasPrice });
        const universeBuilder = this.ethjsContract(this.signatures["Universe"], this.bytecodes["Universe"], { from: this.testAccounts[0], gasPrice: this.gasPrice });
        const delgatorGasEstimate = await this.ethjsQuery.estimateGas(Object.assign({ from: this.testAccounts[0], data: this.bytecodes["Delegator"] }));
        const transactionHash = await delegatorBuilder.new(this.controller.address, stringTo32ByteHex('Universe'), { gas: delgatorGasEstimate });
        const receipt = await waitForTransactionReceipt(this.ethjsQuery, transactionHash, `Instatiating genesis universe.`);
        const universe = await universeBuilder.at(receipt.contractAddress);
        await universe.initialize("0x0000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000000");
        return universe;
    }

    // TODO: move these out of this class. this class is for deploying the contracts, not general purpose Augur interactions.
    // CONSIDER: create a class called Augur or something that deals with the various interactions one may want to participate in
    public async getStakeToken(market, payoutDistribution, invalid): Promise<ContractBlockchainData> {
        const stakeTokenAddress = market.getStakeToken(payoutDistribution, invalid);
        if (!stakeTokenAddress) {
            throw new Error();
        }
        const signature = this.signatures["StakeToken"];
        const bytecode = this.bytecodes["StakeToken"];
        const contractBuilder = await this.ethjsContract(signature, bytecode, { from: this.testAccounts[0] });
        const gasEstimate = await this.ethjsQuery.estimateGas(Object.assign({ from: this.testAccounts[0], data: bytecode }));
        const stakeToken = await contractBuilder.at(stakeTokenAddress, { gas: gasEstimate });

        return stakeToken;
    }

    private async createMarket(universeAddress: string, numOutcomes: number, endTime: number, feePerEthInWei: number, denominationToken: string, designatedReporter: string, numTicks: number): Promise<Contract> {
        const constant = { constant: true };

        const universe = parseAbiIntoMethods(this.ethjsQuery, this.signatures["Universe"], { to: universeAddress, from: this.testAccounts[0], gasPrice: this.gasPrice });
        const legacyReputationToken = parseAbiIntoMethods(this.ethjsQuery, this.signatures['LegacyRepContract'], { to: this.contracts['LegacyRepContract'].address, from: this.testAccounts[0], gasPrice: this.gasPrice });
        const reputationTokenAddress = await universe.getReputationToken();
        const reputationToken = parseAbiIntoMethods(this.ethjsQuery, this.signatures['ReputationToken'], { to: reputationTokenAddress, from: this.testAccounts[0], gasPrice: this.gasPrice });

        // get some REP
        await legacyReputationToken.faucet(0);
        await legacyReputationToken.approve(reputationTokenAddress, "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");
        await reputationToken.migrateFromLegacyRepContract();

        // necessary because it is used part of market creation fee calculation
        const currentReportingWindowTransactionHash = await universe.getCurrentReportingWindow();
        // necessary because it is used as part of market creation fee calculation
        const previousReportingWindowTransactionHash = await universe.getPreviousReportingWindow();
        // necessary because createMarket needs its reporting window already created
        const marketReportingWindowTransactionHash = await universe.getReportingWindowByMarketEndTime(endTime);
        await waitForTransactionReceipt(this.ethjsQuery, currentReportingWindowTransactionHash, `Instantiating current reporting window.`);
        await waitForTransactionReceipt(this.ethjsQuery, previousReportingWindowTransactionHash, `Instantiating previous reporting window.`);
        await waitForTransactionReceipt(this.ethjsQuery, marketReportingWindowTransactionHash, `Instantiating market reporting window.`);

        const targetReportingWindowAddress = await universe.getReportingWindowByMarketEndTime.bind(constant)(endTime);

        const targetReportingWindow = parseAbiIntoMethods(this.ethjsQuery, this.signatures['ReportingWindow'], { to: targetReportingWindowAddress, from: this.testAccounts[0], gasPrice: this.gasPrice });
        const marketCreationFee = await universe.getMarketCreationCost.bind(constant)();
        const marketAddress = await targetReportingWindow.createMarket.bind({ value: marketCreationFee, constant: true })(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter);
        if (!marketAddress) {
            throw new Error("Unable to get address for new categorical market.");
        }
        const createMarketHash = await targetReportingWindow.createMarket.bind({ value: marketCreationFee })(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter);
        const market = parseAbiIntoMethods(this.ethjsQuery, this.signatures["Market"], { to: marketAddress, from: this.testAccounts[0], gasPrice: this.gasPrice });
        const marketNameHex = stringTo32ByteHex("Market");

        if (await market.getTypeName() !== marketNameHex) {
            throw new Error("Unable to create new categorical market");
        }
        return market;
    }

    private async createReasonableMarket(universe: string, denominationToken: string, numOutcomes: number): Promise<Contract> {
        const block = await this.ethjsQuery.getBlockByNumber(0, true);
        const blockDateTime = await this.parseBlockTimestamp(block.timestamp);
        const blockDateTimePlusDay = new Date();
        blockDateTimePlusDay.setDate(blockDateTime.getDate() + 1);
        return await this.createMarket(universe, 2, blockDateTimePlusDay.getTime()/1000, 10 ** 16, denominationToken, this.testAccounts[0], 10 ** 4);
    }
}
