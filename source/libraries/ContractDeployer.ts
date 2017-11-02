#!/usr/bin/env node

// TODO: Use mapped types for arrays
import * as path from "path";
import EthjsAbi = require("ethjs-abi");
import EthjsContract = require("ethjs-contract");
import BN = require('bn.js');
import { Account } from 'ethjs-account';
import { sign } from 'ethjs-signer';
import { TransactionReceipt } from 'ethjs-shared';
import { stringTo32ByteHex, waitForTransactionReceipt } from "./HelperFunctions";
import { CompilerOutputContracts, CompilerOutputAbi } from "solc";
import { Configuration } from './Configuration';
import { Connector } from './Connector';
import { ContractFactory, Contract, Controller, Controlled, Universe, ReputationToken, ReportingWindow, Market, Cash, LegacyReputationToken } from './ContractInterfaces';
import { AccountManager } from './AccountManager';

export class ContractDeployer {
    public readonly accountManager: AccountManager;
    public readonly configuration: Configuration;
    public readonly connector: Connector;
    public readonly ethjsContract: EthjsContract;
    public readonly compiledContracts: CompilerOutputContracts;
    public readonly contracts = new Map<string, Controlled>();
    public readonly abis = new Map<string, Array<CompilerOutputAbi>>();
    public readonly bytecodes = new Map<string, string>();
    public readonly gasAmount = 6*10**6;
    private nonce: BN | null = null;
    public controller: Controller;
    public universe: Universe;
    public market: Market;

    public constructor(configuration: Configuration, connector: Connector, compilerOutput: CompilerOutputContracts) {
        this.accountManager = new AccountManager(connector, configuration);
        this.configuration = configuration;
        this.connector = connector;
        this.ethjsContract = new EthjsContract(this.connector.ethjsQuery);
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
        // FIXME: the rest of this shouldn't be part of the deploy script, it should be part of an integration test
        console.log('Approving central authoritiy...');
        await this.approveCentralAuthority();
        console.log('Creating a reasonable market...');
        this.market = await this.createReasonableMarket(this.universe, this.getContract('Cash').address, 2);
    }

    public async uploadController(): Promise<void> {
        const address = await this.upload("Controller.sol");
        if (typeof address === 'undefined') throw new Error(`Controller.sol contract did not upload correctly, possible abstract?`);
        this.controller = new Controller(this.connector, this.accountManager, address, this.configuration.gasPrice);
        const ownerAddress = await this.controller.owner_();
        if (ownerAddress.toLowerCase() !== this.accountManager.defaultAddress.toLowerCase()) {
            throw new Error("Controller owner does not equal from address");
        }
    }

    private getContract = (contractName: string): Controlled => {
        if (!this.contracts.has(contractName)) throw new Error(`Contract named ${contractName} does not exist.`);
        return this.contracts.get(contractName)!;
    }

    private async uploadAndAddDelegatedToController(contractFileName: string, contractName: string): Promise<Controlled|undefined> {
        const delegationTargetName = contractName + "Target";
        const hexlifiedDelegationTargetName = stringTo32ByteHex(delegationTargetName);
        const delegatorConstructorArgs = [this.controller.address, hexlifiedDelegationTargetName];

        await this.uploadAndAddToController(contractFileName, delegationTargetName, contractName);
        return await this.uploadAndAddToController("libraries/Delegator.sol", contractName, "Delegator", delegatorConstructorArgs);
    }

    private async uploadAndAddToController(relativeFilePath: string, lookupKey: string = "", signatureKey: string = "", constructorArgs: any = []): Promise<Controlled|undefined> {
        lookupKey = (lookupKey === "") ? path.basename(relativeFilePath).split(".")[0] : lookupKey;
        const address = await this.upload(relativeFilePath, lookupKey, signatureKey, constructorArgs);
        if (typeof address === "undefined") {
            return undefined;
        }
        // TODO: Add padding to hexlifiedLookupKey to make it the right length?  It seems to work without padding.
        const hexlifiedLookupKey = stringTo32ByteHex(lookupKey);
        await this.controller.setValue(hexlifiedLookupKey, address);

        const controlled = ContractFactory(this.connector, this.accountManager, lookupKey, address, this.configuration.gasPrice);
        this.contracts.set(lookupKey, controlled);
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
        const gasEstimate = await this.connector.ethjsQuery.estimateGas({ from: this.accountManager.defaultAddress, data: data })
        const signedTransaction = await this.accountManager.signTransaction({ gas: gasEstimate, gasPrice: this.configuration.gasPrice, data: data});
        const transactionHash = await this.connector.ethjsQuery.sendRawTransaction(signedTransaction);
        const receipt = await waitForTransactionReceipt(this.connector.ethjsQuery, transactionHash, failureDetails);
        return receipt.contractAddress;
    }

    private async upload(contractLookupKey: string, lookupKey: string = "", contractName: string = "", constructorArgs: Array<string> = []): Promise<string|undefined> {
        lookupKey = (lookupKey === "") ? path.basename(contractLookupKey).split(".")[0] : lookupKey;
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
        const contractsToDelegate = {"Orders": true, "TradingEscapeHatch": true};

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
        return await waitForTransactionReceipt(this.connector.ethjsQuery, transactionHash, `Whitelisting ${contractName}`);
    }

    private async whitelistTradingContracts(): Promise<void> {
        const promises: Array<Promise<TransactionReceipt>> = [];
        for (let contractFileName in this.compiledContracts) {
            if (contractFileName.indexOf("trading/") > -1) {
                const contractName = path.basename(contractFileName, ".sol");
                if (!this.contracts.has(contractName)) continue;
                promises.push(this.whitelistContract(contractName));
            }
        }

        await Promise.all(promises);
    }

    private async initializeContract(contractName: string): Promise<TransactionReceipt> {
        const transactionHash = await this.getContract(contractName).setController(this.controller.address);
        return await waitForTransactionReceipt(this.connector.ethjsQuery, transactionHash, `Initializing ${contractName}`);
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
        await waitForTransactionReceipt(this.connector.ethjsQuery, transactionHash, `Initializing universe.`);
        console.log(`Genesis universe address: ${universe.address}`);
        return universe;
    }

    // TODO: move these out of this class. this class is for deploying the contracts, not general purpose Augur interactions.
    // CONSIDER: create a class called Augur or something that deals with the various interactions one may want to participate in
    private async approveCentralAuthority(): Promise<void> {
        const authority = this.getContract('Augur');
        const cash = <Cash>this.getContract('Cash');
        const transactionHash = await cash.approve(authority.address, new BN(2).pow(new BN(256)).sub(new BN(1)));
        await waitForTransactionReceipt(this.connector.ethjsQuery, transactionHash, `Approving central authority.`);
    }

    private async createMarket(universe: Universe, numOutcomes: number, endTime: number, feePerEthInWei: number, denominationToken: string, designatedReporter: string, numTicks: number): Promise<Market> {
        const constant = { constant: true };

        const legacyReputationToken = <LegacyReputationToken>this.getContract('LegacyReputationToken');
        const reputationTokenAddress = await universe.getReputationToken_();
        const reputationToken = new ReputationToken(this.connector, this.accountManager, reputationTokenAddress, this.configuration.gasPrice);

        // get some REP
        // TODO: just get enough REP to cover the bonds rather than over-allocating
        const repFaucetTransactionHash = await legacyReputationToken.faucet(new BN(0));
        const repApprovalTransactionHash = await legacyReputationToken.approve(reputationTokenAddress, new BN(2).pow(new BN(256)).sub(new BN(1)));
        await waitForTransactionReceipt(this.connector.ethjsQuery, repFaucetTransactionHash, `Using legacy reputation faucet.`);
        await waitForTransactionReceipt(this.connector.ethjsQuery, repApprovalTransactionHash, `Approving legacy reputation.`);
        const repMigrationTransactionHash = await reputationToken.migrateFromLegacyReputationToken();
        // necessary because it is used part of market creation fee calculation
        const currentReportingWindowTransactionHash = await universe.getCurrentReportingWindow();
        // necessary because it is used as part of market creation fee calculation
        const previousReportingWindowTransactionHash = await universe.getPreviousReportingWindow();
        // necessary because createMarket needs its reporting window already created
        const marketReportingWindowTransactionHash = await universe.getReportingWindowByMarketEndTime(endTime);
        await waitForTransactionReceipt(this.connector.ethjsQuery, repMigrationTransactionHash, `Migrating reputation.`);
        await waitForTransactionReceipt(this.connector.ethjsQuery, currentReportingWindowTransactionHash, `Instantiating current reporting window.`);
        await waitForTransactionReceipt(this.connector.ethjsQuery, previousReportingWindowTransactionHash, `Instantiating previous reporting window.`);
        await waitForTransactionReceipt(this.connector.ethjsQuery, marketReportingWindowTransactionHash, `Instantiating market reporting window.`);

        const targetReportingWindowAddress = await universe.getReportingWindowByMarketEndTime_(endTime);

        const targetReportingWindow = new ReportingWindow(this.connector, this.accountManager, targetReportingWindowAddress, this.configuration.gasPrice);
        const marketCreationFee = await universe.getMarketCreationCost_();
        const marketAddress = await targetReportingWindow.createMarket_(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter, '', { attachedEth: marketCreationFee });
        if (!marketAddress) {
            throw new Error("Unable to get address for new categorical market.");
        }
        const createMarketTransactionHash = await targetReportingWindow.createMarket(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter, '', { attachedEth: marketCreationFee });
        await waitForTransactionReceipt(this.connector.ethjsQuery, createMarketTransactionHash, `Creating market.`);
        const market = new Market(this.connector, this.accountManager, marketAddress, this.configuration.gasPrice);

        if (await market.getTypeName_() !== stringTo32ByteHex("Market")) {
            throw new Error("Unable to create new categorical market");
        }
        return market;
    }

    private async createReasonableMarket(universe: Universe, denominationToken: string, numOutcomes: number): Promise<Market> {
        const endTime = Math.round(new Date().getTime() / 1000);
        return await this.createMarket(universe, 2, endTime, 10 ** 16, denominationToken, this.accountManager.defaultAddress, 10 ** 4);
    }
}
