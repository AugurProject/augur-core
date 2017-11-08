import { Configuration } from '../tools/Configuration';
import { ContractCompiler } from "../tools/ContractCompiler";
require('source-map-support').install();

async function doWork(): Promise<void> {
    const configuration = await Configuration.create();
    const compiler = new ContractCompiler(configuration);
    await compiler.compileContracts();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
