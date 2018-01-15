import BN = require('bn.js');

export type NetworkConfiguration = {
    host: string;
    port: number;
    privateKey: string | undefined;
    gasPrice: BN;
    isProduction: boolean;
}

export type NetworkConfigurations = {
    [networkName: string]: NetworkConfiguration;
}

export const networkConfigurations: NetworkConfigurations = {
    ropsten: {
        isProduction: false,
        host: "ropsten.ethereum.nodes.augur.net",
        port: 80,
        privateKey: process.env.ROPSTEN_PRIVATE_KEY,
        gasPrice: new BN(20)
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
        gasPrice: new BN(20)
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
        host: "aura.ethereum.origin.augur.net",
        port: 8545,
        privateKey: "fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a",
        gasPrice: new BN(1)
    }
}

