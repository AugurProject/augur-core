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
import { CompilerOutputContracts, CompilerOutputAbi } from "solc";

export class ContractDeployer {
    public readonly ethjsQuery: EthjsQuery;
    public readonly ethjsContract: EthjsContract;
    public readonly compiledContracts: CompilerOutputContracts;
    public readonly gasPrice: number;
    public readonly contracts = {};
    public readonly abis = new Map<string, Array<CompilerOutputAbi>>();
    public readonly bytecodes = new Map<string, string>();
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
        console.log('Creating genesis universe...');
        this.universe = await this.createGenesisUniverse();
        // FIXME: the rest of this shouldn't be part of the deploy script, it should be part of an integration test
        console.log('Approving central authoritiy...');
        await this.approveCentralAuthority();
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

    private getEncodedConstructData(abi: Array<CompilerOutputAbi>, bytecode: string, constructorArgs: Array<string>): string {
        if (constructorArgs.length === 0) {
            return bytecode;
        }
        const constructorSignature = abi.find(signature => signature.type === 'constructor')!;
        const constructorInputTypes = constructorSignature.inputs.map(x => x.type);
        const encodedConstructorParameters = EthjsAbi.encodeParams(constructorInputTypes, constructorArgs).substring(2);
        return `${bytecode}${encodedConstructorParameters}`
    }

    private async construct(contractLookupKey: string, contractName: string, constructorArgs: Array<string>, failureDetails: string) {
        const abi = this.compiledContracts[contractLookupKey][contractName]!.abi;
        const bytecode = this.compiledContracts[contractLookupKey][contractName]!.evm.bytecode.object;
        const builder = this.ethjsContract(abi, bytecode, { from: this.testAccounts[0], gasPrice: this.gasPrice });
        const data = this.getEncodedConstructData(abi, bytecode, constructorArgs);
        const gasEstimate = await this.ethjsQuery.estimateGas({ from: this.testAccounts[0], data: data })
        const transactionHash = await builder.new(...constructorArgs, { gas: gasEstimate });
        const receipt = await waitForTransactionReceipt(this.ethjsQuery, transactionHash, failureDetails);
        return builder.at(receipt.contractAddress);
    }

    private async upload(contractLookupKey: string, lookupKey: string = "", contractName: string = "", constructorArgs: Array<string> = []): Promise<ContractBlockchainData|undefined> {
        lookupKey = (lookupKey === "") ? path.basename(contractLookupKey).split(".")[0] : lookupKey;
        contractName = (contractName === "") ? lookupKey : contractName;
        if (this.contracts[lookupKey]) {
            return(this.contracts[lookupKey]);
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
        this.contracts[lookupKey] = await this.construct(contractLookupKey, contractName, constructorArgs, `Uploading ${contractName}`);
        return this.contracts[lookupKey];
    }

    private async uploadAllContracts(): Promise<void> {
        const contractsToDelegate = {"Orders": true, "TradingEscapeHatch": true};

        const promises: Promise<ContractBlockchainData|undefined>[] = [];
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

    private async createGenesisUniverse(): Promise<ContractBlockchainData> {
        const delegator = await this.construct("libraries/Delegator.sol", "Delegator", [ this.controller.address, stringTo32ByteHex('Universe') ], `Instantiating genesis universe.`);
        const universeBuilder = this.ethjsContract(this.abis.get("Universe")!, this.bytecodes.get("Universe")!, { from: this.testAccounts[0], gasPrice: this.gasPrice });
        const universe = universeBuilder.at(delegator.address);
        const transactionHash = await universe.initialize("0x0000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000000");
        await waitForTransactionReceipt(this.ethjsQuery, transactionHash, `Initializing universe.`);
        console.log(`Genesis universe address: ${universe.address}`);
        return universe;
    }

    // TODO: move these out of this class. this class is for deploying the contracts, not general purpose Augur interactions.
    // CONSIDER: create a class called Augur or something that deals with the various interactions one may want to participate in
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

    public async getStakeToken(market, payoutDistribution, invalid): Promise<ContractBlockchainData> {
        const stakeTokenAddress = market.getStakeToken(payoutDistribution, invalid);
        if (!stakeTokenAddress) {
            throw new Error();
        }
        const signature = this.abis.get("StakeToken");
        const bytecode = this.bytecodes.get("StakeToken")!;
        const contractBuilder = await this.ethjsContract(signature, bytecode, { from: this.testAccounts[0] });
        const gasEstimate = await this.ethjsQuery.estimateGas({ from: this.testAccounts[0], data: bytecode });
        const stakeToken = await contractBuilder.at(stakeTokenAddress, { gas: gasEstimate });

        return stakeToken;
    }

    private async createMarket(universeAddress: string, numOutcomes: number, endTime: number, feePerEthInWei: number, denominationToken: string, designatedReporter: string, numTicks: number): Promise<Contract> {
        const constant = { constant: true };

        const universe = parseAbiIntoMethods(this.ethjsQuery, this.abis.get("Universe")!, { to: universeAddress, from: this.testAccounts[0], gasPrice: this.gasPrice });
        const legacyReputationToken = parseAbiIntoMethods(this.ethjsQuery, this.abis.get('LegacyReputationToken')!, { to: this.contracts['LegacyReputationToken'].address, from: this.testAccounts[0], gasPrice: this.gasPrice });
        const reputationTokenAddress = await universe.getReputationToken();
        const reputationToken = parseAbiIntoMethods(this.ethjsQuery, this.abis.get('ReputationToken')!, { to: reputationTokenAddress, from: this.testAccounts[0], gasPrice: this.gasPrice });

        // get some REP
        // TODO: just get enough REP to cover the bonds rather than over-allocating
        const repFaucetTransactionHash = await legacyReputationToken.faucet(0);
        const repApprovalTransactionHash = await legacyReputationToken.approve(reputationTokenAddress, "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");
        await waitForTransactionReceipt(this.ethjsQuery, repFaucetTransactionHash, `Using legacy reputation faucet.`);
        await waitForTransactionReceipt(this.ethjsQuery, repApprovalTransactionHash, `Approving legacy reputation.`);
        const repMigrationTransactionHash = await reputationToken.migrateFromLegacyReputationToken();
        // necessary because it is used part of market creation fee calculation
        const currentReportingWindowTransactionHash = await universe.getCurrentReportingWindow();
        // necessary because it is used as part of market creation fee calculation
        const previousReportingWindowTransactionHash = await universe.getPreviousReportingWindow();
        // necessary because createMarket needs its reporting window already created
        const marketReportingWindowTransactionHash = await universe.getReportingWindowByMarketEndTime(endTime);
        await waitForTransactionReceipt(this.ethjsQuery, repMigrationTransactionHash, `Migrating reputation.`);
        await waitForTransactionReceipt(this.ethjsQuery, currentReportingWindowTransactionHash, `Instantiating current reporting window.`);
        await waitForTransactionReceipt(this.ethjsQuery, previousReportingWindowTransactionHash, `Instantiating previous reporting window.`);
        await waitForTransactionReceipt(this.ethjsQuery, marketReportingWindowTransactionHash, `Instantiating market reporting window.`);

        const targetReportingWindowAddress = await universe.getReportingWindowByMarketEndTime.bind(constant)(endTime);

        const targetReportingWindow = parseAbiIntoMethods(this.ethjsQuery, this.abis.get('ReportingWindow')!, { to: targetReportingWindowAddress, from: this.testAccounts[0], gasPrice: this.gasPrice });
        const marketCreationFee = await universe.getMarketCreationCost.bind(constant)();
        const marketAddress = await targetReportingWindow.createMarket.bind({ value: marketCreationFee, constant: true })(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter);
        if (!marketAddress) {
            throw new Error("Unable to get address for new categorical market.");
        }
        const createMarketTransactionHash = await targetReportingWindow.createMarket.bind({ value: marketCreationFee })(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter);
        await waitForTransactionReceipt(this.ethjsQuery, createMarketTransactionHash, `Creating market.`);
        const market = parseAbiIntoMethods(this.ethjsQuery, this.abis.get("Market")!, { to: marketAddress, from: this.testAccounts[0], gasPrice: this.gasPrice });
        const marketNameHex = stringTo32ByteHex("Market");

        if (await market.getTypeName() !== marketNameHex) {
            throw new Error("Unable to create new categorical market");
        }
        return market;
    }

    private async createReasonableMarket(universe: string, denominationToken: string, numOutcomes: number): Promise<Contract> {
        const endTime = Math.round(new Date().getTime() / 1000);
        return await this.createMarket(universe, 2, endTime, 10 ** 16, denominationToken, this.testAccounts[0], 10 ** 4);
    }
}
