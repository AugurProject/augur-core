#!/usr/bin/env node

require('source-map-support').install();
import { ContractCompiler } from "../libraries/ContractCompiler";
import { CompilerConfiguration } from '../libraries/CompilerConfiguration';
import { ContractInterfaceGenerator } from '../libraries/ContractInterfacesGenerator';

async function doWork(): Promise<void> {
    const configuration = await CompilerConfiguration.create();
    const compiler: ContractCompiler = new ContractCompiler(configuration);
    const interfacesGenerator: ContractInterfaceGenerator = new ContractInterfaceGenerator(configuration, compiler);
    await interfacesGenerator.generateContractInterfaces();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit(1);
});
