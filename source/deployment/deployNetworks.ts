#!/usr/bin/env node

import { deployContracts } from "./deployContracts"
import { Configuration } from '../libraries/Configuration';

export async function deployToNetworks(networks: Array<string>) {
    for(let network of networks) {
        const configuration = Configuration.network(network);
        await deployContracts(configuration);
    }
}

if (require.main === module) {
    const networks: Array<string> = process.argv.slice(2);
    deployToNetworks(networks).then(() => {
        console.log("Deployment to all networks succeeded");
        process.exitCode = 0;
    }).catch((error) => {
        console.log("Deployment interrupted with error: ", error);
        process.exitCode = 1;
    });
}
