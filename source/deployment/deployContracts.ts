#!/usr/bin/env node

import * as fs from "async-file";
import * as getPort from "get-port";
import * as path from "path";
import * as EthjsHttpProvider from "ethjs-provider-http";
import * as EthjsQuery from "ethjs-query";
import { SolidityContractCompiler } from "../libraries/CompileSolidity";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { initializeTestRpcClientOptions } from "../libraries/HelperFunctions";
import { RpcClient } from "../libraries/RpcClient";

const CONTRACT_INPUT_DIR_PATH = path.join(__dirname, "../../source/contracts");
const CONTRACT_OUTPUT_DIR_PATH = path.join(__dirname, "../../output/contracts");
const COMPILED_CONTRACT_OUTPUT_FILE_NAME = "augurCore";
const GAS_AMOUNT = 6500000; // Gas required to upload all Augur contracts
const TEST_ACCOUNT_SECRET_KEYS = ["Augur0", "Augur1", "Augur2", "Augur3", "Augur4", "Augur5", "Augur6", "Augur7", "Augur8", "Augur9"];


export async function compileAndDeployContracts(): Promise<ContractDeployer> {
    // Compile contracts to a single output file
    const solidityContractCompiler = new SolidityContractCompiler(CONTRACT_INPUT_DIR_PATH, CONTRACT_OUTPUT_DIR_PATH, COMPILED_CONTRACT_OUTPUT_FILE_NAME);
    const compilerResult = await solidityContractCompiler.compileContracts();

    const ethjsHttpProviderHost = (typeof process.env.ETHEREUM_PORT === "undefined") ? "localhost" : process.env.ETHEREUM_HOST;
    const ethjsHttpProviderPort = (typeof process.env.ETHEREUM_PORT === "undefined") ? await getPort() : parseInt(process.env.ETHEREUM_PORT || "0");
    // If no Ethereum host has been specified, use TestRPC.
    if (typeof process.env.ETHEREUM_HOST === "undefined") {
        const testRpcOptions = await initializeTestRpcClientOptions(ethjsHttpProviderPort, TEST_ACCOUNT_SECRET_KEYS);
        const rpcClient = new RpcClient();
        await rpcClient.listen(ethjsHttpProviderPort, testRpcOptions);
    }
    const ethjsHttpProvider = new EthjsHttpProvider(`http://${ethjsHttpProviderHost}:${ethjsHttpProviderPort}`);
    const ethjsQuery = new EthjsQuery(ethjsHttpProvider);
    const contractJson = await fs.readFile(CONTRACT_OUTPUT_DIR_PATH + "/" + COMPILED_CONTRACT_OUTPUT_FILE_NAME, "utf8");
    const contractDeployer = new ContractDeployer(ethjsQuery, contractJson, GAS_AMOUNT, TEST_ACCOUNT_SECRET_KEYS);
    await contractDeployer.deploy();

    return contractDeployer;
}

// If this script is not being imported by another module (i.e., it is being run independently via the command line)
if (!module.parent) {
    compileAndDeployContracts().then(() => {
        process.exit();
    }).catch(error => {
        console.log(error);
        process.exit();
    });
}
