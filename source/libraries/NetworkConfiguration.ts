import BN = require('bn.js');

type NetworkOptions = {
    isProduction: boolean;
    host: string;
    port: number;
    privateKey: string | undefined;
    gasPrice: BN;
}

type Networks = {
    [networkName: string]: NetworkOptions;
}

const networks: Networks = {
    ropsten: {
        isProduction: false,
        host: "ropsten.ethereum.nodes.augur.net",
        port: 80,
        privateKey: process.env.ROPSTEN_PRIVATE_KEY,
        gasPrice: new BN(20*1000000000)
    },
    kovan: {
        isProduction: false,
        host: "kovan.ethereum.nodes.augur.net",
        port: 80,
        privateKey: process.env.KOVAN_PRIVATE_KEY,
        gasPrice: new BN(1)
    },
    rinkeby: {
        isProduction: false,
        host: "rinkeby.ethereum.nodes.augur.net",
        port: 80,
        privateKey: process.env.RINKEBY_PRIVATE_KEY,
        gasPrice: new BN(31*1000000000)
    },
    clique: {
        isProduction: false,
        host: "clique.ethereum.nodes.augur.net",
        port: 80,
        privateKey: "fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a",
        gasPrice: new BN(1)
    },
    aura: {
        isProduction: false,
        host: "aura.ethereum.nodes.augur.net",
        port: 80,
        privateKey: "fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a",
        gasPrice: new BN(1)
    },
    environment: {
        isProduction: process.env.PRODUCTION === "true" || false,
        host: process.env.ETHEREUM_HOST || "localhost",
        port: (typeof process.env.ETHEREUM_PORT === "string") ? parseInt(process.env.ETHEREUM_PORT!) : 8545,
        privateKey: process.env.ETHEREUM_PRIVATE_KEY,
        gasPrice: ((typeof process.env.ETHEREUM_GAS_PRICE_IN_NANOETH === "undefined") ? new BN(20) : new BN(process.env.ETHEREUM_GAS_PRICE_IN_NANOETH!)).mul(new BN(1000000000))
    }
}

export class NetworkConfiguration {
    public readonly networkName: string;
    public readonly host: string;
    public readonly port: number;
    public readonly privateKey: string | undefined;
    public readonly gasPrice: BN;
    public readonly isProduction: boolean;

    public constructor(networkName: string, host: string, port: number, gasPrice: BN, privateKey: string, isProduction: boolean) {
        this.networkName = networkName;
        this.host = host;
        this.port = port;
        this.gasPrice = gasPrice;
        this.privateKey = privateKey;
        this.isProduction = isProduction;
    }

    public static create(networkName: string="environment"): NetworkConfiguration {
        const network = networks[networkName];

        if (network === undefined || network === null) throw new Error(`Network configuration ${networkName} not found`);
        if (network.privateKey === undefined || network.privateKey === null) throw new Error(`Network configuration for ${networkName} has no private key available. Check that this key is in the environment ${networkName.toUpperCase()}_PRIVATE_KEY`);

        return new NetworkConfiguration(networkName, network.host, network.port, network.gasPrice, network.privateKey, network.isProduction);
    }
}

