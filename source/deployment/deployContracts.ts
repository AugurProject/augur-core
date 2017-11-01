#!/usr/bin/env node

import * as path from "path";
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { initializeTestRpcClientOptions } from "../libraries/HelperFunctions";
import { RpcClient } from "../libraries/RpcClient";
import { Connector } from '../libraries/Connector';
import { Configuration } from '../libraries/Configuration';

const CONTRACT_INPUT_DIR_PATH = path.join(__dirname, "../../source/contracts");
const CONTRACT_OUTPUT_DIR_PATH = path.join(__dirname, "../../output/contracts");
const COMPILED_CONTRACT_OUTPUT_FILE_NAME = "augurCore";

export async function compileAndDeployContracts(configuration: Configuration, connector: Connector): Promise<ContractDeployer> {
    // Compile contracts to a single output file
    const solidityContractCompiler = new SolidityContractCompiler(CONTRACT_INPUT_DIR_PATH, CONTRACT_OUTPUT_DIR_PATH, COMPILED_CONTRACT_OUTPUT_FILE_NAME);
    const compilerOutput = await solidityContractCompiler.compileContracts();

    // If no Ethereum host has been specified, use TestRPC.
    if (typeof process.env.ETHEREUM_HOST === "undefined") {
        const testRpcOptions = initializeTestRpcClientOptions(configuration.privateKey);
        const rpcClient = new RpcClient();
        await rpcClient.listen(configuration.httpProviderPort, testRpcOptions);
    }
    await connector.waitUntilConnected();
    const contractDeployer = new ContractDeployer(configuration, connector, compilerOutput);
    await contractDeployer.deploy();

    return contractDeployer;
}

// the rest of the code in this file is for running this as a standalone script, rather than as a library
async function runStandalone() {
    require('source-map-support').install();
    const configuration = await Configuration.create();
    const connector = new Connector(configuration);
    await compileAndDeployContracts(configuration, connector);
}

if (!module.parent) {
    runStandalone().then(() => {
        process.exit();
    }).catch(error => {
        console.log(error);
        process.exit();
    });
}
