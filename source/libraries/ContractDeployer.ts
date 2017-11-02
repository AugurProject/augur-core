#!/usr/bin/env node

import { basename as getFilenameFromPath } from "path";
import EthjsAbi = require("ethjs-abi");
import { TransactionReceipt } from 'ethjs-shared';
import { stringTo32ByteHex } from "./HelperFunctions";
import { CompilerOutputContracts, CompilerOutputAbi } from "solc";
import { Configuration } from './Configuration';
import { Connector } from './Connector';
import { ContractFactory, Controller, Controlled, Universe } from './ContractInterfaces';
import { AccountManager } from './AccountManager';

export class ContractDeployer {
    private readonly accountManager: AccountManager;
    private readonly configuration: Configuration;
    private readonly connector: Connector;
    private readonly compiledContracts: CompilerOutputContracts;
    private readonly contracts = new Map<string, Controlled>();
    private readonly abis = new Map<string, Array<CompilerOutputAbi>>();
    private readonly bytecodes = new Map<string, string>();
    public controller: Controller;
    public universe: Universe;

    public constructor(configuration: Configuration, connector: Connector, accountManager: AccountManager, compilerOutput: CompilerOutputContracts) {
        this.configuration = configuration;
        this.connector = connector;
        this.accountManager = accountManager;
        this.compiledContracts = compilerOutput;
    }

    public async deploy(): Promise<void> {
        console.log('Uploading controller...');
        await this.uploadController();
        console.log('Uploading contracts...');
        await this.uploadAllContracts();
        console.log('Whitelisting contracts...');
        await this.whitelistTradingContracts();
        console.log('Initializing contracts...');
        await this.initializeAllContracts();
        console.log('Creating genesis universe...');
        this.universe = await this.createGenesisUniverse();
    }

    public getContract = (contractName: string): Controlled => {
        if (!this.contracts.has(contractName)) throw new Error(`Contract named ${contractName} does not exist.`);
        return this.contracts.get(contractName)!;
    }

    private async uploadController(): Promise<void> {
        const address = await this.upload("Controller.sol");
        if (typeof address === 'undefined') throw new Error(`Controller.sol contract did not upload correctly, possible abstract?`);
        this.controller = new Controller(this.connector, this.accountManager, address, this.configuration.gasPrice);
        const ownerAddress = await this.controller.owner_();
        if (ownerAddress.toLowerCase() !== this.accountManager.defaultAddress.toLowerCase()) {
            throw new Error("Controller owner does not equal from address");
        }
    }

    private async uploadAndAddDelegatedToController(contractFileName: string, contractName: string): Promise<Controlled|undefined> {
        const delegationTargetName = contractName + "Target";
        const hexlifiedDelegationTargetName = stringTo32ByteHex(delegationTargetName);
        const delegatorConstructorArgs = [this.controller.address, hexlifiedDelegationTargetName];

        await this.uploadAndAddToController(contractFileName, delegationTargetName, contractName);
        return await this.uploadAndAddToController("libraries/Delegator.sol", contractName, "Delegator", delegatorConstructorArgs);
    }

    private async uploadAndAddToController(relativeFilePath: string, lookupKey: string = "", signatureKey: string = "", constructorArgs: any = []): Promise<Controlled|undefined> {
        lookupKey = (lookupKey === "") ? getFilenameFromPath(relativeFilePath).split(".")[0] : lookupKey;
        const address = await this.upload(relativeFilePath, lookupKey, signatureKey, constructorArgs);
        if (typeof address === "undefined") {
            return undefined;
        }
        // TODO: Add padding to hexlifiedLookupKey to make it the right length?  It seems to work without padding.
        const hexlifiedLookupKey = stringTo32ByteHex(lookupKey);
        await this.controller.setValue(hexlifiedLookupKey, address);

        const controlled = ContractFactory(this.connector, this.accountManager, lookupKey, address, this.configuration.gasPrice);
        this.contracts.set(lookupKey, controlled);
        return controlled;
    }

    private getEncodedConstructData(abi: Array<CompilerOutputAbi>, bytecode: string, constructorArgs: Array<string>): string {
        if (constructorArgs.length === 0) {
            return bytecode;
        }
        const constructorSignature = abi.find(signature => signature.type === 'constructor');
        if (typeof constructorSignature === 'undefined') throw new Error(`ABI did not contain a constructor.`);
        const constructorInputTypes = constructorSignature.inputs.map(x => x.type);
        const encodedConstructorParameters = EthjsAbi.encodeParams(constructorInputTypes, constructorArgs).substring(2);
        return `${bytecode}${encodedConstructorParameters}`
    }

    private async construct(contractLookupKey: string, contractName: string, constructorArgs: Array<string>, failureDetails: string): Promise<string> {
        const abi = this.compiledContracts[contractLookupKey][contractName]!.abi;
        const bytecode = this.compiledContracts[contractLookupKey][contractName]!.evm.bytecode.object;
        const data = this.getEncodedConstructData(abi, bytecode, constructorArgs);
        const gasEstimate = await this.connector.ethjsQuery.estimateGas({ from: this.accountManager.defaultAddress, data: data });
        const signedTransaction = await this.accountManager.signTransaction({ gas: gasEstimate, gasPrice: this.configuration.gasPrice, data: data});
        const transactionHash = await this.connector.ethjsQuery.sendRawTransaction(signedTransaction);
        const receipt = await this.connector.waitForTransactionReceipt(transactionHash, failureDetails);
        return receipt.contractAddress;
    }

    private async upload(contractLookupKey: string, lookupKey: string = "", contractName: string = "", constructorArgs: Array<string> = []): Promise<string|undefined> {
        lookupKey = (lookupKey === "") ? getFilenameFromPath(contractLookupKey).split(".")[0] : lookupKey;
        contractName = (contractName === "") ? lookupKey : contractName;
        if (this.contracts.has(lookupKey)) {
            return this.contracts.get(lookupKey)!.address;
        }
        const bytecode = this.compiledContracts[contractLookupKey][contractName].evm.bytecode.object;
        if (!this.abis.has(contractName)) {
            this.abis.set(contractName, this.compiledContracts[contractLookupKey][contractName].abi);
            this.bytecodes.set(contractName, bytecode);
        }
        // Abstract contracts have a 0-length array for bytecode
        if (bytecode.length === 0) {
            return undefined;
        }
        return await this.construct(contractLookupKey, contractName, constructorArgs, `Uploading ${contractName}`);
    }

    private async uploadAllContracts(): Promise<void> {
        const contractsToDelegate: {[key:string]: boolean} = {"Orders": true, "TradingEscapeHatch": true};

        const promises: Promise<Controlled|undefined>[] = [];
        for (let contractFileName in this.compiledContracts) {
            if (contractFileName === "Controller.sol" || contractFileName === "libraries/Delegator.sol" || contractFileName.startsWith('legacy_reputation/')) {
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
        const transactionHash = <string>await this.controller.addToWhitelist(this.getContract(contractName).address, { sender: this.accountManager.defaultAddress });
        return await this.connector.waitForTransactionReceipt(transactionHash, `Whitelisting ${contractName}`);
    }

    private async whitelistTradingContracts(): Promise<void> {
        const promises: Array<Promise<TransactionReceipt>> = [];
        for (let contractFileName in this.compiledContracts) {
            if (contractFileName.indexOf("trading/") > -1) {
                const contractName = getFilenameFromPath(contractFileName, ".sol");
                if (!this.contracts.has(contractName)) continue;
                promises.push(this.whitelistContract(contractName));
            }
        }

        await Promise.all(promises);
    }

    private async initializeContract(contractName: string): Promise<TransactionReceipt> {
        const transactionHash = await this.getContract(contractName).setController(this.controller.address);
        return await this.connector.waitForTransactionReceipt(transactionHash, `Initializing ${contractName}`);
    }

    private async initializeAllContracts(): Promise<void> {
        const contractsToInitialize = ["Augur","Cash","CompleteSets","CreateOrder","FillOrder","CancelOrder","Trade","ClaimTradingProceeds","OrdersFetcher"];
        const promises: Array<Promise<TransactionReceipt>> = [];
        for (let contractName of contractsToInitialize) {
            promises.push(this.initializeContract(contractName));
        }

        await Promise.all(promises);
    }

    private async createGenesisUniverse(): Promise<Universe> {
        const delegatorAddress = await this.construct("libraries/Delegator.sol", "Delegator", [ this.controller.address, stringTo32ByteHex('Universe') ], `Instantiating genesis universe.`);
        const universe = new Universe(this.connector, this.accountManager, delegatorAddress, this.configuration.gasPrice);
        const transactionHash = await universe.initialize("0x0000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000000000000000000000000000000");
        await this.connector.waitForTransactionReceipt(transactionHash, `Initializing universe.`);
        console.log(`Genesis universe address: ${universe.address}`);
        return universe;
    }
}
