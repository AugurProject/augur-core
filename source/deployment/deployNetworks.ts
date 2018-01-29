#!/usr/bin/env node

import { ContractDeployer } from "../libraries/ContractDeployer";
import { NetworkConfiguration } from "../libraries/NetworkConfiguration";
import { DeployerConfiguration } from "../libraries/DeployerConfiguration";

export async function deployToNetworks(networks: Array<string>) {
    const deployerConfiguration = DeployerConfiguration.create();
    for(let network of networks) {
        // Deploy sequentially
        await ContractDeployer.deployToNetwork(NetworkConfiguration.create(network), deployerConfiguration);
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
