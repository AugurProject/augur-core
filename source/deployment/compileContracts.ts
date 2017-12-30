import { Configuration } from '../libraries/Configuration';
import { ContractCompiler } from "../libraries/ContractCompiler";
require('source-map-support').install();

async function doWork(): Promise<void> {
    const configuration = await Configuration.create();
    const compiler = new ContractCompiler(configuration);
    await compiler.compileContracts();
}

doWork().then(() => {
    process.exit(0);
}).catch(error => {
    console.log(error);
    process.exit(1);
});
