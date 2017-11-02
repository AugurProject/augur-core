import { Configuration } from '../libraries/Configuration';
import { ContractCompiler } from '../libraries/ContractCompiler';
import { ContractDeployer } from '../libraries/ContractDeployer';
import { Connector } from '../libraries/Connector';
import { AccountManager } from '../libraries/AccountManager';
require('source-map-support').install();

async function doWork(): Promise<void> {
    const configuration = await Configuration.create();
    const contractCompiler = new ContractCompiler(configuration);
    const compiledContracts = await contractCompiler.compileContracts();
    const connector = new Connector(configuration);
    const accountManager = new AccountManager(configuration, connector);
    const contractDeployer = new ContractDeployer(configuration, connector, accountManager, compiledContracts);
    await contractDeployer.deploy();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
