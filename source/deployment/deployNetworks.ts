#!/usr/bin/env node

import { ContractDeployer } from "../libraries/ContractDeployer";
import { NetworkConfiguration } from "../libraries/NetworkConfiguration";
import { DeployerConfiguration } from "../libraries/DeployerConfiguration";

export async function deployToNetworks(networks: Array<string>) {
    // Create all network configs up front so that an error in any of them
    // causes us to die
    const networkConfigurations = networks.map((network) => NetworkConfiguration.create(network));
    const deployerConfiguration = DeployerConfiguration.create();
    for(let network of networkConfigurations) {
        // Deploy sequentially
        await ContractDeployer.deployToNetwork(network, deployerConfiguration);
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
