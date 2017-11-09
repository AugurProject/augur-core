#!/usr/bin/env node

import { ContractCompiler } from "../libraries/ContractCompiler";
import { Configuration } from '../libraries/Configuration';
import { ContractInterfaceGenerator } from '../libraries/ContractInterfacesGenerator';

async function doWork(): Promise<void> {

    const configuration = await Configuration.create();

    const compiler: ContractCompiler = new ContractCompiler(configuration);

    const interfacesGenerator: ContractInterfaceGenerator = new ContractInterfaceGenerator(configuration, compiler);

    interfacesGenerator.generateContractInterfaces();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
