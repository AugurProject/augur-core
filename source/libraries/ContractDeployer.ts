#!/usr/bin/env node

import * as binascii from 'binascii';
import * as path from 'path';
import * as HttpProvider from 'ethjs-provider-http';
import * as Eth from 'ethjs-query';
import * as EthContract from 'ethjs-contract';
// TODO: Update TS type definition for ContractBlockchainData to allow for empty object (e.g. upload() & uploadAndAddToController())?
import { ContractBlockchainData, ContractReceipt } from 'contract-deployment';


export class ContractDeployer {
    private eth;
    private compiledContracts;
    private uploadedContracts;
    private fromAddress;
    private gasAmount;
    private controller;

    public getUploadedContracts() {
        return this.uploadedContracts;
    }

    public async initialize(eth: Eth, contractJson: string, fromAddress: string, gasAmount: number): Promise<boolean> {
        this.eth = eth;
        this.compiledContracts = JSON.parse(contractJson);
        this.uploadedContracts = {};
        this.fromAddress = fromAddress;
        this.gasAmount = gasAmount;

        this.controller = await this.upload("../source/contracts/Controller.sol");
        const ownerAddress = (await this.controller.owner())[0];
        if (ownerAddress != fromAddress) {
            throw new Error("Controller owner does not equal from address");
        }

        await this.uploadAllContracts();
        await this.whitelistTradingContracts();
        await this.initializeAllContracts();
        // await this.approveCentralAuthority();

        return true;
    }

    public async uploadAndAddToController(relativeFilePath: string, lookupKey: string = "", signatureKey: string = "", constructorArgs: any = []): Promise<ContractBlockchainData> {
        lookupKey = (lookupKey == "") ? path.basename(relativeFilePath).split(".")[0] : lookupKey;
        const contract = await this.upload(relativeFilePath, lookupKey, signatureKey, constructorArgs);
        if (typeof contract == "undefined") {
            return {};
        }
        const pad = "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";
        const paddedLookupKey = pad.substring(0, pad.length - lookupKey.length) + lookupKey;
        const hexlifiedLookupKey = '0x' + binascii.hexlify(paddedLookupKey);
        this.controller.setValue(hexlifiedLookupKey, contract.address);

        return contract;
    }

    public async upload(relativeFilePath, lookupKey: string = "", signatureKey: string = "", constructorArgs: string[] = []): Promise<ContractBlockchainData> {
        lookupKey = (lookupKey == "") ? path.basename(relativeFilePath).split(".")[0] : lookupKey;
        signatureKey = (signatureKey == "") ? lookupKey : signatureKey;

        if (this.uploadedContracts[lookupKey]) {
            return(this.uploadedContracts[lookupKey]);
        }

        relativeFilePath = relativeFilePath.replace("../source/contracts/", "");
        const abi = this.compiledContracts[relativeFilePath][signatureKey].abi;
        const bytecode = this.compiledContracts[relativeFilePath][signatureKey].evm.bytecode.object;
        // abstract contracts have a 0-length array for bytecode
        if (bytecode.length == 0) {
            return {};
        }

        const contractBuilder = new EthContract(this.eth)(abi, bytecode, { from: this.fromAddress, gas: this.gasAmount });
        let receiptAddress: string;
        if (constructorArgs.length > 0) {
            receiptAddress = await contractBuilder.new(constructorArgs[0], constructorArgs[1]);
        } else {
            receiptAddress = await contractBuilder.new();
        }
        const receipt: ContractReceipt = await this.eth.getTransactionReceipt(receiptAddress);
        this.uploadedContracts[lookupKey] = contractBuilder.at(receipt.contractAddress);

        return this.uploadedContracts[lookupKey];
    }

    public async uploadAllContracts(): Promise<boolean> {
        const contractsToDelegate = {"Orders": true, "TradingEscapeHatch": true};

        for (let contractFileName in this.compiledContracts) {
            if (contractFileName == "Controller.sol" || contractFileName == "libraries/Delegator.sol") {
                continue;
            }

            for (let contractName in this.compiledContracts[contractFileName]) {
                // Filter out interface contracts, as they do not need to be deployed
                if (this.compiledContracts[contractFileName][contractName].evm.bytecode.object == "") {
                    continue;
                }

                // TODO: Change this to allow contracts to be deployed asynchronously
                if (contractsToDelegate[contractName] == true) {
                    const pad = "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00";
                    const delegationTargetName = contractName + "Target";
                    const paddedDelegationTargetName = pad.substring(0, pad.length - delegationTargetName.length) + delegationTargetName;
                    const hexlifiedDelegationTargetName = '0x' + binascii.hexlify(paddedDelegationTargetName);
                    const delegatorConstructorArgs = [this.controller.address, hexlifiedDelegationTargetName];

                    await this.uploadAndAddToController(contractFileName, delegationTargetName, contractName);
                    await this.uploadAndAddToController("../source/contracts/libraries/Delegator.sol", contractName, "Delegator", delegatorConstructorArgs);
                } else {
                    await this.uploadAndAddToController(contractFileName);
                 }
            }
        }

        return true;
    }

    public async whitelistTradingContracts(): Promise<boolean> {
        for (let contractFileName in this.compiledContracts) {
            if (contractFileName.indexOf("trading/") > -1) {
                const contractName = path.basename(contractFileName, '.sol');
                if (!this.uploadedContracts[contractName]) continue;
                this.controller.addToWhitelist(this.uploadedContracts[contractName].address);
            }
        }

        return true;
    }

    public async initializeAllContracts(): Promise<boolean> {
    const contractsToInitialize = ['Augur', 'Cash', 'CompleteSets', 'MakeOrder', 'TakeOrder', 'CancelOrder', 'Trade', 'ClaimProceeds', 'OrdersFetcher'];
        for (let contractName of contractsToInitialize) {
            if (this.uploadedContracts[contractName]["setController"]) {
                this.uploadedContracts[contractName].setController(this.controller.address);
            } else if (this.uploadedContracts[contractName]["initialize"]) {
                this.uploadedContracts[contractName].initialize(this.controller.address);
            } else {
                throw new Error("contract has neither 'initialize' nor 'setController' method on it.");
            }
        }

        return true;
    }

    public async approveCentralAuthority(self): Promise<boolean> {
        const authority = this.uploadedContracts['Augur'];
        const contractsToApprove = ['Cash'];
        const testersGivingApproval = await this.eth.accounts();
        for (let testerKey of testersGivingApproval) {
            console.log("TesterKey: " + testerKey);
            for (let contractName of contractsToApprove) {
                console.log("contractName: " + contractName);
                this.uploadedContracts[contractName].approve(authority.address, 2**254, sender=testerKey);
            }
        }

        return true;
    }
}
