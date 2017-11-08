#!/usr/bin/env node

import { ContractCompiler } from "../libraries/ContractCompiler";
import { Configuration } from '../libraries/Configuration';
import { generateContractInterfaces } from '../libraries/ContractInterfacesGenerator';

async function doWork(): Promise<void> {

    const configuration = await Configuration.create();

    const compiler: ContractCompiler = new ContractCompiler(configuration);

    generateContractInterfaces(compiler, configuration);
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
