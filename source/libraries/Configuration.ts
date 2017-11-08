import * as path from 'path';
import * as getPort from "get-port";
import BN = require('bn.js');

export class Configuration {
    public readonly httpProviderHost: string;
    public readonly httpProviderPort: number;
    public readonly gasPrice: BN;
    public readonly privateKey: string;
    public readonly contractSourceRoot: string;
    public readonly contractOutputPath: string;
    public readonly contractInterfacesOutputPath: string;
    public readonly controllerAddress: string|undefined;

    public constructor(host: string, port: number, gasPrice: BN, privateKey: string, contractSourceRoot: string, contractOutputPath: string, contractInterfacesOutputPath: string, controllerAddress: string|undefined) {
        this.httpProviderHost = host;
        this.httpProviderPort = port;
        this.gasPrice = gasPrice;
        this.privateKey = privateKey;
        this.contractSourceRoot = contractSourceRoot;
        this.contractOutputPath = contractOutputPath;
        this.contractInterfacesOutputPath = contractInterfacesOutputPath;
        this.controllerAddress = controllerAddress;
    }

    public static create = async (): Promise<Configuration> => {
        const host = (typeof process.env.ETHEREUM_HOST === "undefined") ? "localhost" : process.env.ETHEREUM_HOST!;
        const port = (typeof process.env.ETHEREUM_PORT === "undefined") ? await getPort() : parseInt(process.env.ETHEREUM_PORT || "0");
        const gasPrice = (typeof process.env.ETHEREUM_GAS_PRICE_IN_NANOETH === "undefined") ? new BN(20) : new BN(process.env.ETHEREUM_GAS_PRICE_IN_NANOETH!).mul(new BN(1000000000));
        const privateKey = process.env.ETHEREUM_PRIVATE_KEY || '0xbaadf00dbaadf00dbaadf00dbaadf00dbaadf00dbaadf00dbaadf00dbaadf00d';
        const contractSourceRoot = path.join(__dirname, "../../source/contracts/");
        const contractOutputPath = path.join(__dirname, "../../output/contracts/contracts.json");
        const contractInterfacesOutputPath = path.join(__dirname, "../../source/libraries/ContractInterfaces.ts");
        const controllerAddress = process.env.AUGUR_CONTROLLER_ADDRESS;

        return new Configuration(host, port, gasPrice, privateKey, contractSourceRoot, contractOutputPath, contractInterfacesOutputPath, controllerAddress);
    }
}
