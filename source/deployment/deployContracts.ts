#!/usr/bin/env node

import * as fs from 'async-file';
import * as path from 'path';
import * as HttpProvider from 'ethjs-provider-http';
import * as Eth from 'ethjs-query';
import * as EthContract from 'ethjs-contract';
import { ContractBlockchainData } from 'contract-deployment';
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { RpcClient } from "../libraries/RpcClient";


export async function compileAndDeployContracts(contractInputDirectoryPath, contractOutputDirectoryPath, contractOutputFileName, httpProviderport, gas): Promise<ContractBlockchainData[]> {
    // Compile contracts to a single output file
    const solidityContractCompiler = new SolidityContractCompiler(contractInputDirectoryPath, contractOutputDirectoryPath, contractOutputFileName);
    const compilerResult = await solidityContractCompiler.compileContracts();

    // Initialize RPC client
    const rpcClient = new RpcClient();
    await rpcClient.listen(httpProviderport);

    // Initialize Eth object
    const httpProviderUrl = "http://localhost:" + httpProviderport;
    const eth = new Eth(new HttpProvider(httpProviderUrl));
    const accounts = await eth.accounts();
    const fromAccount = accounts[0];

    // Read in contract ABIs and bytecodes as JSON string
    const contractJson = await fs.readFile(contractOutputDirectoryPath + "/" + contractOutputFileName, "utf8");

    // Deploy contracts to blockchain
    const contractDeployer = new ContractDeployer();
    const contracts = await contractDeployer.deployContracts(eth, contractJson, fromAccount, gas);

    return contracts;
}


// If this script is not being imported by another module (i.e., it is being run independently via the command line)
if (!module.parent) {
    // TODO: This script can either be run independently via the command line or be required by another file (such as a unit test).  In the future, we should probably modify it to accept commmand line parmeters instead of hard-coding the constants below.
    const contractInputDirectoryPath = path.join(__dirname, "../../source/contracts");
    const contractOutputDirectoryPath = path.join(__dirname, "../contracts");
    const contractOutputFileName = "augurCore";
    const httpProviderport = 8545;
    const gas = 3000000;

    compileAndDeployContracts(contractInputDirectoryPath, contractOutputDirectoryPath, contractOutputFileName, httpProviderport, gas).then(() => {
        process.exit();
    }).catch(error => {
        console.log(error);
        process.exit();
    });
}
