#!/usr/bin/env node

import * as binascii from "binascii";
import * as path from "path";
import * as EthContract from "ethjs-contract";
import * as EthQuery from "ethjs-query";
// TODO: Update TS type definition for ContractBlockchainData to allow for empty object (e.g. upload() & uploadAndAddToController())?
import { ContractBlockchainData, ContractReceipt } from "contract-deployment";


export class ContractDeployer {
    private ethQuery;
    private compiledContracts;
    private uploadedContracts = [];
    private fromAddress;
    private gasAmount;
    private controller;

    public getController() {
        return this.controller;
    }

    public getUploadedContracts() {
        return this.uploadedContracts;
    }

    public constructor(ethQuery: EthQuery, contractJson: string, fromAddress: string, gasAmount: number) {
        this.ethQuery = ethQuery;
        this.compiledContracts = JSON.parse(contractJson);
        this.fromAddress = fromAddress;
        this.gasAmount = gasAmount;
    }

    public async deploy(): Promise<boolean> {
        this.controller = await this.upload("../source/contracts/Controller.sol");
        const ownerAddress = (await this.controller.owner())[0];
        if (ownerAddress !== this.fromAddress) {
            throw new Error("Controller owner does not equal from address");
        }

        await this.uploadAllContracts();
        await this.whitelistTradingContracts();
        await this.initializeAllContracts();
        await this.approveCentralAuthority();

        return true;
    }

    public async uploadAndAddDelegatedToController(contractFileName: string, contractName: string): Promise<ContractBlockchainData|undefined> {
        const delegationTargetName = contractName + "Target";
        const hexlifiedDelegationTargetName = "0x" + binascii.hexlify(delegationTargetName);
        const delegatorConstructorArgs = [this.controller.address, hexlifiedDelegationTargetName];

        await this.uploadAndAddToController(contractFileName, delegationTargetName, contractName);
        return await this.uploadAndAddToController("../source/contracts/libraries/Delegator.sol", contractName, "Delegator", delegatorConstructorArgs);
    }

    public async uploadAndAddToController(relativeFilePath: string, lookupKey: string = "", signatureKey: string = "", constructorArgs: any = []): Promise<ContractBlockchainData> {
        lookupKey = (lookupKey === "") ? path.basename(relativeFilePath).split(".")[0] : lookupKey;
        const contract = await this.upload(relativeFilePath, lookupKey, signatureKey, constructorArgs);
        if (typeof contract === "undefined") {
            throw new Error("Unable to upload " + signatureKey + " contract.");
        }
        // TODO: Add padding to hexlifiedLookupKey to make it the right length?  It seems to work without padding.
        const hexlifiedLookupKey = "0x" + binascii.hexlify(lookupKey);
        await this.controller.setValue(hexlifiedLookupKey, contract.address);

        return contract;
    }

    public async upload(relativeFilePath, lookupKey: string = "", signatureKey: string = "", constructorArgs: string[] = []): Promise<ContractBlockchainData> {
        lookupKey = (lookupKey === "") ? path.basename(relativeFilePath).split(".")[0] : lookupKey;
        signatureKey = (signatureKey === "") ? lookupKey : signatureKey;
        if (this.uploadedContracts[lookupKey]) {
            return(this.uploadedContracts[lookupKey]);
        }
        relativeFilePath = relativeFilePath.replace("../source/contracts/", "");
        const abi = this.compiledContracts[relativeFilePath][signatureKey].abi;
        const bytecode = this.compiledContracts[relativeFilePath][signatureKey].evm.bytecode.object;
        // abstract contracts have a 0-length array for bytecode
        if (bytecode.length === 0) {
            throw new Error("Bytecode is not set for " + signatureKey + ".");
        }
        const contractBuilder = new EthContract(this.ethQuery)(abi, bytecode, { from: this.fromAddress, gas: this.gasAmount });
        let receiptAddress: string;
        if (constructorArgs.length > 0) {
            receiptAddress = await contractBuilder.new(constructorArgs[0], constructorArgs[1]);
        } else {
            receiptAddress = await contractBuilder.new();
        }
        const receipt: ContractReceipt = await this.ethQuery.getTransactionReceipt(receiptAddress);
        this.uploadedContracts[lookupKey] = contractBuilder.at(receipt.contractAddress);

        return this.uploadedContracts[lookupKey];
    }

    public async uploadAllContracts(): Promise<boolean> {
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
                } else {
                    uploadedContractPromises.push(this.uploadAndAddToController(contractFileName));
                }
            }
        }

        await Promise.all(uploadedContractPromises);

        return true;
    }

    public async whitelistTradingContracts(): Promise<boolean> {
        for (let contractFileName in this.compiledContracts) {
            if (contractFileName.indexOf("trading/") > -1) {
                const contractName = path.basename(contractFileName, ".sol");
                if (!this.uploadedContracts[contractName]) continue;
                this.controller.addToWhitelist(this.uploadedContracts[contractName].address);
            }
        }

        return true;
    }

    public async initializeAllContracts(): Promise<boolean> {
        const contractsToInitialize = ["Augur","Cash","CompleteSets","CreateOrder","FillOrder","CancelOrder","Trade","ClaimProceeds","OrdersFetcher"];
        for (let contractName of contractsToInitialize) {
            if (this.uploadedContracts[contractName]["setController"]) {
                this.uploadedContracts[contractName].setController(this.controller.address);
            } else if (this.uploadedContracts[contractName]["initialize"]) {
                this.uploadedContracts[contractName].initialize(this.controller.address);
            } else {
                throw new Error("Contract " + contractName + " has neither \"initialize\" nor \"setController\" method on it.");
            }
        }

        return true;
    }

    public async approveCentralAuthority(): Promise<boolean> {
        const authority = this.uploadedContracts["Augur"];
        const contractsToApprove = ["Cash"];

        // TODO: Approve for specific accounts (not sure how to specify sender).

        for (let contractName of contractsToApprove) {
            this.uploadedContracts[contractName].approve(authority.address, 2**254/*, sender=hexlifiedPrivateKey*/);
        }

        return true;
    }
}
