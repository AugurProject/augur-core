import * as path from 'path';
import * as getPort from "get-port";
import BN = require('bn.js');
import { networkConfigurations } from "./NetworkConfigurations";

export class Configuration {
    public readonly httpProviderHost: string;
    public readonly httpProviderPort: number;
    public readonly gasPrice: BN;
    public readonly privateKey: string;
    public readonly contractSourceRoot: string;
    public readonly contractOutputPath: string;
    public readonly abiOutputPath: string;
    public readonly augurContractsRepoUrl: string;
    public readonly augurjsRepoUrl: string;
    public readonly contractAddressesOutputPath: string;
    public readonly contractInterfacesOutputPath: string;
    public readonly controllerAddress: string|undefined;
    public readonly createGenesisUniverse: boolean;
    public readonly isProduction: boolean;
    public readonly useNormalTime: boolean;

    public constructor(host: string, port: number, gasPrice: BN, privateKey: string, contractSourceRoot: string, contractOutputRoot: string, artifactOutputRoot: string, controllerAddress: string|undefined, createGenesisUniverse: boolean=true, isProduction: boolean=false, useNormalTime: boolean=true) {
        this.httpProviderHost = host;
        this.httpProviderPort = port;
        this.gasPrice = gasPrice;
        this.privateKey = privateKey;
        this.contractSourceRoot = contractSourceRoot;
        this.contractOutputPath = path.join(contractOutputRoot, 'contracts.json');
        this.abiOutputPath = path.join(contractOutputRoot, 'abi.json');
        this.contractAddressesOutputPath = path.join(artifactOutputRoot, 'addresses.json');
        this.contractInterfacesOutputPath = path.join(contractSourceRoot, '../libraries', 'ContractInterfaces.ts');
        this.controllerAddress = controllerAddress;
        this.createGenesisUniverse = createGenesisUniverse;
        this.isProduction = isProduction;
        this.useNormalTime = isProduction || useNormalTime;
    }

    private static createWithHost(host: string, port: number, gasPrice: BN, privateKey: string, isProduction: boolean=false, useNormalTime: boolean=true): Configuration {
        const contractSourceRoot = path.join(__dirname, "../../source/contracts/");
        const contractOutputRoot = (typeof process.env.CONTRACT_OUTPUT_ROOT === "undefined") ? path.join(__dirname, "../../output/contracts/") : path.normalize(<string> process.env.CONTRACT_OUTPUT_ROOT);
        const artifactOutputRoot = (typeof process.env.ARTIFACT_OUTPUT_ROOT === "undefined") ? path.join(__dirname, "../../output/artifacts/") : path.normalize(<string> process.env.ARTIFACT_OUTPUT_ROOT);
        const controllerAddress = process.env.AUGUR_CONTROLLER_ADDRESS;
        const createGenesisUniverse = (typeof process.env.CREATE_GENESIS_UNIVERSE === "undefined") ? true : process.env.CREATE_GENESIS_UNIVERSE === "true";

        return new Configuration(host, port, gasPrice, privateKey, contractSourceRoot, contractOutputRoot, artifactOutputRoot, controllerAddress, createGenesisUniverse, isProduction, useNormalTime);
    }

    public static create = async (isProduction: boolean=false, useNormalTime: boolean=true): Promise<Configuration> => {
        const host = (typeof process.env.ETHEREUM_HOST === "undefined") ? "localhost" : process.env.ETHEREUM_HOST!;
        const port = (typeof process.env.ETHEREUM_PORT === "undefined") ? await getPort() : parseInt(process.env.ETHEREUM_PORT || "0");
        const gasPrice = ((typeof process.env.ETHEREUM_GAS_PRICE_IN_NANOETH === "undefined") ? new BN(20) : new BN(process.env.ETHEREUM_GAS_PRICE_IN_NANOETH!)).mul(new BN(1000000000));
        const privateKey = process.env.ETHEREUM_PRIVATE_KEY || '0xbaadf00dbaadf00dbaadf00dbaadf00dbaadf00dbaadf00dbaadf00dbaadf00d';

        return Configuration.createWithHost(host, port, gasPrice, privateKey, isProduction, useNormalTime);
    }

    public static network = (name: string):Configuration => {
        const network = networkConfigurations[name];
        if (network === undefined || network === null) throw new Error(`Network configuration ${name} not found`);
        if (network.privateKey === undefined || network.privateKey === null) throw new Error(`Network configuration for ${name} has no private key available. Check that this key is in the environment ${name.toUpperCase()}_PRIVATE_KEY`);
        return Configuration.createWithHost(network.host, network.port, network.gasPrice, network.privateKey);
    }
}
