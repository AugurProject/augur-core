import { hash } from 'crypto-promise';
import { Repository } from 'nodegit';
import { resolve as resolvePath } from 'path';
import { writeFile } from "async-file";
import { encodeParams } from 'ethjs-abi';
import { TransactionReceipt } from 'ethjs-shared';
import { stringTo32ByteHex, resolveAll } from "./HelperFunctions";
import { CompilerOutput } from "solc";
import { Abi, AbiFunction } from 'ethereum';
import { Configuration } from './Configuration';
import { Connector } from './Connector';
import { Augur, ContractFactory, Controller, Controlled, Universe } from './ContractInterfaces';
import { AccountManager } from './AccountManager';
import { Contracts, Contract } from './Contracts';

export class ContractDeployer {
    private readonly accountManager: AccountManager;
    private readonly configuration: Configuration;
    private readonly connector: Connector;
    private readonly contracts: Contracts;
    public controller: Controller;
    public universe: Universe;

    public constructor(configuration: Configuration, connector: Connector, accountManager: AccountManager, compilerOutput: CompilerOutput) {
        this.configuration = configuration;
        this.connector = connector;
        this.accountManager = accountManager;
        this.contracts = new Contracts(compilerOutput);
    }

    public async deploy(): Promise<void> {
        this.controller = await this.uploadController();
        await this.uploadAugur();
        await this.uploadAllContracts();
        await this.initializeAllContracts();
        await this.whitelistTradingContracts();

        if(this.configuration.createGenesisUniverse) {
            this.universe = await this.createGenesisUniverse();
        }

        await this.generateAddressMappingFile();
    }

    public getContract = (contractName: string): Controlled => {
        if (!this.contracts.has(contractName)) throw new Error(`Contract named ${contractName} does not exist.`);
        const contract = this.contracts.get(contractName);
        if (contract.address === undefined) throw new Error(`Contract name ${contractName} has not yet been uploaded.`);
        const controlled = ContractFactory(this.connector, this.accountManager, contract.address, this.configuration.gasPrice);
        return controlled;
    }

    private static async getGitCommit(): Promise<string> {
        const repositoryRootPath = resolvePath(__dirname, '..', '..');
        const repository = await Repository.open(repositoryRootPath);
        const headCommit = await repository.getHeadCommit();
        return `0x${headCommit.sha()}`;
    }

    private static async getBytecodeSha(bytecode: Buffer): Promise<string> {
        const digest = await hash('sha256')(bytecode);
        return `0x${digest.toString('hex')}`;
    }

    private static getEncodedConstructData(abi: Abi, bytecode: Buffer, constructorArgs: Array<string>): Buffer {
        if (constructorArgs.length === 0) {
            return bytecode;
        }
        // TODO: submit a TypeScript bug that it can't deduce the type is AbiFunction|undefined here
        const constructorSignature = <AbiFunction|undefined>abi.find(signature => signature.type === 'constructor');
        if (typeof constructorSignature === 'undefined') throw new Error(`ABI did not contain a constructor.`);
        const constructorInputTypes = constructorSignature.inputs.map(x => x.type);
        const encodedConstructorParameters = Buffer.from(encodeParams(constructorInputTypes, constructorArgs).substring(2), 'hex');
        return Buffer.concat([bytecode, encodedConstructorParameters]);
    }

    private async uploadController(): Promise<Controller> {
        console.log('Uploading controller...');
        const address = (this.configuration.controllerAddress !== undefined)
            ? this.configuration.controllerAddress
            : await this.construct(this.contracts.get('Controller'), [], `Uploading Controller.sol`);
        const controller = new Controller(this.connector, this.accountManager, address, this.configuration.gasPrice);
        const ownerAddress = await controller.owner_();
        if (ownerAddress.toLowerCase() !== this.accountManager.defaultAddress.toLowerCase()) {
            throw new Error("Controller owner does not equal from address");
        }
        console.log(`Controller address: ${controller.address}`);
        return controller;
    }

    private async uploadAugur(): Promise<void> {
        // We have to upload and initialize Augur first so it can log the registration and whitelisting of other contracts
        const contract = await this.contracts.get("Augur");
        const address = await this.construct(contract, [], `Uploading ${contract.contractName}`);
        const commitHash = await ContractDeployer.getGitCommit();
        const bytecodeHash = await ContractDeployer.getBytecodeSha(contract.bytecode);
        const augur = new Augur(this.connector, this.accountManager, address, this.configuration.gasPrice);
        contract.address = address;
        const setControllerTransactionHash = await augur.setController(this.controller.address);
        await this.connector.waitForTransactionReceipt(setControllerTransactionHash, `Initializing Augur.`);
        await this.controller.registerContract(stringTo32ByteHex("Augur"), address, commitHash, bytecodeHash);
    }

    private async uploadAllContracts(): Promise<void> {
        console.log('Uploading contracts...');
        const promises = [...this.contracts].map(contract => this.upload(contract));
        await resolveAll(promises);
    }

    private async upload(contract: Contract): Promise<void> {
        const contractsToDelegate: {[key:string]: boolean} = {"Orders": true, "TradingEscapeHatch": true, "Cash": true};
        const contractName = contract.contractName
        if (contractName === 'Controller') return;
        if (contractName === 'Delegator') return;
        if (contractName === 'TimeControlled') return;
        if (contractName === 'Augur') return;
        if (contractName === 'Time') contract = this.configuration.useNormalTime ? contract: this.contracts.get('TimeControlled');
        if (contract.relativeFilePath.startsWith('legacy_reputation/')) return;
        if (contract.relativeFilePath.startsWith('libraries/')) return;
        // Check to see if we have already uploded this version of the contract
        if (await this.shouldUpgradeContract(contract, contractsToDelegate[contractName])) {
            console.log(`Using existing contract for ${contractName}`);
            contract.address = await this.getExistingContractAddress(contractName);
        } else {
            console.log(`Uploading new version of contract for ${contractName}`);
            contract.address = contractsToDelegate[contractName]
                ? await this.uploadAndAddDelegatedToController(contract)
                : await this.uploadAndAddToController(contract, contractName);
        }
    }

    private async shouldUpgradeContract(contract: Contract, isDelegated: boolean): Promise<boolean> {
        const bytecodeHash = await ContractDeployer.getBytecodeSha(contract.bytecode);
        const key = stringTo32ByteHex(isDelegated ? `${contract.contractName}Target` : contract.contractName);
        const contractDetails = await this.controller.getContractDetails_(key);
        const previouslyUploadedBytecodeHash = contractDetails[2];
        return bytecodeHash === previouslyUploadedBytecodeHash;
    }

    private async getExistingContractAddress(contractName: string): Promise<string> {
        const key = stringTo32ByteHex(contractName);
        const contractDetails = await this.controller.getContractDetails_(key);
        return contractDetails[0];
    }

    private async uploadAndAddDelegatedToController(contract: Contract): Promise<string> {
        const delegationTargetName = `${contract.contractName}Target`;
        const delegatorConstructorArgs = [this.controller.address, stringTo32ByteHex(delegationTargetName)];
        await this.uploadAndAddToController(contract, delegationTargetName);
        return await this.uploadAndAddToController(this.contracts.get('Delegator'), contract.contractName, delegatorConstructorArgs);
    }

    private async uploadAndAddToController(contract: Contract, registrationContractName: string = contract.contractName, constructorArgs: Array<any> = []): Promise<string> {
        const address = await this.construct(contract, constructorArgs, `Uploading ${contract.contractName}`);
        const commitHash = await ContractDeployer.getGitCommit();
        const bytecodeHash = await ContractDeployer.getBytecodeSha(contract.bytecode);
        await this.controller.registerContract(stringTo32ByteHex(registrationContractName), address, commitHash, bytecodeHash);
        return address;
    }

    private async construct(contract: Contract, constructorArgs: Array<string>, failureDetails: string): Promise<string> {
        const data = `0x${ContractDeployer.getEncodedConstructData(contract.abi, contract.bytecode, constructorArgs).toString('hex')}`;
        // TODO: remove `gas` property once https://github.com/ethereumjs/testrpc/issues/411 is fixed
        const gasEstimate = await this.connector.ethjsQuery.estimateGas({ from: this.accountManager.defaultAddress, data: data });
        const nonce = await this.accountManager.nonces.get(this.accountManager.defaultAddress);
        const signedTransaction = await this.accountManager.signTransaction({ gas: gasEstimate, gasPrice: this.configuration.gasPrice, data: data});
        console.log(`Upload contract: ${contract.contractName} nonce: ${nonce}, gas: ${gasEstimate}`);
        const transactionHash = await this.connector.ethjsQuery.sendRawTransaction(signedTransaction);
        const receipt = await this.connector.waitForTransactionReceipt(transactionHash, failureDetails);
        console.log(`Uploaded contract: ${contract.contractName}: \"${receipt.contractAddress}\"`);
        return receipt.contractAddress;
    }

    private async whitelistTradingContracts(): Promise<void> {
        console.log('Whitelisting contracts...');
        const promises: Array<Promise<TransactionReceipt>> = [];
        for (let contract of this.contracts) {
            if (!contract.relativeFilePath.startsWith("trading/")) continue;
            if (contract.address === undefined) throw new Error(`Attempted to whitelist ${contract.contractName} but it has not yet been uploaded.`);
            // Skip if already whitelisted (happens if this contract was previously uploaded)
            if (await this.controller.whitelist_(contract.address)) {
                console.log(`Skipping already whitelisted ${contract.contractName}.`);
                continue;
            } else {
                console.log(`Whitelisting ${contract.contractName}`);
                promises.push(this.whitelistContract(contract.contractName, contract.address));
            }
        }

        await resolveAll(promises);
    }

    private async whitelistContract(contractName: string, contractAddress: string): Promise<TransactionReceipt> {
        const transactionHash = await this.controller.addToWhitelist(contractAddress, { sender: this.accountManager.defaultAddress });
        return await this.connector.waitForTransactionReceipt(transactionHash, `Whitelisting ${contractName}`);
    }

    private async initializeAllContracts(): Promise<void> {
        console.log('Initializing contracts...');
        const contractsToInitialize = ["CompleteSets","CreateOrder","FillOrder","CancelOrder","Trade","ClaimTradingProceeds","OrdersFetcher","Time"];
        const promises: Array<Promise<any>> = [];
        for (let contractName of contractsToInitialize) {
            promises.push(this.initializeContract(contractName));
        }

        await resolveAll(promises);
    }

    private async initializeContract(contractName: string): Promise<TransactionReceipt|void> {
        // Check if contract already initialized (happens if this contract was previously uploaded)
        if (contractName === 'Time') contractName = this.configuration.useNormalTime ? contractName: "TimeControlled";
        if (await this.getContract(contractName).getController_() === this.controller.address) {
            console.log(`Skipping already initialized ${contractName}.`)
            return;
        }
        console.log(`Initializing ${contractName}`);
        const transactionHash = await this.getContract(contractName).setController(this.controller.address);
        return await this.connector.waitForTransactionReceipt(transactionHash, `Initializing ${contractName}`);
    }

    private async createGenesisUniverse(): Promise<Universe> {
        console.log('Creating genesis universe...');
        const augur = new Augur(this.connector, this.accountManager, this.getContract("Augur").address, this.configuration.gasPrice);
        const universeAddress = await augur.createGenesisUniverse_();
        if (!universeAddress || universeAddress == "0x") {
            throw new Error("Unable to create genesis universe. eth_call failed");
        }
        const transactionHash = await augur.createGenesisUniverse();
        await this.connector.waitForTransactionReceipt(transactionHash, `Waiting on genesis universe creation...`);
        const universe = new Universe(this.connector, this.accountManager, universeAddress, this.configuration.gasPrice);
        await this.connector.waitForTransactionReceipt(transactionHash, `Initializing universe.`);
        console.log(`Genesis universe address: ${universe.address}`);
        if (await universe.getTypeName_() !== stringTo32ByteHex("Universe")) {
            throw new Error("Unable to create genesis universe. Get type name failed");
        }
        return universe;
    }

    private async generateAddressMapping(): Promise<string> {
        const mapping: { [name: string]: string } = {};
        mapping['Controller'] = this.controller.address;
        if (this.universe) mapping['Universe'] = this.universe.address;
        if (this.contracts.get('Augur').address === undefined) throw new Error(`Augur not uploaded.`);
        mapping['Augur'] = this.contracts.get('Augur').address!;
        mapping['LegacyReputationToken'] = this.contracts.get('LegacyReputationToken').address!;
        mapping['Mailbox'] = this.contracts.get('Mailbox').address!;
        for (let contract of this.contracts) {
            if (!contract.relativeFilePath.startsWith('trading/')) continue;
            if (/^I[A-Z].*/.test(contract.contractName)) continue;
            if (contract.address === undefined) throw new Error(`${contract.contractName} not uploaded.`);
            mapping[contract.contractName] = contract.address;
        }
        const networkId = await this.connector.ethjsQuery.net_version();
        return JSON.stringify({ [networkId]: mapping }, null, '\t');
    }

    private async generateAddressMappingFile(): Promise<void> {
        const addressMappingJson = await this.generateAddressMapping();
        await writeFile(this.configuration.contractAddressesOutputPath, addressMappingJson, 'utf8')
    }
}
