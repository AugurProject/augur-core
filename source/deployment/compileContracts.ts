import { CompilerConfiguration } from '../libraries/CompilerConfiguration';
import { ContractCompiler } from "../libraries/ContractCompiler";
require('source-map-support').install();

async function doWork(): Promise<void> {
    const configuration = CompilerConfiguration.create();
    const compiler = new ContractCompiler(configuration);
    await compiler.compileContracts();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
