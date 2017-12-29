#!/usr/bin/env node

import { readFile } from "async-file";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { Connector } from '../libraries/Connector';
import { Configuration } from '../libraries/Configuration';
import { AccountManager } from '../libraries/AccountManager';

// the rest of the code in this file is for running this as a standalone script, rather than as a library
async function doWork() {
    require('source-map-support').install();
    const configuration = await Configuration.create();
    const connector = new Connector(configuration);
    const accountManager = new AccountManager(configuration, connector);
    console.log("Compiling contracts");
    const compilerOutput = JSON.parse(await readFile(configuration.contractOutputPath, "utf8"));
    const contractDeployer = new ContractDeployer(configuration, connector, accountManager, compilerOutput);
    console.log("Beginning deployment");
    await contractDeployer.deploy();
}

doWork().then(() => {
    process.exitCode = 0;
}).catch(error => {
    console.log(error);
    process.exitCode = 1;
});
