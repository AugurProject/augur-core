import BN = require('bn.js');
import { encodeMethod, decodeParams } from 'ethjs-abi';
import { AbiFunction } from 'ethjs-shared';
import { AccountManager } from './AccountManager';
import { Connector } from './Connector';

/**
 * This file is currently authored by hand, but will eventually be auto-generated from an ABI file as a pre-build step.
 * By convention, pure/view methods have a `_` suffix on them indicating to the caller that the function will be executed locally and return the function's result.  payable/nonpayable functions have both a localy version and a remote version (distinguished by the trailing `_`).  If the remote method is called, you will only get back a transaction hash which can be used to lookup the transaction receipt for success/failure (due to EVM limitations you will not get the function results back).
 */

export class Contract {
    protected readonly connector: Connector;
    protected readonly accountManager: AccountManager;
    public readonly address: string;
    protected readonly defaultGasPrice: BN;

    protected constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        this.connector = connector;
        this.accountManager = accountManager;
        this.address = address;
        this.defaultGasPrice = defaultGasPrice;
    }

    protected async localCall(abi: AbiFunction, parameters: Array<any>, sender?: string, attachedEth?: BN): Promise<Array<any>> {
        const from = sender || this.accountManager.defaultAddress;
        const data = encodeMethod(abi, parameters);
        const transaction = Object.assign({ from: from, to: this.address, data: data }, attachedEth ? { value: attachedEth } : {});
        const result = await this.connector.ethjsQuery.call(transaction);
        return decodeParams(abi.outputs.map(x => x.name), abi.outputs.map(x => x.type), result);
    }

    protected async remoteCall(abi: AbiFunction, parameters: Array<any>, sender?: string, gasPrice?: BN, attachedEth?: BN): Promise<string> {
        const from = sender || this.accountManager.defaultAddress;
        const data = encodeMethod(abi, parameters);
        const gas = await this.connector.ethjsQuery.estimateGas(Object.assign({ to: this.address, from: from, data: data }, attachedEth ? { value: attachedEth } : {} ));
        gasPrice = gasPrice || this.defaultGasPrice;
        const transaction = Object.assign({ from: from, to: this.address, data: data, gasPrice: gasPrice, gas: gas }, attachedEth ? { value: attachedEth } : {});
        const signedTransaction = await this.accountManager.signTransaction(transaction);
        return await this.connector.ethjsQuery.sendRawTransaction(signedTransaction);
    }
}

export class Controller extends Contract {
    public constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        super(connector, accountManager, address, defaultGasPrice);
    }

    public owner_ = async (options?: { sender?: string }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"};
        const result = await this.localCall(abi, [], options.sender);
        return <string>result[0];
    }

    public setValue = async (key: string, value: string, options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[{"name":"_key","type":"bytes32"},{"name":"_value","type":"address"}],"name":"setValue","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [key, value], options.sender, options.gasPrice);
    }

    public setValue_ = async (key: string, value: string, options?: { sender?: string }): Promise<boolean> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[{"name":"_key","type":"bytes32"},{"name":"_value","type":"address"}],"name":"setValue","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [key, value], options.sender);
        return <boolean>result[0];
    }

    public addToWhitelist = async (address: string, options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[{"name":"_target","type":"address"}],"name":"addToWhitelist","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [address], options.sender, options.gasPrice);
    }

    public addToWhitelist_ = async (address: string, options?: { sender?: string }): Promise<boolean> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[{"name":"_target","type":"address"}],"name":"addToWhitelist","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [address], options.sender);
        return <boolean>result[0];
    }
}

export class Controlled extends Contract {
    public constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        super(connector, accountManager, address, defaultGasPrice);
    }

    public setController = async (address: string, options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[{"name":"_controller","type":"address"}],"name":"setController","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [address], options.sender, options.gasPrice);
    }

    public setController_ = async (address: string, options?: { sender?: string }): Promise<boolean> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[{"name":"_controller","type":"address"}],"name":"setController","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [address], options.sender);
        return <boolean>result[0];
    }
}

export class StandardToken extends Controlled {
    public constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        super(connector, accountManager, address, defaultGasPrice);
    }

    public balanceOf_ = async(address: string, options?: { sender?: string }): Promise<BN> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[{"name":"target", "type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [address], options.sender);
        return <BN>result[0];
    }

    public approve = async (address: string, amount: BN|number, options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [address, amount], options.sender, options.gasPrice);
    }

    public approve_ = async (address: string, amount: BN|number, options?: { sender?: string }): Promise<boolean> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [address, amount], options.sender);
        return <boolean>result[0];
    }

    public allowance_ = async(address: string, spender: string, options?: { sender?: string }): Promise<BN> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[{"name":"target", "type":"address"}, {"name":"spender", "type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [address, spender], options.sender);
        return <BN>result[0];
    }
}

export class Universe extends Controlled {
    public constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        super(connector, accountManager, address, defaultGasPrice);
    }

    public initialize = async (parentUniverse: string, payoutDistributionHash: string, options?: { sender?: string, gasPrice?: BN }): Promise<string> =>  {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[{"name":"_parentUniverse","type":"address"},{"name":"_parentPayoutDistributionHash","type":"bytes32"}],"name":"initialize","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [parentUniverse, payoutDistributionHash], options.sender, options.gasPrice);
    }

    public initialize_ = async (parentUniverse: string, payoutDistributionHash: string, options?: { sender?: string }): Promise<boolean> =>  {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[{"name":"_parentUniverse","type":"address"},{"name":"_parentPayoutDistributionHash","type":"bytes32"}],"name":"initialize","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [parentUniverse, payoutDistributionHash], options.sender);
        return <boolean>result[0];
    }

    public getTypeName_ = async (options?: { sender?: string }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[],"name":"getTypeName","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"};
        const result = await this.localCall(abi, [], options.sender);
        return <string>result[0];
    }

    public getReputationToken_ = async (options?: { sender?: string }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[],"name":"getReputationToken","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"};
        const result = await this.localCall(abi, [], options.sender);
        return <string>result[0];
    }

    public getCurrentReportingWindow = async (options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[],"name":"getCurrentReportingWindow","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [], options.sender, options.gasPrice);
    }

    public getCurrentReportingWindow_ = async (options?: { sender?: string }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[],"name":"getCurrentReportingWindow","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [], options.sender);
        return <string>result[0];
    }

    public getPreviousReportingWindow = async (options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[],"name":"getPreviousReportingWindow","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [], options.sender, options.gasPrice);
    }

    public getPreviousReportingWindow_ = async (options?: { sender?: string }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[],"name":"getPreviousReportingWindow","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [], options.sender);
        return <string>result[0];
    }

    public getReportingWindowByMarketEndTime = async (endTime: BN|number, options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[{"name":"_endTime","type":"uint256"}],"name":"getReportingWindowByMarketEndTime","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [endTime], options.sender, options.gasPrice);
    }

    public getReportingWindowByMarketEndTime_ = async (endTime: BN|number, options?: { sender?: string }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[{"name":"_endTime","type":"uint256"}],"name":"getReportingWindowByMarketEndTime","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [endTime], options.sender);
        return <string>result[0];
    }

    public getMarketCreationCost = async (options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[],"name":"getMarketCreationCost","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [], options.sender, options.gasPrice);
    }

    public getMarketCreationCost_ = async (options?: { sender?: string }): Promise<BN> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[],"name":"getMarketCreationCost","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [], options.sender);
        return <BN>result[0];
    }
}

export class ReputationToken extends StandardToken {
    public constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        super(connector, accountManager, address, defaultGasPrice);
    }

    public getTypeName_ = async (options?: { sender?: string }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[],"name":"getTypeName","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"};
        const result = await this.localCall(abi, [], options.sender);
        return <string>result[0];
    }

    public migrateFromLegacyReputationToken = async(options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[],"name":"migrateFromLegacyReputationToken","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [], options.sender, options.gasPrice);
    }

    public migrateFromLegacyReputationToken_ = async(options?: { sender?: string }): Promise<boolean> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[],"name":"migrateFromLegacyReputationToken","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [], options.sender);
        return <boolean>result[0];
    }
}

export class ReportingWindow extends Controlled {
    public constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        super(connector, accountManager, address, defaultGasPrice);
    }

    public createMarket = async(endTime: BN|number, numOutcomes: BN|number, numTicks: BN|number, feePerEthInWei: BN|number, denominationToken: string, designatedReporterAddress: string, extraInfo: string, options?: { sender?: string, gasPrice?: BN, attachedEth?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[{"name":"_endTime","type":"uint256"},{"name":"_numOutcomes","type":"uint8"},{"name":"_numTicks","type":"uint256"},{"name":"_feePerEthInWei","type":"uint256"},{"name":"_denominationToken","type":"address"},{"name":"_designatedReporterAddress","type":"address"},{"name":"_extraInfo","type":"string"}],"name":"createMarket","outputs":[{"name":"","type":"address"}],"payable":true,"stateMutability":"payable","type":"function"};
        return await this.remoteCall(abi, [endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporterAddress, extraInfo], options.sender, options.gasPrice, options.attachedEth);
    }

    public createMarket_ = async(endTime: BN|number, numOutcomes: BN|number, numTicks: BN|number, feePerEthInWei: BN|number, denominationToken: string, designatedReporterAddress: string, extraInfo: string, options?: { sender?: string, attachedEth?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[{"name":"_endTime","type":"uint256"},{"name":"_numOutcomes","type":"uint8"},{"name":"_numTicks","type":"uint256"},{"name":"_feePerEthInWei","type":"uint256"},{"name":"_denominationToken","type":"address"},{"name":"_designatedReporterAddress","type":"address"},{"name":"_extraInfo","type":"string"}],"name":"createMarket","outputs":[{"name":"","type":"address"}],"payable":true,"stateMutability":"payable","type":"function"};
        const result = await this.localCall(abi, [endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporterAddress, extraInfo], options.sender, options.attachedEth);
        return <string>result[0];
    }
}

export class Market extends Controlled {
    public constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        super(connector, accountManager, address, defaultGasPrice);
    }

    public getTypeName_ = async (options?: { sender?: string }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[],"name":"getTypeName","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"};
        const result = await this.localCall(abi, [], options.sender);
        return <string>result[0];
    }
}

export class Cash extends StandardToken {
    public constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        super(connector, accountManager, address, defaultGasPrice);
    }
}

// FIXME: this isn't actually controlled, but it is one-off and causes much grief so just faking it for now
export class LegacyReputationToken extends StandardToken {
    public constructor(connector: Connector, accountManager: AccountManager, address: string, defaultGasPrice: BN) {
        super(connector, accountManager, address, defaultGasPrice);
    }

    public faucet = async (amount: BN|number, options?: { sender?: string, gasPrice?: BN }): Promise<string> => {
        options = options || {};
        const abi: AbiFunction = {"constant":false,"inputs":[{"name":"_amount","type":"uint256"}],"name":"faucet","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        return await this.remoteCall(abi, [amount], options.sender, options.gasPrice);
    }

    public faucet_ = async (amount: BN|number, options?: { sender?: string }): Promise<boolean> => {
        options = options || {};
        const abi: AbiFunction = {"constant":true,"inputs":[{"name":"_amount","type":"uint256"}],"name":"faucet","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"};
        const result = await this.localCall(abi, [amount], options.sender);
        return <boolean>result[0];
    }
}

export function ContractFactory(connector: Connector, accountManager: AccountManager, name: string, address: string, defaultGasPrice: BN): Controlled {
    if (name === 'Cash') {
        return new StandardToken(connector, accountManager, address, defaultGasPrice);
    } else if (name === 'LegacyReputationToken') {
        return new LegacyReputationToken(connector, accountManager, address, defaultGasPrice);
    } else {
        return new Controlled(connector, accountManager, address, defaultGasPrice);
    }
}
