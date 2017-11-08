#!/usr/bin/env node

import { readFile } from "async-file";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { Connector } from '../libraries/Connector';
import { Configuration } from '../tools/Configuration';
import { AccountManager } from '../libraries/AccountManager';

// the rest of the code in this file is for running this as a standalone script, rather than as a library
async function doWork() {
    require('source-map-support').install();
    const configuration = await Configuration.create();
    const connector = new Connector(configuration);
    const accountManager = new AccountManager(configuration, connector);
    const compilerOutput = JSON.parse(await readFile(configuration.contractOutputPath, "utf8"));
    const contractDeployer = new ContractDeployer(configuration, connector, accountManager, compilerOutput);
    await contractDeployer.deploy();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
