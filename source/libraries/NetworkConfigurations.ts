import BN = require('bn.js');

export type NetworkConfiguration = {
    host: string;
    port: number;
    privateKey: string | undefined;
    gasPrice: BN;
}

export type NetworkConfigurations = {
    [networkName: string]: NetworkConfiguration;
}

export const networkConfigurations: NetworkConfigurations = {
    ropsten: {
        host: "ropsten.augur.net",
        port: 8545,
        privateKey: process.env.ROPSTEN_PRIVATE_KEY,
        gasPrice: new BN(20)
    },
    kovan: {
        host: "kovan.augur.net",
        port: 8545,
        privateKey: process.env.ROPSTEN_PRIVATE_KEY,
        gasPrice: new BN(1)
    },
    rinkeby: {
        host: "rinkeby.ethereum.origin.augur.net",
        port: 8545,
        privateKey: process.env.ROPSTEN_PRIVATE_KEY,
        gasPrice: new BN(20)
    },
    clique: {
        host: "clique.ethereum.nodes.augur.net",
        port: 80,
        privateKey: "fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a",
        gasPrice: new BN(1)
    },
    aura: {
        host: "aura.ethereum.nodes.augur.net",
        port: 80,
        privateKey: "fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a",
        gasPrice: new BN(1)
    }
}

