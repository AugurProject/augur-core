#!/usr/bin/env node

// TODO: This is a script that can compile/update the contracts without running any unit tests.  If we intend to have such a script, this should be modified to accept commmand line parmeters.

import * as fs from 'async-file';
import * as path from 'path';
import * as HttpProvider from 'ethjs-provider-http';
import * as Eth from 'ethjs-query';
import * as EthContract from 'ethjs-contract';
import { ContractBlockchainData } from 'contract-deployment';
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { RpcClient } from "../libraries/RpcClient";


async function compileAndDeployContracts(): Promise<ContractBlockchainData[]> {
    try {
        // Compile contracts to a single output file
        const contractInputDirectoryPath = path.join(__dirname, "../../source/contracts");
        const contractOutputDirectoryPath = path.join(__dirname, "../contracts");
        const contractOutputFileName = "augurCore";

        const solidityContractCompiler = new SolidityContractCompiler(contractInputDirectoryPath, contractOutputDirectoryPath, contractOutputFileName);
        const compilerResult = await solidityContractCompiler.compileContracts();

        // Initialize RPC client
        const port = 8545;
        const rpcClient = new RpcClient();
        await rpcClient.listen(port);

        // Initialize Eth object
        const httpProviderUrl = "http://localhost:" + port;
        const eth = new Eth(new HttpProvider(httpProviderUrl));
        const accounts = await eth.accounts();
        const fromAccount = accounts[0];

        // Read in contract ABIs and bytecodes as JSON string
        const contractJson = await fs.readFile(contractOutputDirectoryPath + "/" + contractOutputFileName, "utf8");
        const gas = 3000000;

        // Deploy contracts to blockchain
        const contractDeployer = new ContractDeployer();
        const contracts = await contractDeployer.deployContracts(eth, contractJson, fromAccount, gas);

        return contracts;
    } catch (error) {
        throw error;
    }
}

compileAndDeployContracts().then(() => {
    process.exit();
}).catch(error => {
    console.log(error);
    process.exit();
});
