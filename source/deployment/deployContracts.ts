#!/usr/bin/env node

import { ContractDeployer } from "../libraries/ContractDeployer";
import { DeployerConfiguration } from '../libraries/DeployerConfiguration';
import { NetworkConfiguration } from '../libraries/NetworkConfiguration';

// the rest of the code in this file is for running this as a standalone script, rather than as a library
export async function deployContracts() {
    require('source-map-support').install();

    await ContractDeployer.deployToNetwork(NetworkConfiguration.create(), DeployerConfiguration.create());
}

deployContracts().then(() => {
    process.exitCode = 0;
}).catch(error => {
    console.log(error);
    process.exitCode = 1;
});
