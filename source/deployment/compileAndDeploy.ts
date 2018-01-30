import { AccountManager } from '../libraries/AccountManager';
import { CompilerConfiguration } from '../libraries/CompilerConfiguration';
import { ContractCompiler } from '../libraries/ContractCompiler';
import { ContractDeployer } from '../libraries/ContractDeployer';
import { Connector } from '../libraries/Connector';
import { DeployerConfiguration } from '../libraries/DeployerConfiguration';
import { NetworkConfiguration } from '../libraries/NetworkConfiguration';
require('source-map-support').install();

async function doWork(): Promise<void> {
    const compilerConfiguration = CompilerConfiguration.create();
    const contractCompiler = new ContractCompiler(compilerConfiguration);
    const compiledContracts = await contractCompiler.compileContracts();

    const networkConfiguration = NetworkConfiguration.create();
    const connector = new Connector(networkConfiguration);
    const accountManager = new AccountManager(connector, networkConfiguration.privateKey);

    const deployerConfiguration = DeployerConfiguration.create();
    const contractDeployer = new ContractDeployer(deployerConfiguration, connector, accountManager, compiledContracts);
    await contractDeployer.deploy();
}

doWork().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
