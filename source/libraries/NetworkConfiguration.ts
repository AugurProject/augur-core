import BN = require('bn.js');

type NetworkOptions = {
    isProduction: boolean;
    http: string;
    ws?: string;
    privateKey?: string;
    gasPrice: BN;
}

type Networks = {
    [networkName: string]: NetworkOptions;
}

const networks: Networks = {
    ropsten: {
        isProduction: false,
        http: "http://ropsten.ethereum.nodes.augur.net",
        privateKey: process.env.ROPSTEN_PRIVATE_KEY,
        gasPrice: new BN(20*1000000000)
    },
    kovan: {
        isProduction: false,
        http: "http://kovan.ethereum.nodes.augur.net",
        privateKey: process.env.KOVAN_PRIVATE_KEY,
        gasPrice: new BN(1)
    },
    rinkeby: {
        isProduction: false,
        http: "https://rinkeby.augur.net/ethereum-http",
        ws: "wss://rinkeby.augur.net/ethereum-ws",
        privateKey: process.env.RINKEBY_PRIVATE_KEY,
        gasPrice: new BN(31*1000000000)
    },
    clique: {
        isProduction: false,
        http: "http://clique.ethereum.nodes.augur.net",
        privateKey: process.env.CLIQUE_PRIVATE_KEY || "fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a",
        gasPrice: new BN(1)
    },
    aura: {
        isProduction: false,
        http: "http://aura.ethereum.nodes.augur.net",
        privateKey: process.env.AURA_PRIVATE_KEY || "fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a",
        gasPrice: new BN(1)
    },
    environment: {
        isProduction: process.env.PRODUCTION === "true" || false,
        http: process.env.ETHEREUM_HTTP || "http://localhost:8545",
        ws: process.env.ETHEREUM_WS || "http://localhost:8546",
        privateKey: process.env.ETHEREUM_PRIVATE_KEY || "fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a",
        gasPrice: ((typeof process.env.ETHEREUM_GAS_PRICE_IN_NANOETH === "undefined") ? new BN(20) : new BN(process.env.ETHEREUM_GAS_PRICE_IN_NANOETH!)).mul(new BN(1000000000))
    },
    testrpc: {
        isProduction: false,
        http: "http://localhost:18545",
        gasPrice: new BN(1)
    }
}

export class NetworkConfiguration {
    public readonly networkName: string;
    public readonly http: string;
    public readonly ws?: string;
    public readonly privateKey?: string;
    public readonly gasPrice: BN;
    public readonly isProduction: boolean;

    public constructor(networkName: string, http: string, ws: string | undefined, gasPrice: BN, privateKey: string | undefined, isProduction: boolean) {
        this.networkName = networkName;
        this.http = http;
        this.ws = ws;
        this.gasPrice = gasPrice;
        this.privateKey = privateKey;
        this.isProduction = isProduction;
    }

    public static create(networkName: string="environment", validatePrivateKey: boolean=true): NetworkConfiguration {
        const network = networks[networkName];

        if (network === undefined || network === null) throw new Error(`Network configuration ${networkName} not found`);
        if (validatePrivateKey && (network.privateKey === undefined || network.privateKey === null)) throw new Error(`Network configuration for ${networkName} has no private key available. Check that this key is in the environment ${networkName == "environment" ? "ETHEREUM" : networkName.toUpperCase()}_PRIVATE_KEY`);

        return new NetworkConfiguration(networkName, network.http, network.ws, network.gasPrice, network.privateKey, network.isProduction);
    }
}

