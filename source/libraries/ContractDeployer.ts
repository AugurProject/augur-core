#!/usr/bin/env node

// TODO: Add type mappings for array items
import * as binascii from "binascii";
import * as path from "path";
import * as EthjsAbi from "ethjs-abi";
import * as EthjsContract from "ethjs-contract";
import * as EthjsQuery from "ethjs-query";
// TODO: Update TS type definition for ContractBlockchainData to allow for empty object (e.g. upload() & uploadAndAddToController())?
import { ContractBlockchainData, ContractReceipt } from "contract-deployment";
import { Contract, parseAbiIntoMethods } from "./AbiParser";
import { generateTestAccounts, padAndHexlify, stringTo32ByteHex, waitForTransactionToBeSealed } from "./HelperFunctions";
import { CompilerOutputContracts } from "solc";

export class ContractDeployer {
    public readonly ethjsQuery: EthjsQuery;
    public readonly ethjsContract: EthjsContract;
    public readonly compiledContracts: CompilerOutputContracts;
    public readonly gasPrice: number;
    public readonly contracts = [];
    public readonly signatures = [];
    public readonly bytecodes = [];
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

        this.controller = await this.upload("../source/contracts/Controller.sol");
        const ownerAddress = (await this.controller.owner())[0];
        if (ownerAddress.toLowerCase() !== this.testAccounts[0]) {
            throw new Error("Controller owner does not equal from address");
        }
        await this.uploadAllContracts();
        await this.whitelistTradingContracts();
        await this.initializeAllContracts();
        await this.approveCentralAuthority();
        this.universe = await this.createGenesisUniverse();
        this.market = await this.createReasonableMarket(this.universe.address, this.contracts['Cash'].address, 2);
    }

    public async parseBlockTimestamp(blockTimestamp): Promise<Date> {
        const timestampHex = `0x${JSON.stringify(blockTimestamp).replace(/\"/g, "")}`;
        const timestampInt = parseInt(timestampHex, 16) * 1000;
        return new Date(timestampInt);
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
        // Abstract contracts have a 0-length array for bytecode
        if (bytecode.length === 0) {
            return undefined;
        }
        if (!this.signatures[signatureKey]) {
            this.signatures[signatureKey] = this.compiledContracts[relativeFilePath][signatureKey].abi;
            this.bytecodes[signatureKey] = bytecode;
        }
        const signature = this.signatures[signatureKey];
        const contractBuilder = this.ethjsContract(signature, bytecode, { from: this.testAccounts[0], gas: this.gasAmount, gasPrice: this.gasPrice });
        let transactionHash: string;

        if (constructorArgs.length > 0) {
            transactionHash = await contractBuilder.new(constructorArgs[0], constructorArgs[1]);
        } else {
            transactionHash = await contractBuilder.new();
        }
        await waitForTransactionToBeSealed(this.ethjsQuery, transactionHash);
        const receipt = await this.ethjsQuery.getTransactionReceipt(transactionHash);
        this.contracts[lookupKey] = await contractBuilder.at(receipt.contractAddress);

        return this.contracts[lookupKey];
    }

    public async applySignature(signatureName: string, address: string): Promise<ContractBlockchainData> {
        if (!address) {
            throw new Error ("Address not set.");
        }
        // TODO: Add format check of address
        // if () {
        //    address = padAndHexlify(address, 40);
        // }

        const signature = this.signatures[signatureName];
        const bytecode = this.bytecodes[signatureName];
        const contractBuilder = this.ethjsContract(signature, bytecode, { from: this.testAccounts[0], gas: this.gasAmount });
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

    private async approveCentralAuthority(): Promise<boolean> {
        const authority = this.contracts["Augur"];
        const contractsToApprove = ["Cash"];
        for (let testAccount in this.testAccounts) {
            for (let contractName of contractsToApprove) {
                this.contracts[contractName].approve(authority.address, 2 ** 256, { from: this.testAccounts[testAccount] });
            }
        }

        return true;
    }

    private async createGenesisUniverse(): Promise<ContractBlockchainData> {
        const delegatorBuilder = this.ethjsContract(this.signatures["Delegator"], this.bytecodes["Delegator"], { from: this.testAccounts[0], gas: this.gasAmount });
        const universeBuilder = this.ethjsContract(this.signatures["Universe"], this.bytecodes["Universe"], { from: this.testAccounts[0], gas: this.gasAmount });
        const transactionHash = await delegatorBuilder.new(this.controller.address, `0x${binascii.hexlify("Universe")}`);
        await waitForTransactionToBeSealed(this.ethjsQuery, transactionHash);
        const receipt = await this.ethjsQuery.getTransactionReceipt(transactionHash);
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
        const contractBuilder = this.ethjsContract(signature, bytecode, { from: this.testAccounts[0], gas: this.gasAmount });
        const stakeToken = await contractBuilder.at(stakeTokenAddress);

        return stakeToken;
    }

    private async createMarket(universeAddress: string, numOutcomes: number, endTime: number, feePerEthInWei: number, denominationToken: string, designatedReporter: string, numTicks: number): Promise<Contract> {
        const constant = { constant: true };

        const universe = await parseAbiIntoMethods(this.ethjsQuery, this.signatures["Universe"], { to: universeAddress, from: this.testAccounts[0], gas: this.gasAmount, gasPrice: this.gasPrice });
        const legacyReputationToken = await parseAbiIntoMethods(this.ethjsQuery, this.signatures['LegacyRepContract'], { to: this.contracts['LegacyRepContract'].address, from: this.testAccounts[0], gas: this.gasAmount, gasPrice: this.gasPrice });
        const reputationTokenAddress = await universe.getReputationToken();
        const reputationToken = await parseAbiIntoMethods(this.ethjsQuery, this.signatures['ReputationToken'], { to: reputationTokenAddress, from: this.testAccounts[0], gas: this.gasAmount, gasPrice: this.gasPrice });
        console.log("reputationTokenAddress: " + reputationTokenAddress);
        console.log("reputationToken: ");
        console.log(reputationToken);
        // get some REP
        await legacyReputationToken.faucet(0);
        await legacyReputationToken.approve(reputationTokenAddress, "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");
        await reputationToken.migrateFromLegacyRepContract();
        // necessary because it is used part of market creation fee calculation
        await universe.getCurrentReportingWindow();
        // necessary because it is used as part of market creation fee calculation
        await universe.getPreviousReportingWindow();
        // necessary because createMarket needs its reporting window already created
        const reportingWindowTransactionHash = await universe.getReportingWindowByMarketEndTime(endTime);
        waitForTransactionToBeSealed(this.ethjsQuery, reportingWindowTransactionHash);

        const currentReportingWindowAddress = await universe.getCurrentReportingWindow.bind(constant)();
        const targetReportingWindowAddress = await universe.getReportingWindowByMarketEndTime.bind(constant)(endTime);
        const targetReportingWindow = await parseAbiIntoMethods(this.ethjsQuery, this.signatures['ReportingWindow'], { to: targetReportingWindowAddress, from: this.testAccounts[0], gas: this.gasAmount, gasPrice: this.gasPrice });
        const marketCreationFee = await universe.getMarketCreationCost.bind(constant)();

        const marketAddress = await targetReportingWindow.createMarket.bind({ value: marketCreationFee, constant: true })(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter);
        if (!marketAddress) {
            throw new Error("Unable to get address for new categorical market.");
        }
        const createMarketHash = await targetReportingWindow.createMarket.bind({ value: marketCreationFee })(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter);
        waitForTransactionToBeSealed(this.ethjsQuery, createMarketHash);
        const market = await parseAbiIntoMethods(this.ethjsQuery, this.signatures["Market"], { to: marketAddress, from: this.testAccounts[0], gas: this.gasAmount });
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
